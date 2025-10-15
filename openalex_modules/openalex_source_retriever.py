"""
OpenAlex Source Retriever

Handles searching and retrieving source (journal, conference, etc.) data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import extract_openalex_id

logger = logging.getLogger(__name__)


class OpenAlexSourceRetriever:
    """Retrieves and processes source data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the source retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_sources(
        self,
        name: str,
        max_results: int = 10,
        source_type: Optional[str] = None,
        publisher: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for sources in OpenAlex by name.
        
        Args:
            name: Source name to search for
            max_results: Maximum number of results to return
            source_type: Optional source type filter (e.g., 'journal', 'conference', 'repository')
            publisher: Optional publisher filter
        
        Returns:
            List of processed source dictionaries
        """
        try:
            # Build filters
            filters = {}
            
            if source_type:
                filters['type'] = source_type
            if publisher:
                filters['publisher'] = publisher
            
            # Search for sources
            response = self.api_client.search_sources(
                query=name,
                filters=filters,
                per_page=min(max_results, 50)  # API limit
            )
            
            if not response:
                return []
            
            sources = response.get('results', [])
            processed_sources = []
            
            for source in sources[:max_results]:
                processed_source = self._process_source_data(source)
                if processed_source:
                    processed_sources.append(processed_source)
            
            logger.info(f"Retrieved {len(processed_sources)} sources for query: {name}")
            return processed_sources
            
        except Exception as e:
            logger.error(f"Error searching sources: {e}")
            raise
    
    def get_by_issn(self, issn: str) -> Optional[Dict[str, Any]]:
        """
        Get a source by its ISSN.
        
        Args:
            issn: ISSN identifier
        
        Returns:
            Processed source data or None if not found
        """
        try:
            source_data = self.api_client.get_source_by_issn(issn)
            
            if source_data:
                return self._process_source_data(source_data)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving source by ISSN {issn}: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a source by its OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed source data or None if not found
        """
        try:
            # Use filter to get specific source by ID
            response = self.api_client.search_sources(
                query="",  # Empty query since we're filtering by ID
                filters={'openalex_id': openalex_id},
                per_page=1
            )
            
            if not response:
                return None
                
            sources = response.get('results', [])
            if sources:
                return self._process_source_data(sources[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving source by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def _process_source_data(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex source data into a standardized format.
        
        Args:
            source_data: Raw source data from OpenAlex API
        
        Returns:
            Processed source data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(source_data.get('id', '')),
                'display_name': source_data.get('display_name', 'Unknown Source'),
                'issn_l': source_data.get('issn_l'),
                'type': source_data.get('type'),
                'publisher': source_data.get('publisher'),
                'works_count': source_data.get('works_count', 0),
                'cited_by_count': source_data.get('cited_by_count', 0),
                'homepage_url': source_data.get('homepage_url'),
                'is_in_doaj': source_data.get('is_in_doaj', False),
                'is_oa': source_data.get('is_oa', False)
            }
            
            # ISSN information
            issns = source_data.get('issn', [])
            processed['issns'] = issns
            
            # Host organization
            host_organization = source_data.get('host_organization')
            processed['host_organization'] = {
                'openalex_id': extract_openalex_id(host_organization),
                'name': source_data.get('host_organization_name')
            } if host_organization else None
            
            # Works by year
            counts_by_year = source_data.get('counts_by_year', [])
            processed['works_by_year'] = {}
            processed['citations_by_year'] = {}
            
            for year_data in counts_by_year:
                year = year_data.get('year')
                if year:
                    processed['works_by_year'][year] = year_data.get('works_count', 0)
                    processed['citations_by_year'][year] = year_data.get('cited_by_count', 0)
            
            # Calculate metrics
            processed['metrics'] = self._calculate_source_metrics(source_data)
            
            # International information
            international = source_data.get('international', {})
            processed['international_names'] = {}
            for lang_code, info in international.items():
                if isinstance(info, dict) and 'display_name' in info:
                    processed['international_names'][lang_code] = info['display_name']
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing source data: {e}")
            return {
                'display_name': source_data.get('display_name', 'Error processing source'),
                'openalex_id': extract_openalex_id(source_data.get('id', '')),
                'error': str(e)
            }
    
    def _calculate_source_metrics(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional metrics for the source.
        
        Args:
            source_data: Raw source data from OpenAlex
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        works_count = source_data.get('works_count', 0)
        cited_by_count = source_data.get('cited_by_count', 0)
        
        # Citations per work
        if works_count > 0:
            metrics['citations_per_work'] = round(cited_by_count / works_count, 2)
        else:
            metrics['citations_per_work'] = 0
        
        # Recent activity (last 5 years)
        counts_by_year = source_data.get('counts_by_year', [])
        recent_years = [item for item in counts_by_year if item.get('year', 0) >= 2020]
        metrics['recent_works_count'] = sum(item.get('works_count', 0) for item in recent_years)
        metrics['recent_citations_count'] = sum(item.get('cited_by_count', 0) for item in recent_years)
        
        # Growth trend (comparing last 3 years to previous 3 years)
        if len(counts_by_year) >= 6:
            recent_3_years = [item for item in counts_by_year if item.get('year', 0) >= 2022]
            previous_3_years = [item for item in counts_by_year if 2019 <= item.get('year', 0) <= 2021]
            
            recent_avg = sum(item.get('works_count', 0) for item in recent_3_years) / max(len(recent_3_years), 1)
            previous_avg = sum(item.get('works_count', 0) for item in previous_3_years) / max(len(previous_3_years), 1)
            
            if previous_avg > 0:
                metrics['growth_rate'] = round((recent_avg - previous_avg) / previous_avg * 100, 2)
            else:
                metrics['growth_rate'] = 0
        
        # Impact factor approximation (if available)
        summary_stats = source_data.get('summary_stats', {})
        if '2yr_mean_citedness' in summary_stats:
            metrics['impact_factor_approx'] = round(summary_stats['2yr_mean_citedness'], 2)
        
        return metrics