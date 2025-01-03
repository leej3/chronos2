FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.7.1

WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev
RUN mkdir -p /app/src/logs; touch /app/src/logs/chronos.log
COPY . /app
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
