FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies without strict audit to avoid build failures
RUN npm ci --no-audit && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build && \
    npm prune --production

# Production stage
FROM nginx:1.25.3-alpine

# Update packages and install curl for health check
RUN apk update && \
    apk upgrade --no-cache && \
    apk add --no-cache curl && \
    rm -rf /var/cache/apk/*

# Create nginx cache directories with proper permissions
RUN mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp && \
    chmod -R 755 /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    # Ensure proper permissions for logs
    chmod -R 755 /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    # Ensure proper permissions for config
    chmod -R 755 /etc/nginx/conf.d && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    # Fix PID file permissions
    touch /var/run/nginx.pid && \
    chmod 644 /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

# Remove default nginx configuration and unnecessary files
RUN rm -rf /etc/nginx/conf.d/* && \
    rm -rf /usr/share/nginx/html/* && \
    rm -rf /var/www/* && \
    rm -f /etc/nginx/sites-enabled/default || true && \
    rm -f /etc/nginx/sites-available/default || true

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from build stage - use the correct 'build' directory instead of 'dist'
COPY --from=build /app/build /usr/share/nginx/html

# Update permissions for security
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Use the standard nginx user instead of custom one
# NGINX's official image already has a proper nginx user set up
USER nginx

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]