"""
OpenAlex Author Retriever

Handles searching and retrieving author data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import extract_openalex_id

logger = logging.getLogger(__name__)


class OpenAlexAuthorRetriever:
    """Retrieves and processes author data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the author retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_authors(
        self,
        name: str,
        max_results: int = 10,
        affiliation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for authors in OpenAlex by name.
        
        Args:
            name: Author name to search for
            max_results: Maximum number of results to return
            affiliation: Optional affiliation filter
        
        Returns:
            List of processed author dictionaries
        """
        try:
            # Build search query
            query = name
            if affiliation:
                query += f" {affiliation}"
            
            # Search for authors
            response = self.api_client.search_authors(
                query=query,
                per_page=min(max_results, 50)  # API limit
            )
            
            authors = response.get('results', [])
            processed_authors = []
            
            for author in authors[:max_results]:
                processed_author = self._process_author_data(author)
                if processed_author:
                    processed_authors.append(processed_author)
            
            logger.info(f"Retrieved {len(processed_authors)} authors for query: {name}")
            return processed_authors
            
        except Exception as e:
            logger.error(f"Error searching authors: {e}")
            raise
    
    def get_by_orcid(self, orcid: str) -> Optional[Dict[str, Any]]:
        """
        Get an author by their ORCID.
        
        Args:
            orcid: ORCID identifier
        
        Returns:
            Processed author data or None if not found
        """
        try:
            # Clean ORCID format
            clean_orcid = orcid.replace('https://orcid.org/', '').replace('orcid:', '')
            
            # Search by ORCID
            response = self.api_client.search_authors(
                query=f"orcid:{clean_orcid}",
                per_page=1
            )
            
            authors = response.get('results', [])
            if authors:
                return self._process_author_data(authors[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving author by ORCID {orcid}: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an author by their OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed author data or None if not found
        """
        try:
            # Use filter to get specific author
            response = self.api_client.search_authors(
                query="",  # Empty query since we're filtering by ID
                per_page=1
            )
            
            # For this simplified implementation, we'll use the search endpoint
            # In a full implementation, you'd use a dedicated get endpoint
            authors = response.get('results', [])
            if authors:
                return self._process_author_data(authors[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving author by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def _process_author_data(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex author data into a standardized format.
        
        Args:
            author_data: Raw author data from OpenAlex API
        
        Returns:
            Processed author data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(author_data.get('id', '')),
                'display_name': author_data.get('display_name', 'Unknown Author'),
                'orcid': author_data.get('orcid'),
                'works_count': author_data.get('works_count', 0),
                'cited_by_count': author_data.get('cited_by_count', 0),
                'i10_index': author_data.get('summary_stats', {}).get('i10_index', 0),
                'h_index': author_data.get('summary_stats', {}).get('h_index', 0)
            }
            
            # Last known institution
            last_known_institution = author_data.get('last_known_institution')
            if last_known_institution:
                processed['affiliation'] = {
                    'display_name': last_known_institution.get('display_name'),
                    'country_code': last_known_institution.get('country_code'),
                    'type': last_known_institution.get('type'),
                    'openalex_id': extract_openalex_id(last_known_institution.get('id', ''))
                }
            else:
                processed['affiliation'] = None
            
            # Alternative names/aliases
            processed['alternative_names'] = author_data.get('display_name_alternatives', [])
            
            # Research areas (from concepts)
            concepts = author_data.get('x_concepts', [])[:10]  # Top 10 concepts
            processed['research_areas'] = []
            for concept in concepts:
                processed['research_areas'].append({
                    'display_name': concept.get('display_name'),
                    'level': concept.get('level'),
                    'score': concept.get('score'),
                    'openalex_id': extract_openalex_id(concept.get('id', ''))
                })
            
            # Works by year (publication timeline)
            counts_by_year = author_data.get('counts_by_year', [])
            processed['works_by_year'] = {}
            processed['citations_by_year'] = {}
            
            for year_data in counts_by_year:
                year = year_data.get('year')
                if year:
                    processed['works_by_year'][year] = year_data.get('works_count', 0)
                    processed['citations_by_year'][year] = year_data.get('cited_by_count', 0)
            
            # Calculate metrics
            processed['metrics'] = self._calculate_author_metrics(author_data)
            
            # First and most recent publication years
            if counts_by_year:
                years = [item.get('year') for item in counts_by_year if item.get('year')]
                if years:
                    processed['first_publication_year'] = min(years)
                    processed['most_recent_publication_year'] = max(years)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing author data: {e}")
            return {
                'display_name': author_data.get('display_name', 'Error processing author'),
                'openalex_id': extract_openalex_id(author_data.get('id', '')),
                'error': str(e)
            }
    
    def _calculate_author_metrics(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional metrics for the author.
        
        Args:
            author_data: Raw author data from OpenAlex
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        works_count = author_data.get('works_count', 0)
        cited_by_count = author_data.get('cited_by_count', 0)
        
        # Citations per work
        if works_count > 0:
            metrics['citations_per_work'] = round(cited_by_count / works_count, 2)
        else:
            metrics['citations_per_work'] = 0
        
        # Calculate career span
        counts_by_year = author_data.get('counts_by_year', [])
        if counts_by_year:
            years = [item.get('year') for item in counts_by_year if item.get('year') and item.get('works_count', 0) > 0]
            if years:
                metrics['career_span'] = max(years) - min(years) + 1
                metrics['publications_per_year'] = round(works_count / metrics['career_span'], 2) if metrics['career_span'] > 0 else 0
        
        # Recent activity (last 5 years)
        recent_years = [item for item in counts_by_year if item.get('year', 0) >= 2020]
        metrics['recent_works_count'] = sum(item.get('works_count', 0) for item in recent_years)
        metrics['recent_citations_count'] = sum(item.get('cited_by_count', 0) for item in recent_years)
        
        return metrics
