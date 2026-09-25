# Промпт Higgsfield для карусели (маршрут H) — проверенный шаблон

Цель: слайд выходит с первого раза. Один промпт = один слайд. Референс лица (`media_id`) в `medias` на **каждый** слайд. Модель `nano_banana_pro` (списывает как `nano_banana_2`, ≈2 кредита за слайд), `aspect_ratio 4:5`, `resolution 2k`.

## Шаблон (повторяется целиком на каждом слайде)

```
Use the person from the reference image, keep their exact face. Vertical 4:5 Instagram
carousel image, premium editorial magazine photograph, 8K photoreal.
SUBJECT: same person, same outfit on every slide: <один наряд>, same hair.
PALETTE: <цвета из profile/design-system.md: фон dominant, текст, акцент>.
COMPOSITION: ONE single full-bleed photograph covering the entire frame edge to edge.
NO split screen, NO flat color panels, NO blocks, NO borders, NO collage. Rule of thirds.
The ONLY text block sits in <место: lower-left / upper-left / right third> on a calm
dark area of the real scene, never on the face.
TYPOGRAPHY baked into the photo: geometric grotesque bold sans-serif (Montserrat-like),
key words in <акцентный цвет>.
TEXT TO RENDER, ONE block only, each line exactly once (Russian, Cyrillic, exactly as
written, letter by letter):
Line 1 (large, <цвет текста>): <строка>
Line 2 (smaller, <акцент>): <строка>
STRICT: the text appears ONE time only, never duplicated. Do NOT add quotation marks,
slide numbers, labels, watermarks, logos, UI, digits or any other text. No typos.
Never cover the face; do not crop the head; hands undistorted.
SCENE: <сцена на английском, конкретное действие, реквизит, свет, ракурс>.
```

## Правила, из-за которых был брак
- **Без кавычек** вокруг русского текста в промпте: модель рисует «» на слайде.
- **Без «COVER», «slide 6 of 6», «01», «Слайд 01»** внутри промпта: модель пишет их на картинке. Нумерация живёт в таблице, не в промпте.
- **Без цифр** в тексте слайда, если цифра не часть смысла.
- **Текст один раз**: строка про «each line exactly once» обязательна, иначе дубли.
- **Один цельный кадр**: без строк про full-bleed модель режет кадр на плашку и фото.
- **Сцена на каждый слайд своя**, наряд и причёска одни на всю карусель.

## Для тех, у кого нет Soul: референс-лист за 2 кредита
1. Загрузи 1–2 реальных фронтальных фото через `media_upload` (получишь `media_id`).
2. Сгенерируй **один референс-лист**: `nano_banana_pro`, 1:1, промпт «Use the person from the reference image, keep their exact face. Character reference sheet: front view, three-quarter view, profile, same outfit <наряд>, same hair, neutral studio light, no text». Это ≈2 кредита.
3. Проверь, что лицо совпадает. Дальше на каждый из 4–5 слайдов передавай в `medias` и исходное фото, и этот референс-лист. Лицо держится ровнее, чем с одного фото.

## Пример логики (Ангелина). Не копируй сцены примера — придумай свои под тему
```
GLOBAL — repeat on EVERY slide: model nano_banana_pro · face reference <media_id> on every
slide. SUBJECT: same person, same outfit, same hair. PALETTE: brand colors.
COMPOSITION: complete organic editorial frame, never empty background; rule of thirds;
caption in calm negative space, never on the face. TYPOGRAPHY: Montserrat-like bold,
key words in accent color. ON-SLIDE TEXT VERBATIM (Cyrillic), nothing else on the slide.
01 COVER — scene…; TEXT: large «…» / small «…» … 06 CTA — scene…; gold plaque «Пиши СЛОВО».
```
Здесь ценна логика: глобальный блок один на всю карусель, у каждого слайда своя сцена, текст дословно, CTA-плашка на финале. В рабочий промпт слайда номера «01 COVER», «06 CTA» и кавычки «…» **не переносятся** — они только для человека в таблице.

## Чистка промпта из таблицы перед генерацией (carousel, рутина 02)
В таблицах, собранных старым шаблоном, ошибки уже есть. Перед вызовом модели:
1. убери «», “”, "" вокруг русского текста;
2. убери «Слайд NN», «Slide N of M», «COVER», «CTA», «01»–«99» как метки;
3. если нет строк про full-bleed и «each line exactly once» — допиши из шаблона;
4. текст слайда бери из колонки H дословно, строка за строкой.

## QA после генерации (обязательно, перед выдачей)
Открой каждый слайд и проверь: текст побуквенно = H · нет кавычек и цифр · текст один раз · кадр цельный, без плашек и полос · лицо как на референсе · текст не на лице. Брак — 1 перегенерация. Снова брак — лучший вариант + пометка в отчёте.
