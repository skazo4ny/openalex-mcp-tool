"""
Unit tests for OpenAlexSourceRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_source_retriever import OpenAlexSourceRetriever


class TestOpenAlexSourceRetriever:
    """Test OpenAlexSourceRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexSourceRetriever initialization."""
        retriever = OpenAlexSourceRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_sources_basic(self, source_retriever):
        """Test basic source search."""
        mock_response = {
            'results': [
                {'id': 'https://openalex.org/S123', 'display_name': 'Nature'},
                {'id': 'https://openalex.org/S456', 'display_name': 'Science'}
            ],
            'meta': {'count': 2}
        }
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            with patch.object(source_retriever, '_process_source_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = source_retriever.search_sources("Nature", max_results=5)
                
                assert len(result) == 2
                mock_search.assert_called_once_with(
                    query="Nature",
                    filters={},
                    per_page=5
                )
                assert mock_process.call_count == 2
    
    def test_search_sources_with_filters(self, source_retriever):
        """Test source search with type and publisher filters."""
        mock_response = {'results': [{'id': 'S123', 'display_name': 'Nature'}], 'meta': {'count': 1}}
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            with patch.object(source_retriever, '_process_source_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = source_retriever.search_sources("Nature", source_type="journal", publisher="Nature Publishing Group")
                
                mock_search.assert_called_once_with(
                    query="Nature",
                    filters={'type': 'journal', 'publisher': 'Nature Publishing Group'},
                    per_page=10
                )
    
    def test_search_sources_max_results_limit(self, source_retriever):
        """Test source search respects max_results limit."""
        large_response = {
            'results': [{'id': f'S{i}', 'display_name': f'Source {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            with patch.object(source_retriever, '_process_source_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = source_retriever.search_sources("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_sources_api_limit(self, source_retriever):
        """Test source search respects API per_page limit of 50."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            mock_search.return_value = mock_response
            
            result = source_retriever.search_sources("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                filters={},
                per_page=50  # Should be limited to 50
            )
    
    def test_search_sources_error_handling(self, source_retriever):
        """Test source search error handling."""
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                source_retriever.search_sources("test")
    
    def test_get_by_issn_success(self, source_retriever, mock_source_response):
        """Test getting source by ISSN successfully."""
        with patch.object(source_retriever.api_client, 'get_source_by_issn') as mock_get:
            with patch.object(source_retriever, '_process_source_data') as mock_process:
                mock_get.return_value = mock_source_response
                mock_process.return_value = {'processed': True}
                
                result = source_retriever.get_by_issn("1234-5678")
                
                assert result == {'processed': True}
                mock_get.assert_called_once_with("1234-5678")
    
    def test_get_by_issn_not_found(self, source_retriever):
        """Test getting source by ISSN when not found."""
        with patch.object(source_retriever.api_client, 'get_source_by_issn') as mock_get:
            mock_get.return_value = None
            
            result = source_retriever.get_by_issn("1234-5678")
            
            assert result is None
    
    def test_get_by_issn_error_handling(self, source_retriever):
        """Test getting source by ISSN error handling."""
        with patch.object(source_retriever.api_client, 'get_source_by_issn') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                source_retriever.get_by_issn("1234-5678")
    
    def test_get_by_openalex_id_success(self, source_retriever, mock_source_response):
        """Test getting source by OpenAlex ID successfully."""
        mock_response = {'results': [mock_source_response], 'meta': {'count': 1}}
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            with patch.object(source_retriever, '_process_source_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = source_retriever.get_by_openalex_id("S123456789")
                
                assert result == {'processed': True}
                mock_search.assert_called_once_with(
                    query="",
                    filters={'openalex_id': 'S123456789'},
                    per_page=1
                )
    
    def test_get_by_openalex_id_not_found(self, source_retriever):
        """Test getting source by OpenAlex ID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            mock_search.return_value = mock_response
            
            result = source_retriever.get_by_openalex_id("S123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, source_retriever):
        """Test getting source by OpenAlex ID error handling."""
        with patch.object(source_retriever.api_client, 'search_sources') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                source_retriever.get_by_openalex_id("S123456789")
    
    def test_process_source_data_complete(self, source_retriever):
        """Test processing complete source data."""
        source_data = {
            'id': 'https://openalex.org/S123456789',
            'display_name': 'Nature',
            'issn_l': '1234-5678',
            'type': 'journal',
            'publisher': 'Nature Publishing Group',
            'works_count': 150000,
            'cited_by_count': 2500000,
            'homepage_url': 'https://www.nature.com',
            'is_in_doaj': True,
            'is_oa': False,
            'issn': ['1234-5678', '9876-5432'],
            'host_organization': 'https://openalex.org/P123456789',
            'host_organization_name': 'Springer Nature',
            'counts_by_year': [
                {'year': 2022, 'works_count': 15000, 'cited_by_count': 250000},
                {'year': 2023, 'works_count': 20000, 'cited_by_count': 300000}
            ],
            'summary_stats': {
                '2yr_mean_citedness': 42.5
            }
        }
        
        result = source_retriever._process_source_data(source_data)
        
        assert result['display_name'] == 'Nature'
        assert result['works_count'] == 150000
        assert result['cited_by_count'] == 2500000
        assert result['type'] == 'journal'
        assert result['publisher'] == 'Nature Publishing Group'
        assert result['issn_l'] == '1234-5678'
        assert '1234-5678' in result['issns']
        assert result['host_organization']['name'] == 'Springer Nature'
        assert 2022 in result['works_by_year']
        assert result['works_by_year'][2022] == 15000
        assert result['metrics']['impact_factor_approx'] == 42.5
    
    def test_process_source_data_minimal(self, source_retriever):
        """Test processing minimal source data."""
        source_data = {
            'id': 'https://openalex.org/S123456789',
            'display_name': 'Test Source'
        }
        
        result = source_retriever._process_source_data(source_data)
        
        assert result['display_name'] == 'Test Source'
        assert result['works_count'] == 0
        assert result['cited_by_count'] == 0
    
    def test_process_source_data_error_handling(self, source_retriever):
        """Test processing source data with error."""
        source_data = {
            'display_name': 'Test Source',
            'id': 'https://openalex.org/S123456789'
        }
        
        # Mock an exception during processing
        with patch.object(source_retriever, '_calculate_source_metrics', side_effect=Exception("Processing Error")):
            result = source_retriever._process_source_data(source_data)
            
            assert result['display_name'] == 'Test Source'
            assert 'error' in result
    
    def test_calculate_source_metrics(self, source_retriever):
        """Test calculating source metrics."""
        source_data = {
            'works_count': 1000,
            'cited_by_count': 5000,
            'counts_by_year': [
                {'year': 2018, 'works_count': 50, 'cited_by_count': 250},
                {'year': 2019, 'works_count': 100, 'cited_by_count': 500},
                {'year': 2020, 'works_count': 150, 'cited_by_count': 750},
                {'year': 2021, 'works_count': 200, 'cited_by_count': 1000},
                {'year': 2022, 'works_count': 250, 'cited_by_count': 1250},
                {'year': 2023, 'works_count': 300, 'cited_by_count': 1500}
            ],
            'summary_stats': {
                '2yr_mean_citedness': 5.0
            }
        }
        
        metrics = source_retriever._calculate_source_metrics(source_data)
        
        assert metrics['citations_per_work'] == 5.0
        assert metrics['recent_works_count'] == 900  # 2020-2023: 150+200+250+300
        assert metrics['recent_citations_count'] == 4500  # 2020-2023: 750+1000+1250+1500
        assert metrics['growth_rate'] == 83.33  # (250+300)/2 / (100+200)/2 = 275/150 = 1.83 = 83.33% growth
        assert metrics['impact_factor_approx'] == 5.0


@pytest.fixture
def source_retriever(api_client):
    """OpenAlexSourceRetriever fixture."""
    return OpenAlexSourceRetriever(api_client)


@pytest.fixture
def mock_source_response():
    """Mock OpenAlex source response."""
    return {
        "id": "https://openalex.org/S123456789",
        "display_name": "Nature",
        "issn_l": "1234-5678",
        "type": "journal",
        "publisher": "Nature Publishing Group",
        "works_count": 150000,
        "cited_by_count": 2500000,
        "homepage_url": "https://www.nature.com",
        "is_in_doaj": True,
        "is_oa": False,
        "issn": ["1234-5678", "9876-5432"],
        "host_organization": "https://openalex.org/P123456789",
        "host_organization_name": "Springer Nature",
        "counts_by_year": [
            {"year": 2022, "works_count": 15000, "cited_by_count": 250000},
            {"year": 2023, "works_count": 20000, "cited_by_count": 300000}
        ],
        "summary_stats": {
            "2yr_mean_citedness": 42.5
        }
    }