# Multi-stage build for the backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Initialize the database
RUN python InitDatabase.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]