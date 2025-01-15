FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.7.1

WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy pyproject.toml and poetry.lock into the container
COPY pyproject.toml poetry.lock* /app/

# Ensure the correct version of Poetry is used and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction

# Prepare logs folder
RUN mkdir -p /app/src/logs; touch /app/src/logs/chronos.log

# Copy the rest of the application code
COPY . /app

# Ensure the entrypoint script is executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
