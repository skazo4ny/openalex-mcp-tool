"""
OpenAlex Publication Retriever

Handles searching and retrieving publication data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import (
    reconstruct_abstract_from_inverted_index,
    clean_doi,
    extract_openalex_id,
    format_author_name,
    extract_keywords_from_concepts,
    get_publication_venue
)

logger = logging.getLogger(__name__)


class OpenAlexPublicationRetriever:
    """Retrieves and processes publication data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the publication retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_publications(
        self,
        query: str,
        max_results: int = 10,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search for publications in OpenAlex.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            start_year: Start year for publication date filter
            end_year: End year for publication date filter
            sort_by: Sort order ('relevance', 'cited_by_count', 'publication_date')
        
        Returns:
            List of processed publication dictionaries
        """
        try:
            # Build filters
            filters = {}
            
            if start_year and end_year:
                # Use proper OpenAlex year range format
                filters['publication_year'] = f"{start_year}-{end_year}"
            elif start_year:
                filters['publication_year'] = f">={start_year}"
            elif end_year:
                filters['publication_year'] = f"<={end_year}"
            
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
    
    def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get a publication by its DOI.
        
        Args:
            doi: Digital Object Identifier
        
        Returns:
            Processed publication data or None if not found
        """
        try:
            cleaned_doi = clean_doi(doi)
            work_data = self.api_client.get_work_by_doi(cleaned_doi)
            
            if work_data:
                return self._process_work_data(work_data)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving publication by DOI {doi}: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a publication by its OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed publication data or None if not found
        """
        try:
            response = self.api_client.get_multiple_works([openalex_id])
            works = response.get('results', [])
            
            if works:
                return self._process_work_data(works[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving publication by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def _process_work_data(self, work_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex work data into a standardized format.
        
        Args:
            work_data: Raw work data from OpenAlex API
        
        Returns:
            Processed work data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(work_data.get('id', '')),
                'title': work_data.get('title', 'No title available'),
                'doi': clean_doi(work_data.get('doi', '')),
                'publication_year': work_data.get('publication_year'),
                'publication_date': work_data.get('publication_date'),
                'type': work_data.get('type', 'article'),
                'cited_by_count': work_data.get('cited_by_count', 0),
                'is_retracted': work_data.get('is_retracted', False),
                'is_paratext': work_data.get('is_paratext', False)
            }
            
            # Abstract
            abstract_inverted = work_data.get('abstract_inverted_index', {})
            if abstract_inverted:
                processed['abstract'] = reconstruct_abstract_from_inverted_index(abstract_inverted)
            else:
                processed['abstract'] = 'No abstract available'
            
            # Authors
            authorships = work_data.get('authorships', [])
            processed['authors'] = []
            for authorship in authorships:
                author = authorship.get('author', {})
                processed_author = {
                    'display_name': format_author_name(author),
                    'orcid': author.get('orcid'),
                    'openalex_id': extract_openalex_id(author.get('id', '')),
                    'position': authorship.get('author_position', 'unknown')
                }
                
                # Add institutional affiliation
                institutions = authorship.get('institutions', [])
                if institutions:
                    processed_author['affiliation'] = {
                        'display_name': institutions[0].get('display_name'),
                        'country_code': institutions[0].get('country_code'),
                        'type': institutions[0].get('type')
                    }
                
                processed['authors'].append(processed_author)
            
            # Publication venue
            processed['venue'] = get_publication_venue(work_data)
            
            # Keywords from concepts
            concepts = work_data.get('concepts', [])
            processed['keywords'] = extract_keywords_from_concepts(concepts)
            processed['concepts'] = []
            for concept in concepts:
                processed['concepts'].append({
                    'display_name': concept.get('display_name'),
                    'level': concept.get('level'),
                    'score': concept.get('score'),
                    'openalex_id': extract_openalex_id(concept.get('id', ''))
                })
            
            # Open access information
            processed['open_access'] = {
                'is_oa': work_data.get('open_access', {}).get('is_oa', False),
                'oa_date': work_data.get('open_access', {}).get('oa_date'),
                'oa_url': work_data.get('open_access', {}).get('oa_url'),
                'any_repository_has_fulltext': work_data.get('open_access', {}).get('any_repository_has_fulltext', False)
            }
            
            # Add best OA location if available
            best_oa_location = work_data.get('best_oa_location')
            if best_oa_location:
                processed['open_access']['best_oa_url'] = best_oa_location.get('pdf_url') or best_oa_location.get('landing_page_url')
            
            # Referenced works count
            processed['referenced_works_count'] = len(work_data.get('referenced_works', []))
            
            # Related works count
            processed['related_works_count'] = len(work_data.get('related_works', []))
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing work data: {e}")
            return {
                'title': work_data.get('title', 'Error processing work'),
                'doi': clean_doi(work_data.get('doi', '')),
                'error': str(e)
            }
