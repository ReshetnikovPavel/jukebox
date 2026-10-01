#!/bin/sh
set -e

if [ -d "/data" ]; then
    chown -R appuser:appuser /data
fi

for f in /app/browser.json /app/cookies-youtube-com.txt; do
    if [ -f "$f" ]; then
        chown appuser:appuser "$f" || true
    fi
done

exec runuser -u appuser -- "$@"
