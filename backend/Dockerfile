# Use multi-stage build
FROM python:3.11-slim-bookworm AS builder   

# Create a non-root user with explicit UID/GID
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -M appuser

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Set restrictive permissions on system files
    && chmod 750 /etc/shadow \
    && chmod 750 /etc/gshadow \
    && chmod 644 /etc/passwd \
    && chmod 644 /etc/group \
    && chmod -R 700 /root \
    # Set secure umask
    && echo "umask 0027" >> /etc/profile \
    # Update CA certificates
    && update-ca-certificates

# Upgrade pip and setuptools to latest secure versions
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with security flags
RUN pip install --no-cache-dir -r requirements.txt

# Start fresh with a clean image
FROM python:3.11-slim-bookworm AS runtime

# Copy non-root user from builder
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Install runtime dependencies only
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Update CA certificates
    && update-ca-certificates \
    # Set restrictive permissions
    && chmod 750 /etc/shadow \
    && chmod 750 /etc/gshadow \
    && chmod 644 /etc/passwd \
    && chmod 644 /etc/group \
    && chmod -R 700 /root \
    # Set secure umask
    && echo "umask 0027" >> /etc/profile

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Set proper ownership and permissions
RUN chown -R appuser:appgroup /app && \
    chmod -R 750 /app && \
    # Create data directory with restricted permissions
    mkdir -p /data && \
    chown appuser:appgroup /data && \
    chmod 750 /data

# Configure proxy headers and forwarded IPs
ENV FORWARDED_ALLOW_IPS="*" \
    PROXY_HEADERS="1"

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start the application with security flags
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]