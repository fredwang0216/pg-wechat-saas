# Use the official Playwright image which has all browser dependencies installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium is enough for us, but installing all is safer for compatibility)
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Expose port (Cloud platforms like Railway use a dynamic PORT env var, but we verify on 8000)
EXPOSE 8000

# Run the application
# We use 0.0.0.0 to listen on all interfaces within the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
