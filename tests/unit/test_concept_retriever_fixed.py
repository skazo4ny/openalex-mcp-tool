"""
Unit tests for OpenAlexConceptRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_concept_retriever import OpenAlexConceptRetriever


class TestOpenAlexConceptRetriever:
    """Test OpenAlexConceptRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexConceptRetriever initialization."""
        retriever = OpenAlexConceptRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_concepts_basic(self, concept_retriever):
        """Test basic concept search."""
        mock_response = {
            'results': [
                {'id': 'https://openalex.org/C123', 'display_name': 'Machine Learning'},
                {'id': 'https://openalex.org/C456', 'display_name': 'Deep Learning'}
            ],
            'meta': {'count': 2}
        }
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            with patch.object(concept_retriever, '_process_concept_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = concept_retriever.search_concepts("machine learning", max_results=5)
                
                assert len(result) == 2
                mock_search.assert_called_once_with(
                    query="machine learning",
                    per_page=5
                )
                assert mock_process.call_count == 2
    
    def test_search_concepts_with_level_filter(self, concept_retriever):
        """Test concept search with level filter."""
        mock_response = {'results': [{'id': 'C123', 'display_name': 'Machine Learning'}], 'meta': {'count': 1}}
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            with patch.object(concept_retriever, '_process_concept_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = concept_retriever.search_concepts("machine learning", level=1)
                
                mock_search.assert_called_once_with(
                    query="machine learning",
                    per_page=10
                )
    
    def test_search_concepts_max_results_limit(self, concept_retriever):
        """Test concept search respects max_results limit."""
        large_response = {
            'results': [{'id': f'C{i}', 'display_name': f'Concept {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            with patch.object(concept_retriever, '_process_concept_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = concept_retriever.search_concepts("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_concepts_api_limit(self, concept_retriever):
        """Test concept search respects API per_page limit of 50."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            mock_search.return_value = mock_response
            
            result = concept_retriever.search_concepts("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                per_page=50  # Should be limited to 50
            )
    
    def test_search_concepts_error_handling(self, concept_retriever):
        """Test concept search error handling."""
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                concept_retriever.search_concepts("test")
    
    def test_get_by_openalex_id_success(self, concept_retriever, mock_concept_response):
        """Test getting concept by OpenAlex ID successfully."""
        mock_response = {'results': [mock_concept_response], 'meta': {'count': 1}}
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            with patch.object(concept_retriever, '_process_concept_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = concept_retriever.get_by_openalex_id("C123456789")
                
                assert result == {'processed': True}
                mock_search.assert_called_once_with(
                    query="",
                    filters={'openalex_id': 'C123456789'},
                    per_page=1
                )
    
    def test_get_by_openalex_id_not_found(self, concept_retriever):
        """Test getting concept by OpenAlex ID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            mock_search.return_value = mock_response
            
            result = concept_retriever.get_by_openalex_id("C123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, concept_retriever):
        """Test getting concept by OpenAlex ID error handling."""
        with patch.object(concept_retriever.api_client, 'search_concepts') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                concept_retriever.get_by_openalex_id("C123456789")
    
    def test_get_concept_hierarchy_success(self, concept_retriever):
        """Test getting concept hierarchy successfully."""
        mock_concept = {'id': 'C123', 'ancestors': [{'id': 'C456'}], 'related_concepts': [{'id': 'C789'}]}
        
        with patch.object(concept_retriever, 'get_by_openalex_id') as mock_get:
            mock_get.return_value = mock_concept
            
            result = concept_retriever.get_concept_hierarchy("C123456789")
            
            assert result['concept'] == mock_concept
            mock_get.assert_called_once_with("C123456789")
    
    def test_get_concept_hierarchy_not_found(self, concept_retriever):
        """Test getting concept hierarchy when concept not found."""
        with patch.object(concept_retriever, 'get_by_openalex_id') as mock_get:
            mock_get.return_value = None
            
            result = concept_retriever.get_concept_hierarchy("C123456789")
            
            assert result == {}
    
    def test_process_concept_data_complete(self, concept_retriever):
        """Test processing complete concept data."""
        concept_data = {
            'id': 'https://openalex.org/C2741809807',
            'display_name': 'Machine Learning',
            'description': 'A type of artificial intelligence',
            'level': 1,
            'works_count': 150000,
            'cited_by_count': 2500000,
            'wikidata': 'https://www.wikidata.org/wiki/Q2539',
            'ancestors': [
                {
                    'id': 'https://openalex.org/C123',
                    'display_name': 'Computer Science',
                    'level': 0
                }
            ],
            'related_concepts': [
                {
                    'id': 'https://openalex.org/C456',
                    'display_name': 'Deep Learning',
                    'level': 2,
                    'score': 0.95
                }
            ],
            'counts_by_year': [
                {'year': 2020, 'works_count': 5000, 'cited_by_count': 100000},
                {'year': 2021, 'works_count': 8000, 'cited_by_count': 150000},
                {'year': 2022, 'works_count': 12000, 'cited_by_count': 200000}
            ]
        }
        
        result = concept_retriever._process_concept_data(concept_data)
        
        assert result['openalex_id'] == 'C2741809807'
        assert result['display_name'] == 'Machine Learning'
        assert result['description'] == 'A type of artificial intelligence'
        assert result['level'] == 1
        assert result['works_count'] == 150000
        assert result['cited_by_count'] == 2500000
        assert result['wikidata'] == 'https://www.wikidata.org/wiki/Q2539'
        assert len(result['ancestors']) == 1
        assert result['ancestors'][0]['display_name'] == 'Computer Science'
        assert len(result['related_concepts']) == 1
        assert result['related_concepts'][0]['display_name'] == 'Deep Learning'
        assert result['works_by_year'][2020] == 5000
        assert result['citations_by_year'][2021] == 150000
    
    def test_process_concept_data_minimal(self, concept_retriever):
        """Test processing minimal concept data."""
        concept_data = {
            'id': 'https://openalex.org/C123',
            'display_name': 'Minimal Concept'
        }
        
        result = concept_retriever._process_concept_data(concept_data)
        
        assert result['openalex_id'] == 'C123'
        assert result['display_name'] == 'Minimal Concept'
        assert result['description'] is None
        assert result['level'] == 0
        assert result['works_count'] == 0
        assert result['cited_by_count'] == 0
        assert result['ancestors'] == []
        assert result['related_concepts'] == []
    
    def test_process_concept_data_no_wikidata(self, concept_retriever):
        """Test processing concept data without wikidata URL."""
        concept_data = {
            'id': 'https://openalex.org/C123',
            'display_name': 'No Wiki Concept',
            'wikidata': None
        }
        
        result = concept_retriever._process_concept_data(concept_data)
        
        assert result['wikidata'] is None
    
    def test_process_concept_data_error_handling(self, concept_retriever):
        """Test processing concept data with errors."""
        # Malformed data that should cause processing errors
        concept_data = {
            'display_name': 'Error Concept'
            # Missing required fields
        }
        
        result = concept_retriever._process_concept_data(concept_data)
        
        # Should return error information
        assert 'display_name' in result
        assert result['display_name'] == 'Error Concept'
