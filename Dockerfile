
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Playwright Chromium system dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium

# Copy automation framework
COPY . .

# Reports are written to /app/test-results
RUN mkdir -p /app/test-results

# Default command; Jenkins overrides it when running tests
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
