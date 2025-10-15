
## **Guideline: Building Production-Ready MCP Servers with FastMCP and FastAPI**

### 1. Introduction: From Prototype to Production

Many MCP server projects begin as prototypes using rapid development frameworks like Gradio. While excellent for initial validation, these frameworks often introduce architectural bottlenecks (e.g., high per-request overhead, slow cold starts) that are unacceptable in production. This guide outlines a robust pattern for building high-performance, production-grade MCP servers that are scalable, maintainable, and support diverse client integrations from day one.

The core philosophy is a **decoupled architecture** where business logic is cleanly separated from the API and transport layers. This allows for maximum flexibility, testability, and performance.

### 2. The Recommended Architecture

The optimal architecture consists of three primary components built upon a high-performance ASGI foundation:

1.  **Core Logic Module (`logic.py`):** A framework-agnostic Python module containing all business logic. Functions here should accept and return standard Python types, ensuring they are portable and easily testable.
2.  **Service Core (`main.py`):** The main application entrypoint built with FastAPI. It serves as the orchestrator, exposing the core logic through multiple interfaces.
3.  **Interfaces:**
    *   **FastMCP Server:** Exposes core logic functions as MCP tools for AI agents, handling all protocol-level complexities.
    *   **REST API:** (Highly Recommended) Exposes core logic via standard HTTP endpoints (GET, POST) for traditional clients and simple integrations.
    *   **(Optional) Legacy UI:** A mounted legacy application (e.g., a Gradio UI) for backward compatibility during a migration.

This structure allows a single, unified service to serve AI agents, web frontends, and other microservices from a shared, well-tested codebase.

```mermaid
graph TD
    subgraph "Unified Service (main.py on FastAPI)"
        A[FastMCP Server<br>@mcp.tool decorators]
        B[REST API<br>@app.get/post decorators]
        C[(Optional) Mounted Gradio UI<br>/gradio]
    end

    subgraph "Core Logic (logic.py)"
        D{Business Logic Functions}
    end

    E[AI Agent Client<br>(e.g., Claude Desktop)]
    F[Web Frontend/API Client]
    G[Legacy UI User]

    A --> D
    B --> D
    C --> B

    E -- stdio or HTTP/SSE --> A
    F -- HTTP --> B
    G -- Browser --> C
```

### 3. Implementation Steps: A Phased Approach

#### **Phase 1: Decouple Business Logic**

This is the most critical step. Isolate all your core functionality into a separate `logic.py` file.

*   **DO:** Create functions that are "pure"—they should not import from or depend on FastAPI, FastMCP, or Gradio.
*   **DO:** Use standard Python type hints for all function arguments and return values.
*   **DON'T:** Place business logic directly inside FastAPI path operations or Gradio event handlers.

**Example: `logic.py`**
```python
# logic.py
# Framework-agnostic business logic. No FastAPI/FastMCP imports here.

from typing import List, Dict

def perform_forecast(data: List[float], periods: int) -> Dict:
    """
    Performs an exponential smoothing forecast.
    This function contains the core logic and is easily testable in isolation.
    """
    # ... forecasting logic using statsmodels, pandas, etc. ...
    print(f"Forecasting {periods} periods for data with length {len(data)}.")
    # Dummy implementation for clarity
    result = {"forecast": [d * 1.1 for d in data[-periods:]], "confidence": 0.95}
    return result```

#### **Phase 2: Build the FastMCP/FastAPI Service Core**

Create a `main.py` to orchestrate the service.

1.  **Instantiate Frameworks:** Initialize FastAPI and FastMCP.
2.  **Expose MCP Tools:** Import your logic functions and wrap them with the `@mcp.tool` decorator. FastMCP uses the function signature, type hints, and docstring to automatically generate the tool schema for the LLM.
3.  **Implement Dual-Transport Entrypoint:** The service must support being run as a web server (HTTP/SSE) or as a local command-line tool (stdio). This is achieved by parsing command-line arguments in the main execution block.

**Example: `main.py`**
```python
# main.py
import argparse
import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

# Import the decoupled business logic
from logic import perform_forecast

# 1. Instantiate frameworks
app = FastAPI(title="Forecasting Service", version="1.0")
mcp = FastMCP(name="ForecastingServer", description="A server for time-series forecasting.")

# 2. Expose logic as an MCP tool
@mcp.tool
def forecast(data: list[float], forecast_periods: int) -> dict:
    """
    Generates a time-series forecast using exponential smoothing.

    Args:
        data (list[float]): The historical data points to use for the forecast.
        forecast_periods (int): The number of future periods to forecast.
    """
    # This wrapper calls the core logic, keeping the endpoint clean.
    return perform_forecast(data, forecast_periods)

# (Optional but Recommended) Expose as a REST endpoint
@app.post("/api/v1/forecast")
def http_forecast(data: list[float], forecast_periods: int) -> dict:
    return perform_forecast(data, forecast_periods)

# Mount the MCP server onto the FastAPI app
# This makes it available at /mcp/sse, etc.
mcp.mount_to(app, at_path="/mcp")

# 3. Implement dual-transport entrypoint
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MCP/API Server.")
    parser.add_argument(
        "--transport",
        type=str,
        default="http",
        choices=["http", "stdio"],
        help="The transport protocol to use for the MCP server.",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        print("Running MCP server with stdio transport.")
        mcp.run(transport="stdio")
    else:
        print("Running web server with HTTP/SSE transport.")
        uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Production Hardening

A production service requires security, reliability, and observability.

*   **Authentication:** Protect your endpoints. Use FastAPI's security utilities to implement OAuth2 with JWT Bearer tokens. This is the industry standard for securing APIs.
*   **Rate Limiting:** Prevent abuse and ensure service stability. Use a library like `fastapi-limiter` with a Redis backend to enforce rate limits (e.g., 100 requests/minute per IP).
*   **Observability:**
    *   **Logging:** Emit structured (JSON) logs for easy parsing and analysis.
    *   **Metrics:** Instrument your application with a Prometheus client to expose custom metrics (e.g., tool call latency, error counts).
    *   **Health Checks:** Create a simple `/healthz` endpoint that returns a `200 OK` status. This is essential for automated systems to know if your service is alive.

### 5. Deployment Strategies (Prioritized)

#### **Priority 1: Local Standalone Deployment (with Shell Script)**

This is the simplest method for local development and testing, especially for stdio-based clients.

1.  **Create a `run.sh` script:**
    ```bash
    #!/bin/bash
    # run.sh
    # Ensure you have a virtual environment with dependencies installed
    
    # To run the web server: ./run.sh http
    # To run for a local client: ./run.sh stdio
    
    TRANSPORT_MODE=${1:-http} # Default to http if no argument is given
    
    python main.py --transport $TRANSPORT_MODE
    ```
2.  **Configure your local client (`mcp.json`):**
    For clients like Claude Desktop, you provide a JSON configuration that tells it how to launch your server.
    ```json
    {
      "command": "/bin/bash",
      "args": ["/path/to/your/project/run.sh", "stdio"],
      "working_dir": "/path/to/your/project"
    }
    ```

#### **Priority 2: Local Docker Deployment (via Docker MCP Toolkit)**

> **This is the recommended approach for local development.** It offers superior security, simplified client setup, and centralized management without the hassle of manual configuration.

1.  **Create a `Dockerfile`:** A multi-stage build creates a small, secure, and efficient image.
    ```dockerfile
    # ---- Builder Stage ----
    FROM python:3.12-slim AS builder
    RUN pip install uv
    WORKDIR /app
    COPY pyproject.toml ./
    RUN uv pip install --system -r pyproject.toml

    # ---- Final Stage ----
    FROM python:3.12-slim
    WORKDIR /app
    COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
    COPY --from=builder /usr/local/bin /usr/local/bin
    COPY . .
    
    # Default command for cloud deployment (overridden by clients for stdio)
    CMD ["python", "main.py", "--transport", "http"]
    ```
2.  **Build the Image:**
    ```bash
    docker build -t your-mcp-server:latest .
    ```
3.  **Enable in MCP Toolkit:**
    ```bash
    docker mcp server enable your-mcp-server:latest
    ```
4.  **Connect Clients:** Open Docker Desktop, navigate to the "MCP Toolkit" section, find your client (e.g., Claude Desktop), and click "Connect". This automatically and securely configures the client for you.

#### **Priority 3: Cloud Deployment (Fly.io & Alternatives)**

This is the final step for making your service publicly available with low latency and high availability.

1.  **Use the same `Dockerfile` from the previous step.**
2.  **Install the Fly.io CLI (`flyctl`) and log in.**
3.  **Launch the App:**
    ```bash
    fly launch
    ```
    This command inspects your `Dockerfile` and generates a `fly.toml` configuration file.
4.  **Configure `fly.toml` for Production:**
    *   Ensure the `CMD` in your Dockerfile is set to run the HTTP server.
    *   Set health checks to point to your `/healthz` endpoint.
    *   **To eliminate cold starts**, set a minimum number of running machines:
        ```toml
        [http_service]
          # ...
          min_machines_running = 1
        ```
5.  **Deploy:**
    ```bash
    fly deploy
    ```

**Alternatives:** The same Docker container can be deployed to other serverless platforms like **Google Cloud Run** or **AWS App Runner** with similar configuration steps. The key is to use a platform that can run arbitrary containers and has fast cold-start times.

### 6. Conclusion: A Repeatable Pattern for Excellence

By following this guideline, you establish a standardized, repeatable pattern for developing MCP servers that are performant, secure, and production-ready from the outset. Decoupling logic, implementing dual-transport support, and leveraging modern deployment platforms like Docker MCP Toolkit and Fly.io ensures your services meet the high demands of today's AI-powered applications.