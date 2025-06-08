# OpenAlex Explorer MCP Server - API Documentation

## Overview

The OpenAlex Explorer MCP Server provides both a Gradio web interface and MCP (Model Context Protocol) server functionality for accessing academic research data from the OpenAlex API.

## Base URLs

- **Web Interface**: Available at deployment URL (e.g., Hugging Face Spaces)
- **MCP Server**: Accessible via stdio transport for MCP clients

## MCP Tools

### 1. search_openalex_papers

Search for academic papers using various criteria.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query for papers (title, abstract, keywords)"
    },
    "from_publication_date": {
      "type": "string",
      "description": "Start date filter (YYYY-MM-DD format)",
      "format": "date"
    },
    "to_publication_date": {
      "type": "string", 
      "description": "End date filter (YYYY-MM-DD format)",
      "format": "date"
    },
    "results_count": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 10
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns a list of papers with title, authors, publication year, DOI, abstract, and citation count.

### 2. get_publication_by_doi

Retrieve a specific publication by its DOI.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "doi": {
      "type": "string",
      "description": "DOI of the publication to retrieve"
    }
  },
  "required": ["doi"]
}
```

**Response:**
Returns detailed publication information including metadata, authors, and citation data.

### 3. search_openalex_authors

Search for authors in the OpenAlex database.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Author name or search query"
    },
    "results_count": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 10
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns author information including name, affiliation, publication count, and citation metrics.

### 4. search_openalex_concepts

Search for academic concepts and their relationships.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Concept name or search query"
    },
    "results_count": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 10
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns concept information including name, description, level, and related works count.

## Error Handling

All MCP tools return structured error responses:

```json
{
  "error": {
    "type": "string",
    "message": "string",
    "details": "object"
  }
}
```

Common error types:
- `ValidationError`: Invalid input parameters
- `APIError`: OpenAlex API communication issues
- `NotFoundError`: Resource not found
- `RateLimitError`: API rate limit exceeded

## Rate Limits

The server respects OpenAlex API rate limits:
- 100 requests per second for general endpoints
- Automatic retry with exponential backoff
- Request queuing for high-volume operations

## Authentication

No authentication required for OpenAlex API access. The service uses the public OpenAlex API endpoints.

## Examples

### Using with MCP Client

```python
import mcp

# Connect to MCP server via SSE
client = mcp.Client("sse", url="http://localhost:7860/gradio_api/mcp/sse")

# Search for papers
result = await client.call_tool("search_openalex_papers", {
    "query": "machine learning",
    "from_publication_date": "2020-01-01",
    "results_count": 5
})

print(result.content[0].text)
```

**Note**: Replace `localhost:7860` with your actual deployment URL (e.g., Hugging Face Spaces URL).

### Direct Web Interface

Navigate to the deployment URL and use the interactive Gradio interface to:
1. Search papers with filters
2. Look up publications by DOI
3. Find authors and their metrics
4. Explore academic concepts

## Logging

The server maintains comprehensive logs:
- Request/response logging for all MCP calls
- Performance metrics and timing
- Error tracking with stack traces
- Daily log rotation in JSON and XML formats
