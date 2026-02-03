# ARCHCODE - 3D DNA Loop Extrusion Simulator
# Docker image for reproducible scientific simulations

FROM node:20-slim

LABEL maintainer="ARCHCODE Team"
LABEL description="Cohesin loop extrusion simulator with FountainLoader (Mediator-driven loading)"
LABEL version="1.0.2"

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

# Install dependencies
RUN npm ci --only=production=false

# Copy source code and scripts
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tsconfig.json ./

# Copy data inputs if available (BigWig files)
# These can also be mounted as volumes
COPY data/ ./data/ 2>/dev/null || true

# Create results directory
RUN mkdir -p /app/results

# Build TypeScript
RUN npm run build 2>/dev/null || echo "Build step skipped (using tsx)"

# Set environment variables
ENV NODE_ENV=production
ENV MED1_BW=/app/data/inputs/med1/MED1_GM12878_Rep1.bw

# Default command: run all validations
CMD ["npx", "tsx", "scripts/run-all-validations.ts"]
