# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12.9
FROM python:${PYTHON_VERSION}-slim as base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Change ownership of the app directory to appuser BEFORE installing dependencies
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user BEFORE running uv commands
USER appuser

# Install dependencies
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=${UID} \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the source code into the container.
COPY --chown=appuser:appuser . .

# Sync the project
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=${UID} \
    uv sync --locked

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["uv", "run", "gunicorn", "app:app", "--bind=0.0.0.0:8000"]