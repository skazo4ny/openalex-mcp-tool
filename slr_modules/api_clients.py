"""
API Clients

Contains the OpenAlexAPIClient for interacting with the OpenAlex API.
Adapted from tsi-sota-ai repository.
"""

import requests
import time
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlencode

logger = logging.getLogger(__name__)


class OpenAlexAPIClient:
    """Client for interacting with the OpenAlex API."""
    
    def __init__(self, config_manager):
        """
        Initialize the OpenAlex API client.
        
        Args:
            config_manager: ConfigManager instance for configuration
        """
        self.config_manager = config_manager
        self.base_url = config_manager.get('openalex.base_url', 'https://api.openalex.org')
        self.timeout = config_manager.get('openalex.timeout', 30)
        self.retries = config_manager.get('openalex.retries', 3)
        self.default_per_page = config_manager.get('openalex.default_per_page', 25)
        self.max_per_page = config_manager.get('openalex.max_per_page', 200)
        
        # Set up session with headers
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self):
        """Set up HTTP headers for API requests."""
        headers = {
            'User-Agent': 'OpenAlex-Explorer/1.0.0',
            'Accept': 'application/json'
        }
        
        # Add email to User-Agent for polite requests
        email = self.config_manager.get_openalex_email()
        if email:
            headers['User-Agent'] += f' (mailto:{email})'
        
        self.session.headers.update(headers)
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the OpenAlex API with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., '/works', '/authors')
            params: Query parameters
        
        Returns:
            JSON response data
        
        Raises:
            requests.RequestException: If request fails after retries
        """
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        if params:
            # Clean up None values
            params = {k: v for k, v in params.items() if v is not None}
        
        for attempt in range(self.retries + 1):
            try:
                logger.debug(f"Making request to {url} with params: {params}")
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retries:
                    logger.error(f"Request failed after {self.retries + 1} attempts: {e}")
                    raise
                else:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
    
    def search_works(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                    per_page: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
        """
        Search for works (publications) in OpenAlex.
        
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
                    # Handle year range filters properly
                    if key == 'publication_year' and len(value) == 2:
                        # Convert ['>=2020', '<=2024'] to year range format
                        start_val = value[0].replace('>=', '') if value[0].startswith('>=') else value[0]
                        end_val = value[1].replace('<=', '') if value[1].startswith('<=') else value[1]
                        filter_strings.append(f"{key}:{start_val}-{end_val}")
                    else:
                        # Use + for OR within same key (OpenAlex format)
                        filter_strings.append(f"{key}:{'+'.join(map(str, value))}")
                else:
                    filter_strings.append(f"{key}:{value}")
            
            if filter_strings:
                params['filter'] = ','.join(filter_strings)
        
        return self._make_request('/works', params)
    
    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific work by its DOI.
        
        Args:
            doi: Digital Object Identifier
        
        Returns:
            Work data or None if not found
        """
        try:
            # Ensure DOI has proper format
            if not doi.startswith('https://doi.org/'):
                if doi.startswith('doi:'):
                    doi = doi[4:]
                doi = f"https://doi.org/{doi}"
            
            response = self._make_request(f'/works/{doi}')
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Work with DOI {doi} not found")
                return None
            raise
    
    def search_authors(self, query: str, filters: Optional[Dict[str, Any]] = None,
                      per_page: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
        """
        Search for authors in OpenAlex.
        
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
        
        return self._make_request('/authors', params)
    
    def search_concepts(self, query: str, filters: Optional[Dict[str, Any]] = None,
                       per_page: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
        """
        Search for concepts in OpenAlex.
        
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
        
        return self._make_request('/concepts', params)
    
    def get_multiple_works(self, openalex_ids: List[str]) -> Dict[str, Any]:
        """
        Get multiple works by their OpenAlex IDs.
        
        Args:
            openalex_ids: List of OpenAlex IDs
        
        Returns:
            Works data
        """
        params = {
            'filter': f"openalex_id:{'|'.join(openalex_ids)}"
        }
        
        return self._make_request('/works', params)
