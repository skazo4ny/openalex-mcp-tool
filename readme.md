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

# 📚 OpenAlex Explorer MCP Server - Enhanced Edition

**🏆 Agents & MCP Hackathon Submission (June 2-10, 2025)**

An enhanced dual-purpose application that provides both a **Gradio web interface** and **MCP (Model Context Protocol) server** for accessing comprehensive academic research data from the OpenAlex API. Extended with additional entity types, advanced filtering capabilities, and analytical tools for more sophisticated research workflows.

## 🚀 Live Demo

**Try it now**: [https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool](https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool)
**Video Demo Link**: https://youtu.be/XJNCQ5J2yPM 

## 🎯 Core Features

### 🔍 **MCP Tools**
#### Core Tools
1. **`search_openalex_papers`** - Search academic papers with date filtering
2. **`get_publication_by_doi`** - Retrieve specific publications by DOI  
3. **`search_openalex_authors`** - Find authors and their metrics
4. **`search_openalex_concepts`** - Explore academic concepts and fields

#### Phase 1 Enhanced Tools
5. **`search_openalex_topics`** - Explore academic topics (improved replacement for concepts)
6. **`search_openalex_institutions`** - Find research institutions and universities
7. **`search_openalex_sources`** - Discover publication venues (journals, conferences)

#### Phase 2 Advanced Tools
8. **`group_openalex_works`** - Group publications for statistical analysis
9. **`advanced_search`** - Complex queries with boolean operators

#### Phase 3 Additional Tools
10. **`search_openalex_publishers`** - Find academic publishers
11. **`search_openalex_funders`** - Discover research funding organizations
12. **`bulk_retrieve_works`** - Efficiently retrieve large datasets

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

#### Core Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_openalex_papers` | Find academic papers | `query`, `start_year`, `end_year`, `max_results` |
| `get_publication_by_doi` | Get specific paper | `doi` |
| `search_openalex_authors` | Find researchers | `query`, `max_results` |
| `search_openalex_concepts` | Explore topics | `query`, `max_results` |

#### Phase 1 Enhanced Tools
| `search_openalex_topics` | Explore research topics | `topic_name`, `max_results` |
| `search_openalex_institutions` | Find universities and institutions | `institution_name`, `max_results` |
| `search_openalex_sources` | Discover publication venues | `source_name`, `max_results` |

#### Phase 2 Advanced Tools
| `group_openalex_works` | Analyze research trends | `group_by`, `filter_query` |
| `advanced_search` | Complex research queries | `query`, `search_fields` |

#### Phase 3 Additional Tools
| `search_openalex_publishers` | Find academic publishers | `publisher_name`, `max_results` |
| `search_openalex_funders` | Discover funding organizations | `funder_name`, `max_results` |
| `bulk_retrieve_works` | Retrieve large datasets | `query`, `max_results` |

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

### Implementation Plans
- **[Phase 1 Enhancements](docs/plan/phase-1-enhancements.md)** - High-priority entity implementations
- **[Phase 2 Enhancements](docs/plan/phase-2-enhancements.md)** - Advanced features and analytics
- **[Phase 3 Enhancements](docs/plan/phase-3-enhancements.md)** - Additional entities and bulk operations

### Reports
- **[Gap Analysis](docs/reports/openalex-api-mcp-gap-analysis.md)** - Comparison of API capabilities vs. current implementation
- **[Implementation Specification](docs/reports/openalex-api-implementation-spec.md)** - Detailed technical specifications
- **[Enhancement Summary](docs/reports/openalex-mcp-enhancement-summary.md)** - Executive summary of findings
- **[Phase 1 Implementation Report](docs/reports/phase-1-implementation-report.md)** - Comprehensive report on Phase 1 enhancements

### Architecture Decision Records
- **[ADR 001: Enhance OpenAlex MCP Implementation](docs/adr/001-enhance-openalex-mcp-implementation.md)** - Decision to expand API coverage
- **[ADR 002: MCP Server Architecture](docs/adr/002-mcp-server-architecture.md)** - Architectural approach for MCP implementation
- **[ADR 003: Retriever Module Implementation](docs/adr/003-retriever-module-implementation.md)** - Approach for new entity retrievers
- **[ADR 004: Phase 1 Implementation](docs/adr/004-phase-1-implementation.md)** - Architecture decisions for Phase 1

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
- **Research Trends**: Analyze publication patterns over time
- **Institution Analysis**: Compare research output across organizations
- **Venue Assessment**: Evaluate journal and conference reputations

### For AI Agents
- **Research Assistant**: Enable LLMs to access academic data
- **Fact Checking**: Verify claims against scholarly sources  
- **Content Generation**: Enhance writing with academic references
- **Literature Synthesis**: Automatically summarize research areas
- **Expert Identification**: Find specialists for specific topics
- **Trend Analysis**: Identify emerging research areas

### For Developers
- **MCP Integration**: Add research capabilities to any MCP client
- **Data Pipeline**: Automate academic data collection
- **Research Tools**: Build custom academic applications
- **API Extension**: Extend functionality with additional tools
- **Analytics Platform**: Create research insights dashboards
- **Knowledge Base**: Integrate academic data into larger systems

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

**Institution Analysis:**
```
Query: "university"
Country: "US"
Focus: Research output comparison
```

**Publication Venues:**
```
Query: "nature"
Type: "journal"
Focus: Impact factor analysis
```

## 🚀 Project Development Status

### ✅ Phase 1: High-Priority Enhancements (Completed)
- **Topics API**: Implemented enhanced research topics (replacement for deprecated concepts)
- **Institutions API**: Added research institution and university data
- **Sources API**: Integrated publication venue information (journals, conferences, repositories)
- **Total Tools**: 12 MCP tools available
- **Testing**: 58 comprehensive unit and integration tests
- **Documentation**: Complete API and user guide updates

### 🔄 Phase 2: Advanced Features (In Progress)
- Group analysis tools for statistical research insights
- Advanced search capabilities with boolean operators
- Enhanced filtering and sorting options
- Expected completion: 2-3 weeks

### 🔮 Phase 3: Additional Entities (Planned)
- Publisher and funder information
- Bulk data retrieval operations
- Advanced analytics and visualization
- Timeline: To be determined

## 🔄 Development Approach Update

### Repository Migration
As of this stage, we have decided to transition our development efforts to GitHub for the following reasons:
1. **Better collaboration tools** for team development
2. **Enhanced CI/CD capabilities** for automated testing and deployment
3. **Improved issue tracking** and project management features
4. **Preparation for FastMCP migration** - Our next architectural evolution

### Future Architecture: FastMCP Approach
We are planning to migrate from the current Gradio-based MCP implementation to a specialized FastMCP approach for the following benefits:
1. **Performance Optimization**: FastMCP provides better performance for high-throughput MCP operations
2. **Decoupled Architecture**: Separation of business logic from transport layers for better maintainability
3. **Standard Compliance**: Better adherence to MCP specification standards
4. **Scalability**: Improved handling of concurrent connections and requests

This transition will happen in Phase 2 development, where we'll refactor the core MCP server components while maintaining API compatibility.

**Note**: The Hugging Face Space will continue to host the current Gradio-based implementation for demo purposes, but active development will continue on GitHub.

## 🤝 Contributing

This project is part of the **Agents & MCP Hackathon**. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🏷️ Hackathon Tags

`#mcp-server-track` `#openalex` `#academic-research` `#gradio` `#model-context-protocol`

---

**Built for the Agents & MCP Hackathon (June 2-10, 2025)**  
**Track**: MCP Server Development  
**Theme**: Enabling AI agents to access academic research data