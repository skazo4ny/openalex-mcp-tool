"""
Unit tests for OpenAlexInstitutionRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_institution_retriever import OpenAlexInstitutionRetriever


class TestOpenAlexInstitutionRetriever:
    """Test OpenAlexInstitutionRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexInstitutionRetriever initialization."""
        retriever = OpenAlexInstitutionRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_institutions_basic(self, institution_retriever):
        """Test basic institution search."""
        mock_response = {
            'results': [
                {'id': 'https://openalex.org/I123', 'display_name': 'Harvard University'},
                {'id': 'https://openalex.org/I456', 'display_name': 'MIT'}
            ],
            'meta': {'count': 2}
        }
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = institution_retriever.search_institutions("University", max_results=5)
                
                assert len(result) == 2
                mock_search.assert_called_once_with(
                    query="University",
                    filters={},
                    per_page=5
                )
                assert mock_process.call_count == 2
    
    def test_search_institutions_with_filters(self, institution_retriever):
        """Test institution search with country and type filters."""
        mock_response = {'results': [{'id': 'I123', 'display_name': 'Harvard University'}], 'meta': {'count': 1}}
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = institution_retriever.search_institutions("University", country_code="us", institution_type="education")
                
                mock_search.assert_called_once_with(
                    query="University",
                    filters={'country_code': 'US', 'type': 'education'},
                    per_page=10
                )
    
    def test_search_institutions_country_code_normalization(self, institution_retriever):
        """Test institution search with lowercase country code."""
        mock_response = {'results': [{'id': 'I123', 'display_name': 'Harvard University'}], 'meta': {'count': 1}}
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = institution_retriever.search_institutions("University", country_code="de")
                
                mock_search.assert_called_once_with(
                    query="University",
                    filters={'country_code': 'DE'},
                    per_page=10
                )
    
    def test_search_institutions_max_results_limit(self, institution_retriever):
        """Test institution search respects max_results limit."""
        large_response = {
            'results': [{'id': f'I{i}', 'display_name': f'Institution {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = institution_retriever.search_institutions("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_institutions_api_limit(self, institution_retriever):
        """Test institution search respects API per_page limit of 50."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            mock_search.return_value = mock_response
            
            result = institution_retriever.search_institutions("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                filters={},
                per_page=50  # Should be limited to 50
            )
    
    def test_search_institutions_error_handling(self, institution_retriever):
        """Test institution search error handling."""
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                institution_retriever.search_institutions("test")
    
    def test_get_by_ror_id_success(self, institution_retriever, mock_institution_response):
        """Test getting institution by ROR ID successfully."""
        with patch.object(institution_retriever.api_client, 'get_institution_by_ror') as mock_get:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_get.return_value = mock_institution_response
                mock_process.return_value = {'processed': True}
                
                result = institution_retriever.get_by_ror_id("0000-0000-0000-0000")
                
                assert result == {'processed': True}
                mock_get.assert_called_once_with("0000-0000-0000-0000")
    
    def test_get_by_ror_id_with_url_prefix(self, institution_retriever, mock_institution_response):
        """Test getting institution by ROR ID with URL prefix."""
        with patch.object(institution_retriever.api_client, 'get_institution_by_ror') as mock_get:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_get.return_value = mock_institution_response
                mock_process.return_value = {'processed': True}
                
                result = institution_retriever.get_by_ror_id("https://ror.org/0000-0000-0000-0000")
                
                mock_get.assert_called_once_with("0000-0000-0000-0000")
    
    def test_get_by_ror_id_not_found(self, institution_retriever):
        """Test getting institution by ROR ID when not found."""
        with patch.object(institution_retriever.api_client, 'get_institution_by_ror') as mock_get:
            mock_get.return_value = None
            
            result = institution_retriever.get_by_ror_id("0000-0000-0000-0000")
            
            assert result is None
    
    def test_get_by_ror_id_error_handling(self, institution_retriever):
        """Test getting institution by ROR ID error handling."""
        with patch.object(institution_retriever.api_client, 'get_institution_by_ror') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                institution_retriever.get_by_ror_id("0000-0000-0000-0000")
    
    def test_get_by_openalex_id_success(self, institution_retriever, mock_institution_response):
        """Test getting institution by OpenAlex ID successfully."""
        mock_response = {'results': [mock_institution_response], 'meta': {'count': 1}}
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            with patch.object(institution_retriever, '_process_institution_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = institution_retriever.get_by_openalex_id("I123456789")
                
                assert result == {'processed': True}
                mock_search.assert_called_once_with(
                    query="",
                    filters={'openalex_id': 'I123456789'},
                    per_page=1
                )
    
    def test_get_by_openalex_id_not_found(self, institution_retriever):
        """Test getting institution by OpenAlex ID when not found."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            mock_search.return_value = mock_response
            
            result = institution_retriever.get_by_openalex_id("I123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, institution_retriever):
        """Test getting institution by OpenAlex ID error handling."""
        with patch.object(institution_retriever.api_client, 'search_institutions') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                institution_retriever.get_by_openalex_id("I123456789")
    
    def test_process_institution_data_complete(self, institution_retriever):
        """Test processing complete institution data."""
        institution_data = {
            'id': 'https://openalex.org/I123456789',
            'display_name': 'Harvard University',
            'ror': 'https://ror.org/0000-0000-0000-0000',
            'country_code': 'US',
            'type': 'education',
            'works_count': 150000,
            'cited_by_count': 2500000,
            'homepage_url': 'https://www.harvard.edu',
            'geo': {
                'city': 'Cambridge',
                'region': 'Massachusetts',
                'country': 'United States',
                'latitude': 42.3770,
                'longitude': -71.1167
            },
            'associated_institutions': [
                {
                    'id': 'https://openalex.org/I987654321',
                    'display_name': 'Harvard Medical School',
                    'relationship': 'related'
                }
            ],
            'counts_by_year': [
                {'year': 2022, 'works_count': 15000, 'cited_by_count': 250000},
                {'year': 2023, 'works_count': 20000, 'cited_by_count': 300000}
            ]
        }
        
        result = institution_retriever._process_institution_data(institution_data)
        
        assert result['display_name'] == 'Harvard University'
        assert result['works_count'] == 150000
        assert result['cited_by_count'] == 2500000
        assert result['country_code'] == 'US'
        assert result['type'] == 'education'
        assert result['geo']['city'] == 'Cambridge'
        assert result['geo']['latitude'] == 42.3770
        assert len(result['associated_institutions']) == 1
        assert result['associated_institutions'][0]['display_name'] == 'Harvard Medical School'
        assert 2022 in result['works_by_year']
        assert result['works_by_year'][2022] == 15000
    
    def test_process_institution_data_minimal(self, institution_retriever):
        """Test processing minimal institution data."""
        institution_data = {
            'id': 'https://openalex.org/I123456789',
            'display_name': 'Test Institution'
        }
        
        result = institution_retriever._process_institution_data(institution_data)
        
        assert result['display_name'] == 'Test Institution'
        assert result['works_count'] == 0
        assert result['cited_by_count'] == 0
    
    def test_process_institution_data_error_handling(self, institution_retriever):
        """Test processing institution data with error."""
        institution_data = {
            'display_name': 'Test Institution',
            'id': 'https://openalex.org/I123456789'
        }
        
        # Mock an exception during processing
        with patch.object(institution_retriever, '_calculate_institution_metrics', side_effect=Exception("Processing Error")):
            result = institution_retriever._process_institution_data(institution_data)
            
            assert result['display_name'] == 'Test Institution'
            assert 'error' in result
    
    def test_calculate_institution_metrics(self, institution_retriever):
        """Test calculating institution metrics."""
        institution_data = {
            'works_count': 1000,
            'cited_by_count': 5000,
            'counts_by_year': [
                {'year': 2018, 'works_count': 50, 'cited_by_count': 250},
                {'year': 2019, 'works_count': 100, 'cited_by_count': 500},
                {'year': 2020, 'works_count': 150, 'cited_by_count': 750},
                {'year': 2021, 'works_count': 200, 'cited_by_count': 1000},
                {'year': 2022, 'works_count': 250, 'cited_by_count': 1250},
                {'year': 2023, 'works_count': 300, 'cited_by_count': 1500}
            ]
        }
        
        metrics = institution_retriever._calculate_institution_metrics(institution_data)
        
        assert metrics['citations_per_work'] == 5.0
        assert metrics['recent_works_count'] == 900  # 2020-2023: 150+200+250+300
        assert metrics['recent_citations_count'] == 4500  # 2020-2023: 750+1000+1250+1500
        assert metrics['growth_rate'] == 83.33  # (250+300)/2 / (100+200)/2 = 275/150 = 1.83 = 83.33% growth


@pytest.fixture
def institution_retriever(api_client):
    """OpenAlexInstitutionRetriever fixture."""
    return OpenAlexInstitutionRetriever(api_client)


@pytest.fixture
def mock_institution_response():
    """Mock OpenAlex institution response."""
    return {
        "id": "https://openalex.org/I123456789",
        "display_name": "Harvard University",
        "ror": "https://ror.org/0000-0000-0000-0000",
        "country_code": "US",
        "type": "education",
        "works_count": 150000,
        "cited_by_count": 2500000,
        "homepage_url": "https://www.harvard.edu",
        "geo": {
            "city": "Cambridge",
            "region": "Massachusetts",
            "country": "United States",
            "latitude": 42.3770,
            "longitude": -71.1167
        },
        "associated_institutions": [
            {
                "id": "https://openalex.org/I987654321",
                "display_name": "Harvard Medical School",
                "relationship": "related"
            }
        ],
        "counts_by_year": [
            {"year": 2022, "works_count": 15000, "cited_by_count": 250000},
            {"year": 2023, "works_count": 20000, "cited_by_count": 300000}
        ]
    }