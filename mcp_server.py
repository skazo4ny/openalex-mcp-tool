#!/usr/bin/env python3
"""
OpenAlex Explorer: Dedicated MCP Server

A specialized MCP server that exposes OpenAlex research tools directly
for use with LLM clients via the Model Context Protocol.
"""

import gradio as gr
import os
import sys
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import our modules
from slr_modules.config_manager import ConfigManager
from slr_modules.api_clients import OpenAlexAPIClient
from slr_modules.logger import get_logger, setup_logging
from openalex_modules.openalex_publication_retriever import OpenAlexPublicationRetriever
from openalex_modules.openalex_author_retriever import OpenAlexAuthorRetriever
from openalex_modules.openalex_concept_retriever import OpenAlexConceptRetriever

# Set up enhanced logging
logger = setup_logging("openalex_mcp", "logs")

# Initialize configuration and API client
try:
    logger.info("Initializing MCP server components")
    config_manager = ConfigManager()
    api_client = OpenAlexAPIClient(config_manager)
    
    # Initialize retrievers
    publication_retriever = OpenAlexPublicationRetriever(api_client)
    author_retriever = OpenAlexAuthorRetriever(api_client)
    concept_retriever = OpenAlexConceptRetriever(api_client)
    
    logger.info("MCP server components initialized successfully")
    
except Exception as e:
    logger.log_error(e, "MCP server initialization")
    raise


def search_openalex_papers(
    search_query: str,
    max_results: int = 3,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Search OpenAlex database for academic papers and research publications.
    
    This tool searches the comprehensive OpenAlex database containing over 250 million 
    academic papers from all fields of study. Use this to find research papers, 
    analyze publication trends, or gather academic information on any topic.
    
    Args:
        search_query: Keywords or phrases to search for in paper titles, abstracts, 
                     and full text. Examples: "machine learning", "climate change", 
                     "CRISPR gene editing", "quantum computing"
        max_results: Number of papers to return (1-20). Default is 3 for quick results.
                    Use higher values for comprehensive research.
        start_year: Optional earliest publication year filter (e.g., 2020). 
                   Use to focus on recent research.
        end_year: Optional latest publication year filter (e.g., 2024).
                 Combine with start_year for specific time periods.
    
    Returns:
        List of paper dictionaries containing title, DOI, authors, abstract, 
        publication year, citation count, venue information, and OpenAlex ID.
        Each paper includes structured metadata for further analysis.
        
    Examples:
        - search_openalex_papers("neural networks", 5, 2020, 2024)
        - search_openalex_papers("COVID-19 vaccine efficacy", 10)
        - search_openalex_papers("renewable energy storage")
    """
    start_time = time.time()
    args = {
        'search_query': search_query,
        'max_results': max_results,
        'start_year': start_year,
        'end_year': end_year
    }
    
    logger.info(f"MCP Tool called: search_openalex_papers", **args)
    
    try:
        results = publication_retriever.search_publications(
            query=search_query,
            max_results=max_results,
            start_year=start_year,
            end_year=end_year
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_papers", duration, 
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_papers", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_papers", duration, error=True)
        logger.log_mcp_call("search_openalex_papers", args, error=str(e))
        logger.log_error(e, "search_openalex_papers")
        return []


def get_publication_by_doi(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific academic publication using its Digital Object Identifier (DOI).
    
    This tool fetches detailed information about a specific research paper when you 
    have its DOI. DOIs are unique identifiers for academic publications and provide 
    the most reliable way to retrieve exact paper details.
    
    Args:
        doi: Digital Object Identifier of the publication. Can be in any valid DOI format:
             - Full URL: "https://doi.org/10.1038/nature12373"
             - DOI string: "10.1038/nature12373" 
             - Short form: "doi:10.1038/nature12373"
    
    Returns:
        Detailed publication dictionary with complete metadata including:
        title, authors, abstract, publication venue, citation count, 
        referenced works, and bibliographic information. Returns None if DOI not found.
        
    Examples:
        - get_publication_by_doi("10.1038/nature12373")
        - get_publication_by_doi("https://doi.org/10.1126/science.1260419")
        - get_publication_by_doi("10.1103/PhysRevLett.116.061102")
    """
    start_time = time.time()
    args = {'doi': doi}
    
    logger.info(f"MCP Tool called: get_publication_by_doi", doi=doi)
    
    try:
        result = publication_retriever.get_by_doi(doi)
        duration = time.time() - start_time
        
        if result:
            logger.log_performance("get_publication_by_doi", duration, found=True)
            logger.log_mcp_call("get_publication_by_doi", args, {
                'success': True,
                'found': True,
                'response_length': 1
            })
            return result
        else:
            logger.log_performance("get_publication_by_doi", duration, found=False)
            logger.log_mcp_call("get_publication_by_doi", args, {
                'success': True,
                'found': False
            })
            return None
            
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("get_publication_by_doi", duration, error=True)
        logger.log_mcp_call("get_publication_by_doi", args, error=str(e))
        logger.log_error(e, "get_publication_by_doi")
        return None


def search_openalex_authors(author_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for academic researchers and authors in the OpenAlex database.
    
    This tool helps you find researchers, professors, and academic authors by name.
    Use it to discover experts in specific fields, find collaboration opportunities,
    or get detailed information about an author's research profile and publications.
    
    Args:
        author_name: Full or partial name of the researcher to search for.
                    Examples: "Marie Curie", "Einstein", "Jennifer Doudna",
                    "Geoffrey Hinton". Works with various name formats and spellings.
        max_results: Number of author profiles to return (1-20). Default is 5.
                    Use higher values when searching common names.
    
    Returns:
        List of author dictionaries containing display name, ORCID identifier,
        institutional affiliations, publication count, citation count, h-index,
        research areas, and OpenAlex author ID. Sorted by relevance and impact.
        
    Examples:
        - search_openalex_authors("Jennifer Doudna", 3)
        - search_openalex_authors("Geoffrey Hinton", 5) 
        - search_openalex_authors("Marie Curie", 1)
    """
    start_time = time.time()
    args = {'author_name': author_name, 'max_results': max_results}
    
    logger.info(f"MCP Tool called: search_openalex_authors", **args)
    
    try:
        results = author_retriever.search_authors(
            name=author_name,
            max_results=max_results
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_authors", duration,
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_authors", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_authors", duration, error=True)
        logger.log_mcp_call("search_openalex_authors", args, error=str(e))
        logger.log_error(e, "search_openalex_authors")
        return []


def search_openalex_concepts(concept_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Explore academic concepts, research fields, and scientific topics in OpenAlex.
    
    This tool helps you discover and understand research concepts, fields of study,
    and scientific topics. Use it to explore research areas, understand topic 
    hierarchies, or find related fields of study for comprehensive literature reviews.
    
    Args:
        concept_name: Name of the research concept, field, or topic to search for.
                     Examples: "artificial intelligence", "molecular biology", 
                     "climate science", "quantum mechanics", "public health"
        max_results: Number of concept results to return (1-20). Default is 5.
                    Higher values show related and broader/narrower concepts.
    
    Returns:
        List of concept dictionaries containing display name, description,
        level in concept hierarchy, related concepts, work count, 
        citation count, and concept relationships. Helps map research landscapes.
        
    Examples:
        - search_openalex_concepts("machine learning", 5)
        - search_openalex_concepts("renewable energy", 10)
        - search_openalex_concepts("neuroscience", 3)
    """
    start_time = time.time()
    args = {'concept_name': concept_name, 'max_results': max_results}
    
    logger.info(f"MCP Tool called: search_openalex_concepts", **args)
    
    try:
        results = concept_retriever.search_concepts(
            name=concept_name,
            max_results=max_results
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_concepts", duration,
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_concepts", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_concepts", duration, error=True)
        logger.log_mcp_call("search_openalex_concepts", args, error=str(e))
        logger.log_error(e, "search_openalex_concepts")
        return []


def create_mcp_interface():
    """Create a Gradio interface specifically optimized for MCP."""
    
    # Create the interface with our MCP functions
    interface = gr.Interface(
        fn=[
            search_openalex_papers,
            get_publication_by_doi,
            search_openalex_authors,
            search_openalex_concepts
        ],
        inputs=[
            # search_openalex_papers inputs
            [
                gr.Textbox(label="Search Query", placeholder="Enter keywords to search for papers..."),
                gr.Number(label="Max Results", value=3, minimum=1, maximum=20),
                gr.Number(label="Start Year (optional)", minimum=1900, maximum=2030, value=None),
                gr.Number(label="End Year (optional)", minimum=1900, maximum=2030, value=None)
            ],
            # get_publication_by_doi inputs
            [
                gr.Textbox(label="DOI", placeholder="Enter DOI (e.g., 10.1038/nature12373)")
            ],
            # search_openalex_authors inputs
            [
                gr.Textbox(label="Author Name", placeholder="Enter author name..."),
                gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            ],
            # search_openalex_concepts inputs
            [
                gr.Textbox(label="Concept Name", placeholder="Enter concept/field name..."),
                gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            ]
        ],
        outputs=[
            gr.JSON(label="Paper Results"),
            gr.JSON(label="Publication Details"),
            gr.JSON(label="Author Results"),
            gr.JSON(label="Concept Results")
        ],
        title="OpenAlex Explorer MCP Server",
        description="""
        # 🔬 OpenAlex Explorer MCP Server
        
        Academic research tools accessible via Model Context Protocol (MCP).
        
        ## 🚀 MCP Endpoints
        - **SSE**: `http://localhost:7861/gradio_api/mcp/sse`
        - **Schema**: `http://localhost:7861/gradio_api/mcp/schema`
        
        ## 🛠️ Available Tools
        1. **search_openalex_papers** - Search academic papers with optional year filtering
        2. **get_publication_by_doi** - Retrieve specific publications by DOI
        3. **search_openalex_authors** - Find researchers and authors by name
        4. **search_openalex_concepts** - Explore research topics and fields
        
        ## ⚙️ MCP Client Configuration
        
        ### Claude Desktop
        ```json
        {
          "mcpServers": {
            "openalex-explorer": {
              "command": "npx",
              "args": ["mcp-remote", "http://localhost:7861/gradio_api/mcp/sse"]
            }
          }
        }
        ```
        
        ### Cursor/Cline
        ```json
        {
          "mcpServers": {
            "openalex-explorer": {
              "url": "http://localhost:7861/gradio_api/mcp/sse"
            }
          }
        }
        ```
        """
    )
    
    return interface


if __name__ == "__main__":
    try:
        # Check if email is set
        if not os.getenv('OPENALEX_EMAIL'):
            logger.warning("OPENALEX_EMAIL environment variable not set")
            os.environ['OPENALEX_EMAIL'] = 'mcp-server@gradio.ai'
        
        logger.info("OPENALEX_EMAIL configured", email=os.getenv('OPENALEX_EMAIL'))
        
        # Create MCP interface
        logger.info("Creating MCP interface")
        app = create_mcp_interface()
        
        # Launch configuration
        launch_config = {
            'server_name': "0.0.0.0",
            'server_port': 7861,  # Different port from main app
            'share': False,
            'mcp_server': True,
            'mcp_endpoint': "http://0.0.0.0:7861/gradio_api/mcp/sse",
            'mcp_schema': "http://0.0.0.0:7861/gradio_api/mcp/schema"
        }
        
        logger.info("Launching dedicated MCP server", **launch_config)
        
        print("\n" + "="*70)
        print("🔬 OpenAlex Explorer MCP Server Starting...")
        print("="*70)
        print(f"🌐 Web Interface: http://localhost:7861")
        print(f"🔗 MCP SSE Endpoint: http://localhost:7861/gradio_api/mcp/sse")
        print(f"📋 MCP Schema: http://localhost:7861/gradio_api/mcp/schema")
        print("="*70)
        print("🛠️  Available MCP Tools:")
        print("   • search_openalex_papers")
        print("   • get_publication_by_doi")
        print("   • search_openalex_authors")
        print("   • search_openalex_concepts")
        print("="*70)
        print("Ready for MCP client connections!")
        print("="*70 + "\n")
        
        app.launch(
            server_name="0.0.0.0",
            server_port=7861,
            share=False,
            mcp_server=True
        )
        
    except Exception as e:
        logger.log_error(e, "MCP server launch")
        raise
