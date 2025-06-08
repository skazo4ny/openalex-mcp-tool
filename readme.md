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
  - gradio
---

# 📚 OpenAlex Explorer MCP Server

**🏆 Agents & MCP Hackathon Submission (June 2-10, 2025)**

A dual-purpose application that provides both a **Gradio web interface** and **MCP (Model Context Protocol) server** for accessing academic research data from the OpenAlex API. Perfect for AI agents that need to search papers, authors, and academic concepts.

## 🚀 Live Demo

**Try it now**: [https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool](https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool)
**Video Demo Link**: https://youtu.be/XJNCQ5J2yPM 

## 🎯 Core Features

### 🔍 **Four MCP Tools**
1. **`search_openalex_papers`** - Search academic papers with date filtering
2. **`get_publication_by_doi`** - Retrieve specific publications by DOI  
3. **`search_openalex_authors`** - Find authors and their metrics
4. **`search_openalex_concepts`** - Explore academic concepts and fields

### 🤖 **MCP Integration**
Connect your AI agents to academic research:
```json
{
  "mcpServers": {
    "openalex-explorer": {
      "url": "https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool/gradio_api/mcp/sse"
    }
  }
}
```

### 🌐 **Web Interface**
- Interactive Gradio interface for direct use
- Real-time search with customizable filters
- User-friendly result formatting

## ⚡ Quick Start

### Option 1: Use Live Demo
Visit the [Hugging Face Space](https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool) and start searching immediately.

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool
cd openalex-mcp-tool

# Install dependencies
pip install -r requirements.txt

# Set up OpenAlex API access (recommended)
export OPENALEX_EMAIL="your-email@example.com"

# Run the application
python app.py
```

Access at `http://localhost:7860`

## 🛠️ MCP Client Usage

### Example: Search Recent AI Papers
```python
import asyncio
from mcp import Client

async def search_ai_papers():
    url = "https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool/gradio_api/mcp/sse"
    
    async with Client("sse", url=url) as client:
        result = await client.call_tool("search_openalex_papers", {
            "query": "large language models",
            "start_year": 2023,
            "max_results": 5
        })
        
        print(result.content[0].text)

asyncio.run(search_ai_papers())
```

### Available Tools

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_openalex_papers` | Find academic papers | `query`, `start_year`, `end_year`, `max_results` |
| `get_publication_by_doi` | Get specific paper | `doi` |
| `search_openalex_authors` | Find researchers | `query`, `max_results` |
| `search_openalex_concepts` | Explore topics | `query`, `max_results` |

## 🎥 Demo Video

🔗 [Watch the Demo Video](https://your-demo-video-link.com) *(Coming Soon)*

## 🏗️ Technical Architecture

- **Frontend**: Gradio 4.x with MCP support
- **Backend**: Python with pyalex library  
- **Protocol**: MCP via Server-Sent Events (SSE)
- **API**: OpenAlex (free, no API key required)
- **Deployment**: Hugging Face Spaces

## 📖 Documentation

For detailed documentation, see the [`docs/`](docs/) folder:

- **[User Guide](docs/user-guide.md)** - Complete usage instructions
- **[API Documentation](docs/api.md)** - MCP integration details  
- **[Deployment Guide](docs/deployment.md)** - Setup for different platforms
- **[Requirements Specification](docs/requirements.md)** - Detailed technical specs

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Your email for OpenAlex API (recommended for better access)
export OPENALEX_EMAIL="your-email@example.com"

# Optional: Custom configuration file
export SLR_CONFIG_PATH="/path/to/config.yaml"
```

### Dependencies
```
gradio[mcp]>=4.0.0
pyalex>=0.13
PyYAML>=6.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🌟 Use Cases

### For Researchers
- **Literature Reviews**: Search papers by topic and date range
- **Author Discovery**: Find experts in specific fields
- **Citation Tracking**: Get publication details by DOI

### For AI Agents
- **Research Assistant**: Enable LLMs to access academic data
- **Fact Checking**: Verify claims against scholarly sources  
- **Content Generation**: Enhance writing with academic references

### For Developers
- **MCP Integration**: Add research capabilities to any MCP client
- **Data Pipeline**: Automate academic data collection
- **Research Tools**: Build custom academic applications

## 📊 Example Searches

**Recent AI Research:**
```
Query: "transformer neural networks"
Years: 2023 to 2024
```

**Climate Science:**
```
Query: "climate change adaptation"
Authors: Search for climate researchers
```

**Medical Research:**
```
DOI: "10.1038/s41586-023-05881-4"
Related concepts: "machine learning medicine"
```

## 🤝 Contributing

This project is part of the **Agents & MCP Hackathon**. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🏷️ Hackathon Tags

`#mcp-server-track` `#openalex` `#academic-research` `#gradio` `#model-context-protocol`

---

**Built for the Agents & MCP Hackathon (June 2-10, 2025)**  
**Track**: MCP Server Development  
**Theme**: Enabling AI agents to access academic research data