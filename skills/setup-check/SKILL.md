---
name: setup-check
description: "Проверяет установку контент-завода и даёт отчёт с галочками: версия приложения Claude, плагин и число скиллов (19), Python + Pillow, ffmpeg, Node (только для HyperFrames), коннекторы Higgsfield / Composio (Google Sheets + Drive) / Postiz, папка profile/, таблица контент-плана. По каждому ❌ — одна строка, что сделать. Триггеры: проверь установку, setup-check, всё ли готово, диагностика, что не так, проверка системы, готова ли система."
---

# Setup Check — диагностика установки

Цель: за один прогон сказать человеку, что готово и что починить. Ничего не ломай: только читай и проверяй. Чини по подтверждению; безвредное (`/plugin marketplace update prime-ai`) можно предложить сразу.

Проходи по пунктам подряд, ошибки не останавливают прогон. Windows: вместо `python3` пиши `python`.

## 1. Приложение Claude
- Версия ≥ 2.1.193 (иначе команды `/plugin` не работают). Посмотри через `/status` в строке Claude Code или меню приложения → About. ❌ → обнови приложение (Check for updates) и полностью перезапусти.

## 2. Плагин
- Посчитай доступные скиллы `prime-content-system:*` — должно быть **19**: foundation, business-dna, offer-builder, audience-builder, hunt-ladder, tone-of-voice-builder, design-system-builder, content-plan, content-pipeline, reels, carousel, short-post, long-post, stories, article, viral-hooks, autopost, content-routine, setup-check. ❌ (меньше или нет) → `/plugin marketplace add PRIME-AI-ACADEMY/prime-content-system` → `/plugin install prime-content-system@prime-ai` → полный перезапуск приложения.
- Версия плагина 0.11.0 или новее? Старая → `/plugin marketplace update prime-ai`, затем перезапуск.

## 3. Инструменты (Bash)
- `python3 --version` — маршрут C каруселей. ❌ → Mac: `brew install python` (или python.org); Windows: `winget install Python.Python.3.12`, при установке галочка «Add to PATH».
- `python3 -c "import PIL; print(PIL.__version__)"` — Pillow, рисует карусели без браузера. ❌ → `python3 -m pip install --user pillow`. Ответ `externally-managed-environment` → `python3 -m venv ~/.reels-venv && ~/.reels-venv/bin/pip install pillow`, дальше скрипты запускай через `~/.reels-venv/bin/python` (Windows: `%USERPROFILE%\.reels-venv\Scripts\python`).
- `ffmpeg -version` — монтаж видео. ❌ → Mac `brew install ffmpeg` / Windows `winget install Gyan.FFmpeg`, затем полностью закрыть и открыть приложение Claude, чтобы обновился PATH.
- `node -v` — нужен только для HyperFrames (анимации кодом), **опционально**. Нет — это не ошибка, пометь «⚪ не нужен, пока не ставишь HyperFrames».
- Chrome **не нужен**: маршрут C = Python + Pillow, без браузера. Проверяй только если человек сам просит HTML→PNG/PDF.

## 4. Коннекторы (вызови безвредный инструмент-список)
- **Higgsfield:** `balance` или `list_voices`. ❌ → Settings → Connectors → Higgsfield → Connect.
- **Composio (Google Sheets + Drive):** `COMPOSIO_MANAGE_CONNECTIONS` (список подключений) или пробное чтение списка файлов Drive. ❌ → mcp.composio.dev → включить Google Sheets + Google Drive → Add custom connector в Claude → авторизовать Google.
- **Postiz:** `integrationList` — должны быть каналы Instagram и Threads. ❌ (коннектора нет) → Add custom connector, URL `https://mcp.postiz.com/mcp`. ❌ (каналов нет) → app.postiz.com → Add channel → Instagram, Threads.

## 5. Профили
Профили лежат в папке `profile/` в корне проекта: `profile/business-dna.md`, `profile/audience.md`, `profile/hunt-ladder.md`, `profile/offer.md`, `profile/tone-of-voice.md`, `profile/design-system.md`, плюс паспорт `profile/foundation.html`. Google Drive — необязательное зеркало: коннектор подключён → продублируй туда; нет — работай с `profile/` и не останавливайся.
- Папки `profile/` нет или она пустая → «запусти `foundation` (PROMPTS.md, промт №1)».
- Нет только одного файла → назови конструктор: `business-dna`, `audience-builder`, `hunt-ladder`, `offer-builder`, `tone-of-voice-builder`, `design-system-builder`.

## 6. Данные
- Папка `photos/` с фото и `photo-catalog.md`. ❌ → «положи 30+ фото в photos/ и попроси составить каталог».
- Таблица контент-плана открывается (Composio → прочитай первую строку листа «Контент-план»). ❌ → «запусти `content-plan`, таблица создастся».

## 7. Рутины (если настроены)
Перечисли активные рутины и их время; предупреди, если какой-то этап (план / генерация / автопост / публикация) не покрыт. Не настроены → «⚪ рутины пока не нужны».

## 8. Итог
Таблица со столбцами: Пункт · ✅/❌/⚪ · Что сделать (одна строка на каждый ❌). Порядок пунктов — как выше. Внизу — приоритетный список «сделай сейчас» из ❌. Если все критичные пункты ✅ — скажи: «система готова, следующий шаг — `foundation` или `content-plan`».
