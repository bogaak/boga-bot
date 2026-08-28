FROM python:3.13-slim

WORKDIR /data

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

CMD ["uv", "run", "main.py"]
