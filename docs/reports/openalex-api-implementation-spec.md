# OpenAlex API Implementation Specification

## Overview

This document provides technical specifications for implementing the missing OpenAlex API capabilities in the MCP server. It details the required API client methods, retriever classes, and MCP tools for each missing entity.

## 1. Topics Implementation

### 1.1 API Client Methods
Add to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py):

```python
def search_topics(self, query: str, filters: Optional[Dict[str, Any]] = None,
                  per_page: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
    """
    Search for topics in OpenAlex.
    
    Args:
        query: Search query string
        filters: Additional filters to apply
        per_page: Number of results per page
        page: Page number
    
    Returns:
        Search results from OpenAlex
    """
    params = {
        'search': query,
        'page': page,
        'per-page': min(per_page or self.default_per_page, self.max_per_page)
    }
    
    # Add filters
    if filters:
        filter_strings = []
        for key, value in filters.items():
            if isinstance(value, list):
                filter_strings.append(f"{key}:{'+'.join(map(str, value))}")
            else:
                filter_strings.append(f"{key}:{value}")
        
        if filter_strings:
            params['filter'] = ','.join(filter_strings)
    
    return self._make_request('/topics', params)
```

### 1.2 Topic Retriever Class
Create [openalex_modules/openalex_topic_retriever.py](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules/openalex_topic_retriever.py):

```python
"""
OpenAlex Topic Retriever

Handles searching and retrieving topic data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import extract_openalex_id

logger = logging.getLogger(__name__)


class OpenAlexTopicRetriever:
    """Retrieves and processes topic data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the topic retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_topics(
        self,
        name: str,
        max_results: int = 10,
        subfield: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for topics in OpenAlex by name.
        
        Args:
            name: Topic name to search for
            max_results: Maximum number of results to return
            subfield: Optional subfield filter
        
        Returns:
            List of processed topic dictionaries
        """
        try:
            # Search for topics
            response = self.api_client.search_topics(
                query=name,
                per_page=min(max_results, 50)  # API limit
            )
            
            topics = response.get('results', [])
            processed_topics = []
            
            for topic in topics[:max_results]:
                processed_topic = self._process_topic_data(topic)
                if processed_topic:
                    processed_topics.append(processed_topic)
            
            logger.info(f"Retrieved {len(processed_topics)} topics for query: {name}")
            return processed_topics
            
        except Exception as e:
            logger.error(f"Error searching topics: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a topic by its OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed topic data or None if not found
        """
        try:
            # Use filter to get specific topic by ID
            response = self.api_client.search_topics(
                query="",  # Empty query since we're filtering by ID
                filters={'openalex_id': openalex_id},
                per_page=1
            )
            
            topics = response.get('results', [])
            if topics:
                return self._process_topic_data(topics[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving topic by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def _process_topic_data(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex topic data into a standardized format.
        
        Args:
            topic_data: Raw topic data from OpenAlex API
        
        Returns:
            Processed topic data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(topic_data.get('id', '')),
                'display_name': topic_data.get('display_name', 'Unknown Topic'),
                'description': topic_data.get('description'),
                'subfield': topic_data.get('subfield', {}).get('display_name'),
                'field': topic_data.get('field', {}).get('display_name'),
                'domain': topic_data.get('domain', {}).get('display_name'),
                'works_count': topic_data.get('works_count', 0),
                'cited_by_count': topic_data.get('cited_by_count', 0),
                'updated_date': topic_data.get('updated_date')
            }
            
            # Keywords
            processed['keywords'] = topic_data.get('keywords', [])
            
            # Works by year
            counts_by_year = topic_data.get('counts_by_year', [])
            processed['works_by_year'] = {}
            processed['citations_by_year'] = {}
            
            for year_data in counts_by_year:
                year = year_data.get('year')
                if year:
                    processed['works_by_year'][year] = year_data.get('works_count', 0)
                    processed['citations_by_year'][year] = year_data.get('cited_by_count', 0)
            
            # Calculate metrics
            processed['metrics'] = self._calculate_topic_metrics(topic_data)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing topic data: {e}")
            return {
                'display_name': topic_data.get('display_name', 'Error processing topic'),
                'openalex_id': extract_openalex_id(topic_data.get('id', '')),
                'error': str(e)
            }
    
    def _calculate_topic_metrics(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional metrics for the topic.
        
        Args:
            topic_data: Raw topic data from OpenAlex
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        works_count = topic_data.get('works_count', 0)
        cited_by_count = topic_data.get('cited_by_count', 0)
        
        # Citations per work
        if works_count > 0:
            metrics['citations_per_work'] = round(cited_by_count / works_count, 2)
        else:
            metrics['citations_per_work'] = 0
        
        # Recent activity (last 5 years)
        counts_by_year = topic_data.get('counts_by_year', [])
        recent_years = [item for item in counts_by_year if item.get('year', 0) >= 2020]
        metrics['recent_works_count'] = sum(item.get('works_count', 0) for item in recent_years)
        metrics['recent_citations_count'] = sum(item.get('cited_by_count', 0) for item in recent_years)
        
        return metrics
```

### 1.3 MCP Tool Functions
Add to [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) and [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py):

```python
def search_openalex_topics(topic_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Explore academic topics in OpenAlex.
    
    This tool helps you discover and understand research topics, which are the 
    improved system replacing concepts in OpenAlex. Use it to explore research 
    areas, understand topic hierarchies, or find related fields of study.
    
    Args:
        topic_name: Name of the research topic to search for.
                   Examples: "artificial intelligence", "molecular biology", 
                   "climate science", "quantum mechanics", "public health"
        max_results: Number of topic results to return (1-20). Default is 5.
                    Higher values show related and broader/narrower topics.
    
    Returns:
        List of topic dictionaries containing display name, description,
        field, domain, work count, citation count, and keywords.
        
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
```

## 2. Institutions Implementation

### 2.1 API Client Methods
Add to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py):

```python
def search_institutions(self, query: str, filters: Optional[Dict[str, Any]] = None,
                       per_page: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
    """
    Search for institutions in OpenAlex.
    
    Args:
        query: Search query string
        filters: Additional filters to apply
        per_page: Number of results per page
        page: Page number
    
    Returns:
        Search results from OpenAlex
    """
    params = {
        'search': query,
        'page': page,
        'per-page': min(per_page or self.default_per_page, self.max_per_page)
    }
    
    # Add filters
    if filters:
        filter_strings = []
        for key, value in filters.items():
            if isinstance(value, list):
                filter_strings.append(f"{key}:{'+'.join(map(str, value))}")
            else:
                filter_strings.append(f"{key}:{value}")
        
        if filter_strings:
            params['filter'] = ','.join(filter_strings)
    
    return self._make_request('/institutions', params)
```

### 2.2 Institution Retriever Class
Create [openalex_modules/openalex_institution_retriever.py](file:///Users/max/Documents/code/openalex-mcp-tool/openalex_modules/openalex_institution_retriever.py):

```python
"""
OpenAlex Institution Retriever

Handles searching and retrieving institution data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import extract_openalex_id

logger = logging.getLogger(__name__)


class OpenAlexInstitutionRetriever:
    """Retrieves and processes institution data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the institution retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_institutions(
        self,
        name: str,
        max_results: int = 10,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for institutions in OpenAlex by name.
        
        Args:
            name: Institution name to search for
            max_results: Maximum number of results to return
            country_code: Optional country code filter (e.g., 'US', 'GB')
        
        Returns:
            List of processed institution dictionaries
        """
        try:
            # Build filters
            filters = {}
            if country_code:
                filters['country_code'] = country_code
            
            # Search for institutions
            response = self.api_client.search_institutions(
                query=name,
                filters=filters if filters else None,
                per_page=min(max_results, 50)  # API limit
            )
            
            institutions = response.get('results', [])
            processed_institutions = []
            
            for institution in institutions[:max_results]:
                processed_institution = self._process_institution_data(institution)
                if processed_institution:
                    processed_institutions.append(processed_institution)
            
            logger.info(f"Retrieved {len(processed_institutions)} institutions for query: {name}")
            return processed_institutions
            
        except Exception as e:
            logger.error(f"Error searching institutions: {e}")
            raise
    
    def get_by_ror_id(self, ror_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an institution by their ROR ID.
        
        Args:
            ror_id: ROR identifier
        
        Returns:
            Processed institution data or None if not found
        """
        try:
            # Clean ROR ID format
            clean_ror = ror_id.replace('https://ror.org/', '').replace('ror:', '')
            
            # Search by ROR ID
            response = self.api_client.search_institutions(
                query=f"ror:{clean_ror}",
                per_page=1
            )
            
            institutions = response.get('results', [])
            if institutions:
                return self._process_institution_data(institutions[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving institution by ROR ID {ror_id}: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an institution by their OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed institution data or None if not found
        """
        try:
            # Use filter to get specific institution by ID
            response = self.api_client.search_institutions(
                query="",  # Empty query since we're filtering by ID
                filters={'openalex_id': openalex_id},
                per_page=1
            )
            
            institutions = response.get('results', [])
            if institutions:
                return self._process_institution_data(institutions[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving institution by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def _process_institution_data(self, institution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex institution data into a standardized format.
        
        Args:
            institution_data: Raw institution data from OpenAlex API
        
        Returns:
            Processed institution data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(institution_data.get('id', '')),
                'display_name': institution_data.get('display_name', 'Unknown Institution'),
                'ror': institution_data.get('ror'),
                'country_code': institution_data.get('country_code'),
                'type': institution_data.get('type'),
                'works_count': institution_data.get('works_count', 0),
                'cited_by_count': institution_data.get('cited_by_count', 0),
                'homepage_url': institution_data.get('homepage_url')
            }
            
            # Geo information
            geo = institution_data.get('geo', {})
            processed['geo'] = {
                'city': geo.get('city'),
                'region': geo.get('region'),
                'country': geo.get('country'),
                'latitude': geo.get('latitude'),
                'longitude': geo.get('longitude')
            }
            
            # Image URL if available
            processed['image_url'] = institution_data.get('image_url')
            processed['image_thumbnail_url'] = institution_data.get('image_thumbnail_url')
            
            # Associated institutions
            associated_institutions = institution_data.get('associated_institutions', [])
            processed['associated_institutions'] = []
            for associated in associated_institutions:
                processed['associated_institutions'].append({
                    'openalex_id': extract_openalex_id(associated.get('id', '')),
                    'display_name': associated.get('display_name'),
                    'relationship': associated.get('relationship')
                })
            
            # Works by year
            counts_by_year = institution_data.get('counts_by_year', [])
            processed['works_by_year'] = {}
            processed['citations_by_year'] = {}
            
            for year_data in counts_by_year:
                year = year_data.get('year')
                if year:
                    processed['works_by_year'][year] = year_data.get('works_count', 0)
                    processed['citations_by_year'][year] = year_data.get('cited_by_count', 0)
            
            # Calculate metrics
            processed['metrics'] = self._calculate_institution_metrics(institution_data)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing institution data: {e}")
            return {
                'display_name': institution_data.get('display_name', 'Error processing institution'),
                'openalex_id': extract_openalex_id(institution_data.get('id', '')),
                'error': str(e)
            }
    
    def _calculate_institution_metrics(self, institution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional metrics for the institution.
        
        Args:
            institution_data: Raw institution data from OpenAlex
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        works_count = institution_data.get('works_count', 0)
        cited_by_count = institution_data.get('cited_by_count', 0)
        
        # Citations per work
        if works_count > 0:
            metrics['citations_per_work'] = round(cited_by_count / works_count, 2)
        else:
            metrics['citations_per_work'] = 0
        
        # Recent activity (last 5 years)
        counts_by_year = institution_data.get('counts_by_year', [])
        recent_years = [item for item in counts_by_year if item.get('year', 0) >= 2020]
        metrics['recent_works_count'] = sum(item.get('works_count', 0) for item in recent_years)
        metrics['recent_citations_count'] = sum(item.get('cited_by_count', 0) for item in recent_years)
        
        return metrics
```

### 2.3 MCP Tool Functions
Add to [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) and [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py):

```python
def search_openalex_institutions(institution_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for academic institutions in the OpenAlex database.
    
    This tool helps you find universities and research institutions by name.
    Use it to discover institutions, their locations, research output, and 
    affiliated researchers.
    
    Args:
        institution_name: Full or partial name of the institution to search for.
                         Examples: "MIT", "University of Cambridge", "Max Planck",
                         "Stanford University", "Tsinghua University"
        max_results: Number of institution profiles to return (1-20). Default is 5.
                    Use higher values when searching common institution names.
    
    Returns:
        List of institution dictionaries containing display name, ROR identifier,
        country, type, research output count, citation count, and geographic information.
        
    Examples:
        - search_openalex_institutions("MIT", 3)
        - search_openalex_institutions("University of Cambridge", 5)
        - search_openalex_institutions("Max Planck", 10)
    """
    start_time = time.time()
    args = {'institution_name': institution_name, 'max_results': max_results}
    
    logger.info(f"MCP Tool called: search_openalex_institutions", **args)
    
    try:
        results = institution_retriever.search_institutions(
            name=institution_name,
            max_results=max_results
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
```

## 3. Advanced Filtering Implementation

### 3.1 Enhanced Search Methods
Enhance existing search methods in retriever classes to support advanced filtering:

```python
def search_publications(
    self,
    query: str,
    max_results: int = 10,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    sort_by: str = "relevance",
    filter_params: Optional[Dict[str, Any]] = None  # New parameter
) -> List[Dict[str, Any]]:
    """
    Search for publications in OpenAlex with advanced filtering.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        start_year: Start year for publication date filter
        end_year: End year for publication date filter
        sort_by: Sort order ('relevance', 'cited_by_count', 'publication_date')
        filter_params: Additional OpenAlex filters (e.g., {'is_oa': True, 'type': 'article'})
    
    Returns:
        List of processed publication dictionaries
    """
    try:
        # Build filters
        filters = {}
        
        if start_year and end_year:
            filters['publication_year'] = f"{start_year}-{end_year}"
        elif start_year:
            filters['publication_year'] = f">={start_year}"
        elif end_year:
            filters['publication_year'] = f"<={end_year}"
        
        # Add custom filters
        if filter_params:
            filters.update(filter_params)
        
        # Search for works
        response = self.api_client.search_works(
            query=query,
            filters=filters,
            per_page=min(max_results, 50)  # API limit
        )
        
        works = response.get('results', [])
        processed_works = []
        
        for work in works[:max_results]:
            processed_work = self._process_work_data(work)
            if processed_work:
                processed_works.append(processed_work)
        
        logger.info(f"Retrieved {len(processed_works)} publications for query: {query}")
        return processed_works
        
    except Exception as e:
        logger.error(f"Error searching publications: {e}")
        raise
```

## 4. Grouping Implementation

### 4.1 API Client Method
Add to [slr_modules/api_clients.py](file:///Users/max/Documents/code/openalex-mcp-tool/slr_modules/api_clients.py):

```python
def group_works(self, group_by: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Group works by a specific attribute.
    
    Args:
        group_by: Attribute to group by (e.g., 'type', 'publication_year', 'open_access')
        filters: Additional filters to apply
    
    Returns:
        Grouped results from OpenAlex
    """
    params = {
        'group_by': group_by
    }
    
    # Add filters
    if filters:
        filter_strings = []
        for key, value in filters.items():
            if isinstance(value, list):
                filter_strings.append(f"{key}:{'+'.join(map(str, value))}")
            else:
                filter_strings.append(f"{key}:{value}")
        
        if filter_strings:
            params['filter'] = ','.join(filter_strings)
    
    return self._make_request('/works', params)
```

### 4.2 MCP Tool Function
Add to [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) and [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py):

```python
def group_openalex_works(group_by: str, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Group academic works by specific attributes to analyze research trends.
    
    This tool allows you to group publications by various criteria to understand
    research patterns, trends, and distributions. Use it for statistical analysis
    of research data.
    
    Args:
        group_by: Attribute to group by. Options include:
                 - 'type' (article, book, etc.)
                 - 'publication_year' (research over time)
                 - 'open_access' (OA vs non-OA distribution)
                 - 'authorships.institutions.country_code' (by country)
        filter_query: Optional search query to filter works before grouping
                     Examples: "machine learning", "climate change", "2020-2024"
    
    Returns:
        List of groups with their counts and display names.
        
    Examples:
        - group_openalex_works("type")
        - group_openalex_works("publication_year", "artificial intelligence")
        - group_openalex_works("open_access")
    """
    start_time = time.time()
    args = {'group_by': group_by, 'filter_query': filter_query}
    
    logger.info(f"MCP Tool called: group_openalex_works", **args)
    
    try:
        # Build filters
        filters = {}
        if filter_query:
            # For grouping, we might want to apply the query as a search filter
            pass  # The grouping will be done on all works or with additional filters
        
        # Group works
        response = publication_retriever.group_works(
            group_by=group_by,
            filters=filters if filters else None
        )
        
        # Extract group data
        groups = response.get('group_by', [])
        processed_groups = []
        
        for group in groups:
            processed_group = {
                'key': group.get('key'),
                'display_name': group.get('key_display_name'),
                'count': group.get('count')
            }
            processed_groups.append(processed_group)
        
        duration = time.time() - start_time
        logger.log_performance("group_openalex_works", duration,
                              groups_count=len(processed_groups))
        
        logger.log_mcp_call("group_openalex_works", args, {
            'success': True,
            'groups_count': len(processed_groups),
            'response_length': len(processed_groups)
        })
        
        return processed_groups
        
    except Exception as e:
        duration = time.time() - start_time
        logger.log_performance("group_openalex_works", duration, error=True)
        logger.log_mcp_call("group_openalex_works", args, error=str(e))
        logger.log_error(e, "group_openalex_works")
        return []
```

## 5. Required Updates to Main Application Files

### 5.1 Update [app.py](file:///Users/max/Documents/code/openalex-mcp-tool/app.py) Initialization
Add new retriever instances:

```python
# Initialize retrievers
logger.info("Initializing data retrievers")
publication_retriever = OpenAlexPublicationRetriever(api_client)
author_retriever = OpenAlexAuthorRetriever(api_client)
concept_retriever = OpenAlexConceptRetriever(api_client)
topic_retriever = OpenAlexTopicRetriever(api_client)  # New
institution_retriever = OpenAlexInstitutionRetriever(api_client)  # New
```

### 5.2 Update [mcp_server.py](file:///Users/max/Documents/code/openalex-mcp-tool/mcp_server.py) Initialization
Add new retriever instances:

```python
# Initialize retrievers
publication_retriever = OpenAlexPublicationRetriever(api_client)
author_retriever = OpenAlexAuthorRetriever(api_client)
concept_retriever = OpenAlexConceptRetriever(api_client)
topic_retriever = OpenAlexTopicRetriever(api_client)  # New
institution_retriever = OpenAlexInstitutionRetriever(api_client)  # New
```

## 6. Testing Considerations

### 6.1 Unit Tests
Create unit tests for new retriever classes:
- [tests/unit/test_topic_retriever.py](file:///Users/max/Documents/code/openalex-mcp-tool/tests/unit/test_topic_retriever.py)
- [tests/unit/test_institution_retriever.py](file:///Users/max/Documents/code/openalex-mcp-tool/tests/unit/test_institution_retriever.py)

### 6.2 Integration Tests
Update integration tests to include new MCP tools:
- [tests/integration/test_mcp_tools_fixed.py](file:///Users/max/Documents/code/openalex-mcp-tool/tests/integration/test_mcp_tools_fixed.py)

## 7. Documentation Updates

### 7.1 Update README.md
Add new tools to the documentation:
- Update tool list
- Add usage examples
- Update MCP client configuration examples

### 7.2 Update API Documentation
Update [docs/api.md](file:///Users/max/Documents/code/openalex-mcp-tool/docs/api.md) with new tool specifications.

## Conclusion

This specification provides a comprehensive roadmap for implementing the missing OpenAlex API capabilities in the MCP server. By following this plan, the OpenAlex Explorer can become a more powerful research tool for AI agents, providing access to the full range of OpenAlex data and advanced analytical capabilities.