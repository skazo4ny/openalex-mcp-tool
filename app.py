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
from openalex_modules.openalex_topic_retriever import OpenAlexTopicRetriever
from openalex_modules.openalex_institution_retriever import OpenAlexInstitutionRetriever
from openalex_modules.openalex_source_retriever import OpenAlexSourceRetriever

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
    topic_retriever = OpenAlexTopicRetriever(api_client)
    institution_retriever = OpenAlexInstitutionRetriever(api_client)
    source_retriever = OpenAlexSourceRetriever(api_client)
    
    logger.info("All components initialized successfully")
    
except Exception as e:
    logger.log_error(e, "Application initialization")
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


# Add the new MCP tool functions for Topics
def search_openalex_topics(topic_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Explore academic topics in OpenAlex (improved replacement for deprecated Concepts).
    
    This tool provides access to OpenAlex's new Topics entity, which offers more 
    accurate and focused research categorization than the deprecated Concepts.
    Topics are organized in a hierarchical structure: domain → field → subfield → topic.
    
    Args:
        topic_name: Name of the research topic to search for.
                   Examples: "artificial intelligence", "molecular biology", 
                   "climate science", "quantum computing", "public health"
        max_results: Number of topic results to return (1-20). Default is 5.
                    Higher values show related and broader/narrower topics.
    
    Returns:
        List of topic dictionaries containing display name, description,
        hierarchical structure (domain, field, subfield), keywords, work count, 
        citation count, and topic relationships. Helps map precise research landscapes.
        
    Examples:
        - search_openalex_topics("machine learning", 5)
        - search_openalex_topics("renewable energy", 10)
        - search_openalex_topics("neuroscience", 3)
    """
    start_time = time.time()
    args = {'topic_name': topic_name, 'max_results': max_results}
    
    logger.info(f"MCP Tool called: search_openalex_topics", **args)
    
    try:
        results = topic_retriever.search_topics(
            name=topic_name,
            max_results=max_results
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_topics", duration,
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_topics", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_topics", duration, error=True)
        logger.log_mcp_call("search_openalex_topics", args, error=str(e))
        logger.log_error(e, "search_openalex_topics")
        return []


# Add the new MCP tool functions for Institutions
def search_openalex_institutions(institution_name: str, max_results: int = 5, country_code: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for research institutions and universities in OpenAlex.
    
    This tool helps you find academic institutions, universities, and research 
    organizations. Use it to analyze research networks, map geographic research 
    distribution, or connect authors to their institutional affiliations.
    
    Args:
        institution_name: Name of the institution to search for.
                         Examples: "Harvard University", "Max Planck Institute", 
                         "Stanford", "MIT", "University of Tokyo"
        max_results: Number of institution results to return (1-20). Default is 5.
                    Higher values for broader institutional searches.
        country_code: Optional ISO 3166-1 alpha-2 country code to filter results.
                     Examples: "US", "GB", "DE", "JP", "CA"
    
    Returns:
        List of institution dictionaries containing display name, ROR identifier,
        country code, type, geographic location, associated institutions, 
        publication count, citation count, and research metrics.
        
    Examples:
        - search_openalex_institutions("Harvard", 3)
        - search_openalex_institutions("Max Planck", 5, "DE")
        - search_openalex_institutions("University of Tokyo", 3, "JP")
    """
    start_time = time.time()
    args = {'institution_name': institution_name, 'max_results': max_results, 'country_code': country_code}
    
    logger.info(f"MCP Tool called: search_openalex_institutions", **args)
    
    try:
        results = institution_retriever.search_institutions(
            name=institution_name,
            max_results=max_results,
            country_code=country_code
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_institutions", duration,
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_institutions", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_institutions", duration, error=True)
        logger.log_mcp_call("search_openalex_institutions", args, error=str(e))
        logger.log_error(e, "search_openalex_institutions")
        return []


# Add the new MCP tool functions for Sources
def search_openalex_sources(source_name: str, max_results: int = 5, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for academic publication venues (journals, conferences, repositories) in OpenAlex.
    
    This tool helps you discover and analyze publication venues where research 
    is published. Use it to assess journal reputation, compare conference venues,
    or analyze publishing patterns and open access availability.
    
    Args:
        source_name: Name of the publication venue to search for.
                    Examples: "Nature", "Science", "NeurIPS", "arXiv", "The Lancet"
        max_results: Number of source results to return (1-20). Default is 5.
                    Higher values for broader venue searches.
        source_type: Optional source type filter. Valid values: "journal", "conference", 
                    "repository", "ebook platform"
    
    Returns:
        List of source dictionaries containing display name, ISSN, type, publisher,
        homepage URL, publication count, citation count, impact metrics, and 
        open access information.
        
    Examples:
        - search_openalex_sources("Nature", 3)
        - search_openalex_sources("NeurIPS", 5, "conference")
        - search_openalex_sources("arXiv", 3, "repository")
    """
    start_time = time.time()
    args = {'source_name': source_name, 'max_results': max_results, 'source_type': source_type}
    
    logger.info(f"MCP Tool called: search_openalex_sources", **args)
    
    try:
        results = source_retriever.search_sources(
            name=source_name,
            max_results=max_results,
            source_type=source_type
        )
        
        duration = time.time() - start_time
        logger.log_performance("search_openalex_sources", duration,
                              results_count=len(results) if results else 0)
        
        logger.log_mcp_call("search_openalex_sources", args, {
            'success': True,
            'results_count': len(results) if results else 0,
            'response_length': len(results) if results else 0
        })
        
        return results or []
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("search_openalex_sources", duration, error=True)
        logger.log_mcp_call("search_openalex_sources", args, error=str(e))
        logger.log_error(e, "search_openalex_sources")
        return []


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


# Wrapper functions for Gradio UI (convert structured data to formatted strings)
def search_papers_ui(search_query: str, max_results: int = 3, start_year: Optional[int] = None, end_year: Optional[int] = None) -> str:
    """UI wrapper for search_openalex_papers that returns formatted string."""
    try:
        results = search_openalex_papers(search_query, max_results, start_year, end_year)
        return format_paper_results(results)
    except Exception as e:
        return f"Error searching papers: {str(e)}"

def get_paper_by_doi_ui(doi: str) -> str:
    """UI wrapper for get_publication_by_doi that returns formatted string."""
    try:
        result = get_publication_by_doi(doi)
        if result:
            return format_paper_results([result])
        else:
            return f"No publication found for DOI: {doi}"
    except Exception as e:
        return f"Error retrieving publication: {str(e)}"

def search_authors_ui(author_name: str, max_results: int = 5) -> str:
    """UI wrapper for search_openalex_authors that returns formatted string."""
    try:
        results = search_openalex_authors(author_name, max_results)
        return format_author_results(results)
    except Exception as e:
        return f"Error searching authors: {str(e)}"

def search_concepts_ui(concept_name: str, max_results: int = 5) -> str:
    """UI wrapper for search_openalex_concepts that returns formatted string."""
    try:
        results = search_openalex_concepts(concept_name, max_results)
        return format_concept_results(results)
    except Exception as e:
        return f"Error searching concepts: {str(e)}"


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
                search_papers_ui,
                inputs=[query_input, max_results_input, start_year_input, end_year_input],
                outputs=papers_output
            )
        
        with gr.Tab("Get Paper by DOI"):
            doi_input = gr.Textbox(label="DOI", placeholder="Enter DOI (e.g., 10.1038/s41586-021-03358-0)")
            doi_button = gr.Button("Get Paper")
            doi_output = gr.Textbox(label="Paper Details", lines=10)
            
            doi_button.click(
                get_paper_by_doi_ui,
                inputs=doi_input,
                outputs=doi_output
            )
        
        with gr.Tab("Search Authors"):
            author_input = gr.Textbox(label="Author Name", placeholder="Enter author name...")
            author_max_input = gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            author_button = gr.Button("Search Authors")
            authors_output = gr.Textbox(label="Authors", lines=10)
            
            author_button.click(
                search_authors_ui,
                inputs=[author_input, author_max_input],
                outputs=authors_output
            )
        
        with gr.Tab("Search Concepts"):
            concept_input = gr.Textbox(label="Concept Name", placeholder="Enter concept/field name...")
            concept_max_input = gr.Number(label="Max Results", value=5, minimum=1, maximum=20)
            concept_button = gr.Button("Search Concepts")
            concepts_output = gr.Textbox(label="Concepts", lines=10)
            
            concept_button.click(
                search_concepts_ui,
                inputs=[concept_input, concept_max_input],
                outputs=concepts_output
            )
        
        gr.Markdown("## 🔗 MCP Server Information")
        gr.Markdown("""
        This app serves as a **Model Context Protocol (MCP) server** for academic research tools.
        
        ### 🚀 Quick Start
        **Local Endpoint**: `http://127.0.0.1:7860/gradio_api/mcp/sse`  
        **Schema Endpoint**: `http://127.0.0.1:7860/gradio_api/mcp/schema`
        
        ### 🛠️ Available MCP Tools
        1. **search_openalex_papers** - Search academic papers with optional year filtering
        2. **get_publication_by_doi** - Retrieve specific publications by DOI  
        3. **search_openalex_authors** - Find researchers and authors by name
        4. **search_openalex_concepts** - Explore research topics and fields of study
        5. **search_openalex_topics** - Explore academic research topics (improved replacement for concepts)
        6. **search_openalex_institutions** - Find research institutions and universities
        7. **search_openalex_sources** - Discover publication venues (journals, conferences)
        
        ### ⚙️ Claude Desktop Configuration
        Add this to your Claude Desktop MCP settings:
        ```json
        {
          "mcpServers": {
            "openalex-explorer": {
              "command": "npx",
              "args": ["mcp-remote", "http://127.0.0.1:7860/gradio_api/mcp/sse"]
            }
          }
        }
        ```
        
        ### 🔧 Cursor/Cline Configuration  
        Add this to your MCP client settings:
        ```json
        {
          "mcpServers": {
            "openalex-explorer": {
              "url": "http://127.0.0.1:7860/gradio_api/mcp/sse"
            }
          }
        }
        ```
        
        ### 📊 Usage Examples
        - *"Search for recent papers on machine learning"*
        - *"Find authors working on climate change research"* 
        - *"Get publication details for DOI 10.1038/nature12373"*
        - *"Explore concepts related to artificial intelligence"*
        - *"Find research topics in machine learning"*
        - *"Search for institutions in Germany"*
        - *"Find journals related to artificial intelligence"*
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
        
        # Log launch details with MCP configuration
        launch_config = {
            'server_name': "0.0.0.0",
            'server_port': 7860,
            'share': False,
            'mcp_server': True,
            'mcp_endpoint': "http://0.0.0.0:7860/gradio_api/mcp/sse",
            'mcp_schema': "http://0.0.0.0:7860/gradio_api/mcp/schema"
        }
        logger.info("Launching Gradio application with MCP server enabled", **launch_config)
        
        app.launch(
            server_name="0.0.0.0", 
            server_port=7860, 
            share=False,
            mcp_server=True  # Enable MCP server functionality
        )
        
    except Exception as e:
        logger.log_error(e, "Application launch")
        raise
