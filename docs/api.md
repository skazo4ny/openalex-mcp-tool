# OpenAlex Explorer MCP Server - API Documentation

## Overview

The OpenAlex Explorer MCP Server provides both a Gradio web interface and MCP (Model Context Protocol) server functionality for accessing academic research data from the OpenAlex API.

## Base URLs

- **Web Interface**: Available at deployment URL (e.g., Hugging Face Spaces)
- **MCP Server**: Accessible via SSE (Server-Sent Events) at `YOUR_APP_URL/gradio_api/mcp/sse`

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
    "start_year": {
      "type": "integer",
      "description": "Start year filter (e.g., 2020)",
      "minimum": 1950,
      "maximum": 2030
    },
    "end_year": {
      "type": "integer", 
      "description": "End year filter (e.g., 2024)",
      "minimum": 1950,
      "maximum": 2030
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 3
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
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-25)",
      "minimum": 1,
      "maximum": 25,
      "default": 5
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
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 5
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns concept information including name, description, level, and related works count.

### 5. search_openalex_topics

Search for academic topics (improved replacement for deprecated concepts).

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Topic name or search query"
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 5
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns topic information including name, description, hierarchical structure (domain, field, subfield), keywords, and research metrics.

### 6. search_openalex_institutions

Search for research institutions and universities.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Institution name or search query"
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 5
    },
    "country_code": {
      "type": "string",
      "description": "ISO 3166-1 alpha-2 country code to filter results (e.g., 'US', 'DE')"
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns institution information including name, ROR identifier, country code, type, geographic location, and research metrics.

### 7. search_openalex_sources

Search for academic publication venues (journals, conferences, repositories).

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Source name or search query"
    },
    "max_results": {
      "type": "integer",
      "description": "Number of results to return (1-50)",
      "minimum": 1,
      "maximum": 50,
      "default": 5
    },
    "source_type": {
      "type": "string",
      "description": "Source type filter (e.g., 'journal', 'conference', 'repository')"
    }
  },
  "required": ["query"]
}
```

**Response:**
Returns source information including name, ISSN, type, publisher, homepage URL, and publication metrics.

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

### Example: Search Recent AI Papers
```python
import asyncio
from mcp import Client

async def search_ai_papers():
    url = "http://localhost:7860/gradio_api/mcp/sse"
    
    async with Client("sse", url=url) as client:
        result = await client.call_tool("search_openalex_papers", {
            "query": "machine learning",
            "start_year": 2020,
            "max_results": 5
        })
        
        print(result.content[0].text)

asyncio.run(search_ai_papers())
```

### Example: Search Research Topics
```python
import asyncio
from mcp import Client

async def search_research_topics():
    url = "http://localhost:7860/gradio_api/mcp/sse"
    
    async with Client("sse", url=url) as client:
        result = await client.call_tool("search_openalex_topics", {
            "query": "artificial intelligence",
            "max_results": 5
        })
        
        print(result.content[0].text)

asyncio.run(search_research_topics())
```

### Example: Search Institutions by Country
```python
import asyncio
from mcp import Client

async def search_institutions():
    url = "http://localhost:7860/gradio_api/mcp/sse"
    
    async with Client("sse", url=url) as client:
        result = await client.call_tool("search_openalex_institutions", {
            "query": "university",
            "country_code": "DE",
            "max_results": 5
        })
        
        print(result.content[0].text)

asyncio.run(search_institutions())
```

### Direct Web Interface

Navigate to the deployment URL and use the interactive Gradio interface to:
1. Search papers with filters
2. Look up publications by DOI
3. Find authors and their metrics
4. Explore academic concepts
5. Discover research topics
6. Find institutions and universities
7. Search publication venues

## Logging

The server maintains comprehensive logs:
- Request/response logging for all MCP calls
- Performance metrics and timing
- Error tracking with stack traces
- Daily log rotation in JSON format