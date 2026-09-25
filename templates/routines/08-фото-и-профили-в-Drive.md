# 08 · Фото и профили в Drive

**Назначение.** Облачные рутины живут в claude.ai и твоих файлов на ноутбуке не видят. Эта рутина раз в неделю копирует папку `profile/` (фундамент, дизайн-система, профиль Threads), банк фото и каталог в Google Drive. После неё облако «знает» тебя: твою аудиторию, оффер, голос, цвета и фото.

**Когда.** Воскресенье 20:00 (и сразу после любой правки профиля — Run now). **Где.** 💻 Локально, из папки завода.

**Что нужно заранее**
- Папка завода с `.claude/settings.local.json` из `templates/settings.local.safe.json` (allow-лист). Рутину создаёшь ИЗ ЭТОЙ папки; идёт она всегда в режиме Manual, поэтому команды в промте — простые.
- Папка завода с `profile/` (шесть файлов + foundation.html), `photos/`, `photo-catalog.md`, `fonts/`. Профиль Threads в `~/Claude/threads/profile/` (если ведёшь Threads).
- Коннектор Composio (Google Drive) в приложении.
- Папка Drive «Контент-завод» — рутина создаст сама при первом запуске и напечатает ссылку. Эту ссылку вставь во все облачные рутины вместо `[ссылка на папку Drive]`.

---

## ПРОМТ ДЛЯ АНГЕЛИНЫ

```
Ты — рутина «08 зеркало в Drive» контент-завода Angelina (PRIME AI). Работай сама,
ничего не спрашивай. Ты в папке завода. Команды только простые, без $(...) и >.
Коннектор: Composio (Google Drive).

ДАННЫЕ
- Локально: profile/ (business-dna.md, audience.md, hunt-ladder.md, offer.md, funnels.md,
  tone-of-voice.md, design-system.md, foundation.html), photos/, photo-catalog.md,
  fonts/Montserrat-VF.ttf. Профиль Threads: ~/Claude/threads/profile/ (dna.md, voice.md,
  funnel.md, rubrics.md).
- Drive: папка «Контент-завод» в корне Моего диска. Внутри: profile/, profile/threads/,
  photos/, Готовое/.
- Публичная ссылка на локальный файл для импорта (мост drive-bridge): Higgsfield
  media_upload (files[], до 20) → curl -X PUT -H "Content-Type: <тип>" --data-binary @файл
  <upload_url> (.md → application/octet-stream, .html → text/html, .jpg → image/jpeg) →
  media_confirm, если просит → CloudFront-URL → Composio UPLOAD_FROM_URL. Есть папка
  ~/Library/CloudStorage/GoogleDrive-*/ — просто cp туда. Текстовые файлы можно создавать
  напрямую содержимым (CREATE_FILE).

ШАГИ
1. Найди в Drive папку «Контент-завод». Нет — создай её и подпапки profile/,
   profile/threads/, photos/, Готовое/.
2. Профили: каждый .md из profile/ и ~/Claude/threads/profile/ → в Drive тем же именем.
   Файл уже есть в Drive → перезапиши (удали старый в корзину, залей новый).
   foundation.html — тоже залей.
3. photo-catalog.md → в Drive «Контент-завод»/photos/.
4. Фото: сравни список файлов в photos/ (jpg, jpeg, png; HEIC сначала конвертируй
   командой sips -s format jpeg <файл> --out <файл>.jpg) со списком в Drive photos/.
   Заливай только те, которых в Drive ещё нет, по имени. Уже залитые — пропускай.
   Больше 40 новых — залей первые 40, остальные в следующий раз (напиши об этом).
5. Отчёт: ссылка на папку «Контент-завод» в Drive, сколько профилей обновлено,
   сколько фото добавлено, сколько пропущено. Ничего нового — «нет строк».

ОШИБКИ
- Нет profile/ локально → напиши «нет профиля, запусти foundation» и закончи.
- Файл не залился → перечисли имена в отчёте, остальное продолжай.
- Никогда не завершай молча.
```

---

## ПРОМТ ДЛЯ УЧАСТНИКА

```
Ты — рутина «08 зеркало в Drive» моего контент-завода. Работай сама, ничего не
спрашивай. Ты в папке завода. Команды только простые, без $(...) и >.
Коннектор: Composio (Google Drive).

ДАННЫЕ
- Локально: profile/ (business-dna.md, audience.md, hunt-ladder.md, offer.md, funnels.md,
  tone-of-voice.md, design-system.md, foundation.html), photos/, photo-catalog.md,
  fonts/. Профиль Threads: ~/Claude/threads/profile/ (dna.md, voice.md, funnel.md,
  rubrics.md) — если папки нет, пропусти.
- Drive: папка «Контент-завод» в корне Моего диска. Внутри: profile/, profile/threads/,
  photos/, Готовое/.
- Публичная ссылка на локальный файл для импорта (мост drive-bridge): Higgsfield
  media_upload (files[], до 20) → curl -X PUT -H "Content-Type: <тип>" --data-binary @файл
  <upload_url> (.md → application/octet-stream, .html → text/html, .jpg → image/jpeg) →
  media_confirm, если просит → CloudFront-URL → Composio UPLOAD_FROM_URL. Есть папка
  ~/Library/CloudStorage/GoogleDrive-*/ — просто cp туда. Текстовые файлы можно создавать
  напрямую содержимым (CREATE_FILE).

ШАГИ
1. Найди в Drive папку «Контент-завод». Нет — создай её и подпапки profile/,
   profile/threads/, photos/, Готовое/.
2. Профили: каждый .md из profile/ и ~/Claude/threads/profile/ → в Drive тем же именем.
   Файл уже есть в Drive → перезапиши (удали старый в корзину, залей новый).
   foundation.html — тоже залей.
3. photo-catalog.md → в Drive «Контент-завод»/photos/. Нет каталога — составь его сам:
   по каждому фото одна строка «имя · план (портрет/полный/селфи) · где · для чего».
4. Фото: сравни список файлов в photos/ (jpg, jpeg, png; HEIC сначала конвертируй:
   Mac — sips -s format jpeg <файл> --out <файл>.jpg. Windows — через Pillow с
   pillow-heif) со списком в Drive photos/. Заливай только те, которых в Drive ещё нет,
   по имени. Уже залитые — пропускай. Больше 40 новых — залей первые 40, остальные
   в следующий раз (напиши об этом).
5. Отчёт: ссылка на папку «Контент-завод» в Drive, сколько профилей обновлено,
   сколько фото добавлено, сколько пропущено. Ничего нового — «нет строк».

ОШИБКИ
- Нет profile/ локально → напиши «нет профиля, запусти foundation» и закончи.
- Файл не залился → перечисли имена в отчёте, остальное продолжай.
- Никогда не завершай молча.
```

---

## Как проверить, что сработало
- Drive → «Контент-завод» → profile/: шесть .md + foundation.html; profile/threads/: четыре .md; photos/: фото и photo-catalog.md; Готовое/ пустая.
- В отчёте есть ссылка на папку. Скопируй её в рутины 01, 02, 04, 07 вместо `[ссылка на папку Drive]`.
- Второй запуск подряд пишет «нет строк» (ничего нового) — значит, дубли не плодятся.

## Типовые ошибки
| Что видишь | Причина | Что делать |
|---|---|---|
| Рутина спрашивает «Разрешить?» на команду | создана не из папки завода (нет allow-листа `settings.local.safe.json`) или в промте `$(…)`, `>`, `;` | пересоздай из папки завода; упрости команду |
| Спрашивает про коннектор | первый вызов инструмента | «Always allow» один раз, запоминается |
| Фото не залились | HEIC или нет публичной ссылки | конвертируй в jpg; проверь коннектор Higgsfield |
| Две папки «Контент-завод» | создала заново | удали пустую; в промте есть «найди, нет — создай» |
| Облачная рутина не видит профиль | залито в другой Google-аккаунт | Composio Drive должен быть на тот же аккаунт, где таблица |
