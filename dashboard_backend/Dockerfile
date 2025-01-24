FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir -p /app/src/logs; touch /app/src/logs/chronos.log
WORKDIR /app
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /bin/uv
# Install requirements first in a separate layer to avoid re-installing them on
# every code changes
COPY pyproject.toml .
# Create the virtual environment
RUN uv sync --no-dev
# Copy the application code
COPY . .
RUN uv sync
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
