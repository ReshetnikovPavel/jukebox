# Jukebox

Telegram-бот для поиска и загрузки музыки из YouTube и YouTube Music.

[@jukebox_music_downloader_bot](https://t.me/jukebox_music_downloader_bot)

## Возможности

- **Поиск треков** — поиск песен по названию с возможностью скачивания
- **Поиск альбомов** — поиск альбомов с просмотром треков и скачиванием
- **Поиск артистов** — поиск исполнителей с просмотром песен, альбомов и синглов
- **Поиск видео** — поиск и скачивание аудио из видео с YouTube
- **Тексты песен** — поиск и получение текстов песен

## Команды

| Команда    | Описание                                    |
| ---------- | ------------------------------------------- |
| `/start`   | Приветствие и начало работы                 |
| `/help`    | Справка по доступным командам               |
| `/track`   | Поиск трека                                 |
| `/album`   | Поиск альбома                               |
| `/artist`  | Поиск артиста                               |
| `/video`   | Поиск видео                                 |
| `/lyrics`  | Поиск текста песни                          |

## Установка и запуск

### Локальный запуск

1. Cклонируйте репозиторий:

   ```bash
   git clone https://github.com/ReshetnikovPavel/jukebox
   cd jukebox
   ```

2. Установите зависимости:

   - FFmpeg [ffmpeg.org](https://ffmpeg.org/download.html)
   - Node.js [nodejs.org](https://nodejs.org/ru/download/).
   - Deno [deno.com](https://docs.deno.com/runtime/getting_started/installation/).

3. Создайте виртуальное окружение и установите зависимости:

   Linux, macOS
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -e .
   ```
   Windows (cmd)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -e .
   ```

   Windows (PowerShell)
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -e .
   ```

4. Получите токен для Telegram-бота:

   1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
   2. Отправьте команду `/newbot`
   3. Следуйте инструкциям: придумайте название бота и его `@username`
   4. BotFather пришлёт вам токен вида `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ` — сохраните его

5. Получите свой Chat ID:

   Напишите боту [@userinfobot](https://t.me/userinfobot) — он пришлёт ваш ID

6. Создайте файл `.env` и укажите переменные окружения:

   ```env
   TG_TOKEN=полученный_токен_от_BotFather
   DEVELOPER_CHAT_ID=ваш_chat_id
   ```

6. Поместите в папку проекта файлы с cookies:

   - `browser.json` — файл с заголовками браузера для работы с YouTube Music API. Инструкция по получению: [ytmusicapi — передача заголовков](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - `cookies-youtube-com.txt` — файл с cookies для загрузки через yt-dlp. Инструкция по получению: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
   
7.   Очистите cookies от лишних доменов с помощью скрипта:

   ```bash
   python scripts/clean_cookies.py cookies-youtube-com.txt
   ```

8. Скачайте и запустите `bgutil-ytdlp-pot-provider` (в отдельном терминале):

   Вариант 1. Docker (рекомендуется):
   
   ```bash
   docker run --name bgutil-provider -d -p 4416:4416 --init brainicism/bgutil-ytdlp-pot-provider
   ```
   
   Вариант 2. Из исходников:
   
   ```bash
   git clone --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /tmp/bgutil-provider
   cd /tmp/bgutil-provider/server
   npm ci
   npx tsc
   node build/main.js
   ```
   
   По умолчанию сервис запустится на `http://127.0.0.1:4416`. Если вы запускаете его на другом адресе/порту — укажите его в `BGUTIL_PROVIDER_URL` в `.env`.

9. Запустите бота:

   ```bash
   python main.py
   ```

### Запуск через Docker Compose

1. Создайте файл `.env.prod` с переменными окружения:

   ```env
   TG_TOKEN=ваш_токен_от_BotFather
   BGUTIL_PROVIDER_URL=http://bgutil-provider:4416
   ```

2. Поместите в папку проекта файлы с cookies:

   - `browser.json` — файл с заголовками браузера для работы с YouTube Music API. Инструкция по получению: [ytmusicapi — передача заголовков](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - `cookies-youtube-com.txt` — файл с cookies для загрузки через yt-dlp. Инструкция по получению: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

3. Запустите контейнеры:

   ```bash
   docker compose up -d
   ```

## Переменные окружения

| Переменная             | Описание                                                | Обязательная |
| ---------------------- | ------------------------------------------------------- | ------------ |
| `TG_TOKEN`             | Токен Telegram-бота                                     | ✅           |
| `BGUTIL_PROVIDER_URL`  | URL сервиса bgutil-ytdlp-pot-provider                   | ❌           |
| `DEVELOPER_CHAT_ID`    | Chat ID разработчика для уведомлений                    | ❌           |
| `MIGRATION`            | Включить команду миграции (`true`/`false`)              | ❌           |
| `SQLITE_PATH`          | Путь к файлу SQLite-базы (в Docker: `/data/jukebox.db`) | ❌           |
