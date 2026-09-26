# Нейрофотосессия на базе reference sheet — промты для Higgsfield

**Зачем.** Банк из 10–20 «своих» фото под контент за один вечер: обложки каруселей маршрута H, стартовые кадры рилсов, сторис, аватар. Лицо держится, потому что к каждому кадру прикладываются **два референса**: фото анфас + лист-эталон (`reference-sheet-prompt.md`).

**Когда.** После того как лист-эталон сделан и проверен. Один раз для банка, потом по 2–3 кадра под конкретные темы.

## Как запускать (Higgsfield через коннектор)

- Модель: **`nano_banana_pro`**. Кто обучил Soul-персонажа — можно `soul_2` с `--soul-id`, но текстовые слайды всё равно на nano_banana_pro.
- `aspect_ratio`: `3:4` для банка (портрет), `4:5` если кадр сразу под обложку карусели, `9:16` для стартового кадра рилса.
- `resolution: "2k"`. `medias`: `[{type:"image", role:"image", value:"<media_id фото анфас>"}, {type:"image", role:"image", value:"<media_id листа-эталона>"}]` — **на каждый кадр**.
- Промт = **БАЗА** (одна на всю сессию, копируется целиком) + **СЦЕНА** (своя на каждый кадр). Один кадр — одна генерация, батчем через `generate_image_batch` + `jobs_wait`. ≈2 кредита за кадр.
- Перед генерацией покажи владельцу список сцен на утверждение — кредиты не бесконечные.

## БАЗА (копировать целиком, на английском; в угловых скобках — заполнить)

```
Use the person from the reference images and keep the face EXACTLY as in the references:
same facial structure, eyes, nose, lips, eyebrows, skin texture, freckles and moles,
same hairstyle, hair color and length. Do not beautify, retouch, slim, age or stylize the face.
Same person on every image of this session.

SUBJECT: <woman / man>, <age range>, hair exactly as in the references.
OUTFIT for this session: <one outfit, e.g. cream linen blazer over a white silk top>.
Natural minimal makeup, no glasses (unless in the reference).

CAMERA: eye-level, near-frontal or slight three-quarter angle, 85mm lens look, shallow depth
of field. The person is LARGE in the frame — head and shoulders fill the upper half.
Calm expression: soft closed-lips half smile or neutral, mouth closed, eyes to camera or
just off camera. No open-mouth speaking shots, no low angles, no extreme expressions.

LIGHT: soft, directional, flattering; natural skin texture, no beauty smoothing, no filters.
STYLE: photorealistic editorial photography, premium lifestyle magazine, 8K photoreal,
true-to-life colors. Hands undistorted, natural, five fingers.

PALETTE of the scene: <brand colors from profile/design-system.md, e.g. deep pine green,
warm cream, muted gold accents>.

STRICT: no text, no letters, no typography, no logos, no watermarks, no captions, no UI,
no collage, no split screen, no frames or borders. One single photograph.

SCENE: <see below>
```

## СЦЕНЫ (6 универсальных заготовок — замени детали под свою нишу)

Каждая — отдельная генерация; вставляется вместо `<see below>`.

1. **Рабочее место / «эксперт за делом»**
   `She sits at a clean desk with an open laptop, hands resting near the keyboard, looking at the camera with a calm confident half smile. Background: modern office in the brand palette, soft window light from the left, blurred shelves and a plant. Medium shot, head and shoulders in the upper half of the frame.`
2. **Студийный портрет на бренд-фоне**
   `Studio portrait against a seamless <brand color> backdrop, soft key light from the front-left, gentle rim light on the hair, three-quarter angle, hands relaxed and out of frame. Clean, minimal, premium.`
3. **Улица / город**
   `Walking slowly on a quiet city street in soft late-afternoon light, blurred architecture behind, slight breeze in the hair, camera at eye level, natural relaxed expression, medium shot.`
4. **Спикер на сцене (безопасная версия)**
   `Standing on a small conference stage, microphone held low at chest level (not near the face), warm stage light from the front, blurred audience lights in the background, calm confident look toward the camera, closed-lips half smile, eye-level camera.`
5. **Кафе / разговор с клиентом**
   `Seated at a café table with a cup of coffee, laptop closed beside her, leaning slightly forward as if listening, warm interior light, blurred window behind, natural friendly expression.`
6. **Вечер дома / «после работы»**
   `Relaxed evening at home on a sofa, soft warm lamp light, cozy neutral interior in the brand palette, holding a phone loosely, looking at the camera with a gentle smile, medium close-up.`

Под конкретную тему карусели сцена придумывается своя (действие + реквизит + свет + ракурс), но правила базы не меняются.

## Чек-лист результата (каждый кадр)

- Лицо совпадает с листом-эталоном: глаза, нос, губы, линия волос. Сомневаешься — сравни рядом.
- Причёска и наряд одинаковы во всей сессии.
- Руки естественные, пять пальцев, без лишних предметов.
- Ни одной буквы, логотипа, плашки, рамки.
- Кадр цельный, человек крупно, голова не обрезана.
- Брак — одна перегенерация с той же сценой. Снова брак — сцена слишком сложная: упрости действие, верни камеру на уровень глаз, закрой рот.

## Что ломает лицо (проверено)

| Что | Почему | Замена |
|---|---|---|
| Открытый рот, речь, микрофон у лица | модель «дорисовывает» чужое лицо | полуулыбка с закрытыми губами, микрофон у груди |
| Ракурс снизу или сверху | лист-эталон не содержит таких углов | камера на уровне глаз |
| Сильные эмоции, смех, крик | искажает черты | спокойное выражение |
| Мелкий человек в кадре | лицо в 100 пикселей теряет идентичность | «head and shoulders fill the upper half» |
| Текст в сцене (вывески, экран с буквами) | модель пишет свои буквы | убрать текст из сцены, экран «blurred, no readable text» |

## Куда складывать

`photos/neuro/01-<сцена>.png … NN.png` + `photos/neuro/contact-sheet.jpg`. Строку в `photo-catalog.md`: сцена, наряд, где можно использовать (обложка / финал / сторис). Рутина 08 зеркалит папку в Drive.

Связанные файлы: `reference-sheet-prompt.md` (лист-эталон, делается до фотосессии), `higgsfield-prompt-template.md` (промт на слайды карусели с текстом).
