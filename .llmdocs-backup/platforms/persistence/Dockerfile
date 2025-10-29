# ============================================================================
# Persistence Platform - Docker Image
# ============================================================================
#
# @file Dockerfile
# @version 1.0.0
# @author Unhinged Team
# @date 2025-10-19
# @description Multi-stage Docker build for the Persistence Platform
#
# This Dockerfile creates an optimized container image for the persistence
# platform with proper security, performance, and observability features.
#
# ============================================================================

# ==========================================================================
# Build Stage
# ==========================================================================
FROM gradle:8.4-jdk17-alpine AS builder

# Set working directory
WORKDIR /app

# Copy build files
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle.properties ./

# Copy source code
COPY src ./src
COPY config ./config

# Build the application
RUN gradle clean shadowJar --no-daemon --parallel

# ==========================================================================
# Runtime Stage
# ==========================================================================
FROM eclipse-temurin:17-jre-alpine

# Metadata
LABEL maintainer="Unhinged Team"
LABEL version="1.0.0"
LABEL description="Unhinged Persistence Platform - Multi-Database Abstraction Layer"
LABEL org.opencontainers.image.title="Unhinged Persistence Platform"
LABEL org.opencontainers.image.description="Centralized persistence platform abstracting multiple database technologies"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Unhinged Team"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    netcat-openbsd \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user for security
RUN groupadd -r unhinged && useradd -r -g unhinged -s /bin/false unhinged

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/config /app/logs /app/data /app/tmp \
    && chown -R unhinged:unhinged /app

# Copy application JAR from builder stage
COPY --from=builder /app/build/libs/persistence-platform.jar /app/persistence-platform.jar

# Copy configuration files
COPY --chown=unhinged:unhinged config/ /app/config/

# Copy startup scripts
COPY --chown=unhinged:unhinged scripts/docker-entrypoint.sh /app/docker-entrypoint.sh
COPY --chown=unhinged:unhinged scripts/health-check.sh /app/health-check.sh

# Make scripts executable
RUN chmod +x /app/docker-entrypoint.sh /app/health-check.sh

# Set environment variables
ENV JAVA_OPTS="-Xmx2g -Xms1g -XX:+UseG1GC -XX:+UseStringDeduplication -XX:+OptimizeStringConcat"
ENV CONFIG_PATH="/app/config/persistence-platform.yaml"
ENV LOG_LEVEL="INFO"
ENV SERVER_PORT="8090"
ENV GRPC_PORT="9090"

# Expose ports
EXPOSE 8090 9090

# Switch to non-root user
USER unhinged

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health-check.sh

# Use dumb-init to handle signals properly
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Start the application
CMD ["/app/docker-entrypoint.sh"]
