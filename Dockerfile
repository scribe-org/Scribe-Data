# Use an official Python runtime as a base image.
FROM python:slim

# Set the working directory inside the container.
WORKDIR /app

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy lock file and pyproject.toml.
COPY uv.lock pyproject.toml /app/

# Install dependencies with uv.
RUN uv pip install --system --no-build-isolation .

COPY . /app

# Set the PYTHONPATH environment variable to include the src directory.
ENV PYTHONPATH=/app/src

# Set the entry point to the main CLI script.
ENTRYPOINT ["python", "src/scribe_data/cli/main.py"]
