FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system libraries needed by PostgreSQL and Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium and headless browser OS dependencies
RUN playwright install --with-deps chromium

# Copy codebase
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Launch Streamlit app
CMD ["streamlit", "run", "app/dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
