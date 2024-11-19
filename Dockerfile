# Use an official Python runtime as a base image.
FROM python:slim

# Set the working directory inside the container.
WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Set the PYTHONPATH environment variable to include the src directory.
ENV PYTHONPATH=/app/src

# Set the entry point to the main CLI script.
ENTRYPOINT ["python", "src/scribe_data/cli/main.py"]
