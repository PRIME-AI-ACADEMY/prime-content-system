# PRIME AI — Content System

Кастомизируемая контент-система. Каждый пользователь собирает **свой** фундамент (аудитория, оффер, голос, дизайн-система, цели), оркестратор строит контент-план под его цели, генерит готовый контент, **публикует в соцсети** и может работать **на автопилоте**.

Установка с нуля — [SETUP.md](SETUP.md). Готовые промты — [PROMPTS.md](PROMPTS.md). Анимации и Canva — [ADVANCED.md](ADVANCED.md). История версий — [CHANGELOG.md](CHANGELOG.md).

## Логика «одной сессии»

```
«Дай контент-план на 2 недели, задача — 300 регистраций на вебинар»
        │
        ▼
 foundation  (интервью → 6 блоков → profile/foundation.html + профили в profile/)
        │
        ▼
 design-system-builder  (цвета, шрифты → profile/design-system.md)
        │
        ▼
 content-plan  (читает profile/ → календарь в Google-таблице, статусы: План → Запланировано → Опубликовано)
        │
        ▼
 content-pipeline → reels · carousel · short-post · long-post · stories · article   (генерация под профиль + дизайн-систему)
        │
        ▼
 медиа (Higgsfield / Python + Pillow / Canva) → Google Drive → ссылка + статус в контент-плане
        │
        ▼
 autopost → Postiz (Instagram + Threads)      ← content-routine ставит это на автопилот
```

## Скиллы — 19

**Фундамент (7):**
- `foundation` — **первый шаг.** Один промт → интервью → шесть блоков (ЦА, отстройка, смыслы, оффер, путь клиента, стратегия) одним HTML-паспортом + профили в `profile/`. Промт №1 в [PROMPTS.md](PROMPTS.md).
- `business-dna` — цели, продуктовая лестница, стратегия, KPI
- `offer-builder` — оффер по методологии Хормози
- `audience-builder` — ДНК клиента: аватары, боли, язык
- `hunt-ladder` — лестница Бена Ханта: уровни осознанности
- `tone-of-voice-builder` — голос бренда из примеров текстов
- `design-system-builder` — палитра, шрифты, сетка, правила читаемости (читают carousel/reels/stories)

Точечные конструкторы — продвинутый путь: дорабатывают один блок после `foundation` или собирают фундамент вручную по цепочке business-dna → audience → hunt-ladder → offer → tone-of-voice → design-system.

**Производство (9):**
- `content-plan` — оркестратор: цель → контент-календарь → генерация. Назначает каждой карусели тип (T1–T4) и маршрут (H/C/K)
- `content-pipeline` — конвейер: исходник → золотые куски → все форматы; здесь живёт движок текста `copy-engine.md`
- `carousel` — 4 типа × 3 маршрута: H (Higgsfield с референсом лица) · C (Python + Pillow, без браузера) · K (Canva)
- `reels` — сценарии коротких видео: 3 хука, 5 блоков, CTA на рост
- `short-post` · `long-post` · `article` — тексты от 1000 знаков до лонгрида
- `stories` — линии сторис 7–20, продающая линия на 5 этапов
- `viral-hooks` — банк из 300 готовых хуков, 10 категорий, под русскоязычный рынок

**Публикация (2):**
- `autopost` — планирование в соцсети через **Postiz** по умолчанию (Instagram + Threads); альтернативы: Metricool, Meta Graph API, ручной препост
- `content-routine` — ежедневный автопилот: утром генерит на N дней вперёд, ночью автопостит (cron)

**Диагностика (1):**
- `setup-check` — проверяет приложение, плагин, Python + Pillow, ffmpeg, коннекторы, `profile/`, таблицу; таблица ✅/❌ + что сделать

## Таксономия каруселей (общая для content-plan и carousel)

Колонка «Формат» в контент-плане: `Карусель · T2 · H`.

| Тип | Название | Маршрут по умолчанию |
|---|---|---|
| T1 | Текст-на-фоне | C |
| T2 | Фото-аватар | H |
| T3 | Скриншоты | C |
| T4 | Кейс-инфографика | C (сложная графика → K) |

H = Higgsfield `nano_banana_pro` с референсом лица · C = код Python + Pillow, без браузера · K = Canva через коннектор.

## Где лежат профили
Профили лежат в папке `profile/` в корне проекта: `profile/business-dna.md`, `profile/audience.md`, `profile/hunt-ladder.md`, `profile/offer.md`, `profile/tone-of-voice.md`, `profile/design-system.md`, плюс паспорт `profile/foundation.html`. Google Drive — необязательное зеркало: коннектор подключён → продублируй туда; нет — работай с `profile/` и не останавливайся. Для облачного автопилота (`content-routine`) зеркало в Drive обязательно.

## Коннекторы и инструменты
Higgsfield (генерация картинок и видео) · Composio: Google Sheets + Google Drive (контент-план, медиа) · Postiz (автопостинг, MCP `https://mcp.postiz.com/mcp`) · Canva (опционально, маршрут K).
Локально: Python 3 + Pillow (карусели маршрутом C, без браузера) · ffmpeg (монтаж) · Node.js только для HyperFrames (опционально). Chrome нужен только для HTML→PNG/PDF, если сам захочешь этот путь.

## Принципы (обязательно)
- **Фундамент первичен:** контент-завод без собранного фундамента не на чём строить.
- **Дизайн-система первична:** весь визуал (carousel/reels/stories) читает `profile/design-system.md` (палитра, шрифты, сетка). Палитра по умолчанию: pine `#00311e`, cream `#fef7e5`, gold `#e8b96a`, шрифт Montserrat — участник ставит свою.
- **Читаемость текста:** на фото — тёмная подложка-скрим, контраст, текст никогда не на лице.
- **Обращение:** нейтральное на «ты», никогда женский род.
- **Банк фото:** выбор по `photo-catalog.md`; лицо не обрезать. См. `skills/carousel/references/text-and-photo-rules.md`.
- **Текст:** по `skills/content-pipeline/references/copy-engine.md` — без «не X, а Y», без скобок-рода, без канцелярита.

## Как пользоваться
1. Установи плагин по [SETUP.md](SETUP.md), подключи коннекторы (Higgsfield, Composio Google Drive/Sheets, Postiz). Скажи «запусти setup-check» — увидишь, что готово.
2. Собери фундамент одним промтом: `foundation` (промт №1 в [PROMPTS.md](PROMPTS.md)) → `profile/foundation.html` и профили в `profile/`. Потом `design-system-builder` — цвета и шрифты.
3. «Нужен контент-план на 2 недели, задача — …» (промт №4) → система построит календарь и сгенерит контент.
4. Поставь `content-routine` на расписание — генерация и автопостинг пойдут сами.

---
Автор: Angelina Khudiakova · PRIME AI
