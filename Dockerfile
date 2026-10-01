FROM python:3.14

WORKDIR /app

RUN apt update && apt install nodejs ffmpeg -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh && \
    mv /root/.deno/bin/deno /usr/local/bin/deno

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

RUN groupadd --gid 1000 appuser 2>/dev/null || true; \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser 2>/dev/null || useradd -m appuser; \
    mkdir -p /data && \
    chown -R appuser:appuser /app /data

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "main"]
