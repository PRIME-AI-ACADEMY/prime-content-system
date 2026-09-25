# Changelog

## 0.11.0 — 2026-09-25 · подготовка к тренингу «Контент-завод за один день» (26.09, Цюрих)

### Таксономия каруселей — один словарь для `content-plan` и `carousel`
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
