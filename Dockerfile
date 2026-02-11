FROM python:3.14-slim

WORKDIR /app

RUN apt update && apt upgrade && apt install ffmpeg -y && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "-m", "main"]
