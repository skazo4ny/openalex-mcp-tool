"""
Unit tests for OpenAlexAuthorRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_author_retriever import OpenAlexAuthorRetriever


class TestOpenAlexAuthorRetriever:
    """Test OpenAlexAuthorRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexAuthorRetriever initialization."""
        retriever = OpenAlexAuthorRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_authors_basic(self, author_retriever):
        """Test basic author search."""
        mock_response = {
            'results': [
                {'id': 'https://openalex.org/A123', 'display_name': 'John Doe'},
                {'id': 'https://openalex.org/A456', 'display_name': 'Jane Smith'}
            ],
            'meta': {'count': 2}
        }
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = author_retriever.search_authors("John Doe", max_results=5)
                
                assert len(result) == 2
                mock_search.assert_called_once_with(
                    query="John Doe",
                    per_page=5
                )
                assert mock_process.call_count == 2
    
    def test_search_authors_with_affiliation(self, author_retriever):
        """Test author search with affiliation."""
        mock_response = {'results': [{'id': 'A123', 'display_name': 'John Doe'}], 'meta': {'count': 1}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = author_retriever.search_authors("John Doe", affiliation="MIT")
                
                mock_search.assert_called_once_with(
                    query="John Doe MIT",
                    per_page=10
                )
    
    def test_search_authors_max_results_limit(self, author_retriever):
        """Test author search respects max_results limit."""
        large_response = {
            'results': [{'id': f'A{i}', 'display_name': f'Author {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = author_retriever.search_authors("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_authors_api_limit(self, author_retriever):
        """Test author search respects API per_page limit of 50."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.return_value = mock_response
            
            result = author_retriever.search_authors("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                per_page=50  # Should be limited to 50
            )
    
    def test_search_authors_error_handling(self, author_retriever):
        """Test author search error handling."""
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                author_retriever.search_authors("test")
    
    def test_get_by_orcid_success(self, author_retriever, mock_author_response):
        """Test getting author by ORCID successfully."""
        mock_response = {'results': [mock_author_response], 'meta': {'count': 1}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = author_retriever.get_by_orcid("0000-0000-0000-0000")
                
                assert result == {'processed': True}
                mock_search.assert_called_once_with(
                    query="orcid:0000-0000-0000-0000",
                    per_page=1
                )
    
    def test_get_by_orcid_with_url_prefix(self, author_retriever, mock_author_response):
        """Test getting author by ORCID with URL prefix."""
        mock_response = {'results': [mock_author_response], 'meta': {'count': 1}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = author_retriever.get_by_orcid("https://orcid.org/0000-0000-0000-0000")
                
                mock_search.assert_called_once_with(
                    query="orcid:0000-0000-0000-0000",
                    per_page=1
                )
    
    def test_get_by_orcid_not_found(self, author_retriever):
        """Test getting author by ORCID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.return_value = mock_response
            
            result = author_retriever.get_by_orcid("0000-0000-0000-0000")
            
            assert result is None
    
    def test_get_by_orcid_error_handling(self, author_retriever):
        """Test getting author by ORCID error handling."""
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                author_retriever.get_by_orcid("0000-0000-0000-0000")
    
    def test_get_by_openalex_id_success(self, author_retriever, mock_author_response):
        """Test getting author by OpenAlex ID successfully."""
        mock_response = {'results': [mock_author_response], 'meta': {'count': 1}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            with patch.object(author_retriever, '_process_author_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = author_retriever.get_by_openalex_id("A123456789")
                
                assert result == {'processed': True}
                mock_search.assert_called_once_with(
                    query="",
                    filters={'openalex_id': 'A123456789'},
                    per_page=1
                )
    
    def test_get_by_openalex_id_not_found(self, author_retriever):
        """Test getting author by OpenAlex ID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.return_value = mock_response
            
            result = author_retriever.get_by_openalex_id("A123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, author_retriever):
        """Test getting author by OpenAlex ID error handling."""
        with patch.object(author_retriever.api_client, 'search_authors') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                author_retriever.get_by_openalex_id("A123456789")
    
    def test_process_author_data_complete(self, author_retriever):
        """Test processing complete author data."""
        author_data = {
            'id': 'https://openalex.org/A2741809807',
            'display_name': 'John Doe',
            'orcid': 'https://orcid.org/0000-0000-0000-0000',
            'works_count': 150,
            'cited_by_count': 2500,
            'summary_stats': {
                'i10_index': 45,
                'h_index': 25
            },
            'last_known_institution': {
                'id': 'https://openalex.org/I123',
                'display_name': 'Test University',
                'country_code': 'US',
                'type': 'education'
            },
            'display_name_alternatives': ['J. Doe', 'Jonathan Doe'],
            'x_concepts': [
                {
                    'id': 'https://openalex.org/C123',
                    'display_name': 'Machine Learning',
                    'level': 1,
                    'score': 0.95
                },
                {
                    'id': 'https://openalex.org/C456',
                    'display_name': 'Artificial Intelligence',
                    'level': 2,
                    'score': 0.85
                }
            ],
            'counts_by_year': [
                {'year': 2020, 'works_count': 5, 'cited_by_count': 100},
                {'year': 2021, 'works_count': 8, 'cited_by_count': 150},
                {'year': 2022, 'works_count': 12, 'cited_by_count': 200}
            ]
        }
        
        with patch.object(author_retriever, '_calculate_author_metrics') as mock_metrics:
            mock_metrics.return_value = {'productivity': 0.8, 'impact': 0.9}
            
            result = author_retriever._process_author_data(author_data)
            
            assert result['openalex_id'] == 'A2741809807'
            assert result['display_name'] == 'John Doe'
            assert result['orcid'] == 'https://orcid.org/0000-0000-0000-0000'
            assert result['works_count'] == 150
            assert result['cited_by_count'] == 2500
            assert result['i10_index'] == 45
            assert result['h_index'] == 25
            assert result['affiliation']['display_name'] == 'Test University'
            assert result['affiliation']['openalex_id'] == 'I123'
            assert len(result['alternative_names']) == 2
            assert len(result['research_areas']) == 2
            assert result['research_areas'][0]['display_name'] == 'Machine Learning'
            assert result['works_by_year'][2020] == 5
            assert result['citations_by_year'][2021] == 150
            assert result['first_publication_year'] == 2020
            assert result['most_recent_publication_year'] == 2022
            assert result['metrics'] == {'productivity': 0.8, 'impact': 0.9}
    
    def test_process_author_data_minimal(self, author_retriever):
        """Test processing minimal author data."""
        author_data = {
            'id': 'https://openalex.org/A123',
            'display_name': 'Minimal Author'
        }
        
        with patch.object(author_retriever, '_calculate_author_metrics') as mock_metrics:
            mock_metrics.return_value = {}
            
            result = author_retriever._process_author_data(author_data)
            
            assert result['openalex_id'] == 'A123'
            assert result['display_name'] == 'Minimal Author'
            assert result['orcid'] is None
            assert result['works_count'] == 0
            assert result['cited_by_count'] == 0
            assert result['affiliation'] is None
            assert result['alternative_names'] == []
            assert result['research_areas'] == []
    
    def test_process_author_data_no_institution(self, author_retriever):
        """Test processing author data without institution."""
        author_data = {
            'id': 'https://openalex.org/A123',
            'display_name': 'Independent Author',
            'last_known_institution': None
        }
        
        with patch.object(author_retriever, '_calculate_author_metrics') as mock_metrics:
            mock_metrics.return_value = {}
            
            result = author_retriever._process_author_data(author_data)
            
            assert result['affiliation'] is None
    
    def test_process_author_data_error_handling(self, author_retriever):
        """Test processing author data with errors."""
        # Malformed data that should cause processing errors
        author_data = {
            'display_name': 'Error Author'
            # Missing required fields
        }
        
        result = author_retriever._process_author_data(author_data)
        
        # Should return error information
        assert 'display_name' in result
        assert result['display_name'] == 'Error Author'
