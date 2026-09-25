# Changelog

## 0.12.0 — 2026-09-26 · по итогам живого прохождения промта «Контент-завод» (14 проблем + обратная связь)

### Новые скиллы (19 → 21)
- **`funnels`** — агент по воронкам: после `foundation` собирает 1–3 паспорта вечных воронок, словарь CTA и кодовых слов, прогрев по дням, точки касания; сохраняет `profile/funnels.md`. База знаний `skills/funnels/references/vechnye-voronki.md`. Цепочка фундамента: foundation → offer → **funnels** → tone-of-voice → design-system.
- **`reels-montazh`** — монтаж внутри плагина: трек А (клип из `clips/` + хук + CTA, `build_reel.py`), трек Б (говорящая голова через HyperFrames: паузы −45 дБ / 0.4 с со сверкой по whisper, субтитры по `faces.json`, `data-layout-allow-overflow`, CTA на top 1120, финал всегда в H.264).

### Фундамент и профили — универсальные
- Никаких цветов, шрифтов, ников и PDF автора плагина как дефолтов: `foundation`, `design-system-builder`, `higgsfield-visual-standard`, README — палитра pine/cream/gold теперь только пример структуры. `design-system-builder` просит скриншот своего поста и снимает цвет пипеткой; в профиле подписи «фон / текст / акцент / карточка».
- `foundation` отдельно спрашивает **ключевые события и воронки** (даты эфира, марафона, потока, кодовые слова, что не использовать) → раздел **«Актуальный запуск»** первым в `business-dna.md`; все текстовые скиллы и рутины читают его раньше остального. Шаблон в `business-dna`.
- `tone-of-voice-builder`: поле **«Мои запреты»** (без длинного тире, без «автопилот» и т.п.), читают все текст-скиллы.

### content-plan
- Три вопроса до плана: горизонт (по умолчанию **2 недели**), ритм (по умолчанию **карусель каждый день + 3 рилса**), события и воронки.
- Каждая строка размечена воронкой: колонки **I «Воронка»** и **J «Функция · Этап · Точка назначения»** (старые I «Медиа из банка» и J «Источник скриншота» ушли; заметка о фото/клипе/скрине живёт в конце H). Колонка A — строго `ДД.ММ.ГГГГ ЧЧ:ММ`.
- Reels в трёх форматах: `Reels · M · говорящая голова` / `Reels · M` (клип) / `Reels · S` (аватар). Карусели C — обложка и финал всегда с реальными фото из `photos/`; H — только человек в кадре, ≤ 2 в неделю.
- Сверка с трендами: `skills/content-plan/references/trends-2026-2027.pdf`.
- Сайт контент-плана — сразу после таблицы, через Vercel MCP `create_deployment` (CLI запасной).

### Higgsfield (маршрут H) — брак закрыт
- `skills/carousel/references/higgsfield-prompt-template.md`: проверенный шаблон (референс лица на каждый слайд, один наряд, ONE full-bleed frame, текст один раз, «each line exactly once», без «», без COVER и номеров слайдов), пример логики (не копировать сцены), референс-лист за 2 кредита для тех, у кого нет Soul, чистка старых промптов, QA. `carousel` и рутина 02 чистят промпт перед генерацией.

### Мост в Drive и Postiz
- `skills/content-pipeline/references/drive-bridge.md`: папка Google Drive для компьютера → иначе Higgsfield `media_upload` → `curl PUT` → Composio `UPLOAD_FROM_URL` → permission anyone/reader. Никогда не просить грузить руками и не гонять base64. На него ссылаются carousel / reels / reels-montazh / foundation / autopost / content-pipeline / рутины 02, 03, 08. `setup-check` проверяет один из путей.
- В K везде: ссылка на папку Drive + CloudFront-ссылки файлов (Postiz принимает только их). `autopost`: черновики «ЧЕРНОВИК …» не создаются заново, время по формату из «Актуальный запуск», UTC с учётом зимнего времени.

### Разрешения и установка
- `templates/settings.local.safe.json`: + `npx`, `npm`, `node`, `whisper-cli`, `touch`, `cd`, `rm` (без `-rf`/`-r`), `mcp__vercel`. `setup-check` вызывает безвредный инструмент каждого коннектора, берёт префикс `mcp__<uuid>` и **сам дописывает его в `.claude/settings.local.json`** — без этого локальные рутины встают.
- ПРОМТ-УЧАСТНИКА → 17 шагов: OpenCV `<5` + проверка `CascadeClassifier`, `pip --timeout 120 --retries 5`, каскад лиц в `fonts/`, HEIC → `sips`, копирование `build_c.py`/`build_reel.py` в `tools/`; необязательный шаг **3-М «монтаж»** (Node.js, `npx hyperframes@latest skills update`, `npx -y skills@latest add remotion-dev/skills -g -y`, `reels-hf`, whisper-cpp + модель); коннектор **Vercel**; шаги funnels → ToV → дизайн → план → сайт → карусель → рилс → автопост → **рутины** (08 → 01 → 02 → 03 → 04) → итог.
- `setup-check`: 21 скилл, 0.12.0, OpenCV<5 и каскад, трек «монтаж», Vercel, мост в Drive, `funnels.md`, «Актуальный запуск», формат колонки A, cron в UTC.

### Код
- `templates/carousel-code/build_c.py`: карточка `brand.card` под текстом T1 (CARD_PAD 40), блок по вертикали, верхнее затемнение на фото-слайдах (`scrim top 215/0.24`), **код выхода 6**, если нет детектора лиц при фото-слайдах. `lab_common.py`: каскад ищется ещё в `fonts/` корня проекта и `cwd/fonts`, цвет «карточка» из design-system.
- `templates/montage/tools/build_reel.py`: **код выхода 5**, если детектора нет и `--no-face-check` не задан.

### Рутины
- `01-план-на-две-недели.md` (бывший 01-план-на-неделю): 14 дней с понедельника, только пустые дни, 7 каруселей + 3 рилса, промпты H по шаблону, разметка воронками, параметры ГОРИЗОНТ / КАРУСЕЛЕЙ / РИЛСОВ.
- 02 и 03: `ГОРИЗОНТ: 7 дней`, предупреждение о кредитах (≈24 за неделю с двумя H), чистка промптов H, карусели C через `build_c.py` с фото на обложке и финале, `Reels · M · говорящая голова` через HyperFrames + H.264, CloudFront-ссылки в K, коды 5/6 «нет детектора».
- 04: черновики, время по формату, UTC с учётом зимнего времени. 00-КАРТА: строка про id коннекторов в allow-листе, таблица пересчёта cron UTC лето/зима, обход для `schedule` без списка коннекторов, новая схема колонок.
- `МОНТАЖ-ЗАПУСК.md`: пять пунктов из прогона (паузы −45 дБ, ложные лица, H.264, `data-layout-allow-overflow`, CTA top 1120); установщик: Remotion-скиллы и модель whisper.

### Документы
- README (21 скилл, воронки в принципах, Vercel), SETUP (OpenCV, монтаж 3.5, Vercel 7.4, цепочка funnels → ToV → дизайн, 21 скилл, новые строки в «Частые проблемы»), PROMPTS (промт №3.5 «Воронки», №4 на 2 недели с воронками и сайтом, порядок на тренинге), `content-dashboard/README.md` (Vercel MCP основной путь).
- Версия 0.12.0 в `plugin.json` и `marketplace.json`.

## 0.11.0 — 2026-09-25 · подготовка к тренингу «Контент-завод за один день» (26.09, Цюрих)

### Таксономия каруселей — один словарь для `content-plan` и `carousel`
- **Разрешения:** два готовых шаблона `templates/settings.local.safe.json` (acceptEdits + allow-лист под завод + deny) и `templates/settings.local.autopilot.json` (bypassPermissions + deny) — чтобы локальные рутины шли без запросов; SETUP.md шаг 6 переписан под них.
- Типы контента переименованы, чтобы буквы не пересекались с маршрутами: **T1** текст-на-фоне · **T2** фото-аватар · **T3** скриншоты · **T4** кейс-инфографика.
- Маршруты производства: **H** Higgsfield `nano_banana_pro` с референсом лица · **C** код Python + Pillow, без браузера · **K** Canva.
- Таблица «тип → маршрут по умолчанию»: T1→C, T2→H, T3→C, T4→C (сложная графика → K).
- Колонка «Формат» хранит оба поля: `Карусель · T2 · H`. `content-plan` пишет оба, `carousel` читает оба; без маршрута — берёт по умолчанию из таблицы.

### Рендер каруселей — без противоречий
- Маршрут C = Python + Pillow, браузер не нужен. README, SETUP, ADVANCED, plugin.json говорят одно и то же.
- Chrome упоминается только как необязательный путь HTML→PNG/PDF. Node.js — только для HyperFrames (необязательный трек).

### Автопостинг — Postiz по умолчанию
- `autopost`: режим A Postiz (MCP `https://mcp.postiz.com/mcp`, каналы Instagram + Threads, медиа — публичный URL, даты в UTC, первый пост — draft); B Metricool (бесплатная альтернатива); C Meta Graph API; D ручной препост.
- Из скиллов убраны личные данные автора (blogId, часовой пояс, id интеграций, таблиц, папок Drive) — вместо них плейсхолдеры вида `[blogId из getBrandSettings]`.

### Контракт хранения профилей — одно место
- Папка `profile/` в корне проекта: `business-dna.md`, `audience.md`, `hunt-ladder.md`, `offer.md`, `tone-of-voice.md`, `design-system.md` + паспорт `profile/foundation.html`. Google Drive — необязательное зеркало (обязательное для облачного автопилота).
- Одинаковая формулировка «Где лежат профили» в README, `foundation`, всех шести конструкторах и всех потребителях (content-plan, content-pipeline, carousel, reels, stories, short-post, long-post, article, autopost, content-routine, setup-check).
- `foundation` сохраняет паспорт как `profile/foundation.html` и раскладывает четыре профиля; отстройка — разделом внутри `offer.md`.

### Пути между скиллами
- Все `../<skill>/…` заменены на `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/…` — в SKILL.md и в reference-файлах (hooks-database, copy-engine, human-voice-gallery).
- В copy-engine исправлено описание банка хуков: 300 готовых — в `viral-hooks`, 22 каркаса — в `reels/references/hooks-database.md`.

### `setup-check` переписан
- Проверяет: версию приложения Claude (≥ 2.1.193), плагин и число скиллов (19), `python3`/`python` + Pillow (с веткой `externally-managed-environment`), ffmpeg, Node (только для HyperFrames — опционально), коннекторы Higgsfield / Composio / Postiz безвредными list-вызовами, папку `profile/`, таблицу контент-плана.
- Вывод — таблица ✅/❌/⚪ и одна строка «что сделать» на каждый ❌.

### SETUP.md → v4
- Чек-лист «Что взять с собой на тренинг».
- Шаг «Приложение Claude»: версия ≥ 2.1.193 и как её проверить (`/status`).
- Шаг «Python + Pillow» для Mac и Windows, включая venv `~/.reels-venv`.
- Команды плагина: `/plugin marketplace add PRIME-AI-ACADEMY/prime-content-system` → `/plugin install prime-content-system@prime-ai` → полный перезапуск. Проверка: 19 скиллов.
- Шаг «Фундамент» = промт №1 из PROMPTS.md (№2 — быстрый вариант для тренинга), затем `design-system-builder`.
- Раздел «Windows: что иначе»: `python` вместо `python3`, `winget install Gyan.FFmpeg` + полный перезапуск приложения, `libx264 -preset veryfast -crf 21` вместо `h264_videotoolbox`, путь к Chrome, whisper пропустить.
- Автопостинг переписан вокруг Postiz (Metricool — бесплатная альтернатива), три правила: публичная ссылка, UTC, первый пост draft.
- Разделы «Телефон» и «Одолженный ноутбук» сохранены; из разрешений убран Chrome, добавлены python/pip.

### Прочее
- README: все 19 скиллов по группам Фундамент / Производство / Публикация / Диагностика, таблица таксономии, контракт `profile/`, палитра по умолчанию pine `#00311e` / cream `#fef7e5` / gold `#e8b96a`, Montserrat.
- PROMPTS.md: промт №0 «проверка установки», в №4 — типы и маршруты каруселей, порядок на тренинге с шагом «дизайн-система».
- ADVANCED.md: HyperFrames — необязательный трек для видео; Canva — маршрут K; таблица сравнения без Chrome.
- `design-system-builder`: сохраняет в `profile/design-system.md`, дефолт Montserrat + путь к TTF для маршрута C.
- `higgsfield-visual-standard.md`: шаблон промпта гендерно-нейтральный (`same person … their exact face`).
- Версия 0.11.0 в `plugin.json` и `marketplace.json`.

## 0.10.0
- `foundation`: интервью на 20 минут, режим «материалы есть» без вопросов, HTML-шаблон паспорта, PROMPTS.md.
