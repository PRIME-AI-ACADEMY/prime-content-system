# -*- coding: utf-8 -*-
"""Маршрут C — карусель кодом (Python + Pillow, без браузера).

  python build_c.py examples/t1-text.json            (Mac: ~/.reels-venv/bin/python ...)
  python build_c.py spec.json --out out --name moya-karusel

JSON → out/<name>/slide-01..NN.png (1080×1350) + 00-contact.jpg + 00-check.jpg + report.md
Типы: T1 текст-на-фоне · T2 фото-аватар · T3 скриншоты · T4 кейс-инфографика (см. spec.schema.md).

Коды выхода: 0 ок · 2 битый JSON · 3 текст на лице · 4 контраст не вытянули · 5 нет шрифта/фото/скрина.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageOps

import lab_common as L
from lab_common import W, H

M = 92           # поле
TOP_Y = 72       # счётчик
KICK_Y = 122     # кикер
FOOT_Y = H - 78  # ник
MIN_CONTRAST = 3.0   # крупный текст: ≥3:1 (WCAG large text)

REPORT = []      # строки отчёта
MARKS = {}       # для 00-check.jpg
EXIT = 0


def note(code, msg):
    global EXIT
    print(msg)
    REPORT.append(msg)
    if code and (EXIT == 0 or code < EXIT):
        EXIT = code


# ---------- текст ----------
def parse_rich(text):
    """'5 признаков *ставить систему*' → [(word, accent)], поддерживает \\n как жёсткий перенос."""
    out = []
    accent = False
    for para_i, para in enumerate(text.split("\n")):
        if para_i:
            out.append(("\n", False))
        for tok in para.split("*"):
            for wd in tok.split():
                out.append((wd, accent))
            accent = not accent
    return out


def wrap_rich(draw, tokens, ft, maxw):
    lines, cur = [], []
    for wd, acc in tokens:
        if wd == "\n":
            lines.append(cur)
            cur = []
            continue
        trial = cur + [(wd, acc)]
        if draw.textlength(" ".join(w for w, _ in trial), font=ft) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = [(wd, acc)]
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, weight, maxw, maxh, start, minimum, lh, fontpath):
    """Уменьшаем кегль, пока блок не влезет по ширине и высоте. → (font, lines, height)."""
    tokens = parse_rich(text)
    size = start
    while True:
        ft = L.font(fontpath, weight, size)
        lines = wrap_rich(draw, tokens, ft, maxw)
        widest = max((draw.textlength(" ".join(w for w, _ in ln), font=ft) for ln in lines), default=0)
        height = int(len(lines) * size * lh)
        if (widest <= maxw and height <= maxh) or size <= minimum:
            if size <= minimum and (widest > maxw or height > maxh):
                note(0, "[warn] текст не влезает даже при {}px: «{}…»".format(minimum, text[:40]))
            return ft, lines, height
        size -= 2


def draw_rich(draw, x, y, lines, ft, col, accent, lh, align="left", maxw=None):
    for ln in lines:
        words = [w for w, _ in ln]
        lw = draw.textlength(" ".join(words), font=ft)
        cx = x + ((maxw - lw) // 2 if (align == "center" and maxw) else 0)
        for i, (wd, acc) in enumerate(ln):
            draw.text((cx, y), wd, font=ft, fill=accent if acc else col)
            cx += draw.textlength(wd + (" " if i < len(ln) - 1 else ""), font=ft)
        y += int(ft.size * lh)
    return y


# ---------- фото ----------
def cover_fit(im, w, h, focus=0.12):
    """Вписать по cover; focus=0 держим верх (лицо), 1 — низ."""
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int((im.height - h) * focus)
    return im.crop((x, y, x + w, y + h))


def scrim(img, color, side="bottom", strength=250, stop=0.66):
    mask = Image.new("L", (1, H))
    px = mask.load()
    for y in range(H):
        t = y / H if side == "bottom" else 1 - y / H
        t = (t - (1 - stop)) / stop
        px[0, y] = int(max(0.0, min(1.0, t)) ** 1.35 * strength)
    mask = mask.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), color), img, mask)


def zone_mean(img, zone):
    reg = img.crop(zone).resize((32, 32))
    px = list(reg.getdata())
    n = len(px)
    return tuple(sum(p[i] for p in px) // n for i in range(3))


def ensure_contrast(img, zone, text_rgb, bg_rgb, slide_no):
    """Контраст текста к фону зоны. Мало → подкладываем полупрозрачный бренд-фон под зону. → (img, ratio)"""
    ratio = L.contrast(text_rgb, zone_mean(img, zone))
    tries = 0
    while ratio < MIN_CONTRAST and tries < 3:
        tries += 1
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        x0, y0, x1, y1 = zone
        od.rounded_rectangle((x0 - 30, y0 - 24, x1 + 30, y1 + 24), radius=28, fill=bg_rgb + (150,))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        ratio = L.contrast(text_rgb, zone_mean(img, zone))
    if tries:
        note(0, "[contrast] слайд {}: усилил подложку под текстом ×{} (контраст {:.1f})".format(slide_no, tries, ratio))
    return img, ratio


# ---------- элементы ----------
class Ctx:
    def __init__(self, spec, brand, out_dir, base_dirs):
        self.spec, self.brand, self.out, self.base = spec, brand, out_dir, base_dirs
        self.fp = brand["font"]
        self.bg, self.tx, self.ac = brand["bg"], brand["text"], brand["accent"]
        self.muted = L.mix(self.tx, self.bg, 0.28)
        self.card = L.mix(self.bg, (255, 255, 255), 0.05)
        self.handle = spec.get("handle") or brand.get("handle") or "@ник"
        self.total = len(spec["slides"])

    def f(self, weight, size):
        return L.font(self.fp, weight, size)


def chrome(c, d, n, on_photo=False):
    """Счётчик сверху-слева, ник снизу-слева. Правые углы IG не трогаем."""
    fs = c.f(700, 26)
    d.text((M, TOP_Y), "{:02d} / {:02d}".format(n, c.total), font=fs, fill=c.ac)
    d.text((M, FOOT_Y), c.handle, font=fs, fill=c.tx)


def kicker(c, d, text, y=KICK_Y):
    if text:
        d.text((M, y), text.upper(), font=c.f(800, 28), fill=c.ac)
        return y + 28 + 24
    return y


def plaque(c, d, x, y, text):
    ft = c.f(800, 44)
    tw = d.textlength(text, font=ft)
    pad = (44, 26)
    box = (x, y, x + tw + pad[0] * 2, y + ft.size + pad[1] * 2)
    d.rounded_rectangle(box, radius=22, fill=c.ac)
    d.text((x + pad[0], y + pad[1] - 4), text, font=ft, fill=c.bg)
    return box[3]


def block_height(c, d, s, maxw, big_start=88, big_min=44, small_size=40):
    """Считаем высоту текстового блока (big + small + cta), чтобы разместить его целиком."""
    ft, lines, hb = fit_text(d, s.get("big", ""), 800, maxw, 620, big_start, big_min, 1.08, c.fp) if s.get("big") else (None, [], 0)
    hs = 0
    fs, slines = None, []
    if s.get("small"):
        fs, slines, hs = fit_text(d, s["small"], 500, maxw, 260, small_size, 28, 1.32, c.fp)
        hs += 18
    hc = 44 + 52 + 26 if s.get("cta") else 0
    return dict(ft=ft, lines=lines, hb=hb, fs=fs, slines=slines, hs=hs, hc=hc, total=hb + hs + hc)


def draw_block(c, d, s, blk, x, y, maxw, align="left"):
    if blk["lines"]:
        y = draw_rich(d, x, y, blk["lines"], blk["ft"], c.tx, c.ac, 1.08, align, maxw)
    if blk["slines"]:
        y += 18
        y = draw_rich(d, x, y, blk["slines"], blk["fs"], c.muted if blk["lines"] else c.tx, c.ac, 1.32, align, maxw)
    if s.get("cta"):
        y = plaque(c, d, x, y + 26, s["cta"])
    return y


# ---------- фото-слайд (T2 обложка/финал, любой слайд с photo) ----------
def photo_slide(c, s, n):
    p = L.resolve(s["photo"], c.base)
    if not os.path.isfile(p):
        note(5, "[fail] слайд {}: нет фото {}".format(n, p))
        return Image.new("RGB", (W, H), c.bg)
    src = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    maxw = W - 2 * M
    blk = block_height(c, probe, s, maxw, big_start=84)
    total = blk["total"]
    y_bottom = H - 150 - total
    zone_b = (M, y_bottom, W - M, y_bottom + total)
    y_top = KICK_Y + 70
    zone_t = (M, y_top, W - M, y_top + total)

    focus0 = float(s.get("focus", 0.06))
    focuses = [focus0] + [f for f in (0.0, 0.06, 0.12, 0.25, 0.4, 0.6, 0.8, 1.0) if f != focus0]
    crops = [(f, cover_fit(src, W, H, f)) for f in focuses]
    crops = [(f, im, L.face_box(im)) for f, im in crops]

    pick = None
    # 1) лицо найдено и не пересекает нижнюю зону
    for f, im, fb in crops:
        if fb and not L.hit(zone_b, fb):
            pick = (f, im, fb, "bottom", zone_b)
            break
    # 2) лицо найдено, но мешает внизу → текст наверх
    if not pick:
        for f, im, fb in crops:
            if fb and not L.hit(zone_t, fb):
                pick = (f, im, fb, "top", zone_t)
                break
    # 3) лицо не найдено ни в одном кадре — берём исходный кадр, предупреждаем
    if not pick:
        for f, im, fb in crops:
            if fb is None:
                pick = (f, im, None, "bottom", zone_b)
                note(0, "[face] слайд {}: лицо не найдено (focus={}) — проверь 00-check.jpg глазами".format(n, f))
                break
    # 4) лицо везде под текстом → нижняя треть + сильный скрим + код 3
    fail = False
    if not pick:
        f, im, fb = crops[0]
        pick = (f, im, fb, "bottom", zone_b)
        fail = True
    focus, img, face, side, zone = pick
    if side == "top" and not fail:
        note(0, "[face] слайд {}: лицо внизу — текст наверху (focus={})".format(n, focus))
    elif focus != focus0 and not fail:
        note(0, "[face] слайд {}: лицо было под текстом — кадрирую focus={}".format(n, focus))

    img = scrim(img, c.bg, side, 255 if fail else 250, 0.75 if fail else 0.66)
    img, ratio = ensure_contrast(img, zone, c.tx, c.bg, n)
    d = ImageDraw.Draw(img)
    kicker(c, d, s.get("kicker"))
    draw_block(c, d, s, blk, M, zone[1], maxw)
    chrome(c, d, n, on_photo=True)

    ok = not L.hit(zone, face) and not fail
    MARKS[n - 1] = dict(face=face, zone=zone, ok=ok, label="{:02d} {}".format(n, "ok" if ok else "ТЕКСТ НА ЛИЦЕ"))
    if ok:
        note(0, "[ok] слайд {}: текст вне лица, контраст {:.1f}".format(n, ratio))
    else:
        note(3, "[FAIL] слайд {}: ТЕКСТ НА ЛИЦЕ — поменяй фото или focus в JSON".format(n))
    if ratio < MIN_CONTRAST:
        note(4, "[FAIL] слайд {}: контраст {:.1f} < {} — текст нечитаем".format(n, ratio, MIN_CONTRAST))
    return img


# ---------- T1: текст на бренд-фоне ----------
def text_slide(c, s, n):
    img = Image.new("RGB", (W, H), c.bg)
    d = ImageDraw.Draw(img)
    y = kicker(c, d, s.get("kicker"))
    maxw = W - 2 * M
    if s["role"] == "cover":
        blk = block_height(c, d, s, maxw, big_start=100, big_min=52, small_size=44)
        y0 = max(y + 40, (H - blk["total"]) // 2 - 40)
        draw_block(c, d, s, blk, M, y0, maxw)
    elif s.get("number"):
        num = str(s["number"])
        fn, nlines, nh = fit_text(d, num, 800, maxw, 260, 230, 90, 1.0, c.fp)
        d.text((M - 6, 236), num, font=fn, fill=c.ac)
        y0 = 236 + nh + 40
        blk = block_height(c, d, s, maxw, big_start=76, big_min=40, small_size=40)
        draw_block(c, d, s, blk, M, y0, maxw)
    else:
        blk = block_height(c, d, s, maxw, big_start=84, big_min=44, small_size=42)
        y0 = max(y + 40, (H - blk["total"]) // 2 - 30)
        draw_block(c, d, s, blk, M, y0, maxw)
    chrome(c, d, n)
    MARKS[n - 1] = dict(ok=True, label="{:02d} ok".format(n))
    note(0, "[ok] слайд {}: текст на бренд-фоне".format(n))
    return img


# ---------- T3: скриншот в рамке ----------
def screen_slide(c, s, n):
    p = L.resolve(s["screenshot"], c.base)
    if not os.path.isfile(p):
        note(5, "[fail] слайд {}: нет скрина {}".format(n, p))
        return Image.new("RGB", (W, H), c.bg)
    shot = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    img = Image.new("RGB", (W, H), c.bg)
    d = ImageDraw.Draw(img)
    y = kicker(c, d, s.get("kicker"))
    maxw = W - 2 * M
    blk = block_height(c, d, s, maxw, big_start=64, big_min=36, small_size=36)
    cap_h = blk["total"]
    avail_top = y + 16
    avail_bottom = FOOT_Y - 40 - cap_h - 40
    ratio = shot.height / shot.width
    phone = ratio > 1.3
    if phone:
        sh = min(avail_bottom - avail_top, 760)
        sw = int(sh / ratio)
        sw = min(sw, maxw)
        sh = int(sw * ratio)
        sx = (W - sw) // 2
        r_out, r_in, bez = 48, 34, 14
    else:
        sw = maxw - 40
        sh = int(sw * ratio)
        if sh > avail_bottom - avail_top:
            sh = avail_bottom - avail_top
            sw = int(sh / ratio)
        sx = (W - sw) // 2
        r_out, r_in, bez = 30, 18, 12
    sy = avail_top + max(0, (avail_bottom - avail_top - sh) // 2)
    # рамка
    d.rounded_rectangle((sx - bez, sy - bez, sx + sw + bez, sy + sh + bez), radius=r_out, fill=c.card)
    d.rounded_rectangle((sx - bez, sy - bez, sx + sw + bez, sy + sh + bez), radius=r_out, outline=c.ac, width=2)
    sm = shot.resize((sw, sh), Image.LANCZOS)
    msk = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(msk).rounded_rectangle((0, 0, sw, sh), radius=r_in, fill=255)
    img.paste(sm, (sx, sy), msk)
    # подпись под скрином
    cy = sy + sh + bez + 44
    draw_block(c, d, s, blk, M, cy, maxw)
    chrome(c, d, n)
    MARKS[n - 1] = dict(ok=True, label="{:02d} ok".format(n))
    note(0, "[ok] слайд {}: скрин {} ({})".format(n, os.path.basename(p), "телефон" if phone else "карточка"))
    return img


# ---------- T4: цифры и сравнение ----------
def compare_slide(c, s, n):
    img = Image.new("RGB", (W, H), c.bg)
    d = ImageDraw.Draw(img)
    y = kicker(c, d, s.get("kicker"))
    maxw = W - 2 * M
    if s.get("big"):
        ft, lines, hb = fit_text(d, s["big"], 800, maxw, 220, 64, 40, 1.08, c.fp)
        y = draw_rich(d, M, y + 16, lines, ft, c.tx, c.ac, 1.08) + 40
    else:
        y += 40
    cmp = s["compare"]
    gap = 28
    cw = (maxw - gap) // 2
    ch = 480
    cy = max(y, 380)
    for i, key in enumerate(("left", "right")):
        item = cmp.get(key, {})
        x = M + i * (cw + gap)
        accent = (i == 1)
        fill = c.ac if accent else c.card
        d.rounded_rectangle((x, cy, x + cw, cy + ch), radius=30, fill=fill)
        if not accent:
            d.rounded_rectangle((x, cy, x + cw, cy + ch), radius=30, outline=L.mix(c.ac, c.bg, 0.5), width=2)
        tcol = c.bg if accent else c.tx
        lcol = c.bg if accent else c.ac
        d.text((x + 36, cy + 36), str(item.get("label", "")).upper(), font=c.f(800, 26), fill=lcol)
        fv, vlines, vh = fit_text(d, str(item.get("value", "")), 800, cw - 72, 160, 120, 60, 1.0, c.fp)
        draw_rich(d, x + 36, cy + 120, vlines, fv, tcol, tcol, 1.0)
        fn_, nlines, nh = fit_text(d, str(item.get("note", "")), 500, cw - 72, 150, 32, 24, 1.3, c.fp)
        draw_rich(d, x + 36, cy + 120 + vh + 30, nlines, fn_, tcol, tcol, 1.3)
    if s.get("small"):
        fs, slines, hs = fit_text(d, s["small"], 500, maxw, 160, 36, 26, 1.32, c.fp)
        draw_rich(d, M, cy + ch + 40, slines, fs, c.muted, c.ac, 1.32)
    chrome(c, d, n)
    MARKS[n - 1] = dict(ok=True, label="{:02d} ok".format(n))
    note(0, "[ok] слайд {}: сравнение".format(n))
    return img


# ---------- маршрутизация слайда ----------
def render(c, s):
    n = int(s["n"])
    txt = " ".join(str(s.get(k, "")) for k in ("kicker", "big", "small", "cta", "number"))
    bad = L.missing_glyphs(c.fp, txt)
    if bad:
        note(0, "[warn] слайд {}: в шрифте нет глифов {} — на слайде будут квадраты".format(n, "".join(bad)))
    if s.get("photo"):
        return photo_slide(c, s, n)
    if s.get("screenshot"):
        return screen_slide(c, s, n)
    if s.get("compare"):
        return compare_slide(c, s, n)
    return text_slide(c, s, n)


def main():
    ap = argparse.ArgumentParser(description="Маршрут C: JSON → PNG-слайды карусели")
    ap.add_argument("spec", help="путь к JSON-спеке карусели")
    ap.add_argument("--out", default=os.path.join(L.LAB, "out"), help="папка вывода (по умолчанию out/)")
    ap.add_argument("--name", help="имя подпапки (по умолчанию name из JSON)")
    a = ap.parse_args()

    try:
        spec = L.load_spec(a.spec)
    except Exception as e:
        print("[fail] JSON: {}".format(e))
        sys.exit(2)
    base_dirs = [os.path.dirname(os.path.abspath(a.spec)), L.LAB, os.getcwd()]
    try:
        brand = L.load_brand(spec, base_dirs)
    except FileNotFoundError as e:
        print("[fail] " + str(e))
        sys.exit(5)
    err = L.check_font_file(brand["font"])
    if err:
        print("[fail] " + err)
        sys.exit(5)

    name = a.name or spec["name"]
    out_dir = os.path.join(a.out, name)
    os.makedirs(out_dir, exist_ok=True)
    if spec.get("route") == "H":
        note(0, "[info] в JSON маршрут H (Higgsfield), собираю кодом как тест маршрута C")
    c = Ctx(spec, brand, out_dir, base_dirs)
    note(0, "[info] {} · {} · {} слайдов · шрифт {}".format(spec["type"], name, c.total, os.path.basename(brand["font"])))

    images = []
    for s in spec["slides"]:
        im = render(c, s)
        fn = os.path.join(out_dir, "slide-{:02d}.png".format(int(s["n"])))
        im.save(fn)
        images.append(im)
    L.contact_sheet(images, os.path.join(out_dir, "00-contact.jpg"), None, label_font=c.f(600, 18))
    L.contact_sheet(images, os.path.join(out_dir, "00-check.jpg"), MARKS, label_font=c.f(600, 18))
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write("# Отчёт build_c · {} · {}\n\n".format(spec["type"], name))
        fh.write("\n".join("- " + r for r in REPORT))
        fh.write("\n\nКод выхода: {}\n".format(EXIT))
    print("готово: {} слайдов → {}\nконтрольный лист: {}".format(
        len(images), out_dir, os.path.join(out_dir, "00-contact.jpg")))
    sys.exit(EXIT)


if __name__ == "__main__":
    main()
