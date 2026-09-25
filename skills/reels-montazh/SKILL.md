---
name: reels-montazh
description: "Монтаж вертикальных Reels внутри контент-завода: трек А — хук + CTA поверх клипа из clips/ (ffmpeg + Pillow, tools/build_reel.py, текст никогда не на лице), трек Б — говорящая голова через HyperFrames (паузы, субтитры фразами, вставки, CTA), финал в H.264. Читает profile/design-system.md и строку контент-плана. Триггеры: смонтируй рилс, наложи хук, монтаж, субтитры, говорящая голова, вставки, reels · M, монтаж из клипа."
---

# Reels-монтаж — правила и процесс

## Формат и вход
- Вертикаль 1080×1920, 30 fps, `.mp4`, вывод в `output/ДД.ММ-<тема>/`. Бренд — только из `profile/design-system.md`. Текст (хук, подпись, CTA) — из строки плана: D, H, F.
- Исходники: `clips/` (трек А) или один длинный файл говорящей головы (трек Б). Файлы ищи без учёта регистра: `.mp4 .MP4 .mov .MOV .m4v`. Пути — в кавычках.
- Python: `python3` (Mac) / `python` (Windows) / `~/.reels-venv/bin/python`, если venv. Кодек: Mac `h264_videotoolbox`, иначе `libx264 -preset veryfast -crf 21`.

## Два трека — главное решение
**Трек А — хук поверх клипа** (`Reels · M`). Pillow рисует прозрачный оверлей, ffmpeg накладывает. Whisper и HyperFrames не нужны. Для пачек, тестов хуков, клипов 5–15 сек.
**Трек Б — говорящая голова** (`Reels · M · говорящая голова`). HyperFrames: паузы → транскрипт → субтитры фразами → вставки → CTA → рендер → H.264. Нужен Node.js, скиллы HyperFrames, whisper-cli (Mac) или `npx hyperframes transcribe`.
Вопрос для выбора: нужна анимация и синхрон с речью? Да → Б. Нет → А.
Формат (в) — аватар Higgsfield (`Reels · S`) — делает не этот скилл, а `reels` через облако.

## Подготовка видео (оба трека)
- Горизонтальные — не растягивать: `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`.
- Проверь звук: `ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 <файл>`. Пусто → подмешай `-f lavfi -t <D> -i anullsrc=r=44100:cl=stereo`.
- 4K → сначала даунскейл до 1080×1920. Клип короче цели — бери целиком.

## Трек А — текст на видео: три правила
1. **Градиент сверху всегда**: цвет фона бренда → прозрачный, ~800 px, под верхним текстом; плюс градиент снизу ~540 px под плашку.
2. **Хук высоко, не на лице**: блок с y≈120 (кикер → строка 1 → строка 2 акцентом → подпись), кегль уменьшается до ширины 1080−2×80, низ блока не ниже зоны лица. Ключевое слово — подчёркивание акцентом.
3. **CTA внутри плашки**: акцентная плашка, скругление 30 px, y 1560–1720, текст с полями 40 px, @ник по центру под плашкой. Плашка не наезжает на ник: если ник ниже — подними плашку (top ≈1120 px при субтитрах у лица).

Накладывай только через `tools/build_reel.py` (копия из `${CLAUDE_PLUGIN_ROOT}/templates/montage/tools/build_reel.py`):
`$PY tools/build_reel.py --src "<клип>" --out "output/…/reel.mp4" --kicker "…" --l1 "…" --l2 "…" --sub "…" --cta "<CTA из F>" --handle "<ник>"`.
Скрипт сам находит лица (OpenCV `<5`, каскад в `fonts/` или `~/.reels-fonts/`), строит запретную зону, ставит блок над ней, рендерит, проверяет 3 кадра и пишет `<имя>.check.jpg` всегда.
Коды выхода: 0 ок · 2 нет шрифта · 3 текст на лице → укороти строки или другой клип · 4 лицо на весь кадр → другой клип · 5 нет детектора → поставь `opencv-python-headless<5` и каскад; `--no-face-check` только с обязательным просмотром `.check.jpg` глазами.
**Ложные лица**: Haar находит «лица» на листьях и орхидеях. Код 3 на клипе без человека → другой клип или `--no-face-check` + проверка `.check.jpg`.

## Трек Б — говорящая голова (HyperFrames)
1. **Паузы.** `silencedetect noise=-45dB:d=0.4` (при −30 дБ тихая речь режется как пауза). Режь только паузы > 0.4 с с запасом 0.2 с по краям, плюс пустые начало и хвост. Сверь срезы с таймкодами whisper: срез не должен попадать внутрь слова. Собери `cut.mp4` одним ffmpeg.
2. **Транскрипт** с нарезанного `cut.mp4`: `whisper-cli -m ~/.whisper-models/ggml-medium-q5_0.bin -l ru` (Windows: `npx hyperframes transcribe`). Вычитай термины («промд» → «промпт»), покажи текст человеку.
3. **Хук и тезисы**: заголовок ≤6 слов, 2–4 тезиса для вставок — показать до сборки.
4. **Кадры лица** на 5 таймкодах → `faces.json`; лицо двигается, субтитры и чипы считай от него.
5. **Композиция** (генерируй скриптом из транскрипта): видео фон → субтитры фразами 2–3 слова над головой (top ≈210 px, Montserrat 900 ≈58 px, ключевые слова акцентом, сдвиг +0.15 с) → 2–4 полноэкранные вставки по 2–3 с (бренд-панель, `gsap.fromTo` от opacity 0, субтитры поверх) → чипы на торс → лёгкий зум 1.0→1.06 → @ник + прогресс-бар → CTA-плашка (top ≈1120 px, не на нике). Каждый `<audio>` с `id`, `class="clip"`, `data-start/duration/track-index`, `src`.
6. **Наезд камеры и `hyperframes check`**: зум помечается как выход за рамку → на контейнер `data-layout-allow-overflow`.
7. `npm run check` → `snapshot` на 5 таймкодах (текст не на лице, вставки не закрывают лицо дольше 3 с) → `npm run render`.
8. **Финал всегда в H.264** (HyperFrames отдаёт HEVC, Instagram и Postiz принимают хуже):
   `ffmpeg -i render.mp4 -c:v h264_videotoolbox -b:v 8M -movflags +faststart -pix_fmt yuv420p -c:a aac -b:a 128k out.mp4` (Windows: `-c:v libx264 -preset veryfast -crf 21`).
9. `ffprobe`: есть видео, есть звук, длительность = `cut.mp4`.

## Рендер (оба трека)
`-pix_fmt yuv420p` и `-movflags +faststart` всегда. Аудио `-c:a aac -b:a 128k`. Пачку — параллельно (Mac 4–6, Windows 2–3), длинные первыми. Не запускать ffmpeg через `nohup … &` в фоне рутины. После рендера — `ffprobe`.

## Выдача
Готовый файл + `.check.jpg` (или 5 кадров для трека Б) → залей по `${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/references/drive-bridge.md` → в K ссылка на папку + CloudFront-ссылка файла, L = «На утверждении». Имя использованного клипа допиши в `output/used-clips.txt`. Правки человека — одной строкой в `MEMORY.md`.

## Установка (один раз, шаг «монтаж» в ПРОМТ-УЧАСТНИКА)
Node.js ≥ 18 → `npx hyperframes@latest skills update` → `npx -y skills@latest add remotion-dev/skills -g -y` → `npx hyperframes init reels-hf --resolution portrait --example blank --non-interactive` → Mac: `brew install whisper-cpp` + модель `~/.whisper-models/ggml-medium-q5_0.bin` → новый чат. Подробно: `${CLAUDE_PLUGIN_ROOT}/templates/montage/УСТАНОВЩИК-МОНТАЖ.md`, промты запуска — `МОНТАЖ-ЗАПУСК.md`.

## Не спрашивать разрешения на ffmpeg / ffprobe / python / npx / npm / whisper-cli / check / snapshot / render — они в allow-листе `templates/settings.local.safe.json`.
