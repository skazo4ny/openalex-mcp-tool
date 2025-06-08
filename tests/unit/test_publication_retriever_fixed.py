"""
Unit tests for OpenAlexPublicationRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_publication_retriever import OpenAlexPublicationRetriever


class TestOpenAlexPublicationRetriever:
    """Test OpenAlexPublicationRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexPublicationRetriever initialization."""
        retriever = OpenAlexPublicationRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_publications_basic(self, publication_retriever, mock_search_response):
        """Test basic publication search."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.return_value = mock_search_response
            
            result = publication_retriever.search_publications("machine learning", max_results=5)
            
            assert len(result) <= 5
            mock_search.assert_called_once_with(
                query="machine learning",
                filters={},
                per_page=5
            )
    
    def test_search_publications_with_year_range(self, publication_retriever, mock_search_response):
        """Test publication search with year range."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.return_value = mock_search_response
            
            result = publication_retriever.search_publications(
                "machine learning", 
                max_results=10,
                start_year=2020,
                end_year=2024
            )
            
            mock_search.assert_called_once_with(
                query="machine learning",
                filters={'publication_year': ['>=2020', '<=2024']},
                per_page=10
            )
    
    def test_search_publications_with_start_year_only(self, publication_retriever, mock_search_response):
        """Test publication search with start year only."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.return_value = mock_search_response
            
            result = publication_retriever.search_publications(
                "machine learning", 
                start_year=2020
            )
            
            mock_search.assert_called_once_with(
                query="machine learning",
                filters={'publication_year': '>=2020'},
                per_page=10
            )
    
    def test_search_publications_with_end_year_only(self, publication_retriever, mock_search_response):
        """Test publication search with end year only."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.return_value = mock_search_response
            
            result = publication_retriever.search_publications(
                "machine learning", 
                end_year=2024
            )
            
            mock_search.assert_called_once_with(
                query="machine learning",
                filters={'publication_year': '<=2024'},
                per_page=10
            )
    
    def test_search_publications_max_results_limit(self, publication_retriever, mock_search_response):
        """Test publication search respects max_results limit."""
        # Create a response with more results than max_results
        large_response = {
            'results': [{'id': f'W{i}', 'title': f'Paper {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            with patch.object(publication_retriever, '_process_work_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = publication_retriever.search_publications("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_publications_api_limit(self, publication_retriever, mock_search_response):
        """Test publication search respects API per_page limit of 50."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.return_value = mock_search_response
            
            # Request more than API limit
            result = publication_retriever.search_publications("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                filters={},
                per_page=50  # Should be limited to 50
            )
    
    def test_search_publications_error_handling(self, publication_retriever):
        """Test publication search error handling."""
        with patch.object(publication_retriever.api_client, 'search_works') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                publication_retriever.search_publications("test")
    
    def test_get_by_doi_success(self, publication_retriever, mock_work_response):
        """Test getting publication by DOI successfully."""
        with patch.object(publication_retriever.api_client, 'get_work_by_doi') as mock_get:
            with patch.object(publication_retriever, '_process_work_data') as mock_process:
                mock_get.return_value = mock_work_response
                mock_process.return_value = {'processed': True}
                
                result = publication_retriever.get_by_doi("10.1038/nature12373")
                
                assert result == {'processed': True}
                mock_get.assert_called_once_with("10.1038/nature12373")
                mock_process.assert_called_once_with(mock_work_response)
    
    def test_get_by_doi_not_found(self, publication_retriever):
        """Test getting publication by DOI when not found."""
        with patch.object(publication_retriever.api_client, 'get_work_by_doi') as mock_get:
            mock_get.return_value = None
            
            result = publication_retriever.get_by_doi("10.1000/nonexistent")
            
            assert result is None
    
    def test_get_by_doi_error_handling(self, publication_retriever):
        """Test getting publication by DOI error handling."""
        with patch.object(publication_retriever.api_client, 'get_work_by_doi') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                publication_retriever.get_by_doi("10.1038/nature12373")
    
    def test_get_by_openalex_id_success(self, publication_retriever, mock_work_response):
        """Test getting publication by OpenAlex ID successfully."""
        mock_response = {'results': [mock_work_response], 'meta': {'count': 1}}
        
        with patch.object(publication_retriever.api_client, 'get_multiple_works') as mock_get:
            with patch.object(publication_retriever, '_process_work_data') as mock_process:
                mock_get.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = publication_retriever.get_by_openalex_id("W123456789")
                
                assert result == {'processed': True}
                mock_get.assert_called_once_with(["W123456789"])
                mock_process.assert_called_once_with(mock_work_response)
    
    def test_get_by_openalex_id_not_found(self, publication_retriever):
        """Test getting publication by OpenAlex ID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(publication_retriever.api_client, 'get_multiple_works') as mock_get:
            mock_get.return_value = mock_response
            
            result = publication_retriever.get_by_openalex_id("W123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, publication_retriever):
        """Test getting publication by OpenAlex ID error handling."""
        with patch.object(publication_retriever.api_client, 'get_multiple_works') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                publication_retriever.get_by_openalex_id("W123456789")
    
    def test_process_work_data_complete(self, publication_retriever):
        """Test processing complete work data."""
        work_data = {
            'id': 'https://openalex.org/W2741809807',
            'title': 'Test Paper Title',
            'doi': 'https://doi.org/10.1038/nature12373',
            'publication_year': 2023,
            'publication_date': '2023-01-15',
            'type': 'article',
            'cited_by_count': 150,
            'is_retracted': False,
            'is_paratext': False,
            'abstract_inverted_index': {
                'This': [0], 'is': [1], 'a': [2], 'test': [3], 'abstract': [4]
            },
            'authorships': [
                {
                    'author': {
                        'id': 'https://openalex.org/A123',
                        'display_name': 'John Doe',
                        'orcid': 'https://orcid.org/0000-0000-0000-0000'
                    },
                    'author_position': 'first',
                    'institutions': [
                        {
                            'id': 'https://openalex.org/I123',
                            'display_name': 'Test University',
                            'country_code': 'US',
                            'type': 'education'
                        }
                    ]
                }
            ],
            'primary_location': {
                'source': {
                    'id': 'https://openalex.org/S123',
                    'display_name': 'Test Journal',
                    'type': 'journal'
                }
            },
            'concepts': [
                {
                    'id': 'https://openalex.org/C123',
                    'display_name': 'Machine Learning',
                    'level': 1,
                    'score': 0.95
                }
            ],
            'open_access': {
                'is_oa': True,
                'oa_date': '2023-01-15',
                'oa_url': 'https://example.com/paper.pdf',
                'any_repository_has_fulltext': True
            },
            'best_oa_location': {
                'pdf_url': 'https://example.com/paper.pdf',
                'landing_page_url': 'https://example.com/paper'
            },
            'referenced_works': ['W1', 'W2', 'W3'],
            'related_works': ['W4', 'W5']
        }
        
        result = publication_retriever._process_work_data(work_data)
        
        assert result['openalex_id'] == 'W2741809807'
        assert result['title'] == 'Test Paper Title'
        assert result['doi'] == '10.1038/nature12373'
        assert result['publication_year'] == 2023
        assert result['cited_by_count'] == 150
        assert result['abstract'] == 'This is a test abstract'
        assert len(result['authors']) == 1
        assert result['authors'][0]['display_name'] == 'John Doe'
        assert result['authors'][0]['openalex_id'] == 'A123'
        assert result['venue']['name'] == 'Test Journal'
        assert len(result['concepts']) == 1
        assert result['concepts'][0]['display_name'] == 'Machine Learning'
        assert result['open_access']['is_oa'] is True
        assert result['referenced_works_count'] == 3
        assert result['related_works_count'] == 2
    
    def test_process_work_data_minimal(self, publication_retriever):
        """Test processing minimal work data."""
        work_data = {
            'id': 'https://openalex.org/W123',
            'title': 'Minimal Paper'
        }
        
        result = publication_retriever._process_work_data(work_data)
        
        assert result['openalex_id'] == 'W123'
        assert result['title'] == 'Minimal Paper'
        assert result['doi'] == ''
        assert result['abstract'] == 'No abstract available'
        assert result['authors'] == []
        assert result['cited_by_count'] == 0
    
    def test_process_work_data_error_handling(self, publication_retriever):
        """Test processing work data with errors."""
        # Malformed data that should cause processing errors
        work_data = {
            'title': 'Error Paper',
            'doi': 'malformed-doi'
        }
        
        result = publication_retriever._process_work_data(work_data)
        
        # Should return basic information, not error field
        assert result['title'] == 'Error Paper'
        assert result['doi'] == 'malformed-doi'
        assert result['openalex_id'] == ''  # Should extract empty ID from missing id field
