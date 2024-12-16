FROM python:3.11-slim

# Install necessary packages including PostgreSQL development packages
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /opt/app
COPY pyproject.toml poetry.lock /opt/app/
RUN poetry install --no-root

SHELL ["/bin/bash", "--login", "-c"]
COPY --from=ghcr.io/astral-sh/uv:0.4.0 /uv /bin/uv
RUN mkdir -p /opt/data
COPY . /opt/app/
RUN uv sync
# CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5172"]
CMD ["poetry", "run", "python", "main.py"]