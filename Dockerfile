# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.13.2
FROM python:${PYTHON_VERSION}-slim as base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1
ENV UV_PYTHON_PREFERENCE=only-system
ENV TORCH_HOME=/home/appuser/.cache/torch

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

# Optional: bake torchvision weights into the image at build time.
# Example: docker build --build-arg PRELOAD_TORCHVISION_WEIGHTS=1 .
ARG PRELOAD_TORCHVISION_WEIGHTS=0
RUN --mount=type=cache,target=/home/appuser/.cache/torch,uid=${UID} \
    if [ "$PRELOAD_TORCHVISION_WEIGHTS" = "1" ]; then \
      uv run python -c "from torchvision.models import ResNet152_Weights; ResNet152_Weights.DEFAULT.get_state_dict(progress=True)"; \
    fi

# Expose the port that the application listens on.
EXPOSE 80

# Run the application.
CMD ["uv", "run", "gunicorn", "app:app", "--bind=0.0.0.0:80"]
