FROM python:3.12-slim-bookworm
SHELL ["/bin/bash", "--login", "-c"]
WORKDIR /app
# Add virtual env to the path
ENV PATH="/app/.venv/bin:$PATH"
RUN mkdir -p /var/log/chronos; touch /var/log/chronos/chronos.log
ENV W1_MOUNT_POINT=/mock_1wire/sys/bus/w1/devices/
RUN mkdir -p ${W1_MOUNT_POINT}
# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates socat tini

COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /bin/uv
# Install requirements first in a separate layer to avoid re-installing them on
# every code changes
COPY pyproject.toml .
# Create the virtual environment
RUN uv sync
# Copy the application code
COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["tini", "--"]
CMD ["./entrypoint.sh"]

