FROM python:3.11-slim
SHELL ["/bin/bash", "--login", "-c"]
COPY --from=ghcr.io/astral-sh/uv:0.4.0 /uv /bin/uv
RUN mkdir -p /opt/data
RUN mkdir -p /opt/app
WORKDIR /opt/app
COPY . /opt/app/
RUN uv sync
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5172"]
