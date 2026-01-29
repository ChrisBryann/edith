FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (git is often needed for some python packages)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

# We use python -u to ensure print statements show up immediately in Docker logs
CMD ["python", "-u", "api.py"]