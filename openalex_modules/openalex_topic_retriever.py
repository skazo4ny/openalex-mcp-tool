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
        domain: Optional[str] = None,
        field: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for topics in OpenAlex by name.
        
        Args:
            name: Topic name to search for
            max_results: Maximum number of results to return
            domain: Optional domain filter
            field: Optional field filter
        
        Returns:
            List of processed topic dictionaries
        """
        try:
            # Build filters
            filters = {}
            
            if domain:
                filters['domain.id'] = domain
            if field:
                filters['field.id'] = field
            
            # Search for topics
            response = self.api_client.search_topics(
                query=name,
                filters=filters,
                per_page=min(max_results, 50)  # API limit
            )
            
            if not response:
                return []
            
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
            topic_data = self.api_client.get_topic_by_id(openalex_id)
            
            if topic_data:
                return self._process_topic_data(topic_data)
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
                'works_count': topic_data.get('works_count', 0),
                'cited_by_count': topic_data.get('cited_by_count', 0),
                'subfield_count': topic_data.get('subfield_count', 0),
                'created_date': topic_data.get('created_date')
            }
            
            # Topic hierarchy
            domain = topic_data.get('domain', {})
            field = topic_data.get('field', {})
            subfield = topic_data.get('subfield', {})
            
            processed['domain'] = {
                'openalex_id': extract_openalex_id(domain.get('id', '')),
                'display_name': domain.get('display_name')
            } if domain else None
            
            processed['field'] = {
                'openalex_id': extract_openalex_id(field.get('id', '')),
                'display_name': field.get('display_name')
            } if field else None
            
            processed['subfield'] = {
                'openalex_id': extract_openalex_id(subfield.get('id', '')),
                'display_name': subfield.get('display_name')
            } if subfield else None
            
            # Keywords
            keywords = topic_data.get('keywords', [])
            processed['keywords'] = keywords
            
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
            
            # International information
            international = topic_data.get('international', {})
            processed['international_names'] = {}
            for lang_code, info in international.items():
                if isinstance(info, dict) and 'display_name' in info:
                    processed['international_names'][lang_code] = info['display_name']
            
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
        
        return metrics