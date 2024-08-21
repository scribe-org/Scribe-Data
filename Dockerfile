# Use an official Python runtime as a base image
FROM python:3.9-slim AS builder

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=300 -r requirements.txt


COPY . /app

FROM python:3.9-slim
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the project files from the builder stage
COPY --from=builder /app /app

# Set the PYTHONPATH environment variable to include the src directory
ENV PYTHONPATH=/app/src

# Set the entry point to the main CLI script
ENTRYPOINT ["python", "src/scribe_data/cli/main.py"]
