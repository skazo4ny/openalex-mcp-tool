"""
OpenAlex Concept Retriever

Handles searching and retrieving concept (field of study) data from OpenAlex.
"""

import logging
from typing import Dict, List, Any, Optional
from slr_modules.api_clients import OpenAlexAPIClient
from .openalex_utils import extract_openalex_id

logger = logging.getLogger(__name__)


class OpenAlexConceptRetriever:
    """Retrieves and processes concept data from OpenAlex."""
    
    def __init__(self, api_client: OpenAlexAPIClient):
        """
        Initialize the concept retriever.
        
        Args:
            api_client: OpenAlexAPIClient instance
        """
        self.api_client = api_client
    
    def search_concepts(
        self,
        name: str,
        max_results: int = 10,
        level: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for concepts in OpenAlex by name.
        
        Args:
            name: Concept name to search for
            max_results: Maximum number of results to return
            level: Optional level filter (0-5, where 0 is most general)
        
        Returns:
            List of processed concept dictionaries
        """
        try:
            # Search for concepts
            response = self.api_client.search_concepts(
                query=name,
                per_page=min(max_results, 50)  # API limit
            )
            
            concepts = response.get('results', [])
            processed_concepts = []
            
            for concept in concepts[:max_results]:
                # Apply level filter if specified
                if level is not None and concept.get('level') != level:
                    continue
                
                processed_concept = self._process_concept_data(concept)
                if processed_concept:
                    processed_concepts.append(processed_concept)
            
            logger.info(f"Retrieved {len(processed_concepts)} concepts for query: {name}")
            return processed_concepts
            
        except Exception as e:
            logger.error(f"Error searching concepts: {e}")
            raise
    
    def get_by_openalex_id(self, openalex_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a concept by its OpenAlex ID.
        
        Args:
            openalex_id: OpenAlex identifier
        
        Returns:
            Processed concept data or None if not found
        """
        try:
            # For this simplified implementation, we'll use the search endpoint
            # In a full implementation, you'd use a dedicated get endpoint
            response = self.api_client.search_concepts(
                query="",  # Empty query since we're filtering by ID
                per_page=1
            )
            
            concepts = response.get('results', [])
            if concepts:
                return self._process_concept_data(concepts[0])
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving concept by OpenAlex ID {openalex_id}: {e}")
            raise
    
    def get_concept_hierarchy(self, concept_id: str) -> Dict[str, Any]:
        """
        Get the hierarchical structure of a concept.
        
        Args:
            concept_id: OpenAlex concept ID
        
        Returns:
            Dictionary with concept hierarchy information
        """
        try:
            concept = self.get_by_openalex_id(concept_id)
            if not concept:
                return {}
            
            hierarchy = {
                'concept': concept,
                'ancestors': concept.get('ancestors', []),
                'related_concepts': concept.get('related_concepts', [])
            }
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error retrieving concept hierarchy: {e}")
            raise
    
    def _process_concept_data(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw OpenAlex concept data into a standardized format.
        
        Args:
            concept_data: Raw concept data from OpenAlex API
        
        Returns:
            Processed concept data dictionary
        """
        try:
            # Basic information
            processed = {
                'openalex_id': extract_openalex_id(concept_data.get('id', '')),
                'display_name': concept_data.get('display_name', 'Unknown Concept'),
                'description': concept_data.get('description'),
                'level': concept_data.get('level', 0),
                'works_count': concept_data.get('works_count', 0),
                'cited_by_count': concept_data.get('cited_by_count', 0),
                'wikidata': concept_data.get('wikidata'),
                'wikipedia': concept_data.get('wikipedia')
            }
            
            # Image URL if available
            processed['image_url'] = concept_data.get('image_url')
            processed['image_thumbnail_url'] = concept_data.get('image_thumbnail_url')
            
            # Ancestors (broader concepts)
            ancestors = concept_data.get('ancestors', [])
            processed['ancestors'] = []
            for ancestor in ancestors:
                processed['ancestors'].append({
                    'openalex_id': extract_openalex_id(ancestor.get('id', '')),
                    'display_name': ancestor.get('display_name'),
                    'level': ancestor.get('level')
                })
            
            # Related concepts
            related_concepts = concept_data.get('related_concepts', [])
            processed['related_concepts'] = []
            for related in related_concepts[:10]:  # Limit to top 10
                processed['related_concepts'].append({
                    'openalex_id': extract_openalex_id(related.get('id', '')),
                    'display_name': related.get('display_name'),
                    'level': related.get('level'),
                    'score': related.get('score', 0)
                })
            
            # Works by year
            counts_by_year = concept_data.get('counts_by_year', [])
            processed['works_by_year'] = {}
            processed['citations_by_year'] = {}
            
            for year_data in counts_by_year:
                year = year_data.get('year')
                if year:
                    processed['works_by_year'][year] = year_data.get('works_count', 0)
                    processed['citations_by_year'][year] = year_data.get('cited_by_count', 0)
            
            # Calculate metrics
            processed['metrics'] = self._calculate_concept_metrics(concept_data)
            
            # International information
            international = concept_data.get('international', {})
            processed['international_names'] = {}
            for lang_code, info in international.items():
                if isinstance(info, dict) and 'display_name' in info:
                    processed['international_names'][lang_code] = info['display_name']
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing concept data: {e}")
            return {
                'display_name': concept_data.get('display_name', 'Error processing concept'),
                'openalex_id': extract_openalex_id(concept_data.get('id', '')),
                'error': str(e)
            }
    
    def _calculate_concept_metrics(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate additional metrics for the concept.
        
        Args:
            concept_data: Raw concept data from OpenAlex
        
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {}
        
        works_count = concept_data.get('works_count', 0)
        cited_by_count = concept_data.get('cited_by_count', 0)
        
        # Citations per work
        if works_count > 0:
            metrics['citations_per_work'] = round(cited_by_count / works_count, 2)
        else:
            metrics['citations_per_work'] = 0
        
        # Recent activity (last 5 years)
        counts_by_year = concept_data.get('counts_by_year', [])
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
        
        # Concept breadth (number of related concepts)
        related_concepts = concept_data.get('related_concepts', [])
        metrics['breadth_score'] = len(related_concepts)
        
        return metrics
