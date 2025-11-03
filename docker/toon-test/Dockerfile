# TOON Testing Container
# Purpose: Test TOON CLI and measure token savings vs JSON
# Base: Node.js 20 on Alpine Linux (lightweight)

FROM node:20-alpine

# Install system dependencies
RUN apk add --no-cache \
    curl \
    bash \
    jq

# Install TOON CLI globally
RUN npm install -g @toon-format/cli

# Install tokenx for token counting
RUN npm install -g tokenx

# Create working directory
WORKDIR /workspace

# Create directories for test data and results
RUN mkdir -p /workspace/test-data /workspace/results

# Set default shell to bash for better UX
SHELL ["/bin/bash", "-c"]

# Default command: interactive bash shell
CMD ["/bin/bash"]
