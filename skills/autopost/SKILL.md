---
name: autopost
description: "Автопостинг готового контента в соцсети. Режимы: Metricool (MCP, бесплатно, РЕКОМЕНДУЕМ), Postiz (платно), Meta Graph API (бесплатно по токену), Meta ручной-препост. Берёт строки «Утверждено» + медиа, планирует и ставит статус. Триггеры: автопостинг, запости, опубликуй, metricool, postiz, meta, instagram, расписание."
---

# Autopost — автопостинг (выбери режим по тому, что подключено)

Назначение: опубликовать/запланировать готовый контент из контент-плана.

## Какой режим
- **Metricool подключён (MCP)** → режим **M** — бесплатно, авто, через MCP. **ПО УМОЛЧАНИЮ.**
- Postiz подключён → режим A (много каналов; платно после триала).
- Есть Meta-токен → режим B (полный авто Instagram, бесплатно).
- Ничего нет → режим C (ручной-препост в планировщик).

## Вход
Строка контент-плана: подпись, ссылка на медиа (Drive), дата. Отбирай: Статус = «Утверждено», есть медиа, отметка публикации пуста. Не падай, если постить нечего.

## Режим M — Metricool (MCP, бесплатно) — РЕКОМЕНДУЕМ
1. `getBrandSettings` → возьми blogId бренда и timezone (напр. Instagram «angelinaa.kh» blogId 6384128, Europe/Zurich).
2. Медиа — ПУБЛИЧНЫЕ URL (Drive с доступом «по ссылке», или CDN Higgsfield). Карусель = несколько картинок в media[]; Reels = видео + instagramData.type="REEL".
3. `createScheduledPost`: blogId, date (ISO с оффсетом), info = JSON:
   providers:[{"network":"instagram"}], text=подпись, media:[URL…],
   publicationDate:{dateTime, timezone}, instagramData:{type:"POST"|"REEL"},
   autoPublish:true (авто) или draft:true (черновик для теста/ручного контроля).
4. Статус → «Запланировано» + plannerUrl в колонку Postiz.
Лимиты free Metricool: 1 бренд и ограниченное число запланированных постов/мес — если лимит, пометь ошибку и продолжай.

## Режим A — Postiz
1. Composio GOOGLESHEETS_BATCH_GET → отбор. 2. Медиа → Postiz `uploadFromUrlTool`. 3. `integrationSchedulePostTool` (integrationId из `integrationList`, type="schedule"). 4. Статус → «Запланировано».

## Режим B — Meta Graph API (бесплатный полный авто)
Требует токена (Instagram-бизнес + FB App, право instagram_content_publish; META_TOKEN/IG_USER_ID в локальном .env). Instagram Content Publishing API: POST /{ig-user-id}/media (image_url+caption) → creation_id → POST /{ig-user-id}/media_publish. Токен — только в .env, не в чате.

## Режим C — ручной-препост (бесплатно)
Собери финальную подпись + дату, впиши в таблицу статус «Готово к постингу» + готовую подпись; человек вставляет в планировщик Metricool/Meta.

## Правила
- ТОЛЬКО строки «Утверждено». Подпись — голосом бренда, без «не X, а Y».
- Первый тест — всегда draft:true (ничего не публикуется), покажи plannerUrl.
- Токены — только в .env.

Коннекторы: Metricool (режим M), Composio (Google Sheets + Drive), Postiz (A), Meta-токен (B).