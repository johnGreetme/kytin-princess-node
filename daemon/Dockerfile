FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for serial communication
RUN apt-get update && apt-get install -y \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY daemon/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy daemon scripts
COPY daemon/ ./daemon/

# The Gatekeeper is the primary entry point
CMD ["python", "-u", "daemon/sting_gatekeeper.py"]
