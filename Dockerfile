# Stable Python version supported everywhere
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# App Runner port
ENV PORT=8080
EXPOSE 8080

# Start app
CMD ["python", "main.py"]