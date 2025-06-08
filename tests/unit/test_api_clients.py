"""
Unit tests for OpenAlexAPIClient.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from slr_modules.api_clients import OpenAlexAPIClient


class TestOpenAlexAPIClient:
    """Test OpenAlexAPIClient functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexAPIClient initialization."""
        assert api_client.base_url == 'https://api.openalex.org'
        assert api_client.timeout == 30
        assert api_client.retries == 2
        assert api_client.default_per_page == 10  # Matches test config
        assert api_client.max_per_page == 50  # Matches test config
    
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, api_client, mock_search_response):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_search_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = api_client._make_request('/works', {'search': 'test'})
        
        assert result == mock_search_response
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_make_request_http_error_retry(self, mock_get, api_client):
        """Test API request with HTTP error retries."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.RequestException):
            api_client._make_request('/works', {'search': 'test'})
        
        assert mock_get.call_count == api_client.retries + 1  # Initial call + retries
    
    def test_search_works_basic(self, api_client):
        """Test basic works search."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {
                'results': [
                    {'id': 'W123', 'title': 'Test Paper'},
                    {'id': 'W456', 'title': 'Another Paper'}
                ],
                'meta': {'count': 2}
            }
            mock_request.return_value = mock_response
            
            result = api_client.search_works("machine learning", per_page=10)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'search': 'machine learning',
                'page': 1,
                'per-page': 10
            })
    
    def test_search_works_with_year_range_filters(self, api_client):
        """Test works search with year range filters."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {'results': [], 'meta': {'count': 0}}
            mock_request.return_value = mock_response
            
            filters = {
                'publication_year': ['>=2020', '<=2024']
            }
            
            result = api_client.search_works('machine learning', filters=filters)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'search': 'machine learning',
                'page': 1,
                'per-page': 10,
                'filter': 'publication_year:2020-2024'
            })
    
    def test_search_works_with_multiple_filters(self, api_client):
        """Test works search with multiple filters."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {'results': [], 'meta': {'count': 0}}
            mock_request.return_value = mock_response
            
            filters = {
                'publication_year': '2023',
                'type': 'article',
                'is_oa': 'true'
            }
            
            result = api_client.search_works('machine learning', filters=filters, page=2)
            
            assert result == mock_response
            expected_filter = 'publication_year:2023,type:article,is_oa:true'
            mock_request.assert_called_once_with('/works', {
                'search': 'machine learning',
                'page': 2,
                'per-page': 10,
                'filter': expected_filter
            })
    
    def test_search_works_with_list_filter(self, api_client):
        """Test works search with list filter (non-year)."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {'results': [], 'meta': {'count': 0}}
            mock_request.return_value = mock_response
            
            filters = {
                'type': ['article', 'review']
            }
            
            result = api_client.search_works('machine learning', filters=filters)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'search': 'machine learning',
                'page': 1,
                'per-page': 10,
                'filter': 'type:article+review'
            })
    
    def test_get_work_by_doi_success(self, api_client, mock_work_response):
        """Test getting work by DOI successfully."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = mock_work_response
            
            result = api_client.get_work_by_doi('10.1038/nature12373')
            
            assert result == mock_work_response
            mock_request.assert_called_once_with('/works/https://doi.org/10.1038/nature12373')
    
    def test_get_work_by_doi_with_prefix(self, api_client, mock_work_response):
        """Test getting work by DOI with https prefix."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = mock_work_response
            
            result = api_client.get_work_by_doi('https://doi.org/10.1038/nature12373')
            
            assert result == mock_work_response
            mock_request.assert_called_once_with('/works/https://doi.org/10.1038/nature12373')
    
    def test_get_work_by_doi_not_found(self, api_client):
        """Test getting work by DOI when not found."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.side_effect = requests.exceptions.HTTPError(
                response=Mock(status_code=404)
            )
            
            result = api_client.get_work_by_doi('10.1000/nonexistent')
            
            assert result is None
    
    def test_search_authors_basic(self, api_client):
        """Test basic authors search."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {"results": [{"id": "A123", "display_name": "Jane Smith"}]}
            mock_request.return_value = mock_response
            
            result = api_client.search_authors('jane smith')
            
            assert result == mock_response
            mock_request.assert_called_once_with('/authors', {
                'search': 'jane smith',
                'page': 1,
                'per-page': 10
            })
    
    def test_search_authors_with_filters(self, api_client):
        """Test authors search with filters."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {"results": [{"id": "A123", "display_name": "Jane Smith"}]}
            mock_request.return_value = mock_response
            
            filters = {'works_count': '>=10', 'cited_by_count': '>=100'}
            
            result = api_client.search_authors('jane smith', filters=filters, per_page=50)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/authors', {
                'search': 'jane smith',
                'page': 1,
                'per-page': 50,
                'filter': 'works_count:>=10,cited_by_count:>=100'
            })
    
    def test_search_concepts_basic(self, api_client):
        """Test basic concepts search."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {"results": [{"id": "C123", "display_name": "Machine Learning"}]}
            mock_request.return_value = mock_response
            
            result = api_client.search_concepts('machine learning')
            
            assert result == mock_response
            mock_request.assert_called_once_with('/concepts', {
                'search': 'machine learning',
                'page': 1,
                'per-page': 10
            })
    
    def test_search_concepts_with_filters(self, api_client):
        """Test concepts search with filters."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {"results": [{"id": "C123", "display_name": "Machine Learning"}]}
            mock_request.return_value = mock_response
            
            filters = {'level': ['1', '2']}
            
            result = api_client.search_concepts('machine learning', filters=filters)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/concepts', {
                'search': 'machine learning',
                'page': 1,
                'per-page': 10,
                'filter': 'level:1+2'
            })
    
    def test_get_multiple_works(self, api_client):
        """Test getting multiple works by OpenAlex IDs."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {"results": [{"id": "W123"}, {"id": "W456"}]}
            mock_request.return_value = mock_response
            
            openalex_ids = ['W123', 'W456', 'W789']
            result = api_client.get_multiple_works(openalex_ids)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'filter': 'openalex_id:W123|W456|W789'
            })
    
    def test_per_page_limit_enforced(self, api_client):
        """Test that per_page is limited to max_per_page."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {'results': [], 'meta': {'count': 0}}
            mock_request.return_value = mock_response
            
            # Try to request more than max_per_page
            result = api_client.search_works('test', per_page=500)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'search': 'test',
                'page': 1,
                'per-page': 50  # Should be limited to max_per_page
            })
    
    def test_none_values_filtered_from_params(self, api_client):
        """Test that None values are filtered from request parameters."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_response = {'results': [], 'meta': {'count': 0}}
            mock_request.return_value = mock_response
            
            # per_page=None should be filtered out and use default
            result = api_client.search_works('test', per_page=None)
            
            assert result == mock_response
            mock_request.assert_called_once_with('/works', {
                'search': 'test',
                'page': 1,
                'per-page': 10  # Should use default_per_page
            })
