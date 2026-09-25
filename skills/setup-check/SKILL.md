---
name: setup-check
description: "Проверяет установку контент-завода и даёт отчёт с галочками: версия приложения Claude, плагин и число скиллов (21), Python + Pillow + OpenCV<5 с каскадом лиц, ffmpeg, Node.js + HyperFrames + Remotion + whisper (трек «монтаж», опционально), коннекторы Higgsfield / Composio (Google Sheets + Drive) / Postiz / Vercel с записью их реальных id в allow-лист, мост в Drive, папка profile/, таблица контент-плана. По каждому ❌ — одна строка, что сделать. Триггеры: проверь установку, setup-check, всё ли готово, диагностика, что не так, проверка системы, готова ли система."
---

# Setup Check — диагностика установки

Цель: за один прогон сказать человеку, что готово и что починить. Ничего не ломай: только читай и проверяй. Единственная запись — id коннекторов в `.claude/settings.local.json` (раздел 4), она безвредна. Остальное чини по подтверждению.

Проходи по пунктам подряд, ошибки не останавливают прогон. Windows: вместо `python3` пиши `python`. Есть venv `~/.reels-venv` — проверяй его питоном.

## 1. Приложение Claude
- Версия ≥ 2.1.193 (иначе команды `/plugin` не работают). Посмотри через `/status` или меню → About. ❌ → обнови приложение (Check for updates) и полностью перезапусти.

## 2. Плагин
- Посчитай доступные скиллы `prime-content-system:*` — должно быть **21**: foundation, business-dna, offer-builder, audience-builder, hunt-ladder, funnels, tone-of-voice-builder, design-system-builder, content-plan, content-pipeline, reels, reels-montazh, carousel, short-post, long-post, stories, article, viral-hooks, autopost, content-routine, setup-check. ❌ → `/plugin marketplace add PRIME-AI-ACADEMY/prime-content-system` → `/plugin install prime-content-system@prime-ai` → полный перезапуск.
- Версия плагина 0.12.0 или новее? Старая → `/plugin marketplace update prime-ai`, затем перезапуск.

## 3. Инструменты (Bash)
- `python3 --version` — маршрут C каруселей. ❌ → Mac: `brew install python`; Windows: `winget install Python.Python.3.12`, галочка «Add to PATH».
- `python3 -c "import PIL; print(PIL.__version__)"` — Pillow. ❌ → `python3 -m pip install --user pillow --timeout 120 --retries 5`. Ответ `externally-managed-environment` → `python3 -m venv ~/.reels-venv && ~/.reels-venv/bin/pip install pillow`, дальше скрипты через `~/.reels-venv/bin/python` (Windows: `%USERPROFILE%\.reels-venv\Scripts\python`).
- `python3 -c "import cv2; assert hasattr(cv2,'CascadeClassifier'); print(cv2.__version__)"` — детектор лиц («текст не на лице»). ❌ или версия 5.x → `python3 -m pip install "opencv-python-headless<5"` (в OpenCV 5 нет CascadeClassifier, проверка молча выключается).
- Файл `fonts/haarcascade_frontalface_default.xml` в проекте (или в `~/.reels-fonts/`). ❌ → `curl -sL -o fonts/haarcascade_frontalface_default.xml "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml"`.
- `fonts/Montserrat-VF.ttf` > 100 КБ и глифы `ыъэё→` рисуются (`lab_common.missing_glyphs`). ❌ → скачать с Google Fonts (ссылка в ПРОМТ-УЧАСТНИКА, шаг 4).
- `ffmpeg -version` — монтаж. ❌ → Mac `brew install ffmpeg` / Windows `winget install Gyan.FFmpeg`, затем полный перезапуск приложения.
- **Трек «монтаж» (опционально, если человек хочет `Reels · M` и говорящую голову):**
  - `node -v` ≥ 18. ❌ → Mac `brew install node`, Windows `winget install OpenJS.NodeJS.LTS` + перезапуск.
  - Скиллы HyperFrames в `~/.claude/skills/` (`ls ~/.claude/skills | grep -i hyperframes`). ❌ → `npx hyperframes@latest skills update`.
  - Скиллы Remotion (`ls ~/.claude/skills | grep -i remotion`). ❌ → `npx -y skills@latest add remotion-dev/skills -g -y`.
  - Проект `reels-hf/package.json`. ❌ → `npx hyperframes init reels-hf --resolution portrait --example blank --non-interactive`.
  - Mac: `whisper-cli --help` и модель `~/.whisper-models/ggml-medium-q5_0.bin`. ❌ → `brew install whisper-cpp`; модель: `mkdir -p ~/.whisper-models && curl -L -o ~/.whisper-models/ggml-medium-q5_0.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium-q5_0.bin`. Windows → «⚪ субтитры через `npx hyperframes transcribe`».
  - Монтаж не нужен → все пункты трека «⚪ не нужен, пока не ставишь монтаж».
- Chrome **не нужен**: маршрут C = Python + Pillow.

## 4. Коннекторы — проверь и запиши их id в allow-лист
Вызови безвредный инструмент каждого коннектора. **Реальное имя инструмента выглядит как `mcp__<uuid>__<tool>`** — возьми префикс `mcp__<uuid>` и допиши его в `allow` файла `.claude/settings.local.json` проекта (создай из `${CLAUDE_PLUGIN_ROOT}/templates/settings.local.safe.json`, если файла нет). Имена `mcp__postiz` / `mcp__higgsfield` / `mcp__composio` / `mcp__vercel` из шаблона ничего не разрешают — без реальных id локальные рутины встают на каждом вызове. После записи скажи человеку перезапустить чат.
- **Higgsfield:** `balance`. ❌ → Settings → Connectors → Higgsfield → Connect.
- **Composio (Google Sheets + Drive):** `COMPOSIO_MANAGE_CONNECTIONS` (список подключений, должны быть googlesheets и googledrive). ❌ → mcp.composio.dev → включить оба → Add custom connector → авторизовать Google.
- **Postiz:** `integrationList` — каналы Instagram (и Threads). ❌ (коннектора нет) → Add custom connector `https://mcp.postiz.com/mcp`. ❌ (каналов нет) → app.postiz.com → Add channel.
- **Vercel (сайт контент-плана):** `list_projects` или `get_auth_user`. ❌ → Settings → Connectors → Vercel → Connect. Нет коннектора — запасной путь `npx vercel --prod --yes` (попросит вход).
- Итог раздела: список `mcp__<uuid>` в allow-листе = число подключённых коннекторов.

## 5. Мост в Drive (загрузка файлов)
Проверь один из путей по `${CLAUDE_PLUGIN_ROOT}/skills/content-pipeline/references/drive-bridge.md`:
- есть папка `~/Library/CloudStorage/GoogleDrive-*/` (Mac) или диск `G:\` (Windows) → ✅ «копирование в папку Drive»;
- иначе Higgsfield ✅ и Composio Drive ✅ → ✅ «мост Higgsfield → Drive»;
- ни того ни другого → ❌ «подключи Higgsfield + Composio Drive: без этого файлы в Drive не попадут».

## 6. Профили
Папка `profile/` в корне проекта: `business-dna.md` (с разделом «Актуальный запуск»), `audience.md`, `hunt-ladder.md`, `offer.md`, `funnels.md`, `tone-of-voice.md`, `design-system.md`, паспорт `foundation.html`.
- Папки нет или пустая → «запусти `foundation`».
- Нет одного файла → назови конструктор: `business-dna`, `audience-builder`, `hunt-ladder`, `offer-builder`, `funnels`, `tone-of-voice-builder`, `design-system-builder`.
- В `business-dna.md` нет «Актуальный запуск» → «⚠️ спроси события и кодовые слова, допиши раздел» (без него в тексты попадают старые даты).

## 7. Данные
- `photos/` с фото (HEIC → `sips -s format jpeg`), `photo-catalog.md`. ❌ → «положи 30+ фото в photos/ и попроси составить каталог».
- `clips/` с 3–10 вертикальными клипами (для `Reels · M`). Пусто → «⚪ рилсы из клипов пока не делаем».
- Таблица контент-плана открывается (Composio → первая строка листа «Контент-план»), колонка A в формате `ДД.ММ.ГГГГ ЧЧ:ММ`. ❌ → «запусти `content-plan`».

## 8. Рутины (если настроены)
Перечисли активные рутины и время; предупреди, если этап (план / медиа / автопост / статус) не покрыт. Напомни: облачный cron идёт в UTC. Не настроены → «⚪ рутины ставятся после первой карусели и рилса (ПРОМТ-УЧАСТНИКА, шаг рутин)».

## 9. Итог
Таблица: Пункт · ✅/❌/⚪ · Что сделать (одна строка на каждый ❌). Внизу — «сделай сейчас» из ❌ по порядку. Все критичные ✅ → «система готова, следующий шаг — `foundation` (потом `funnels`, `tone-of-voice-builder`, `design-system-builder`, `content-plan`)».
