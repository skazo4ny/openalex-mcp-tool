# OpenAlex API Comprehensive Usage Guidelines

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication & Rate Limits](#authentication--rate-limits)
3. [Entity Types](#entity-types)
4. [Search & Filtering](#search--filtering)
5. [Pagination](#pagination)
6. [Date Handling](#date-handling)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)
9. [Error Handling](#error-handling)

## API Overview

The OpenAlex API provides access to scholarly metadata including works, authors, institutions, sources, topics, publishers, funders, and concepts. All endpoints are RESTful and return JSON responses.

**Base URL**: `https://api.openalex.org`

### Key Principles
- **Open Access**: No API key required, but email recommended for higher rate limits
- **RESTful Design**: Standard HTTP methods and status codes
- **Standardized IDs**: Uses OpenAlex IDs, DOIs, ORCIDs, RORs, etc.
- **Comprehensive Coverage**: 200M+ works, 90M+ authors, 100K+ institutions

## Authentication & Rate Limits

### Email Parameter
While not required, providing your email increases rate limits:
```
https://api.openalex.org/works?mailto=your-email@example.com
```

### Rate Limits
- **Without email**: 10 requests per second
- **With email**: 100 requests per second
- **Burst limits**: Up to 1000 requests in short bursts

### Implementation
```python
# Always include email in API client configuration
client = OpenAlexAPIClient(email="your-email@example.com")
```

## Entity Types

### 1. Works (`/works`)
Publications, papers, books, datasets, software, etc.

**Key Fields:**
- `id`: OpenAlex ID (W123456789)
- `doi`: Digital Object Identifier
- `title`: Work title
- `publication_year`: Year published
- `cited_by_count`: Citation count
- `authorships`: Author information with affiliations
- `primary_location`: Primary publication venue
- `open_access`: Open access status and URLs

### 2. Authors (`/authors`)
Individual researchers and creators.

**Key Fields:**
- `id`: OpenAlex ID (A123456789)
- `orcid`: ORCID identifier
- `display_name`: Author's name
- `works_count`: Number of works
- `cited_by_count`: Total citations
- `affiliations`: Current affiliations

### 3. Sources (`/sources`)
Journals, conferences, repositories, etc.

**Key Fields:**
- `id`: OpenAlex ID (S123456789)
- `issn_l`: Linking ISSN
- `display_name`: Source name
- `type`: journal, conference, repository, etc.
- `works_count`: Number of works published

### 4. Institutions (`/institutions`)
Universities, companies, research organizations.

**Key Fields:**
- `id`: OpenAlex ID (I123456789)
- `ror`: Research Organization Registry ID
- `display_name`: Institution name
- `country_code`: ISO country code
- `type`: education, healthcare, company, etc.

### 5. Topics (`/topics`)
Research areas and subjects.

**Key Fields:**
- `id`: OpenAlex ID (T123456789)
- `display_name`: Topic name
- `description`: Topic description
- `keywords`: Related keywords
- `works_count`: Number of related works

## Search & Filtering

### Basic Search
```python
# Simple text search
works = client.search_works(query="machine learning")

# Search specific fields
works = client.search_works(query="title.search:neural networks")
```

### Filter Syntax

#### Single Filters
```python
# Publication year
filters = {"publication_year": "2023"}

# Citation count range
filters = {"cited_by_count": ">100"}

# Multiple values (OR logic)
filters = {"publication_year": "2022|2023|2024"}
```

#### Date Ranges
**CRITICAL**: Use proper OpenAlex date range syntax:
```python
# Correct format for year ranges
filters = {"publication_year": "2020-2024"}

# NOT this format (common error):
filters = {"publication_year": [">=2020", "<=2024"]}  # WRONG
```

#### Complex Filters
```python
# Institution filter
filters = {
    "authorships.institutions.id": "I27837315",  # Stanford
    "publication_year": "2020-2024",
    "cited_by_count": ">10"
}

# Open access filter
filters = {
    "open_access.is_oa": "true",
    "type": "article"
}
```

#### Boolean Logic
```python
# AND logic (default)
filters = {
    "publication_year": "2023",
    "open_access.is_oa": "true"
}

# OR logic within same field
filters = {"publication_year": "2022|2023|2024"}

# NOT logic
filters = {"publication_year": "!2020"}
```

### Advanced Search Operators

#### Text Search Operators
- `title.search:machine learning` - Search in title
- `abstract.search:neural networks` - Search in abstract
- `fulltext.search:deep learning` - Search in full text
- `raw_affiliation_string.search:stanford` - Search affiliations

#### Wildcards and Exact Matches
```python
# Wildcard search
query = "title.search:machine*"

# Exact phrase
query = 'title.search:"machine learning"'

# Case-insensitive by default
query = "title.search:MACHINE"  # Same as "machine"
```

## Pagination

### Cursor-Based Pagination (Recommended)
```python
def get_all_results(client, **kwargs):
    all_results = []
    cursor = "*"
    
    while cursor:
        response = client.search_works(cursor=cursor, per_page=200, **kwargs)
        results = response.get("results", [])
        all_results.extend(results)
        
        # Get next cursor
        meta = response.get("meta", {})
        cursor = meta.get("next_cursor")
        
        if not cursor or len(results) < 200:
            break
    
    return all_results
```

### Page-Based Pagination
```python
# Not recommended for large datasets
response = client.search_works(page=1, per_page=100)
```

### Performance Tips
- **Use cursor pagination** for large datasets
- **Limit per_page** to 200 (maximum)
- **Sort consistently** when using pagination
- **Cache results** when possible

## Date Handling

### Publication Dates

#### Year-only Filters
```python
# Single year
filters = {"publication_year": "2023"}

# Year range
filters = {"publication_year": "2020-2023"}

# Before/after specific year
filters = {"publication_year": "<2020"}
filters = {"publication_year": ">2020"}
```

#### Exact Date Filters
```python
# Specific date
filters = {"publication_date": "2023-01-15"}

# Date range
filters = {"publication_date": "2023-01-01-2023-12-31"}
```

### Common Date Patterns
```python
# Last 5 years
current_year = datetime.now().year
filters = {"publication_year": f"{current_year-5}-{current_year}"}

# Decade filter
filters = {"publication_year": "2010-2019"}

# Recent publications
filters = {"publication_date": ">2023-01-01"}
```

## Best Practices

### 1. Email Configuration
Always configure your email for better rate limits:
```python
config = {
    "openalex": {
        "email": "your-email@example.com",
        "rate_limit": 100
    }
}
```

### 2. Efficient Filtering
- **Filter early**: Apply restrictive filters first
- **Use specific fields**: Target exact fields rather than general search
- **Combine filters**: Use multiple filters to narrow results

### 3. Result Processing
```python
# Select only needed fields
select_fields = "id,title,publication_year,cited_by_count"
response = client.search_works(select=select_fields)

# Group and count results
group_by = "publication_year"
response = client.search_works(group_by=group_by)
```

### 4. Error Handling
```python
try:
    results = client.search_works(query="machine learning")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limit exceeded
        time.sleep(1)
        results = client.search_works(query="machine learning")
    else:
        raise
```

## Common Patterns

### 1. Author Publication Analysis
```python
def analyze_author_publications(author_id, start_year=2020):
    filters = {
        "authorships.author.id": author_id,
        "publication_year": f"{start_year}-{datetime.now().year}"
    }
    
    works = client.search_works(
        filters=filters,
        sort="publication_year:desc",
        select="id,title,publication_year,cited_by_count"
    )
    
    return works
```

### 2. Institution Collaboration Analysis
```python
def find_collaborations(institution_id, min_citations=10):
    filters = {
        "authorships.institutions.id": institution_id,
        "cited_by_count": f">{min_citations}",
        "authorships.institutions.id": f"!{institution_id}"  # External collaborators
    }
    
    return client.search_works(filters=filters)
```

### 3. Topic Trend Analysis
```python
def analyze_topic_trends(topic_keywords, years_range="2020-2024"):
    results = {}
    
    for keyword in topic_keywords:
        filters = {
            "title.search": keyword,
            "publication_year": years_range
        }
        
        response = client.search_works(
            filters=filters,
            group_by="publication_year"
        )
        
        results[keyword] = response.get("group_by", [])
    
    return results
```

### 4. Open Access Analysis
```python
def analyze_open_access(institution_id, year=2023):
    base_filters = {
        "authorships.institutions.id": institution_id,
        "publication_year": str(year)
    }
    
    # Total works
    total_response = client.search_works(filters=base_filters)
    total_count = total_response.get("meta", {}).get("count", 0)
    
    # Open access works
    oa_filters = {**base_filters, "open_access.is_oa": "true"}
    oa_response = client.search_works(filters=oa_filters)
    oa_count = oa_response.get("meta", {}).get("count", 0)
    
    return {
        "total_works": total_count,
        "open_access_works": oa_count,
        "oa_percentage": (oa_count / total_count * 100) if total_count > 0 else 0
    }
```

## Error Handling

### Common HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **403**: Forbidden (rate limit exceeded)
- **404**: Not Found
- **500**: Internal Server Error

### Robust Error Handling
```python
import time
import requests
from typing import Dict, Any, Optional

class OpenAlexAPIClient:
    def __init__(self, email: str, max_retries: int = 3):
        self.email = email
        self.max_retries = max_retries
        self.base_url = "https://api.openalex.org"
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params["mailto"] = self.email
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
                continue
        
        raise Exception(f"Failed to fetch data after {self.max_retries} attempts")
```

### Validation Helpers
```python
def validate_year_range(year_range: str) -> bool:
    """Validate year range format: YYYY-YYYY or YYYY"""
    if "-" in year_range:
        try:
            start, end = year_range.split("-")
            return (len(start) == 4 and len(end) == 4 and 
                   start.isdigit() and end.isdigit() and
                   int(start) <= int(end))
        except ValueError:
            return False
    else:
        return len(year_range) == 4 and year_range.isdigit()

def validate_openalex_id(entity_id: str, entity_type: str) -> bool:
    """Validate OpenAlex ID format"""
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
```

## Performance Optimization

### 1. Selective Field Retrieval
```python
# Only get essential fields
essential_fields = "id,title,publication_year,cited_by_count"
response = client.search_works(select=essential_fields)
```

### 2. Efficient Sorting
```python
# Sort by indexed fields for better performance
response = client.search_works(sort="cited_by_count:desc")
response = client.search_works(sort="publication_year:desc")
```

### 3. Caching Strategy
```python
import functools
import time

@functools.lru_cache(maxsize=128)
def cached_search(query_str: str, filters_str: str) -> Dict[str, Any]:
    """Cache search results for repeated queries"""
    # Convert string parameters back to proper formats
    # Implementation depends on your caching needs
    pass
```

This comprehensive guide covers all essential aspects of working with the OpenAlex API effectively and avoiding common pitfalls.
