# Jukebox

Telegram bot for searching for and downloading music from YouTube and YouTube Music.

[English](README.md) | [Русский](README.ru.md)

[@jukebox_music_downloader_bot](https://t.me/jukebox_music_downloader_bot)

## Features

- **Track search** — search for songs by title and download them
- **Album search** — search for albums, view tracks, and download them
- **Artist search** — search for artists and view their songs, albums, and singles
- **Video search** — search for and download audio from YouTube videos
- **Lyrics** — search for and retrieve song lyrics

## Commands

| Command    | Description                                      |
| ---------- | ------------------------------------------------ |
| `/start`   | Greeting and getting started                     |
| `/help`    | Help on available commands                       |
| `/track`   | Search for a track                               |
| `/album`   | Search for an album                              |
| `/artist`  | Search for an artist                             |
| `/video`   | Search for a video                               |
| `/lyrics`  | Search for song lyrics                           |

## Installation and running

### Local run

1. Clone the repository:

   ```bash
   git clone https://github.com/ReshetnikovPavel/jukebox
   cd jukebox
   ```

2. Install dependencies:

   - FFmpeg [ffmpeg.org](https://ffmpeg.org/download.html)
   - Node.js [nodejs.org](https://nodejs.org/ru/download/)
   - Deno [deno.com](https://docs.deno.com/runtime/getting_started/installation/)

3. Create a virtual environment and install dependencies:

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

4. Get a token for the Telegram bot:

   1. Open [@BotFather](https://t.me/BotFather) in Telegram
   2. Send the `/newbot` command
   3. Follow the instructions: choose a name for the bot and its `@username`
   4. BotFather will send you a token like `123456789:ABCDefGhIJKlmNoPQRsTUVwxyZ` — save it

5. Get your Chat ID:

   Message the [@userinfobot](https://t.me/userinfobot) bot — it will send you your ID

6. Create a `.env` file and specify the environment variables:

   ```env
   TG_TOKEN=token_received_from_BotFather
   DEVELOPER_CHAT_ID=your_chat_id
   ```

7. Place the cookie files in the project folder:

   - `browser.json` — a file with browser headers for working with the YouTube Music API. Instructions for obtaining it: [ytmusicapi — passing headers](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - `cookies-youtube-com.txt` — a cookie file for downloading via yt-dlp. Instructions for obtaining it: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

8. Clean the cookies of unnecessary domains using the script:

   ```bash
   python scripts/clean_cookies.py cookies-youtube-com.txt
   ```

9. Download and run `bgutil-ytdlp-pot-provider` (in a separate terminal):

   Option 1. Docker (recommended):

   ```bash
   docker run --name bgutil-provider -d -p 4416:4416 --init brainicism/bgutil-ytdlp-pot-provider
   ```

   Option 2. From source:

   ```bash
   git clone --depth 1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /tmp/bgutil-provider
   cd /tmp/bgutil-provider/server
   npm ci
   npx tsc
   node build/main.js
   ```

   By default, the service will start at `http://127.0.0.1:4416`. If you run it on a different address/port, specify it in `BGUTIL_PROVIDER_URL` in `.env`.

10. Start the bot:

   ```bash
   python main.py
   ```

### Running with Docker Compose

1. Create a `.env.prod` file with the environment variables:

   ```env
   TG_TOKEN=your_token_from_BotFather
   BGUTIL_PROVIDER_URL=http://bgutil-provider:4416
   ```

2. Place the cookie files in the project folder:

   - `browser.json` — a file with browser headers for working with the YouTube Music API. Instructions for obtaining it: [ytmusicapi — passing headers](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html)
   - `cookies-youtube-com.txt` — a cookie file for downloading via yt-dlp. Instructions for obtaining it: [yt-dlp — cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

3. Start the containers:

   ```bash
   docker compose up -d
   ```

## Environment variables

| Variable               | Description                                                | Required |
| ---------------------- | ---------------------------------------------------------- | -------- |
| `TG_TOKEN`             | Telegram bot token                                         | ✅       |
| `BGUTIL_PROVIDER_URL`  | URL of the `bgutil-ytdlp-pot-provider` service             | ❌       |
| `DEVELOPER_CHAT_ID`    | Developer Chat ID for notifications                        | ❌       |
| `MIGRATION`            | Enable the migration command (`true`/`false`)              | ❌       |
| `SQLITE_PATH`          | Path to the SQLite database file (in Docker: `/data/jukebox.db`) | ❌       |
