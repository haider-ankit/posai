# 1. Use the official Python 3.13 image
FROM python:3.13-slim

# 2. Install the specific Linux libraries Flet needs to serve the web UI
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy your entire project (including pyproject.toml) into the container
COPY . .

# 5. Install your project and its dependencies (dotenv, flet, boto3, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose the port for AWS App Runner
EXPOSE 8080

# 7. Start the app (Make sure your file is named main.py!)
CMD ["python", "main.py"]