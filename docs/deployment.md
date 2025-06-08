# OpenAlex Explorer MCP Server - Deployment Guide

## Overview

This guide covers deploying the OpenAlex Explorer MCP Server to various platforms, with specific focus on Hugging Face Spaces deployment.

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
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: mit
tags:
  - mcp
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
git clone https://github.com/YOUR_USERNAME/openalex-mcp-tool.git
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
  rate_limit: 100  # requests per second
  timeout: 30      # seconds
  retry_attempts: 3
  retry_delay: 1   # seconds

# Application Configuration
app:
  debug: false
  log_level: "INFO"
  max_results: 50
  default_results: 10

# Gradio Configuration
gradio:
  interface:
    title: "OpenAlex Explorer MCP Server"
    description: "Search academic papers, authors, and concepts"
    theme: "default"
  server:
    port: 7860
    host: "0.0.0.0"
    share: false

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_rotation: "daily"
  max_log_files: 30
  log_directory: "logs"
```

### Environment Variables

Set these environment variables for production:

```bash
# Optional: Custom configuration
export SLR_CONFIG_PATH="/path/to/config.yaml"

# Optional: Override log level
export LOG_LEVEL="INFO"

# Optional: Override port
export PORT="7860"
```

## Troubleshooting

### Common Issues

#### 1. White Page on Hugging Face Spaces

**Symptoms:** Deployment succeeds but shows blank page

**Solutions:**
1. Check application logs in HF Spaces interface
2. Verify all dependencies in requirements.txt
3. Ensure app.py doesn't have blocking operations
4. Check Gradio version compatibility

```bash
# Check logs
# In HF Spaces, click "Logs" tab to view runtime logs
```

#### 2. Import Errors

**Symptoms:** ModuleNotFoundError or ImportError

**Solutions:**
1. Verify all modules are included in repository
2. Check Python path configuration
3. Ensure __init__.py files exist in module directories

```bash
# Add __init__.py files
touch slr_modules/__init__.py
touch openalex_modules/__init__.py
```

#### 3. Configuration Errors

**Symptoms:** Application fails to start with config errors

**Solutions:**
1. Verify YAML syntax in config file
2. Check file paths and permissions
3. Ensure all required config sections exist

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/slr_config.yaml'))"
```

#### 4. API Rate Limiting

**Symptoms:** Frequent API errors or timeouts

**Solutions:**
1. Implement request throttling
2. Add retry logic with exponential backoff
3. Cache frequently requested data

#### 5. Memory Issues

**Symptoms:** Application crashes or becomes unresponsive

**Solutions:**
1. Optimize data processing
2. Implement pagination for large results
3. Add memory usage monitoring

### Performance Optimization

1. **Enable Caching:**
   ```python
   # Add to app.py
   import functools
   
   @functools.lru_cache(maxsize=100)
   def cached_api_call(query, params):
       # Your API call logic
       pass
   ```

2. **Optimize Gradio Interface:**
   ```python
   # Use queue for better concurrency
   demo.queue(concurrency_count=10)
   ```

3. **Monitor Resource Usage:**
   ```python
   # Add memory and CPU monitoring
   import psutil
   ```

### Logs Analysis

The application generates structured logs in `/logs` directory:

- `app_YYYY-MM-DD.json` - JSON formatted logs
- `app_YYYY-MM-DD.xml` - XML formatted logs

Use log analysis tools:

```bash
# Parse JSON logs
cat logs/app_$(date +%Y-%m-%d).json | jq '.level=="ERROR"'

# Monitor real-time logs
tail -f logs/app_$(date +%Y-%m-%d).json
```

## Monitoring and Maintenance

### Health Checks

Implement basic health monitoring:

```python
# Add to app.py
@demo.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Backup Strategy

1. **Code Backup:** Use Git for version control
2. **Configuration Backup:** Store configs in version control
3. **Logs Backup:** Implement log archival for long-term storage

### Updates and Maintenance

1. **Dependency Updates:**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **Configuration Updates:**
   - Test changes in development first
   - Use gradual rollout for production changes
   - Monitor application behavior after updates

3. **Log Rotation:**
   - Automatic daily rotation configured
   - Manual cleanup of old logs if needed
   - Monitor disk usage in deployment environment
