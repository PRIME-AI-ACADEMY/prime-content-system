# Character reference sheet — лист-эталон лица для Higgsfield

**Зачем.** Одно фото анфас даёт модели только один ракурс. Лист с шестью ракурсами одного и того же лица — это «паспорт», который потом прикладывается референсом к каждой генерации (карусели H, стартовые кадры рилсов). С ним лицо держится стабильно, причёска не «плавает», профиль не превращается в чужого человека.

**Делается один раз.** Потом обновляется только если изменилась причёска или цвет волос.

## Как запускать (Higgsfield через коннектор)

1. Выбери **одно чёткое фото анфас**: дневной или студийный свет, без очков и головного убора, волосы — той причёски, которую хочешь видеть во всём контенте (она «запирается» на весь завод). Положи в `photos/reference-front.jpg`.
2. Загрузи фото в Higgsfield (`media_upload`) → получи `media_id`.
3. Генерация: модель **`nano_banana_pro`**, `aspect_ratio: "3:2"`, `resolution: "2k"`, `medias: [{type: "image", role: "image", value: "<media_id>"}]`, prompt — блок ниже **дословно, на английском** (модель лучше держит идентичность по английскому промту).
4. Проверь результат по чек-листу. Брак — перегенерируй один раз с тем же промтом. Если снова брак — замени исходное фото на более чёткое, проблема почти всегда в нём.
5. Сохрани лист как `photos/reference-sheet.png`, загрузи в Higgsfield → второй `media_id`. В рутинах 02/03 и в скилле `carousel` прикладывай **оба** референса: фото анфас + лист.

## Промт (копировать целиком)

```
Create a character reference sheet of the person in the attached photo.

This is a strict identity-preservation task. Keep the face EXACTLY as in the reference:
the same facial structure, head shape, eye shape and eye color, nose, lips, eyebrows,
skin tone and skin texture, freckles and moles, hairstyle, hair color, hair length and parting.
It must be the same person in every view — same age, same makeup, same expression style.
Do not beautify, retouch, slim, age, de-age, or stylize the face in any way.

Layout: a clean grid of six head-and-shoulders portraits of this one person,
3 columns × 2 rows, equal cell size, even spacing, generous margins around each portrait.
Row 1: front view looking straight into the camera · three-quarter view turned to the left ·
three-quarter view turned to the right.
Row 2: left profile · right profile · front view with the head slightly tilted down,
eyes looking at the camera.
Neutral calm expression, mouth closed, in every cell. The same outfit in all six cells:
a plain black top.

Background: pure white (#FFFFFF), seamless, no objects, no shadows, no gradients, no props.
Lighting: soft, even, frontal studio light; no harsh shadows, no color cast, no rim light.
Style: photorealistic, high detail, tack sharp focus on the eyes, natural skin, no filters,
no beauty smoothing.
Format: horizontal 3:2, high resolution.
Absolutely no text, labels, captions, numbers, arrows, frames, borders, logos or watermarks.
```

## Чек-лист результата

- Шесть ячеек, ровная сетка 3×2, белый фон без теней.
- Во всех шести — одно лицо: сравни глаза, нос и линию волос с исходным фото по очереди.
- Причёска одинаковая во всех ячейках (длина, пробор, цвет).
- Нет текста, цифр, рамок и «лишних» людей.
- Профили похожи на тебя, а не на «усреднённую модель» — это самая частая ошибка.

## Типовые ошибки

| Что видишь | Причина | Что делать |
|---|---|---|
| Лицо «улучшили», другие скулы или губы | исходное фото мягкое, с фильтром | взять фото без фильтров и ретуши |
| В профиле другой нос или подбородок | модель не видит профиль на исходнике | добавить вторым референсом реальное фото в три четверти |
| Волосы разной длины в ячейках | на исходнике волосы убраны или скрыты | фото с полностью видимой причёской |
| Появились подписи или сетка с рамками | промт сокращён | вставить промт целиком, последняя строка обязательна |
| Возраст «поплыл» | свет на исходнике контровой | фото с ровным фронтальным светом |

Связанные файлы: `higgsfield-prompt-template.md` (промт на слайды), рутина `templates/routines/02-генерация-медиа-облако.md`.
