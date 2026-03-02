FROM python:3.11-slim

WORKDIR /app

# Install minimal runtime libs required by Flet
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    libglib2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]