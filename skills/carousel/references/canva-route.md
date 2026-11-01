# Маршрут K — Canva через коннектор

Canva сама по себе выдаёт средний дизайн. Хороший результат даёт **свой шаблон**: один раз собираем его по сильному промту, человек доправляет руками, дальше каждая карусель — копия шаблона с новым текстом и фото. Бесплатного Canva хватает.

Названия инструментов коннектора Canva могут отличаться: ищи по смыслу (поиск дизайнов, генерация дизайна, создание дизайна из кандидата, редактирование текста, загрузка картинки, экспорт). Нет нужного инструмента — скажи человеку одной строкой, что сделать руками в Canva, и продолжай.

## Шаг 1. Есть ли шаблон
Поищи в Canva дизайн с названием `ШАБЛОН карусель`. Нашёлся → шаг 3. Нет → шаг 2.

## Шаг 2. Шаблон (один раз)
1. Загрузи в Canva 2 фото из `photos/` (обложка и финал по `photo-catalog.md`, или кадры из `photos/банк/`).
2. Сгенерируй дизайн по промту ниже, тип Instagram-пост 4:5 (1080×1350). Если 4:5 нет, бери Instagram-пост и потом измени размер.
3. Покажи кандидатов, человек выбирает один → создай из него дизайн, назови `ШАБЛОН карусель · <ник>`.
4. Скажи человеку: «Открой шаблон в Canva и поправь руками то, что не нравится: шрифт, отступы, цвет плашки. Это один раз». Ссылку на дизайн — в чат.

Промт (заполни из `profile/design-system.md`, тексты дословно из колонки H):

```
Instagram carousel, <N> slides, portrait 4:5, 1080×1350.
Brand colors: background <hex>, text <hex>, accent <hex>, card <hex>. Use only these colors.
Font: <шрифт из дизайн-системы, например Montserrat>. Headlines ExtraBold, large, left aligned. Body Medium, 1–2 short lines.
Style: minimal editorial, generous white space, strong typographic hierarchy. No stock illustrations, no icons, no emojis, no decorative blobs, no gradients unless in the brand colors.
Slide 1 (cover): uploaded photo of the person, face fully visible in the upper half. Headline on a solid <card hex> plate in the lower third. Text never covers the face.
Slides 2–<N-1>: brand background, one thought per slide: headline + 1–2 lines, small slide number in the accent color.
Slide <N> (final): uploaded photo, call to action on a plate: <точная фраза с кодовым словом>.
Small handle <@ник> at the bottom of every slide.
Use exactly this text, do not rewrite, translate or add anything:
01 <текст>
02 <текст>
…
```

## Шаг 3. Карусель из шаблона
1. Сделай копию шаблона (инструмент копии или создания из шаблона). Нет такого инструмента — попроси человека: «В Canva на шаблоне: Файл → Создать копию, пришли ссылку».
2. Замени текст на каждой странице дословно из колонки H, число страниц под число слайдов (лишние удали, недостающие дублируй со средней).
3. Замени фото обложки и финала. Текст не на лице: если лицо под плашкой, сдвинь фото или плашку.
4. Экспорт PNG всех страниц → `output/<дата>-<тема>/K/`, ссылку на дизайн в чат: в Canva можно доправить руками.

## Чем Canva полезна, а чем нет
Плюс: всё правится руками, привычный редактор, работает из облачной рутины. Минус: без шаблона дизайн средний, текст иногда переносится криво — смотри PNG перед отправкой.
