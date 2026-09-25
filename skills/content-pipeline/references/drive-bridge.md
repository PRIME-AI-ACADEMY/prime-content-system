# Мост: локальный файл → Google Drive (и публичная ссылка для Postiz)

Ни один коннектор не берёт файл с диска человека напрямую: Composio `UPLOAD_FILE` ждёт `s3key`, Drive MCP `create_file` тянет base64 (1–2 МБ на слайд = сотни тысяч токенов). Поэтому файлы едут через Higgsfield. Проверено: слайды, рилсы, профили — размеры совпали.

## Порядок выбора пути
1. **Есть папка Google Drive для компьютера** — `~/Library/CloudStorage/GoogleDrive-*/` (Mac) или `G:\` (Windows): просто скопируй файл туда (`cp`), ссылку возьми через Composio `GOOGLEDRIVE_FIND_FILE`.
2. **Иначе — мост Higgsfield → Drive** (ниже).
3. **Никогда**: не проси человека грузить руками, не гоняй base64 через чат.

## Мост Higgsfield → Drive (4 шага)

**1. Подписанные ссылки.** Higgsfield `media_upload` с `files[]` (до 20 файлов за вызов): на каждый файл вернёт `upload_url` (подписанный PUT) и постоянную ссылку CloudFront.

**2. Загрузка локально.** На каждый файл одна команда, ответ должен быть `200`:
```bash
curl -X PUT -H "Content-Type: <тип>" --data-binary @<файл> '<upload_url>'
```
Тип строго как подписан `upload_url`: `.png` → `image/png` · `.jpg` → `image/jpeg` · `.mp4` → `video/mp4` · `.html` → `text/html` · `.md` и прочий текст → `application/octet-stream`. Если ответ `media_upload` просит `media_confirm` — вызови его.

**3. Импорт в Drive.** Composio `GOOGLEDRIVE_UPLOAD_FROM_URL`: `source_url` = ссылка CloudFront, `name`, `mime_type`, `parent_folder_id`. Все файлы одной пачкой через `COMPOSIO_MULTI_EXECUTE_TOOL`.

**4. Доступ и ссылка.** Папке — `GOOGLEDRIVE_CREATE_PERMISSION` (anyone, reader). В колонку K контент-плана: первой строкой ссылка на папку Drive, дальше с новой строки ссылки CloudFront каждого файла по порядку — их берёт Postiz (`uploadFromUrlTool` принимает только публичные прямые ссылки, ссылки Drive не подходят).

## Кто этим пользуется
`carousel`, `reels`, `reels-montazh`, `foundation` (зеркало профилей), `autopost`, `content-pipeline`, рутины 02/03/08. `setup-check` проверяет, что доступен хотя бы один путь: папка Drive для компьютера или коннектор Higgsfield + Composio Drive.

## Грабли
- Цикл в zsh: `for f in *.png` работает, а `for seg in "a b"` не делится на слова. Пути с пробелами и кириллицей — в кавычках.
- HEIC Pillow не открывает: `sips -s format jpeg <файл> --out <файл>.jpg` (Mac), оригинал оставь.
- В локальной рутине — одна команда на файл, без `$(...)`, `>` и `;`, иначе она встанет на разрешении.
