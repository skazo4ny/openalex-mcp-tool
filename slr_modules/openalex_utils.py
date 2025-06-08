"""
OpenAlex API Utilities

Utility functions for validating and formatting OpenAlex API requests.
"""

import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime


def validate_year_range(year_range: str) -> bool:
    """
    Validate year range format for OpenAlex API.
    
    Args:
        year_range: Year range string in format 'YYYY-YYYY' or 'YYYY'
        
    Returns:
        True if valid, False otherwise
    """
    if not year_range:
        return False
        
    if "-" in year_range:
        try:
            start, end = year_range.split("-", 1)
            return (len(start) == 4 and len(end) == 4 and 
                   start.isdigit() and end.isdigit() and
                   1950 <= int(start) <= int(end) <= 2030)
        except ValueError:
            return False
    else:
        return (len(year_range) == 4 and year_range.isdigit() and
               1950 <= int(year_range) <= 2030)


def validate_openalex_id(entity_id: str, entity_type: str) -> bool:
    """
    Validate OpenAlex ID format.
    
    Args:
        entity_id: The OpenAlex ID to validate
        entity_type: Type of entity (work, author, source, institution, topic, publisher, funder)
        
    Returns:
        True if valid, False otherwise
    """
    prefixes = {
        "work": "W",
        "author": "A", 
        "source": "S",
        "institution": "I",
        "topic": "T",
        "publisher": "P",
        "funder": "F"
    }
    
    expected_prefix = prefixes.get(entity_type.lower())
    if not expected_prefix:
        return False
    
    return (entity_id.startswith(expected_prefix) and 
            len(entity_id) > 1 and 
            entity_id[1:].isdigit())


def validate_doi(doi: str) -> bool:
    """
    Validate DOI format.
    
    Args:
        doi: DOI string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not doi:
        return False
        
    # Remove https://doi.org/ prefix if present
    if doi.startswith("https://doi.org/"):
        doi = doi[16:]
    elif doi.startswith("doi:"):
        doi = doi[4:]
    
    # Basic DOI pattern: 10.xxxx/yyyy
    pattern = r'^10\.\d{4,}[\/\.].*'
    return bool(re.match(pattern, doi))


def format_date_filter(start_year: Optional[int] = None, end_year: Optional[int] = None) -> Optional[str]:
    """
    Format date filter for OpenAlex API.
    
    Args:
        start_year: Starting year for filter
        end_year: Ending year for filter
        
    Returns:
        Formatted date filter string or None
    """
    current_year = datetime.now().year
    
    # Validate years
    if start_year and (start_year < 1950 or start_year > 2030):
        raise ValueError(f"Start year must be between 1950 and 2030, got {start_year}")
    if end_year and (end_year < 1950 or end_year > 2030):
        raise ValueError(f"End year must be between 1950 and 2030, got {end_year}")
    if start_year and end_year and start_year > end_year:
        raise ValueError(f"Start year ({start_year}) cannot be greater than end year ({end_year})")
    
    if start_year and end_year:
        return f"{start_year}-{end_year}"
    elif start_year:
        return f">={start_year}"
    elif end_year:
        return f"<={end_year}"
    else:
        return None


def normalize_filter_value(value: Union[str, int, List]) -> str:
    """
    Normalize filter values for OpenAlex API.
    
    Args:
        value: Filter value to normalize
        
    Returns:
        Normalized string value
    """
    if isinstance(value, list):
        return "|".join(map(str, value))
    return str(value)


def build_openalex_filters(filters: Dict[str, Any]) -> Dict[str, str]:
    """
    Build and validate OpenAlex API filters.
    
    Args:
        filters: Dictionary of filter key-value pairs
        
    Returns:
        Validated and normalized filters dictionary
        
    Raises:
        ValueError: If filters are invalid
    """
    validated_filters = {}
    
    for key, value in filters.items():
        if value is None:
            continue
            
        # Special handling for year filters
        if key == 'publication_year':
            if isinstance(value, list) and len(value) == 2:
                # Handle legacy format ['>=2020', '<=2024']
                start_val = value[0].replace('>=', '').strip() if isinstance(value[0], str) and value[0].startswith('>=') else str(value[0]).strip()
                end_val = value[1].replace('<=', '').strip() if isinstance(value[1], str) and value[1].startswith('<=') else str(value[1]).strip()
                try:
                    start_year = int(start_val)
                    end_year = int(end_val)
                    validated_filters[key] = format_date_filter(start_year, end_year)
                except ValueError as e:
                    raise ValueError(f"Invalid year range format: {value}") from e
            elif isinstance(value, str):
                if not validate_year_range(value):
                    raise ValueError(f"Invalid year range format: {value}")
                validated_filters[key] = value
            else:
                validated_filters[key] = str(value)
        else:
            validated_filters[key] = normalize_filter_value(value)
    
    return {k: v for k, v in validated_filters.items() if v is not None}


def get_search_suggestions(query: str) -> List[str]:
    """
    Get search suggestions for improving query results.
    
    Args:
        query: The search query
        
    Returns:
        List of suggested improvements
    """
    suggestions = []
    
    if len(query) < 3:
        suggestions.append("Use at least 3 characters for better search results")
    
    if query.isupper():
        suggestions.append("Consider using mixed case instead of all caps")
    
    if not any(char.isalpha() for char in query):
        suggestions.append("Include some letters in your search query")
    
    # Check for common search operators
    if '"' not in query and ' ' in query:
        suggestions.append(f'Try using quotes for exact phrases: "{query}"')
    
    if not any(op in query for op in ['title:', 'abstract:', 'author:']):
        suggestions.append("Use field-specific searches like 'title:keyword' or 'author:name'")
    
    return suggestions


def estimate_api_cost(num_requests: int, has_email: bool = True) -> Dict[str, Any]:
    """
    Estimate API usage and rate limits.
    
    Args:
        num_requests: Number of API requests planned
        has_email: Whether email is configured for higher rate limits
        
    Returns:
        Dictionary with cost estimation details
    """
    rate_limit = 100 if has_email else 10  # requests per second
    
    estimated_time = num_requests / rate_limit
    
    return {
        "num_requests": num_requests,
        "rate_limit_per_second": rate_limit,
        "estimated_time_seconds": estimated_time,
        "estimated_time_minutes": estimated_time / 60,
        "recommendation": "Configure email for higher rate limits" if not has_email and num_requests > 50 else "Rate limit sufficient"
    }


def format_search_error(error: Exception, query: str, filters: Dict[str, Any] = None) -> str:
    """
    Format search error messages in a user-friendly way.
    
    Args:
        error: The exception that occurred
        query: The search query that failed
        filters: The filters that were applied
        
    Returns:
        User-friendly error message
    """
    error_msg = str(error).lower()
    
    if "timeout" in error_msg:
        return f"Search request timed out. Try simplifying your query: '{query}'"
    elif "rate limit" in error_msg or "429" in error_msg:
        return "API rate limit exceeded. Please wait a moment and try again."
    elif "400" in error_msg or "bad request" in error_msg:
        return f"Invalid search parameters. Check your query: '{query}' and filters: {filters}"
    elif "404" in error_msg:
        return "OpenAlex API endpoint not found. This may be a temporary issue."
    elif "500" in error_msg or "503" in error_msg:
        return "OpenAlex API is temporarily unavailable. Please try again later."
    else:
        return f"Search failed: {error}. Query: '{query}'"


# Common filter presets for convenience
FILTER_PRESETS = {
    "recent_papers": {
        "publication_year": f"{datetime.now().year - 2}-{datetime.now().year}",
        "type": "article"
    },
    "highly_cited": {
        "cited_by_count": ">100",
        "type": "article"
    },
    "open_access": {
        "open_access.is_oa": "true",
        "type": "article"
    },
    "last_decade": {
        "publication_year": f"{datetime.now().year - 10}-{datetime.now().year}"
    },
    "peer_reviewed": {
        "type": "article",
        "primary_location.source.type": "journal"
    }
}
