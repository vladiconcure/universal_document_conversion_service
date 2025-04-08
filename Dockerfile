FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-uno \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-draw \
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Set up UNO Python path
RUN uno_path=$(find /usr -name "uno.py" 2>/dev/null | head -1 | xargs dirname) && \
    echo "$uno_path" > $(python3 -c "import site; print(site.getsitepackages()[0])")/libreoffice.pth && \
    python3 -c "import uno; print('PyUNO is available')"

# Create directories for file storage
RUN mkdir -p /app/data/uploads /app/data/output

# Copy the application code
COPY . .

# Set up supervisord to manage processes
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Configure environment variables
ENV UPLOAD_DIR=/app/data/uploads
ENV OUTPUT_DIR=/app/data/output
ENV LIBREOFFICE_HOST=localhost
ENV LIBREOFFICE_PORT=2002

# Expose the API port
EXPOSE 8000

# Start supervisord to manage the LibreOffice and API processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
