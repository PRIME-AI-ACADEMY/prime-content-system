# -*- coding: utf-8 -*-
"""Общие функции carousel-lab: бренд, шрифт, детекция лица, контрольный лист.
Импортируется из build_c.py и run_h.py. Работает на Mac и Windows (только os.path, без shell).
"""
import io
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

LAB = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350

# Кодировка консоли: на Windows cp1251 ломает print кириллицы
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_BRAND = {
    "bg": "#00311e",       # pine — фон
    "text": "#fef7e5",     # cream — основной текст
    "accent": "#e8b96a",   # gold — акцент/номер/кикер
    "font": os.path.join("fonts", "Montserrat-VF.ttf"),
    "font_name": "Montserrat",
}


# ---------- цвета ----------

def _glyph_bytes(ft, ch):
    from PIL import Image, ImageDraw
    im = Image.new("L", (160, 160), 0)
    ImageDraw.Draw(im).text((8, 8), ch, font=ft, fill=255)
    return im.tobytes()

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(rgb_a, rgb_b):
    la, lb = luminance(rgb_a), luminance(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


# ---------- пути ----------
def resolve(path, base_dirs):
    """Относительный путь ищем по списку папок (папка JSON, папка лаборатории, cwd)."""
    if not path:
        return None
    if os.path.isabs(path):
        return path
    for b in base_dirs:
        p = os.path.normpath(os.path.join(b, path))
        if os.path.exists(p):
            return p
    return os.path.normpath(os.path.join(base_dirs[0], path))


# ---------- бренд ----------
def parse_design_system(md_path):
    """Вытаскиваем HEX-цвета, имя шрифта/путь к TTF и ник из profile/design-system.md.
    Эвристика: строка с «фон/background» → bg, «акцент/accent/маркер/gold» → accent,
    «текст/text/cream/беж» → text. Нет подсказок → порядок появления: bg, text, accent."""
    text = open(md_path, "r", encoding="utf-8", errors="replace").read()
    brand = dict(DEFAULT_BRAND)
    found = {}
    hexes_in_order = []
    for line in text.splitlines():
        hx = re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", line)
        if not hx:
            continue
        low = line.lower()
        for h in hx:
            hexes_in_order.append("#" + h)
        h0 = "#" + hx[0]
        if "bg" not in found and re.search(r"фон|background|base", low):
            found["bg"] = h0
        elif "accent" not in found and re.search(r"акцент|accent|маркер|gold|золот", low):
            found["accent"] = h0
        elif "text" not in found and re.search(r"текст|text|cream|беж|слонов", low):
            found["text"] = h0
        elif "card" not in found and re.search(r"карточк|card|плашк", low):
            found["card"] = h0
    if "card" in found:
        brand["card"] = found.pop("card")
    order = [h for h in hexes_in_order if h not in found.values()]
    for key in ("bg", "text", "accent"):
        if key in found:
            brand[key] = found[key]
        elif order:
            brand[key] = order.pop(0)
    m = re.search(r"([\w./\\ \-]+\.(?:ttf|otf))", text)
    if m:
        brand["font"] = m.group(1).strip()
    m = re.search(r"(Montserrat|Inter|Manrope|Roboto|Lora|Playfair|Unbounded|Golos|Onest)", text, re.I)
    if m:
        brand["font_name"] = m.group(1)
    m = re.search(r"(@[A-Za-z0-9_.]{3,})", text)
    if m:
        brand["handle"] = m.group(1)
    return brand


def load_brand(spec, base_dirs):
    """brand = объект {bg,text,accent,font} или строка-путь к design-system.md."""
    b = spec.get("brand")
    if isinstance(b, str):
        p = resolve(b, base_dirs)
        if not os.path.isfile(p):
            sys.exit_code = 5
            raise FileNotFoundError("Нет файла дизайн-системы: " + p)
        brand = parse_design_system(p)
        base_dirs = [os.path.dirname(p)] + list(base_dirs)
    else:
        brand = dict(DEFAULT_BRAND)
        brand.update(b or {})
    brand["font"] = resolve(brand.get("font") or DEFAULT_BRAND["font"], base_dirs)
    for k in ("bg", "text", "accent"):
        if isinstance(brand[k], str):
            brand[k] = hex_to_rgb(brand[k])
    if contrast(brand["text"], brand["bg"]) < 3.0:
        print("[warn] текст и фон бренда почти одного тона (контраст {:.1f}) — "
              "слайды будут нечитаемыми, проверь design-system".format(contrast(brand["text"], brand["bg"])))
    return brand


# ---------- шрифт ----------
_FONT_CACHE = {}


def font(path, weight, size):
    """Montserrat variable (или любой TTF). weight 400..900 работает для variable-шрифтов."""
    key = (path, int(weight), int(size))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    ft = ImageFont.truetype(path, int(size))
    try:
        ft.set_variation_by_axes([int(weight)])
    except Exception:
        pass
    _FONT_CACHE[key] = ft
    return ft


def check_font_file(path):
    if not path or not os.path.isfile(path) or os.path.getsize(path) < 100_000:
        return ("Нет шрифта {} (или файл битый, < 100 КБ). Скачай Montserrat:\n"
                '  curl -sL -o "fonts/Montserrat-VF.ttf" '
                '"https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"\n'
                "  (Windows PowerShell: curl.exe вместо curl)").format(path)
    return None


def missing_glyphs(font_path, text, size=40):
    """Тофу-проверка: символ, чей растр совпадает с .notdef, считаем отсутствующим."""
    ft = font(font_path, 700, size)
    notdef = _glyph_bytes(ft, "\U0010FFFF")
    bad = set()
    for ch in set(text):
        if ch.isspace():
            continue
        try:
            if _glyph_bytes(ft, ch) == notdef:
                bad.add(ch)
        except Exception:
            bad.add(ch)
    return sorted(bad)


# ---------- детекция лица (OpenCV Haar) ----------
FACE_PAD = 40
_CASCADE = None
HAAR_NAME = "haarcascade_frontalface_default.xml"
HAAR_URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/" + HAAR_NAME


def cascade():
    global _CASCADE
    if _CASCADE is not None:
        return _CASCADE or None
    try:
        import cv2
    except ImportError:
        print("[warn] OpenCV не установлен — лица не проверяю. Поставь: "
              'python -m pip install "opencv-python-headless<5" (в OpenCV 5 нет CascadeClassifier)')
        _CASCADE = False
        return None
    cands = []
    if hasattr(cv2, "data") and getattr(cv2.data, "haarcascades", ""):
        cands.append(os.path.join(cv2.data.haarcascades, HAAR_NAME))
    cands.append(os.path.join(LAB, "fonts", HAAR_NAME))
    cands.append(os.path.join(os.path.dirname(LAB), "fonts", HAAR_NAME))  # fonts/ в корне проекта (tools/../fonts)
    cands.append(os.path.join(os.getcwd(), "fonts", HAAR_NAME))            # fonts/ текущей папки
    cands.append(os.path.join(os.getcwd(), HAAR_NAME))
    cands.append(os.path.join(os.path.expanduser("~"), ".reels-fonts", HAAR_NAME))
    path = next((p for p in cands if os.path.isfile(p)), None)
    if not path or not hasattr(cv2, "CascadeClassifier"):
        print("[warn] Haar-каскад не найден — лица не проверяю. Скачай в fonts/:\n  " + HAAR_URL)
        _CASCADE = False
        return None
    _CASCADE = cv2.CascadeClassifier(path)
    return _CASCADE


def faces(img, min_size=90):
    """Список bbox лиц (x,y,w,h) на PIL-картинке. Пусто — не найдено. None — детектора нет."""
    c = cascade()
    if c is None:
        return None
    import cv2
    import numpy as np
    gray = cv2.equalizeHist(cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY))
    det = c.detectMultiScale(gray, 1.1, 5, minSize=(min_size, min_size))
    return [tuple(int(v) for v in f) for f in det]


def face_box(img):
    """Объединённый bbox лиц + запас, или None (не найдено / детектора нет)."""
    fs = faces(img)
    if not fs:
        return None
    x0 = max(0, min(x for x, y, w, h in fs) - FACE_PAD)
    y0 = max(0, min(y for x, y, w, h in fs) - FACE_PAD)
    x1 = min(img.width, max(x + w for x, y, w, h in fs) + FACE_PAD)
    y1 = min(img.height, max(y + h for x, y, w, h in fs) + FACE_PAD)
    return (x0, y0, x1, y1)


def hit(a, b):
    return bool(a and b and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3])


# ---------- контрольный лист ----------
def contact_sheet(images, path, marks=None, cols=4, thumb_w=360, label_font=None):
    """00-contact.jpg: сетка слайдов. marks[i] = {"face": box, "zone": box, "ok": bool, "label": str}."""
    n = len(images)
    if n == 0:
        return
    cols = min(cols, n)
    rows = (n + cols - 1) // cols
    tw = thumb_w
    th = int(tw * H / W)
    pad = 16
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + 28) + pad), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(images):
        c = im.convert("RGB").resize((W, H)) if im.size != (W, H) else im.convert("RGB").copy()
        cd = ImageDraw.Draw(c)
        m = (marks or {}).get(i) or {}
        if m.get("face"):
            cd.rectangle(list(m["face"]), outline=(255, 40, 40), width=8)
        if m.get("zone"):
            cd.rectangle(list(m["zone"]), outline=(255, 0, 0) if m.get("ok") is False else (232, 185, 106), width=8)
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + pad + 28)
        sheet.paste(c.resize((tw, th), Image.LANCZOS), (x, y))
        label = m.get("label") or "{:02d}".format(i + 1)
        col = (255, 90, 90) if m.get("ok") is False else (220, 220, 220)
        d.text((x, y + th + 6), label, fill=col, font=label_font)
    sheet.save(path, quality=88)
    return path


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    for k in ("type", "slides"):
        if k not in spec:
            raise ValueError("В JSON нет поля «{}»".format(k))
    spec.setdefault("name", os.path.splitext(os.path.basename(path))[0])
    spec.setdefault("route", {"T2": "H"}.get(spec["type"], "C"))
    for i, s in enumerate(spec["slides"], 1):
        s.setdefault("n", i)
        s.setdefault("role", "cover" if i == 1 else ("cta" if i == len(spec["slides"]) else "body"))
    return spec
