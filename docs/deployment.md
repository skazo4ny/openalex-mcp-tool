# OpenAlex Explorer MCP Server - Deployment Guide

## Overview

This guide covers deploying the OpenAlex Explorer MCP Server to various platforms. As of the current development stage, active development has migrated to GitHub, though Hugging Face Spaces deployment is still supported for demo purposes.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hugging Face Spaces Deployment](#hugging-face-spaces-deployment)
3. [Local Development Setup](#local-development-setup)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.9 or higher
- Git
- Access to target deployment platform
- (Optional) Docker for containerized deployment

## Repository Migration Notice

**Important**: As of Phase 1 completion, active development has migrated to GitHub. The Hugging Face Space will continue to host the current Gradio-based implementation for demo purposes, but all future development will occur on GitHub.

To contribute or access the latest development version:
```bash
git clone https://github.com/YOUR_USERNAME/openalex-mcp-tool.git
cd openalex-mcp-tool
```

## Hugging Face Spaces Deployment

### Step 1: Repository Setup

1. **Create Hugging Face Space:**
   ```bash
   # Visit https://huggingface.co/new-space
   # Choose:
   # - Space name: openalex-mcp-tool
   # - License: MIT
   # - SDK: Gradio
   # - Python version: 3.9+
   ```

2. **Clone the repository:**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/openalex-mcp-tool
   cd openalex-mcp-tool
   ```

### Step 2: Add Required Files

Ensure your repository contains:

- `app.py` - Main application file
- `requirements.txt` - Python dependencies
- `README.md` - With proper HF Spaces configuration
- `config/slr_config.yaml` - Configuration file
- All module directories (`slr_modules/`, `openalex_modules/`)

### Step 3: Configure README.md

Add this YAML frontmatter to the top of README.md:

```yaml
---
title: OpenAlex Explorer MCP Server
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
tags:
  - mcp-server-track
  - openalex
  - academic-research
  - model-context-protocol
---
```

### Step 4: Deploy

```bash
git add .
git commit -m "Deploy OpenAlex MCP Server"
git push origin main
```

The deployment will automatically start on Hugging Face Spaces.

## Local Development Setup

### Step 1: Clone Repository

```bash
# For latest development version (recommended)
git clone https://github.com/YOUR_USERNAME/openalex-mcp-tool.git
cd openalex-mcp-tool

# For stable Hugging Face version (demo purposes)
git clone https://huggingface.co/spaces/YOUR_USERNAME/openalex-mcp-tool
cd openalex-mcp-tool
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example configuration
cp config/slr_config.yaml.example config/slr_config.yaml

# Edit configuration as needed
nano config/slr_config.yaml
```

### Step 5: Run Application

```bash
python app.py
```

Access the application at `http://localhost:7860`

## Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs

EXPOSE 7860

CMD ["python", "app.py"]
```

### Step 2: Build and Run

```bash
# Build image
docker build -t openalex-mcp-tool .

# Run container
docker run -p 7860:7860 -v $(pwd)/logs:/app/logs openalex-mcp-tool
```

## Environment Configuration

### Configuration File Structure

The `config/slr_config.yaml` file should contain:

```yaml
# OpenAlex API Configuration
openalex:
  base_url: "https://api.openalex.org"
  default_per_page: 25
  max_per_page: 200
  timeout: 30
  retries: 3

# Search Configuration
search:
  default_max_results: 10
  max_allowed_results: 50

# Application Configuration
app:
  title: "OpenAlex Explorer"
  description: "MCP Server for OpenAlex API interactions"
  version: "1.0.0"

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Environment Variables

Set these environment variables for production:

```bash
# Optional: Custom configuration
export SLR_CONFIG_PATH="/path/to/config.yaml"

# Optional: Override log level
export LOG_LEVEL="INFO"

# Optional: Override port
export PORT=7860
```

## Future Architecture: FastMCP Transition

As part of our development roadmap, we are planning to transition from the current Gradio-based MCP implementation to a specialized FastMCP approach. This will provide:

1. **Better Performance**: Optimized for high-throughput MCP operations
2. **Decoupled Architecture**: Separation of business logic from transport layers
3. **Standard Compliance**: Better adherence to MCP specification
4. **Enhanced Scalability**: Improved handling of concurrent connections

This transition will begin in Phase 2 development and will maintain API compatibility with existing clients.

## Troubleshooting

### Common Issues

1. **Port Already in Use:**
   ```bash
   # Kill process using port 7860
   lsof -ti:7860 | xargs kill -9
   ```

2. **Dependency Installation Issues:**
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   
   # Install with no cache
   pip install --no-cache-dir -r requirements.txt
   ```

3. **API Rate Limiting:**
   ```bash
   # Set your email for better API access
   export OPENALEX_EMAIL="your-email@example.com"
   ```

### Logs and Debugging

Check logs in the `logs/` directory for detailed error information:
```bash
tail -f logs/openalex_mcp.log
```

For development debugging, set the log level to DEBUG:
```bash
export LOG_LEVEL="DEBUG"
```