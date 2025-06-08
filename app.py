"""
OpenAlex Explorer: Gradio MCP Server

Main application file that serves as both a Gradio web interface
and an MCP server for OpenAlex API interactions.
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

# Log application startup
app_info = {
    'python_version': sys.version,
    'gradio_version': gr.__version__,
    'working_directory': os.getcwd(),
    'environment_vars': {
        'OPENALEX_EMAIL': os.getenv('OPENALEX_EMAIL', 'NOT_SET'),
        'HF_SPACE': os.getenv('HF_SPACE', 'local')
    }
}
logger.log_startup(app_info)

# Initialize configuration and API client
try:
    logger.info("Initializing configuration manager")
    config_manager = ConfigManager()
    
    logger.info("Initializing OpenAlex API client")
    api_client = OpenAlexAPIClient(config_manager)
    
    # Initialize retrievers
    logger.info("Initializing data retrievers")
    publication_retriever = OpenAlexPublicationRetriever(api_client)
    author_retriever = OpenAlexAuthorRetriever(api_client)
    concept_retriever = OpenAlexConceptRetriever(api_client)
    
    logger.info("All components initialized successfully")
    
except Exception as e:
    logger.log_error(e, "Application initialization")
    raise


def search_openalex_papers(
    search_query: str,
    max_results: int = 3,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
) -> str:
    """
    Searches OpenAlex for academic papers by query, with optional date filtering.
    
    Args:
        search_query: The search query for papers
        max_results: Maximum number of results to return (default: 3)
        start_year: Optional start year for filtering
        end_year: Optional end year for filtering
    
    Returns:
        Formatted string with paper details
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
        
        formatted_results = format_paper_results(results)
        logger.log_mcp_call("search_openalex_papers", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(formatted_results)
        })
        
        return formatted_results
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_papers", duration, error=True)
        logger.log_mcp_call("search_openalex_papers", args, error=str(e))
        logger.log_error(e, "search_openalex_papers")
        return f"Error searching papers: {str(e)}"


def get_publication_by_doi(doi: str) -> str:
    """
    Retrieves a specific OpenAlex publication by its DOI.
    
    Args:
        doi: Digital Object Identifier of the publication
    
    Returns:
        Formatted string with publication details
    """
    start_time = time.time()
    args = {'doi': doi}
    
    logger.info(f"MCP Tool called: get_publication_by_doi", doi=doi)
    
    try:
        result = publication_retriever.get_by_doi(doi)
        duration = time.time() - start_time
        
        if result:
            formatted_result = format_paper_results([result])
            logger.log_performance("get_publication_by_doi", duration, found=True)
            logger.log_mcp_call("get_publication_by_doi", args, {
                'success': True,
                'found': True,
                'response_length': len(formatted_result)
            })
            return formatted_result
        else:
            logger.log_performance("get_publication_by_doi", duration, found=False)
            logger.log_mcp_call("get_publication_by_doi", args, {
                'success': True,
                'found': False
            })
            return f"No publication found for DOI: {doi}"
            
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("get_publication_by_doi", duration, error=True)
        logger.log_mcp_call("get_publication_by_doi", args, error=str(e))
        logger.log_error(e, "get_publication_by_doi")
        return f"Error retrieving publication: {str(e)}"


def search_openalex_authors(author_name: str, max_results: int = 5) -> str:
    """
    Searches OpenAlex for authors by their name.
    
    Args:
        author_name: Name of the author to search for
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted string with author details
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
        
        formatted_results = format_author_results(results)
        logger.log_mcp_call("search_openalex_authors", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(formatted_results)
        })
        
        return formatted_results
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_authors", duration, error=True)
        logger.log_mcp_call("search_openalex_authors", args, error=str(e))
        logger.log_error(e, "search_openalex_authors")
        return f"Error searching authors: {str(e)}"


def search_openalex_concepts(concept_name: str, max_results: int = 5) -> str:
    """
    Searches OpenAlex for concepts (fields of study) by name.
    
    Args:
        concept_name: Name of the concept to search for
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted string with concept details
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
        
        formatted_results = format_concept_results(results)
        logger.log_mcp_call("search_openalex_concepts", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(formatted_results)
        })
        
        return formatted_results
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_concepts", duration, error=True)
        logger.log_mcp_call("search_openalex_concepts", args, error=str(e))
        logger.log_error(e, "search_openalex_concepts")
        return f"Error searching concepts: {str(e)}"


def format_paper_results(papers: List[Dict[str, Any]]) -> str:
    """Format paper search results for display."""
    if not papers:
        return "No papers found."
    
    formatted = []
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'No title')
        doi = paper.get('doi', 'No DOI')
        abstract = paper.get('abstract', 'No abstract available')
        authors = paper.get('authors', [])
        year = paper.get('publication_year', 'Unknown year')
        
        author_names = [author.get('display_name', '') for author in authors[:3]]
        author_str = ', '.join(author_names)
        if len(authors) > 3:
            author_str += f" and {len(authors) - 3} others"
        
        formatted.append(f"""
{i}. {title}
   DOI: {doi}
   Year: {year}
   Authors: {author_str}
   Abstract: {abstract[:300]}{'...' if len(abstract) > 300 else ''}
""")
    
    return '\n'.join(formatted)


def format_author_results(authors: List[Dict[str, Any]]) -> str:
    """Format author search results for display."""
    if not authors:
        return "No authors found."
    
    formatted = []
    for i, author in enumerate(authors, 1):
        name = author.get('display_name', 'No name')
        orcid = author.get('orcid', 'No ORCID')
        affiliation = author.get('affiliation', {}).get('display_name', 'No affiliation')
        works_count = author.get('works_count', 0)
        
        formatted.append(f"""
{i}. {name}
   ORCID: {orcid}
   Affiliation: {affiliation}
   Works count: {works_count}
""")
    
    return '\n'.join(formatted)


def format_concept_results(concepts: List[Dict[str, Any]]) -> str:
    """Format concept search results for display."""
    if not concepts:
        return "No concepts found."
    
    formatted = []
    for i, concept in enumerate(concepts, 1):
        name = concept.get('display_name', 'No name')
        description = concept.get('description', 'No description')
        works_count = concept.get('works_count', 0)
        level = concept.get('level', 'Unknown level')
        
        formatted.append(f"""
{i}. {name}
   Level: {level}
   Works count: {works_count}
   Description: {description}
""")
    
    return '\n'.join(formatted)


# Create Gradio interface
def create_gradio_interface():
    """Create the Gradio web interface."""
    
    with gr.Blocks(title="OpenAlex Explorer") as app:
        gr.Markdown("# OpenAlex Explorer: MCP Server")
        gr.Markdown("Search academic papers, authors, and concepts from OpenAlex database.")
        
        with gr.Tab("Search Papers"):
            with gr.Row():
                query_input = gr.Textbox(label="Search Query", placeholder="Enter keywords to search for papers...")
                max_results_input = gr.Number(label="Max Results", value=3, minimum=1, maximum=20)
            
            with gr.Row():
                start_year_input = gr.Number(label="Start Year (optional)", minimum=1900, maximum=2030, value=None)
                end_year_input = gr.Number(label="End Year (optional)", minimum=1900, maximum=2030, value=None)
            
            search_button = gr.Button("Search Papers")
            papers_output = gr.Textbox(label="Results", lines=10)
            
            search_button.click(
                search_openalex_papers,
                inputs=[query_input, max_results_input, start_year_input, end_year_input],
                outputs=papers_output
            )
        
        with gr.Tab("Get Paper by DOI"):
            doi_input = gr.Textbox(label="DOI", placeholder="Enter DOI (e.g., 10.1038/s41586-021-03358-0)")
            doi_button = gr.Button("Get Paper")
            doi_output = gr.Textbox(label="Paper Details", lines=10)
            
            doi_button.click(
                get_publication_by_doi,
                inputs=doi_input,
                outputs=doi_output
            )
        
        with gr.Tab("Search Authors"):
            author_input = gr.Textbox(label="Author Name", placeholder="Enter author name...")
            author_max_input = gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            author_button = gr.Button("Search Authors")
            authors_output = gr.Textbox(label="Authors", lines=10)
            
            author_button.click(
                search_openalex_authors,
                inputs=[author_input, author_max_input],
                outputs=authors_output
            )
        
        with gr.Tab("Search Concepts"):
            concept_input = gr.Textbox(label="Concept Name", placeholder="Enter concept/field name...")
            concept_max_input = gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            concept_button = gr.Button("Search Concepts")
            concepts_output = gr.Textbox(label="Concepts", lines=10)
            
            concept_button.click(
                search_openalex_concepts,
                inputs=[concept_input, concept_max_input],
                outputs=concepts_output
            )
        
        gr.Markdown("## MCP Server Information")
        gr.Markdown("""
        This app also serves as an MCP server. You can connect MCP clients to:
        - **Local:** `http://127.0.0.1:7860/gradio_api/mcp/sse`
        - **Available Tools:** search_openalex_papers, get_publication_by_doi, search_openalex_authors, search_openalex_concepts
        """)
    
    return app


if __name__ == "__main__":
    try:
        # Check if email is set
        if not os.getenv('OPENALEX_EMAIL'):
            logger.warning("OPENALEX_EMAIL environment variable not set", 
                          recommendation="Set OPENALEX_EMAIL for better API access")
        else:
            logger.info("OPENALEX_EMAIL is configured", 
                       email=os.getenv('OPENALEX_EMAIL'))
        
        # Create and launch the Gradio app
        logger.info("Creating Gradio interface")
        app = create_gradio_interface()
        
        # Log launch details
        launch_config = {
            'server_name': "0.0.0.0",
            'server_port': 7860,
            'share': False,
            'mcp_endpoint': "http://0.0.0.0:7860/gradio_api/mcp/sse"
        }
        logger.info("Launching Gradio application", **launch_config)
        
        app.launch(server_name="0.0.0.0", server_port=7860, share=False)
        
    except Exception as e:
        logger.log_error(e, "Application launch")
        raise
