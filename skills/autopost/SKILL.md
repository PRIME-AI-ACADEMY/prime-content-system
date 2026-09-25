---
name: autopost
description: "Автопостинг готового контента в соцсети. Режимы: A — Postiz (MCP, по умолчанию; Instagram + Threads), B — Metricool (MCP, бесплатная альтернатива), C — Meta Graph API (бесплатно по токену), D — ручной препост в планировщик. Берёт строки «Утверждено» + медиа, планирует и ставит статус. Триггеры: автопостинг, запости, опубликуй, postiz, metricool, meta, instagram, threads, расписание."
---

# Autopost — автопостинг (выбери режим по тому, что подключено)

Назначение: опубликовать/запланировать готовый контент из контент-плана.

## Где лежат профили
Профили лежат в папке `profile/` в корне проекта: `profile/business-dna.md`, `profile/audience.md`, `profile/hunt-ladder.md`, `profile/offer.md`, `profile/tone-of-voice.md`, `profile/design-system.md`, плюс паспорт `profile/foundation.html`. Google Drive — необязательное зеркало: коннектор подключён → продублируй туда; нет — работай с `profile/` и не останавливайся.

Подпись пишется голосом из `profile/tone-of-voice.md`; часовой пояс человека — из `profile/business-dna.md` (нет → спроси один раз).

## Какой режим
- **Postiz подключён (MCP)** → режим **A**. **ПО УМОЛЧАНИЮ.** Каналы Instagram + Threads.
- Metricool подключён (MCP) → режим **B** — бесплатная альтернатива.
- Есть Meta-токен → режим **C** — полный авто Instagram по Graph API, бесплатно.
- Ничего нет → режим **D** — ручной препост: система готовит, человек нажимает «опубликовать».

## Вход
Строка контент-плана: подпись, ссылка на медиа (Drive), дата. Отбирай: Статус = «Утверждено», есть медиа, колонка «Postiz (запланировано)» пуста. Не падай, если постить нечего — скажи «к публикации ничего нет» и закончи.

## Режим A — Postiz (MCP) — по умолчанию
Коннектор: Settings → Connectors → Add custom connector → URL `https://mcp.postiz.com/mcp`. В Postiz заранее подключены каналы Instagram и Threads.
1. `integrationList` → найди id каналов Instagram и Threads: `[integrationId из integrationList]`. Нет каналов → скажи человеку подключить их в app.postiz.com → Add channel.
2. **Медиа — только ПУБЛИЧНЫЙ URL.** Drive-файл с доступом «все, у кого есть ссылка» в виде прямой ссылки `https://drive.google.com/uc?export=download&id=[id файла]`, или CDN-ссылка Higgsfield. Загрузи через `uploadFromUrlTool` → получишь путь медиа для поста. Карусель = несколько картинок по порядку; Reels = одно видео.
3. **Дата — в UTC.** Возьми время из плана в часовом поясе человека и переведи в UTC сам (`2026-09-27T07:00:00Z`). Ошибка в поясе = пост в чужое время.
4. `integrationSchedulePostTool`: integrationId канала, дата в UTC, текст подписи, список медиа, `type="schedule"`. Для Threads — та же подпись, укороченная до лимита, картинки те же. Первый тест — `type="draft"`: ничего не публикуется, пост виден в календаре Postiz.
5. Проверь через `postsListTool`, что пост стоит на нужную дату. Статус в таблице → «Запланировано», в колонку «Postiz (запланировано)» — дата UTC + id поста.

## Режим B — Metricool (MCP, бесплатная альтернатива)
1. `getBrandSettings` → `[blogId из getBrandSettings]` и `[timezone из getBrandSettings]`.
2. Медиа — ПУБЛИЧНЫЕ URL (как в режиме A). Карусель = несколько картинок в media[]; Reels = видео + instagramData.type="REEL".
3. `createScheduledPost`: blogId, date (ISO с оффсетом), info = JSON: providers:[{"network":"instagram"}], text=подпись, media:[URL…], publicationDate:{dateTime, timezone}, instagramData:{type:"POST"|"REEL"}, autoPublish:true (авто) или draft:true (черновик для теста).
4. Статус → «Запланировано» + plannerUrl в колонку «Postiz (запланировано)».
Лимиты free-плана: 1 бренд и ограниченное число запланированных постов в месяц — упёрся в лимит → пометь ошибку в строке и продолжай.

## Режим C — Meta Graph API (бесплатный полный авто)
Требует токена: Instagram-бизнес + FB App, право instagram_content_publish; `META_TOKEN` / `IG_USER_ID` только в локальном `.env`. Instagram Content Publishing API: POST /{ig-user-id}/media (image_url + caption) → creation_id → POST /{ig-user-id}/media_publish. Токен — только в .env, не в чате.

## Режим D — ручной препост (бесплатно)
Собери финальную подпись + дату, впиши в таблицу статус «Готово к постингу» + готовую подпись; человек вставляет в планировщик Meta Business Suite / Metricool / Buffer руками.

## Правила
- ТОЛЬКО строки «Утверждено». Подпись — голосом бренда, без «не X, а Y», без скобок-рода.
- Первый тест — всегда черновик (draft): ничего не публикуется, покажи, где его посмотреть.
- Даты в Postiz — UTC; в Metricool — с оффсетом и timezone. Не смешивай.
- Токены и ключи — только в `.env`.

Коннекторы: Postiz (A), Metricool (B), Meta-токен (C), Composio (Google Sheets + Drive) — для чтения плана и ссылок на медиа во всех режимах.
