# PRIME AI — Content System

Кастомизируемая контент-система. Каждый пользователь собирает **свой** фундамент (оффер, аудиторию, голос, дизайн-систему, цели), оркестратор строит контент-план под его цели, генерит готовый контент, **публикует в соцсети** и может работать **на автопилоте**. Хранение — Google Drive / Таблицы.

## Логика «одной сессии»

```
«Дай контент-план на 2 недели, задача — 300 регистраций на вебинар»
        │
        ▼
 business-dna → audience-builder → hunt-ladder → offer-builder → tone-of-voice-builder → design-system-builder   (фундамент: профили в Google Drive)
        │
        ▼
 content-plan  (читает профили → календарь в Google-таблице, статусы: План → Запланировано → Опубликовано)
        │
        ▼
 content-pipeline → reels · carousel · short-post · long-post · stories · article   (генерация под профиль + дизайн-систему)
        │
        ▼
 медиа (Higgsfield / код) → Google Drive → ссылка + статус в контент-плане
        │
        ▼
 autopost → Postiz (Instagram, TikTok, Facebook, …)      ← content-routine ставит это на автопилот
```

## Скиллы

**Фундамент (конструкторы — каждый собирает СВОЁ):**
- `business-dna` — цели, продуктовая лестница, стратегия, KPI
- `offer-builder` — оффер по методологии Хормози
- `audience-builder` — ДНК клиента: аватары, боли, язык
- `hunt-ladder` — лестница Бена Ханта: уровни осознанности
- `tone-of-voice-builder` — голос бренда из примеров текстов
- `design-system-builder` — визуальный стандарт: палитра, шрифты, сетка/безопасные зоны, правила читаемости (читают carousel/reels/stories)

**Производство контента:**
- `content-plan` — оркестратор: цель → контент-календарь → генерация
- `content-pipeline` — конвейер: исходник → золотые куски → все форматы
- `reels` · `carousel` · `short-post` · `long-post` · `stories` · `article`

**Публикация и автопилот:**
- `autopost` — публикация/планирование готового контента в соцсети через **Postiz** (Instagram, TikTok, Facebook и др.)
- `content-routine` — ежедневный автопилот: утром генерит на N дней вперёд, ночью автопостит (cron)

## Коннекторы
Higgsfield (генерация) · Google Drive · Google Sheets · Postiz (автопостинг) — через Composio. Код-рендер каруселей — через headless Chrome + ffmpeg.

## Принципы (обязательно)
- **Дизайн-система первична:** весь визуал (carousel/reels/stories) читает профиль `design-system` (палитра, шрифты, сетка).
- **Читаемость текста:** на фото — тёмная подложка-скрим, контраст, текст никогда не на лице.
- **Обращение:** нейтральное на «ты», никогда женский род.
- **Банк фото:** выбор по `photo-catalog.md`; лицо не обрезать. См. `skills/carousel/references/text-and-photo-rules.md`.

## Как пользоваться
1. Установи плагин, подключи коннекторы (Higgsfield, Google Drive/Sheets, Postiz).
2. Собери фундамент: `business-dna`, `offer-builder`, `audience-builder`, `hunt-ladder`, `tone-of-voice-builder`, `design-system-builder`.
3. «Нужен контент-план на 2 недели, задача — …» → система построит календарь и сгенерит контент.
4. Поставь `content-routine` на расписание — генерация и автопостинг пойдут сами.

---
Автор: Angelina Khudiakova · PRIME AI
