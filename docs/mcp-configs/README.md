# MCP Client Configuration Files

This directory contains configuration files for connecting various MCP clients to the OpenAlex Explorer MCP server.

## Available Configurations

### 1. Claude Desktop (`claude-desktop.json`)
For Claude Desktop application (requires `mcp-remote` wrapper due to SSE limitations):

```json
{
  "mcpServers": {
    "openalex-explorer": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:7860/gradio_api/mcp/sse"
      ]
    }
  }
}
```

**Setup Instructions:**
1. Install Node.js if not already installed
2. Copy the configuration to your Claude Desktop MCP settings
3. Start the OpenAlex Explorer server locally
4. Claude Desktop will automatically connect via the mcp-remote proxy

### 2. Cursor/Cline (`cursor-cline.json`)
For Cursor IDE and Cline VS Code extension (direct SSE support):

```json
{
  "mcpServers": {
    "openalex-explorer": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    }
  }
}
```

**Setup Instructions:**
1. Copy the configuration to your MCP client settings
2. Start the OpenAlex Explorer server locally
3. The client will connect directly to the SSE endpoint

### 3. Hugging Face Spaces (`huggingface-spaces.json`)
For connecting to a deployed version on Hugging Face Spaces:

```json
{
  "mcpServers": {
    "openalex-explorer": {
      "url": "https://YOUR-USERNAME-openalex-mcp-tool.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

**Setup Instructions:**
1. Replace `YOUR-USERNAME` with your actual Hugging Face username
2. Deploy the OpenAlex Explorer to Hugging Face Spaces
3. Use the Space URL in your MCP client configuration

## Available MCP Tools

The OpenAlex Explorer MCP server provides the following tools:

### 1. `search_openalex_papers`
Search for academic papers and research publications.

**Parameters:**
- `search_query` (string): Keywords or phrases to search for
- `max_results` (integer, optional): Number of results to return (default: 3, max: 20)
- `start_year` (integer, optional): Earliest publication year
- `end_year` (integer, optional): Latest publication year

**Example Usage:**
```
Search for papers on "machine learning" published between 2020-2024
```

### 2. `get_publication_by_doi`
Retrieve a specific publication using its DOI.

**Parameters:**
- `doi` (string): Digital Object Identifier of the publication

**Example Usage:**
```
Get details for DOI: 10.1038/nature12373
```

### 3. `search_openalex_authors`
Find researchers and authors by name.

**Parameters:**
- `author_name` (string): Full or partial name of the researcher
- `max_results` (integer, optional): Number of results to return (default: 5, max: 20)

**Example Usage:**
```
Find author "Jennifer Doudna"
```

### 4. `search_openalex_concepts`
Explore research concepts and fields of study.

**Parameters:**
- `concept_name` (string): Name of the research concept or field
- `max_results` (integer, optional): Number of results to return (default: 5, max: 20)

**Example Usage:**
```
Explore concepts related to "artificial intelligence"
```

## Endpoints

### Local Development
- **MCP SSE Endpoint**: `http://localhost:7860/gradio_api/mcp/sse`
- **MCP Schema Endpoint**: `http://localhost:7860/gradio_api/mcp/schema`
- **Gradio Web Interface**: `http://localhost:7860`

### Production (Hugging Face Spaces)
- **MCP SSE Endpoint**: `https://your-username-openalex-mcp-tool.hf.space/gradio_api/mcp/sse`
- **MCP Schema Endpoint**: `https://your-username-openalex-mcp-tool.hf.space/gradio_api/mcp/schema`
- **Gradio Web Interface**: `https://your-username-openalex-mcp-tool.hf.space`

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure the OpenAlex Explorer server is running
   - Check that the URL in your configuration is correct
   - Verify your firewall isn't blocking the connection

2. **Claude Desktop Not Working**
   - Make sure Node.js is installed
   - Verify that `npx mcp-remote` command works
   - Check Claude Desktop logs for error messages

3. **Tools Not Appearing**
   - Restart your MCP client after adding the configuration
   - Check the MCP schema endpoint to verify tools are exposed
   - Ensure the server started with `mcp_server=True`

### Testing the Connection

1. **Check Server Status**: Visit `http://localhost:7860` to see if the Gradio interface loads
2. **Verify MCP Schema**: Visit `http://localhost:7860/gradio_api/mcp/schema` to see available tools
3. **Test SSE Endpoint**: Use a tool like curl to test the SSE connection:
   ```bash
   curl -H "Accept: text/event-stream" http://localhost:7860/gradio_api/mcp/sse
   ```

## Environment Variables

### Required
- `OPENALEX_EMAIL`: Your email address for OpenAlex API access (recommended for higher rate limits)

### Optional
- `GRADIO_MCP_SERVER`: Set to `True` to enable MCP server (alternative to `mcp_server=True` parameter)

## Support

For issues with:
- **OpenAlex API**: Check the [OpenAlex documentation](https://docs.openalex.org/)
- **MCP Protocol**: See the [Model Context Protocol documentation](https://modelcontextprotocol.io/)
- **Gradio MCP**: Refer to the [Gradio MCP guide](https://huggingface.co/blog/gradio-mcp)

---

*Last updated: June 8, 2025*
