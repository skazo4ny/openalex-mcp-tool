# OpenAlex Explorer MCP Server - Documentation Index

Welcome to the OpenAlex Explorer MCP Server documentation! This project provides both a user-friendly Gradio web interface and MCP (Model Context Protocol) server functionality for accessing academic research data from the OpenAlex API.

## Quick Start

1. **For End Users**: Check out the [User Guide](user-guide.md) to learn how to search papers, authors, and concepts
2. **For Developers**: See the [API Documentation](api.md) for MCP integration details
3. **For Deployment**: Follow the [Deployment Guide](deployment.md) for setup instructions
4. **For Requirements**: Review the [Requirements Specification](requirements.md) for detailed technical specs

## Documentation Structure

### Core Documentation

| Document | Description | Target Audience |
|----------|-------------|-----------------|
| [User Guide](user-guide.md) | How to use the web interface and MCP tools effectively | End users, researchers |
| [API Documentation](api.md) | MCP tool schemas, examples, and integration guide | Developers, MCP clients |
| [Deployment Guide](deployment.md) | Setup instructions for various platforms | DevOps, administrators |
| [Requirements Specification](requirements.md) | Detailed functional and technical requirements | Product managers, developers |

### Quick Reference

#### Web Interface Access
- Navigate to your deployment URL
- Use the tabbed interface for different search types
- Apply filters for refined results

#### MCP Integration
```json
{
  "mcpServers": {
    "openalex-explorer": {
      "command": "python",
      "args": ["/path/to/app.py"]
    }
  }
}
```

#### Available MCP Tools
- `search_openalex_papers` - Search academic papers
- `get_publication_by_doi` - Retrieve specific publications
- `search_openalex_authors` - Find authors and metrics
- `search_openalex_concepts` - Explore academic concepts

## Key Features

### 🔍 **Comprehensive Search**
- Full-text search across OpenAlex's database
- Advanced filtering by date, author, and concepts
- Real-time results with pagination

### 🤖 **MCP Integration**
- Standards-compliant Model Context Protocol server
- Structured JSON schemas for all tools
- Error handling and validation

### 📊 **Rich Data Access**
- Publication details with abstracts and citations
- Author metrics and affiliations
- Concept hierarchies and relationships

### 🚀 **Easy Deployment**
- One-click Hugging Face Spaces deployment
- Docker support for containerized environments
- Local development setup with virtual environments

### 📝 **Comprehensive Logging**
- Structured JSON and XML logging
- Performance monitoring and error tracking
- Daily log rotation and archival

## Getting Started

### Option 1: Use Deployed Version
Visit the [live demo on Hugging Face Spaces](https://huggingface.co/spaces/skazo4nick/openalex-mcp-tool) to try the interface immediately.

### Option 2: Deploy Your Own
Follow the [Deployment Guide](deployment.md) to set up your own instance on:
- Hugging Face Spaces
- Local development environment
- Docker containers
- Cloud platforms

### Option 3: Integrate via MCP
Use the [API Documentation](api.md) to integrate with:
- Claude Desktop
- Custom MCP clients
- AI agents and tools
- Research workflows

## Support and Contributions

### Getting Help
- Check the [User Guide](user-guide.md) for usage questions
- Review [Deployment Guide](deployment.md) for setup issues
- Examine logs for debugging information

### Contributing
This project is open for contributions:
1. Fork the repository
2. Create feature branches
3. Follow documentation standards
4. Submit pull requests with tests

### Reporting Issues
When reporting issues, include:
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs
- Environment details

## Technical Overview

### Architecture
- **Frontend**: Gradio web interface
- **Backend**: Python with pyalex library
- **Protocol**: MCP stdio transport
- **API**: OpenAlex REST API
- **Logging**: Structured multi-format logging

### Dependencies
- Python 3.9+
- Gradio 5.33.0+
- pyalex 0.13+
- MCP framework
- Standard logging libraries

### Performance
- Rate limiting: 100 requests/second
- Concurrent users: Configurable via Gradio
- Response times: <2 seconds typical
- Data freshness: Real-time from OpenAlex

## Project Status

### Current Version: 1.0
- ✅ Complete MCP server implementation
- ✅ Full Gradio web interface
- ✅ Comprehensive logging system
- ✅ Hugging Face Spaces deployment
- ✅ Complete documentation suite

### Upcoming Features
- Enhanced caching mechanisms
- Additional export formats
- Advanced search filters
- Performance optimizations

## Resources

### External Links
- [OpenAlex API Documentation](https://docs.openalex.org/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Gradio Documentation](https://gradio.app/docs/)
- [Hugging Face Spaces Guide](https://huggingface.co/docs/hub/spaces)

### Related Projects
- [pyalex](https://github.com/J535D165/pyalex) - Python OpenAlex client
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) - Python MCP implementation
- [OpenAlex](https://openalex.org/) - Open catalog of scholarly papers

---

**Last Updated**: June 8, 2025  
**Version**: 1.0  
**License**: MIT
