#!/usr/bin/env python3
"""
Безопасный текстовый оверлей на рилс (вертикаль 9:16) + АВТОМАТИЧЕСКАЯ проверка «текст не на лице».

Решает четыре вечные проблемы:
  1) текст сверху нечитаемый  -> всегда кладём СИЛЬНЫЙ градиент сверху;
  2) текст лезет на лицо      -> лицо ищется детектором на кадрах исходника (каждые 0.5 с),
     строится ЗАПРЕТНАЯ ЗОНА (объединённый bbox всех лиц + 40 px), и верхний блок
     размещается строго над ней: сначала уменьшаем шрифты, потом убираем подпись,
     потом переносим блок в нижнюю свободную зону над плашкой;
  3) нижний текст вылезает за плашку -> CTA авто-вписывается ВНУТРЬ плашки, плашка не пересекает лицо;
  4) «на глаз» никто не проверяет -> ПОСЛЕ рендера скрипт сам достаёт 3 кадра (10/50/90 %),
     снова ищет лица и сравнивает с зонами текста. Пересечение → [FAIL] и код выхода 3.
     Контрольный лист out.check.jpg сохраняется ВСЕГДА — его смотрит участник.

Почему PNG-оверлей, а не drawtext: многие сборки ffmpeg (Homebrew в т.ч.) БЕЗ libfreetype.
Почему Montserrat-VF: системные Montserrat-*.ttf БЕЗ кириллицы (квадраты-«тофу»).

Запуск:
  python3 build_reel.py --src <video.mp4> --out <out.mp4> --config <text.json>
  python3 build_reel.py --src ... --out ... \
     --kicker "БЕСПЛАТНО · 16 СЕНТЯБРЯ" --l1 "СЕГОДНЯ" --l2 "ХАКАТОН ПО AI" \
     --sub "покажу, как я автоматизировала блог и продажи" --cta "Пиши «ХАКАТОН» и регистрируйся"
  Windows: python вместо python3, пути в кавычках.

Флаги: --no-face-check (без детекции, старое поведение с --head_top),
       --head_top N (ручной предел нижней границы верхнего блока; с детекцией — дополнительное ограничение).

text.json (все поля опциональны):
  {"kicker":"...", "l1":"...", "l2":"...", "sub":"...", "cta":"...", "handle":"@angelinaa.kh", "head_top": 330}

Портативность (Mac и Windows):
  Шрифт: ./brand/assets/fonts/Montserrat-VF.ttf → ./fonts/Montserrat-VF.ttf → пути Ангелины → ~/.reels-fonts/.
  Ник: --handle > REEL_HANDLE > HANDLE= в .studio-env (текущая папка) > @angelinaa.kh.
  Детектор лиц: opencv-python-headless (<5 — с Haar-каскадом). Каскад ищется в cv2.data, потом в
  ~/.reels-fonts/, потом скачивается сам. Нет cv2 — печатает команду установки и работает без детекции.

Коды выхода: 0 ок · 2 нет шрифта · 3 текст на лице после рендера · 4 лицо занимает весь кадр.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
FONT_NAME = "Montserrat-VF.ttf"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"
HOME = os.path.expanduser("~")
SHARED_DIR = os.path.join(HOME, ".reels-fonts")           # общие ассеты: шрифт, каскад, модель
VF_CANDIDATES = [
    os.path.join("brand", "assets", "fonts", FONT_NAME),          # проект участника
    os.path.join("fonts", FONT_NAME),                             # простой проект
    "/Users/angelinahudakova/Claude/brand/assets/fonts/Montserrat-VF.ttf",
    "/Users/angelinahudakova/Claude/reels-lab/deck-assets/Montserrat-VF.ttf",
    os.path.join(SHARED_DIR, FONT_NAME),                          # общий запасной
]
DEFAULT_HANDLE = "@angelinaa.kh"
PINE, CREAM, GOLD = (0, 49, 30), (254, 247, 229), (232, 185, 106)
FACE_PAD = 40           # запас вокруг лиц, px
SAMPLE_FPS = 2          # кадр каждые 0.5 с
SCALE_VF = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"

HAAR_NAME = "haarcascade_frontalface_default.xml"
HAAR_URL = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/" + HAAR_NAME
YUNET_NAME = "face_detection_yunet_2023mar.onnx"
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/" + YUNET_NAME

# ------------------------------------------------------------------ шрифт / окружение
def vf_path():
    for p in VF_CANDIDATES:
        if os.path.isfile(p) and os.path.getsize(p) > 100_000:   # < 100 КБ — страница ошибки, не шрифт
            return p
    d = SHARED_DIR.replace("\\", "/")
    print("Montserrat-VF.ttf не найден — кириллица без него не отрисуется (будут квадраты).\n"
          "Скачай шрифт одной командой и запусти скрипт снова:\n"
          f'  mkdir -p "{d}" && curl -sL -o "{d}/{FONT_NAME}" "{FONT_URL}"\n'
          "(Windows PowerShell: вместо curl пиши curl.exe; в Git Bash команда та же.)\n"
          "Или положи файл в brand/assets/fonts/ или fonts/ рядом с проектом.", file=sys.stderr)
    sys.exit(2)

_VF = None
def _vf():
    global _VF
    if _VF is None:
        _VF = vf_path()
    return _VF

def read_studio_env(path=".studio-env"):
    env = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.split("#", 1)[0].strip().strip('"').strip("'")
    except OSError:
        pass
    return env

def default_handle():
    h = os.environ.get("REEL_HANDLE", "").strip()
    if h:
        return h
    se = read_studio_env()
    h = (se.get("HANDLE") or se.get("REEL_HANDLE") or "").strip()
    if h:
        return h if h.startswith("@") else "@" + h
    return DEFAULT_HANDLE

def font(size, weight):
    f = ImageFont.truetype(_vf(), size)
    try:
        f.set_variation_by_axes([weight])   # ось веса 100..900 (кириллица есть)
    except Exception:
        pass
    return f

def _download(url, dst, what):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    print(f"[info] скачиваю {what} → {dst}", file=sys.stderr)
    urllib.request.urlretrieve(url, dst)
    return dst

# ------------------------------------------------------------------ детектор лиц
class FaceDetector:
    """Haar-каскад (opencv<5) или YuNet (opencv 5+). Если cv2 нет — self.ok=False."""
    def __init__(self):
        self.ok, self.kind, self.cv2 = False, None, None
        try:
            import cv2
        except ImportError:
            py = sys.executable.replace("\\", "/")
            print("[warn] OpenCV не установлен — работаю БЕЗ детекции лиц (только правило head_top).\n"
                  "       Поставь один раз и запусти снова:\n"
                  f'         "{py}" -m pip install "opencv-python-headless<5"\n'
                  "       (Mac: python3 -m pip ... ; venv: ~/.reels-venv/bin/python -m pip ... ;\n"
                  "        Windows: python -m pip ... ; venv: ~/.reels-venv/Scripts/python.exe -m pip ...)",
                  file=sys.stderr)
            return
        self.cv2 = cv2
        force = os.environ.get("REEL_FACE_DETECTOR", "").lower()
        try:
            if hasattr(cv2, "CascadeClassifier") and force != "yunet":
                cands = [os.path.join(cv2.data.haarcascades, HAAR_NAME) if hasattr(cv2, "data") else "",
                         os.path.join(SHARED_DIR, HAAR_NAME)]
                path = next((p for p in cands if p and os.path.isfile(p)), None) \
                    or _download(HAAR_URL, os.path.join(SHARED_DIR, HAAR_NAME), "Haar-каскад лиц (0.9 МБ)")
                self.det = cv2.CascadeClassifier(path)
                if self.det.empty():
                    raise RuntimeError("каскад не загрузился: " + path)
                self.kind = "haar"
            elif hasattr(cv2, "FaceDetectorYN"):
                path = os.path.join(SHARED_DIR, YUNET_NAME)
                if not os.path.isfile(path):
                    _download(YUNET_URL, path, "модель YuNet (0.2 МБ)")
                self.det = cv2.FaceDetectorYN.create(path, "", (W, H), 0.7, 0.3, 500)
                self.kind = "yunet"
            else:
                raise RuntimeError("в этой сборке cv2 нет ни CascadeClassifier, ни FaceDetectorYN")
            self.ok = True
        except Exception as e:  # noqa
            print(f"[warn] детектор лиц не запустился ({e}) — работаю БЕЗ детекции.", file=sys.stderr)

    def faces(self, img_path):
        """→ список (x0, y0, x1, y1) в координатах 720×1280."""
        cv2 = self.cv2
        img = cv2.imread(img_path)
        if img is None:
            return []
        if img.shape[1] != W or img.shape[0] != H:
            img = cv2.resize(img, (W, H))
        out = []
        if self.kind == "haar":
            gray = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            for (x, y, w, h) in self.det.detectMultiScale(gray, 1.1, 5, minSize=(56, 56)):
                out.append((int(x), int(y), int(x + w), int(y + h)))
        else:
            self.det.setInputSize((W, H))
            _, res = self.det.detect(img)
            for r in (res if res is not None else []):
                x, y, w, h = map(int, r[:4])
                out.append((max(0, x), max(0, y), min(W, x + w), min(H, y + h)))
        return out

def video_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def extract_frames(src, tmp, fps=SAMPLE_FPS, at=None):
    """Кадры исходника в геометрии рендера (720×1280). fps — каждые 1/fps с; at — список секунд."""
    paths = []
    os.makedirs(tmp, exist_ok=True)
    if at is None:
        pat = os.path.join(tmp, "f_%03d.png")
        subprocess.run(["ffmpeg", "-y", "-i", src, "-vf", f"{SCALE_VF},fps={fps}", pat,
                        "-loglevel", "error"], check=True)
        paths = sorted(os.path.join(tmp, f) for f in os.listdir(tmp) if f.startswith("f_"))
    else:
        for i, t in enumerate(at):
            p = os.path.join(tmp, f"c_{i}.png")
            subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1",
                            "-vf", SCALE_VF, p, "-loglevel", "error"], check=True)
            if os.path.isfile(p):
                paths.append(p)
    return paths

def union(boxes, pad=0):
    if not boxes:
        return None
    x0 = max(0, min(b[0] for b in boxes) - pad); y0 = max(0, min(b[1] for b in boxes) - pad)
    x1 = min(W, max(b[2] for b in boxes) + pad); y1 = min(H, max(b[3] for b in boxes) + pad)
    return (x0, y0, x1, y1)

def intersects(a, b):
    return a and b and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

# ------------------------------------------------------------------ оверлей
SIDE = 56
MAXW = W - 2 * SIDE
PLATE_H, PLATE_X0, PLATE_X1, PLATE_PAD = 106, 48, 672, 28
PLATE_Y0_DEFAULT = 1044     # плашка и ник ниже этого не опускаются (низ ~250 px — интерфейс Instagram)
IG_TOP = 200                # верхние ~200 px перекрывает интерфейс Instagram — текст стартует не выше
IG_TOP_MIN = 60             # абсолютный минимум старта, только с предупреждением
DEFAULT_HEAD_TOP = 330      # предел верхнего блока, когда детекции нет

def build_overlay(cfg, out_png, forbid=None):
    """Рисует оверлей. forbid — запретная зона (x0,y0,x1,y1) или None.
    Возвращает список зон текста [(name, box)]."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    zones = []

    def measure(t, f):
        bb = d.textbbox((0, 0), t, font=f); return bb[2] - bb[0]
    def fit(t, maxw, weight, start, mins=18):
        s = max(start, mins)
        while s > mins and measure(t, font(s, weight)) > maxw:
            s -= 2
        return font(s, weight)

    # --- макет верхнего блока: список (ключ, font, fill, gap_after)
    def block_layout(scale, with_sub):
        items = []
        if cfg.get("kicker"):
            items.append(("kicker", fit(cfg["kicker"], MAXW, 600, int(28 * scale)), GOLD, int(40 * scale)))
        if cfg.get("l1"):
            f = fit(cfg["l1"], MAXW, 800, int(80 * scale)); items.append(("l1", f, CREAM, f.size + int(14 * scale)))
        if cfg.get("l2"):
            f = fit(cfg["l2"], MAXW, 800, int(54 * scale)); items.append(("l2", f, GOLD, f.size + int(12 * scale)))
        if with_sub and cfg.get("sub"):
            items.append(("sub", fit(cfg["sub"], MAXW, 600, int(26 * scale)), CREAM, int(34 * scale)))
        return items
    def block_h(items):
        return sum(g for _, _, _, g in items)

    # --- плашка CTA: не пересекает лицо
    plate = None
    if cfg.get("cta"):
        py0 = PLATE_Y0_DEFAULT
        plate = (PLATE_X0, py0, PLATE_X1, py0 + PLATE_H)
        if intersects(plate, forbid):
            down = forbid[3] + 16                                  # под лицом, но не ниже дефолта (зона IG)
            up = forbid[1] - 16 - PLATE_H                          # над лицом
            if down <= PLATE_Y0_DEFAULT:
                py0 = down
            elif up >= 420:                                        # не залезать в верхний блок
                py0 = up
            else:
                print("[warn] плашка CTA пересекает лицо, некуда сдвинуть — оставляю снизу, проверь out.check.jpg",
                      file=sys.stderr)
            plate = (PLATE_X0, py0, PLATE_X1, py0 + PLATE_H)

    # --- ПРАВИЛО 2: верхний блок ВЫШЕ запретной зоны, но НЕ в зоне интерфейса Instagram.
    # Приоритет: (1) старт y=IG_TOP, целиком над лицом; (2) уменьшить шрифт / убрать sub;
    # (3) только потом поднимать старт выше IG_TOP (до IG_TOP_MIN) с предупреждением;
    # (4) с детекцией — нижняя свободная зона над плашкой; иначе — код 4.
    top_limit = forbid[1] if forbid else DEFAULT_HEAD_TOP          # нижняя граница разрешённого места
    if cfg.get("head_top") is not None:
        top_limit = min(top_limit, cfg["head_top"])
    SCALES = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)

    def fit_top(y0):
        for with_sub in (True, False):
            for sc in SCALES:
                cand = block_layout(sc, with_sub)
                if not cand or y0 + block_h(cand) <= top_limit:
                    return cand
        return None

    placement, items, y_top = "top", fit_top(IG_TOP), IG_TOP
    if items is None:                                              # (3) выше IG_TOP — с предупреждением
        for y0 in range(IG_TOP - 20, IG_TOP_MIN - 1, -20):
            items = fit_top(y0)
            if items is not None:
                y_top = y0
                print(f"[warn] текст в зоне интерфейса Instagram (старт y={y0} < {IG_TOP}) — "
                      "над лицом мало места; укороти строки, если важно.", file=sys.stderr)
                break
    if items is None and forbid is not None:                       # (4) нижняя свободная зона над плашкой
        bottom_limit = (plate[1] - 16) if plate else (PLATE_Y0_DEFAULT - 16)
        free_y0 = forbid[3] + 16
        for with_sub in (True, False):
            for sc in SCALES:
                cand = block_layout(sc, with_sub)
                if free_y0 + block_h(cand) <= bottom_limit:
                    items, placement, y_top = cand, "bottom", free_y0; break
            if items is not None:
                break
    if items is None:
        if forbid is not None:
            print("[FAIL] лицо занимает весь кадр — тексту негде встать. Возьми другой клип "
                  "или укороти текст (только l1 без kicker/sub).", file=sys.stderr)
            sys.exit(4)
        items, y_top = block_layout(0.4, False), IG_TOP_MIN       # без детекции не падаем: минимум + warn
        print(f"[warn] верхний текст не помещается выше head_top={top_limit} даже мелко — "
              "лицо не проверялось (нет детекции). Укороти строки и проверь кадр.", file=sys.stderr)
    if placement == "bottom":
        print(f"[info] верхняя зона занята лицом (y≥{forbid[1]}) — переношу текст вниз, y={y_top}", file=sys.stderr)
    if cfg.get("sub") and not any(k == "sub" for k, _f, _c, _g in items):
        print("[info] подпись (sub) убрана — не помещалась над лицом", file=sys.stderr)

    # --- ПРАВИЛО 1: сильный градиент сверху (тёмный -> прозрачный), и снизу под плашку/текст
    TG = 540 if placement == "top" else 420
    g = Image.new("RGBA", (W, TG), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(TG):
        gd.line([(0, y), (W, y)], fill=(0, 15, 9, int(250 * (1 - y / TG) ** 1.1)))
    img.alpha_composite(g, (0, 0))
    BG = 360 if placement == "top" else min(720, H - y_top + 60)
    b = Image.new("RGBA", (W, BG), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
    for y in range(BG):
        bd.line([(0, y), (W, y)], fill=(0, 17, 10, int(200 * (y / BG) ** 1.3)))
    img.alpha_composite(b, (0, H - BG))

    def ctr(y, t, f, fill, name, shadow=True):
        x = (W - measure(t, f)) / 2
        if shadow:
            for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2), (0, 3)):
                d.text((x + dx, y + dy), t, font=f, fill=(0, 12, 7, 210))
        d.text((x, y), t, font=f, fill=fill)
        bb = d.textbbox((x, y), t, font=f)
        zones.append((name, (int(bb[0]) - 4, int(bb[1]) - 4, int(bb[2]) + 4, int(bb[3]) + 4)))

    y = y_top
    for key, f, fill, gap in items:
        ctr(y, cfg[key], f, fill, key); y += gap

    # --- ПРАВИЛО 3: CTA внутри плашки
    if plate:
        d.rounded_rectangle(list(plate), radius=20, fill=GOLD)
        cf = fit(cfg["cta"], (plate[2] - plate[0]) - 2 * PLATE_PAD, 700, 34)
        bb = d.textbbox((0, 0), cfg["cta"], font=cf)
        cw, chh = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((W - cw) / 2, (plate[1] + plate[3]) / 2 - chh / 2 - bb[1]), cfg["cta"], font=cf, fill=PINE)
        zones.append(("cta", plate))
        hy = plate[3] + 16
    else:
        hy = H - 90
    h = cfg.get("handle") or default_handle()
    hf = font(25, 600)
    hx = (W - measure(h, hf)) / 2
    d.text((hx, hy), h, font=hf, fill=(254, 247, 229, 235))
    bb = d.textbbox((hx, hy), h, font=hf)
    zones.append(("handle", (int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3]))))

    img.save(out_png)
    return zones

def render(src, out, png):
    fc = (f"[0:v]{SCALE_VF}[bg];[bg][1:v]overlay=0:0[v]")
    cmd = ["ffmpeg", "-y", "-i", src, "-i", png, "-filter_complex", fc,
           "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium",
           "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
           "-pix_fmt", "yuv420p", out, "-loglevel", "error"]
    subprocess.run(cmd, check=True)

# ------------------------------------------------------------------ проверка после рендера
def check_after_render(src, out, zones, det, forbid, check_jpg):
    """3 кадра (10/50/90 %): лица ищем на ИСХОДНИКЕ (текст не мешает детектору),
    рисуем на кадрах ГОТОВОГО ролика. Лист сохраняется всегда. → (ok, failed_frames)"""
    dur = video_duration(out) or video_duration(src)
    ts = [max(0.0, dur * k) for k in (0.10, 0.50, 0.90)]
    tmp = tempfile.mkdtemp(prefix="reel_chk_")
    ok, failed = True, []
    try:
        src_frames = extract_frames(src, os.path.join(tmp, "s"), at=ts) if det and det.ok else []
        out_frames = extract_frames(out, os.path.join(tmp, "o"), at=ts)
        sw, sh = 360, 640
        sheet = Image.new("RGB", (sw * len(out_frames), sh + 40), (20, 20, 20))
        sd = ImageDraw.Draw(sheet)
        lab = font(18, 600)
        for i, fp in enumerate(out_frames):
            fr = Image.open(fp).convert("RGB")
            fd = ImageDraw.Draw(fr)
            faces = det.faces(src_frames[i]) if i < len(src_frames) else []
            if forbid:
                fd.rectangle(list(forbid), outline=(255, 80, 80), width=2)
            hit = False
            for fb in faces:
                fd.rectangle(list(fb), outline=(255, 40, 40), width=5)
                for name, z in zones:
                    if intersects(z, fb):
                        hit = True
                        fd.rectangle(list(z), outline=(255, 0, 0), width=6)
            for name, z in zones:
                fd.rectangle(list(z), outline=(232, 185, 106), width=3)
            if hit:
                ok = False; failed.append(i + 1)
            fr = fr.resize((sw, sh))
            sheet.paste(fr, (i * sw, 0))
            txt = f"{i+1}: {ts[i]:.1f}s  " + ("ТЕКСТ НА ЛИЦЕ" if hit else ("ок" if (det and det.ok) else "без детекции"))
            sd.text((i * sw + 10, sh + 10), txt, font=lab, fill=(255, 80, 80) if hit else (200, 230, 200))
        sheet.save(check_jpg, quality=88)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok, failed

# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config")
    for k in ("kicker", "l1", "l2", "sub", "cta", "handle"):
        ap.add_argument("--" + k)
    ap.add_argument("--head_top", type=int, help="ручной предел (px) нижней границы верхнего блока")
    ap.add_argument("--no-face-check", action="store_true", help="отключить детекцию и проверку лиц")
    a = ap.parse_args()
    _vf()   # шрифт проверяем до рендера — чтобы упасть сразу и с понятной подсказкой

    cfg = {}
    if a.config:
        cfg = json.load(open(a.config, encoding="utf-8"))
    for k in ("kicker", "l1", "l2", "sub", "cta", "handle"):
        if getattr(a, k) is not None:
            cfg[k] = getattr(a, k)
    if a.head_top is not None:
        cfg["head_top"] = a.head_top

    det, forbid = None, None
    if not a.no_face_check:
        det = FaceDetector()
        if det.ok:
            tmp = tempfile.mkdtemp(prefix="reel_faces_")
            try:
                frames = extract_frames(a.src, tmp)
                all_faces = [fb for fp in frames for fb in det.faces(fp)]
                n_with = sum(1 for fp in frames if det.faces(fp))
                forbid = union(all_faces, FACE_PAD)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
            if forbid:
                print(f"[face] лица на {n_with}/{len(frames)} кадрах ({det.kind}); запретная зона "
                      f"x{forbid[0]}–{forbid[2]}, y{forbid[1]}–{forbid[3]}", file=sys.stderr)
            else:
                print(f"[warn] лицо не найдено ни на одном из {len(frames)} кадров — размещаю по умолчанию, "
                      "посмотри out.check.jpg глазами.", file=sys.stderr)

    tmp_png = a.out + ".overlay.png"
    zones = build_overlay(cfg, tmp_png, forbid)
    render(a.src, a.out, tmp_png)
    os.remove(tmp_png)

    check_jpg = os.path.splitext(a.out)[0] + ".check.jpg"
    if det is not None and det.ok:
        ok, failed = check_after_render(a.src, a.out, zones, det, forbid, check_jpg)
        print("контрольный лист:", check_jpg)
        if not ok:
            for n in failed:
                print(f"[FAIL] текст на лице на кадре {n}", file=sys.stderr)
            print("готово с ошибкой:", a.out, "— проверь", check_jpg, file=sys.stderr)
            sys.exit(3)
        print("[ok] текст не пересекает лицо на 3 контрольных кадрах")
    else:
        check_after_render(a.src, a.out, zones, None, None, check_jpg)
        print("контрольный лист (без детекции — посмотри глазами):", check_jpg)
    print("готово:", a.out)

if __name__ == "__main__":
    main()
