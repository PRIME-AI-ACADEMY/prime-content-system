---
name: setup-check
description: "Проверяет установку контент-завода и даёт отчёт с галочками: Chrome, ffmpeg, Node, плагин и его версия, коннекторы (Higgsfield / Composio Google Sheets+Drive / Postiz), профили фундамента, папки и данные. Чинит найденное по подтверждению. Триггеры: проверь установку, setup-check, всё ли готово, диагностика, что не так, проверка системы, готова ли система."
---

# Setup Check — диагностика установки

Цель: за один прогон сказать человеку, что у него готово и что починить. Ничего не ломай: только читай/проверяй; чини по подтверждению (безвредное — `/plugin marketplace update` — можно сразу).

Пройди по пунктам, по каждому — ✅ или ❌ + как починить:

## 1. Инструменты (Bash)
- `ffmpeg -version` — монтаж. ❌ → Mac `brew install ffmpeg` / Windows `winget install ffmpeg`.
- `node -v` — для hyperframes. ❌ → `brew install node` / `winget install OpenJS.NodeJS.LTS`.
- Google Chrome по пути (рендер каруселей). ❌ → google.com/chrome.

## 2. Плагин
- Спроси у себя: какие скиллы prime-content-system доступны (должно быть ≥ 16).
- Версия актуальная? ❌/старая → `/plugin marketplace update prime-ai`, затем Customize → Plugins → Update.

## 3. Коннекторы
- **Higgsfield:** вызови `list_voices` или `balance`. ❌ → Connectors → подключить Higgsfield.
- **Composio (Google Sheets + Drive):** пробно прочитай любую ячейку / список Drive. ❌ → mcp.composio.dev, подключить Sheets+Drive.
- **Postiz:** `integrationList`. ❌ → postiz.com → подключить Instagram + MCP.

## 4. Фундамент
- Есть ли профили: business-dna, audience, hunt-ladder, offer, tone-of-voice, design-system, photo-catalog. ❌ → какой конструктор запустить.

## 5. Данные
- Папка `photos` с фото; банк фонов в Drive; таблица контент-плана доступна. ❌ → что добавить.

## 6. Рутины (если настроены)
- Перечисли активные рутины и их время; предупреди, если какой-то этап (план / генерация / автопост / публикация) не покрыт.

## 7. Итог
Таблица ✅/❌ по всем пунктам + **приоритетный список «что сделать сейчас»**. Если всё ✅ — скажи «система готова, можно запускать контент-план».
