---
title: OpenAlex Explorer MCP Server
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "5.9.1"
app_file: app.py
pinned: false
license: mit
tags:
  - mcp-server
  - openalex
  - academic-research
  - scientific-papers
  - model-context-protocol
  - hackathon
---

# OpenAlex Explorer: Gradio MCP Server

**Hackathon Tag:** `mcp-server-track`

**Demo Video:** [Link to our video recording of the MCP server in action] (e.g., YouTube, Loom, or a link to another Gradio Space acting as a client)
*(Will replace this with the actual link to our demo video!)*

## Project Description

OpenAlex Explorer is a Gradio application that serves as a powerful Model Context Protocol (MCP) tool for interacting with the [OpenAlex](https://openalex.org/) scholarly database. It allows Language Models (LLMs) and other MCP clients to easily search for academic papers, authors, and concepts, and retrieve specific publications by DOI.

This tool aims to provide a standardized and accessible way for AI agents to leverage the rich, interconnected data within OpenAlex, enabling them to ground their responses in scientific literature, find relevant research, and understand scholarly trends.

This project is built for the **Agents & MCP Hackathon (June 2-10, 2025)** and participates in Track 1: MCP Tool / Server.

**Based on and inspired by:** This project leverages and adapts components from the [tsi-sota-ai](https://github.com/skazo4nick/tsi-sota-ai) repository, particularly its modules for OpenAlex API interaction.

## Features

*   **MCP Server Functionality**: Exposes OpenAlex search capabilities as tools for MCP clients.
*   **Search Academic Papers**: Query OpenAlex for publications based on keywords, with optional filtering by publication year.
*   **Retrieve Publication by DOI**: Fetch specific paper details using its Digital Object Identifier.
*   **Search Authors**: Find authors in OpenAlex by name.
*   **Search Concepts**: Discover academic concepts (fields of study) by name.
*   **User-Friendly Gradio UI**: Provides a web interface for direct interaction and testing of the search functionalities.
*   **Standardized Output**: Returns structured data (title, DOI, abstract, authors, keywords, etc.) suitable for LLM consumption.
*   **Abstract Reconstruction**: Handles OpenAlex's inverted-index abstract format to provide full abstracts.

## Tech Stack

*   Python 3.x
*   Gradio (with `gradio[mcp]`)
*   Pyalex (for OpenAlex API interaction)
*   PyYAML (for configuration management)

## Project Structure

The project is organized into modular components:

```
/openalex_mcp_tool
├── app.py                     # Main Gradio app & MCP server logic
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── config/
│   └── slr_config.yaml        # Configuration file (primarily for non-sensitive settings)
├── slr_modules/               # Adapted modules from tsi-sota-ai
│   ├── __init__.py
│   ├── api_clients.py         # Contains the OpenAlexAPIClient
│   └── config_manager.py      # Handles configuration loading
└── openalex_modules/          # Specific OpenAlex interaction modules
    ├── __init__.py
    ├── openalex_author_retriever.py
    ├── openalex_publication_retriever.py
    ├── openalex_concept_retriever.py
    └── openalex_utils.py      # Utility functions for OpenAlex data
```

## Setup and Running Locally

1.  **Clone the Repository (or create from files):**
    ```bash
    # If it's a Git repo:
    # git clone https://your-repo-url.git
    # cd openalex_mcp_tool
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variable:**
    For polite and reliable access to the OpenAlex API, you **must** set your email address as an environment variable:
    ```bash
    export OPENALEX_EMAIL="your.email@example.com"
    ```
    (On Windows, use `set OPENALEX_EMAIL=your.email@example.com` or set it through system properties). This email is used in the `User-Agent` header for `pyalex` calls.

5.  **Run the Gradio App:**
    ```bash
    python app.py
    ```
    The application will start, and you'll see a local URL in the console (e.g., `http://127.0.0.1:7860`).

## Using as an MCP Server

Once the Gradio app is running (either locally or deployed on Hugging Face Spaces), it exposes its functionalities as MCP tools.

1.  **MCP Server URL:**
    *   **Local:** `http://127.0.0.1:7860/gradio_api/mcp/sse` (or your local port)
    *   **Hugging Face Space:** `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/gradio_api/mcp/sse`

2.  **Configure Your MCP Client:**
    Add the MCP Server URL to your MCP client's configuration (e.g., Tiny Agents, Claude Desktop, Cursor). Example configuration:
    ```json
    {
      "mcpServers": {
        "openalex_explorer": { // You can name this key as you like
          "url": "YOUR_MCP_SERVER_URL_HERE"
        }
      }
    }
    ```
    *Note: Some clients like Claude Desktop might require `mcp-remote` if they don't support SSE directly. Refer to the Gradio MCP documentation for setup with `mcp-remote`.*

3.  **Available Tools:**
    The following functions are exposed as MCP tools. The descriptions and parameters are derived from their Python docstrings. You can view the full schema at `YOUR_GRADIO_APP_URL/gradio_api/mcp/schema`.

    *   **`search_openalex_papers(search_query: str, max_results: int = 3, start_year: Optional[int] = None, end_year: Optional[int] = None)`**
        *   Description: Searches OpenAlex for academic papers by query, with optional date filtering.
        *   Example Usage by LLM: "Find 5 recent papers on quantum machine learning published since 2022."

    *   **`get_publication_by_doi(doi: str)`**
        *   Description: Retrieves a specific OpenAlex publication by its DOI.
        *   Example Usage by LLM: "Get the abstract for the paper with DOI 10.1038/s41586-021-03358-0."

    *   **`search_openalex_authors(author_name: str, max_results: int = 5)`**
        *   Description: Searches OpenAlex for authors by their name.
        *   Example Usage by LLM: "Find authors named 'Yoshua Bengio' and their affiliations."

    *   **`search_openalex_concepts(concept_name: str, max_results: int = 5)`**
        *   Description: Searches OpenAlex for concepts (fields of study) by name.
        *   Example Usage by LLM: "What is the OpenAlex concept ID for 'computational linguistics'?"

## Development Notes

*   **Modularity**: The application is structured with a clear separation between the Gradio UI/MCP layer (`app.py`), API client logic (`slr_modules/api_clients.py`), and specific OpenAlex data retrievers (`openalex_modules/`).
*   **Configuration**: `ConfigManager` loads settings from `config/slr_config.yaml` and environment variables (especially `OPENALEX_EMAIL`).
*   **Error Handling**: Basic error handling is in place, returning error messages as part of the MCP response if issues occur.

## Future Enhancements (Post-Hackathon Ideas)

*   More advanced filtering and sorting options for paper search.
*   Support for retrieving works by OpenAlex ID directly.
*   Tools for exploring author collaborations or concept relationships.
*   Pagination support for MCP tool results if a client requests more items than `max_results`.