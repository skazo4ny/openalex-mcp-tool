"""
OpenAlex Utilities

Utility functions for processing OpenAlex data.
"""

import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def reconstruct_abstract_from_inverted_index(abstract_inverted_index: Dict[str, List[int]]) -> str:
    """
    Reconstruct full abstract text from OpenAlex's inverted index format.
    
    Args:
        abstract_inverted_index: Dictionary mapping words to their positions
    
    Returns:
        Reconstructed abstract text
    """
    if not abstract_inverted_index:
        return ""
    
    try:
        # Create a list to hold words at their positions
        max_position = max(max(positions) for positions in abstract_inverted_index.values())
        words = [''] * (max_position + 1)
        
        # Place each word at its correct positions
        for word, positions in abstract_inverted_index.items():
            for position in positions:
                words[position] = word
        
        # Join words and clean up
        abstract = ' '.join(word for word in words if word)
        return abstract.strip()
        
    except Exception as e:
        logger.error(f"Error reconstructing abstract: {e}")
        return ""


def clean_doi(doi: str) -> str:
    """
    Clean and normalize DOI format.
    
    Args:
        doi: DOI string in various formats
    
    Returns:
        Cleaned DOI
    """
    if not doi:
        return ""
    
    # Remove common prefixes
    doi = doi.replace('https://doi.org/', '')
    doi = doi.replace('http://doi.org/', '')
    doi = doi.replace('doi:', '')
    
    return doi.strip()


def extract_openalex_id(openalex_url: str) -> str:
    """
    Extract OpenAlex ID from URL.
    
    Args:
        openalex_url: OpenAlex URL (e.g., 'https://openalex.org/W2741809807')
    
    Returns:
        OpenAlex ID (e.g., 'W2741809807')
    """
    if not openalex_url:
        return ""
    
    # Extract ID from URL
    match = re.search(r'/([A-Z]\d+)/?$', openalex_url)
    return match.group(1) if match else openalex_url


def format_author_name(author_data: Dict[str, Any]) -> str:
    """
    Format author name from OpenAlex author data.
    
    Args:
        author_data: Author data dictionary
    
    Returns:
        Formatted author name
    """
    display_name = author_data.get('display_name', '')
    if display_name:
        return display_name
    
    # Fallback to constructing from first/last name if available
    first_name = author_data.get('first_name', '')
    last_name = author_data.get('last_name', '')
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif last_name:
        return last_name
    elif first_name:
        return first_name
    
    return "Unknown Author"


def extract_keywords_from_concepts(concepts: List[Dict[str, Any]], max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from OpenAlex concepts.
    
    Args:
        concepts: List of concept dictionaries
        max_keywords: Maximum number of keywords to return
    
    Returns:
        List of keyword strings
    """
    keywords = []
    
    for concept in concepts[:max_keywords]:
        display_name = concept.get('display_name', '')
        if display_name:
            keywords.append(display_name)
    
    return keywords


def get_publication_venue(work_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract publication venue information from work data.
    
    Args:
        work_data: OpenAlex work data
    
    Returns:
        Dictionary with venue information
    """
    venue_info = {
        'name': None,
        'type': None,
        'issn': None,
        'is_oa': None
    }
    
    # Check primary location first
    primary_location = work_data.get('primary_location', {})
    if primary_location:
        source = primary_location.get('source', {})
        if source:
            venue_info['name'] = source.get('display_name')
            venue_info['type'] = source.get('type')
            venue_info['issn'] = source.get('issn_l')
            venue_info['is_oa'] = source.get('is_oa')
    
    # Fallback to best OA location
    if not venue_info['name']:
        best_oa_location = work_data.get('best_oa_location', {})
        if best_oa_location:
            source = best_oa_location.get('source', {})
            if source:
                venue_info['name'] = source.get('display_name')
                venue_info['type'] = source.get('type')
    
    return venue_info


def calculate_citation_percentile(cited_by_count: int, publication_year: int, current_year: int = None) -> Optional[float]:
    """
    Calculate a rough citation percentile based on citation count and age.
    This is a simplified calculation for demonstration purposes.
    
    Args:
        cited_by_count: Number of citations
        publication_year: Year of publication
        current_year: Current year (defaults to 2025)
    
    Returns:
        Estimated citation percentile (0-100) or None
    """
    if current_year is None:
        current_year = 2025
    
    if not publication_year or publication_year > current_year:
        return None
    
    paper_age = current_year - publication_year
    
    # Very rough estimation based on typical academic citation patterns
    # This is simplified and not scientifically rigorous
    if paper_age == 0:
        if cited_by_count >= 10:
            return 95.0
        elif cited_by_count >= 5:
            return 85.0
        elif cited_by_count >= 2:
            return 70.0
        elif cited_by_count >= 1:
            return 50.0
        else:
            return 25.0
    
    # For older papers, adjust expectations
    citations_per_year = cited_by_count / max(paper_age, 1)
    
    if citations_per_year >= 20:
        return 99.0
    elif citations_per_year >= 10:
        return 95.0
    elif citations_per_year >= 5:
        return 85.0
    elif citations_per_year >= 2:
        return 70.0
    elif citations_per_year >= 1:
        return 50.0
    elif citations_per_year >= 0.5:
        return 30.0
    else:
        return 10.0
