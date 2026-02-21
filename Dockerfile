FROM python:3.14

WORKDIR /app

RUN apt update && apt upgrade -y && apt install nodejs -y && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "-m", "main"]
