# Use multi-stage build
FROM python:3.9-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies and security updates
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update --no-cache && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add security labels
LABEL org.opencontainers.image.vendor="alpha-tran" \
      org.opencontainers.image.title="NoteApp Backend" \
      org.opencontainers.image.description="Secure Python Backend Service" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.url="https://github.com/alpha-tran/NoteApp" \
      org.opencontainers.image.licenses="MIT" \
      security.selinux.type="container_runtime_t" \
      security.capabilities="cap_net_bind_service"

# Upgrade pip and setuptools to latest versions
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UMASK=0027 \
    PYTHONPATH=/app \
    PATH="/app/bin:$PATH"

# Create non-root user with explicit UID/GID
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -M appuser && \
    mkdir -p /app /app/logs /app/data && \
    chown -R appuser:appgroup /app && \
    chmod -R 750 /app

# Install runtime dependencies and security updates
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update --no-cache && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    tzdata \
    tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Secure system files
    chmod 640 /etc/passwd /etc/group && \
    chmod 600 /etc/shadow && \
    # Create data directory with restricted permissions
    mkdir -p /data && \
    chown appuser:appgroup /data && \
    chmod 750 /data

# Set working directory
WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    find /usr/local/lib/python3.9/site-packages -type d -exec chmod 750 {} \; && \
    find /usr/local/lib/python3.9/site-packages -type f -exec chmod 640 {} \;

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser:appgroup

# Configure proxy headers and forwarded IPs
ENV FORWARDED_ALLOW_IPS="*" \
    PROXY_HEADERS=1

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Use tini as init system
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run application with security flags
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--no-access-log", \
     "--workers", "4", \
     "--limit-concurrency", "1000", \
     "--backlog", "2048"]