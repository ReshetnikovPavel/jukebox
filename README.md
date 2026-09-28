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

1. Клонируйте репозиторий:

   ```bash
   git clone <url-репозитория>
   cd jukebox
   ```

2. Создайте виртуальное окружение и установите зависимости:

   ```bash
   uv sync
   ```

3. Создайте файл `.env` и укажите токен бота:

   ```env
   TG_TOKEN=ваш_токен_телеграм_бота
   ```

4. Поместите в папку проекта файлы с cookies:

   - **`browser.json`** — файл с заголовками браузера для работы с YouTube Music API. Инструкция по получению: [ytmusicapi — передача заголовков](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - **`cookies-youtube-com.txt`** — файл с cookies для загрузки через yt-dlp. Инструкция по получению: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

5. Запустите бота:

   ```bash
   uv run python main.py
   ```

### Запуск через Docker Compose

1. Создайте файл `.env.prod` с переменными окружения:

   ```env
   TG_TOKEN=ваш_токен_телеграм_бота
   BGUTIL_PROVIDER_URL=http://bgutil-provider:4416
   ```

2. Поместите в папку проекта файлы с cookies:

   - **`browser.json`** — файл с заголовками браузера для работы с YouTube Music API. Инструкция по получению: [ytmusicapi — передача заголовков](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - **`cookies-youtube-com.txt`** — файл с cookies для загрузки через yt-dlp. Инструкция по получению: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

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
