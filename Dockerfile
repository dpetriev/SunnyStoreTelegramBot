FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot/ bot/
COPY lambda_function.py .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m botuser
RUN chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "-m", "bot"]