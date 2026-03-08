# ARCHCODE v1.1 - 3D DNA Loop Extrusion Simulator
# Docker image for reproducible scientific simulations
#
# Main finding: MED1-mediated loading bias (FountainLoader) is a sufficient
# mechanism for the formation of super-enhancer architecture.

FROM node:20-slim

LABEL maintainer="ARCHCODE Team"
LABEL description="Cohesin loop extrusion simulator with FountainLoader (Mediator-driven loading)"
LABEL version="1.1.0"

# Install system dependencies for BigWig processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    libz-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies (including devDependencies for tsx)
RUN npm ci

# Copy source code and scripts
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tsconfig.json ./

# Create directories
RUN mkdir -p /app/data/inputs/med1 \
    && mkdir -p /app/data/inputs/histone \
    && mkdir -p /app/results

# Runtime hardening: run as non-root user.
RUN groupadd -r archcode && useradd -r -g archcode -d /app archcode \
    && chown -R archcode:archcode /app

# Set environment variables
ENV NODE_ENV=production
ENV MED1_BW=/app/data/inputs/med1/MED1_GM12878_Rep1.bw
ENV H3K27AC_BW=/app/data/inputs/histone/H3K27ac_GM12878.bw

USER archcode

# Default command: run all validations
CMD ["npx", "tsx", "scripts/run-all-validations.ts"]
