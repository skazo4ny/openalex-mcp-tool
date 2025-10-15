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
        country_code: Optional[str] = None,
        institution_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for institutions in OpenAlex by name.
        
        Args:
            name: Institution name to search for
            max_results: Maximum number of results to return
            country_code: Optional country code filter (ISO 3166-1 alpha-2)
            institution_type: Optional institution type filter (e.g., 'education', 'healthcare')
        
        Returns:
            List of processed institution dictionaries
        """
        try:
            # Build filters
            filters = {}
            
            if country_code:
                filters['country_code'] = country_code.upper()
            if institution_type:
                filters['type'] = institution_type
            
            # Search for institutions
            response = self.api_client.search_institutions(
                query=name,
                filters=filters,
                per_page=min(max_results, 50)  # API limit
            )
            
            if not response:
                return []
            
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
        Get an institution by its ROR ID.
        
        Args:
            ror_id: ROR identifier
        
        Returns:
            Processed institution data or None if not found
        """
        try:
            # Clean ROR ID format
            clean_ror_id = ror_id.replace('https://ror.org/', '').replace('ror:', '')
            
            institution_data = self.api_client.get_institution_by_ror(clean_ror_id)
            
            if institution_data:
                return self._process_institution_data(institution_data)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving institution by ROR ID {ror_id}: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an institution by its OpenAlex ID.
        
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
            
            if not response:
                return None
                
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
            
            # Location information
            geo = institution_data.get('geo', {})
            processed['geo'] = {
                'city': geo.get('city'),
                'region': geo.get('region'),
                'country': geo.get('country'),
                'latitude': geo.get('latitude'),
                'longitude': geo.get('longitude')
            } if geo else None
            
            # Associated institutions
            associated_institutions = institution_data.get('associated_institutions', [])
            processed['associated_institutions'] = []
            for associated in associated_institutions:
                processed['associated_institutions'].append({
                    'openalex_id': extract_openalex_id(associated.get('id', '')),
                    'display_name': associated.get('display_name'),
                    'relationship': associated.get('relationship')
                })
            
            # Image URLs
            processed['image_url'] = institution_data.get('image_url')
            processed['image_thumbnail_url'] = institution_data.get('image_thumbnail_url')
            
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
            
            # International information
            international = institution_data.get('international', {})
            processed['international_names'] = {}
            for lang_code, info in international.items():
                if isinstance(info, dict) and 'display_name' in info:
                    processed['international_names'][lang_code] = info['display_name']
            
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