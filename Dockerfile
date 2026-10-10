
# 1. Use Python as the base image
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install system dependencies needed by Playwright browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Install Chromium and its required system dependencies
RUN playwright install --with-deps chromium

# 6. Copy the automation framework
COPY . .

# 7. Run Pytest by default
CMD ["pytest", "-v", "--tb=short"]
