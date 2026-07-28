FROM python:3.14

WORKDIR /app

RUN apt update && apt install nodejs ffmpeg curl -y  --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh && \
    mv /root/.deno/bin/deno /usr/local/bin/deno

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "-m", "main"]
