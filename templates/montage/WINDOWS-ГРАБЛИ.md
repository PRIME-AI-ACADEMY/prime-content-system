# WINDOWS-ГРАБЛИ — что ломается у участников на Windows и как чинить (для ведущей)

> Контекст: Claude Code на Windows выполняет команды через **Git Bash** (нужен Git for Windows). Значит: `~` работает, `mkdir -p`/`curl`/`grep` есть, пути можно писать с прямыми слэшами. PowerShell участник не открывает. Установка на Windows в прошлый раз не тестировалась — прогнать на одном ноутбуке до старта.

| # | Симптом | Причина | Фикс (что говоришь участнику) |
|---|---|---|---|
| 1 | Claude вообще не выполняет команды: «bash not found» / Bash tool не работает | Нет Git for Windows — Claude Code использует его bash | Поставить Git руками с git-scm.com (Next-Next-Next), **полностью закрыть и открыть Claude Code**. Это единственный «ручной» шаг на Windows |
| 2 | После `winget install ...` команда «не найдена» (`ffmpeg`, `node`, `python`, `git`) | PATH обновился только для новых процессов; приложение держит старый | **Полностью закрыть Claude Code** (и из трея, правый клик → Quit) → открыть заново → продолжить с того же шага. Не «перезапустить чат», а именно приложение |
| 3 | `winget` не найден | Старый Windows 10 / нет «App Installer» | Microsoft Store → «Установщик приложений» (App Installer) → обновить. Либо ставить ffmpeg/Node/Python руками с сайтов и вернуться |
| 4 | `python` открывает Microsoft Store или молча ничего не делает | Windows подсовывает «псевдоним выполнения приложений» вместо питона | Параметры → Приложения → Дополнительные параметры приложений → Псевдонимы выполнения приложений → выключить `python.exe` и `python3.exe`. Либо `winget install Python.Python.3.12` → закрыть/открыть приложение |
| 5 | `python3: command not found` | На Windows команда называется `python` (или `py`) | Везде `python`. В `.studio-env` — `PY=python` или полный путь |
| 6 | venv создан, но `~/.reels-venv/bin/python` нет | На Windows структура venv другая | `~/.reels-venv/Scripts/python.exe`. В `.studio-env` — полный путь с прямыми слэшами: `PY=C:/Users/Имя/.reels-venv/Scripts/python.exe` |
| 7 | `pip` не найден / `No module named pip` | Питон без pip (Store-версия, урезанная сборка) | `python -m ensurepip --upgrade` → `python -m pip install pillow "opencv-python-headless<5"` |
| 8 | `Unknown encoder 'h264_videotoolbox'` | Аппаратный кодек Apple, на Windows его нет | `-c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p`. В `.studio-env` — `VCODEC=libx264 -preset veryfast -crf 21`. `build_reel.py` и так рендерит libx264 |
| 9 | `whisper-cli: command not found` / `brew: command not found` | Homebrew и whisper-cpp — только Mac | Пропустить Шаг 9. Для субтитров дома — `npx hyperframes transcribe`. Промт А whisper не нужен |
| 10 | Путь с `C:\Users\...` ломает команду / «No such file» | В bash обратный слэш — экранирование | Прямые слэши `C:/Users/...` или `/c/Users/...`; путь в двойных кавычках. Кириллица и пробелы в пути — только в кавычках |
| 11 | Node/Chrome/npx падают с непонятной ошибкой в пути | Кириллица в имени пользователя или папки (`C:\Users\Оля\Рабочий стол`) | Папку студии делать `C:\reels`. Если имя пользователя кириллицей — ставить HyperFrames дома, трек А работает |
| 12 | «Путь слишком длинный» / ENAMETOOLONG в `node_modules` | Лимит 260 символов | Короткая папка `C:\reels`. Радикально: включить long paths (`reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1` — нужны права админа, лучше дома) |
| 13 | Всплывает окно «Контроль учётных записей» (UAC) при winget | Установка требует прав администратора | Участник жмёт «Да». Claude это окно не видит — предупредить заранее |
| 14 | SmartScreen «Windows защитил ваш компьютер» / Defender «сканирование» при первом запуске ffmpeg или Chrome | Неподписанные/новые бинарники | «Подробнее» → «Выполнить в любом случае». Defender может 1–2 минуты проверять Chrome (~150 МБ) при первом рендере HyperFrames — это не зависание |
| 15 | Первый `npm run render` (HyperFrames) висит 3–5 минут | Качает собственный Chrome ~150 МБ | Только дома, не на воркшоп-wi-fi. На воркшопе трек Б не запускать |
| 16 | `curl: (…)` в PowerShell / скачался файл 0 байт или HTML | В PowerShell `curl` — алиас Invoke-WebRequest | В Git Bash (внутри Claude Code) настоящий curl, всё ок. В PowerShell писать `curl.exe`. Проверять размер: шрифт > 100 КБ, каскад ≈ 930 КБ |
| 17 | В выводе команд кракозябры вместо кириллицы | Консоль в cp1251/cp866 | Не ошибка. Проверять результат кадрами (`.check.jpg`), не текстом в консоли. При желании `export PYTHONIOENCODING=utf-8` |
| 18 | Видео/скрипт «занят другим процессом», файл не перезаписывается | OneDrive синхронизирует Рабочий стол/Документы; антивирус держит файл | Студия и видео — вне OneDrive (`C:\reels`). Повторить команду через 10 сек |
| 19 | `externally-managed-environment` | Только Homebrew-питон на Mac | На Windows не бывает. Если pip ругается на права — `python -m pip install --user ...` |
| 20 | Рендер пачки очень медленный / ноутбук замирает | Нет аппаратного кодека, слабый CPU, антивирус сканирует каждый mp4 | Рендерить по одному ролику (Промт А так и делает), `-preset veryfast`, закрыть браузер. 5 роликов по 6 сек — 3–5 минут |
| 21 | `import cv2` — «DLL load failed» | Нет Visual C++ Redistributable | `winget install Microsoft.VCRedist.2015+.x64` → закрыть/открыть приложение. Пока нет — скрипт работает без детекции и предупреждает |
| 22 | `sips`, `say`, `open` — «не найдено» | Команды macOS | Не нужны для монтажа. Уменьшить фото для карусели — Pillow (`Image.thumbnail`) или просто взять фото с телефона как есть |

## Порядок действий, если у участника на Windows «ничего не работает»
1. `git --version` работает? Нет → грабля 1.
2. Полностью закрыть/открыть Claude Code (грабля 2) — лечит 60 % случаев.
3. Папка `C:\reels`, без кириллицы и OneDrive (грабли 11, 18).
4. `python` → Store? Грабля 4.
5. Всё остальное — трек А без cv2 всё равно рендерит; детекцию и HyperFrames доделать дома.

## На слайд — коротко
- Windows: команда «не найдена» после установки → **полностью закрой и открой Claude Code**.
- `python`, не `python3`; venv → `Scripts/python.exe`.
- Папка `C:\reels` — латиницей, не OneDrive, не Рабочий стол.
- Кодек `libx264`, не videotoolbox. Whisper и Homebrew — только Mac, пропускаем.
- Пути в кавычках, слэши прямые.
- Окна UAC / SmartScreen / Defender — жми «Да» / «Выполнить в любом случае».
- HyperFrames (Chrome 150 МБ) — дома.
