"""
Unit tests for OpenAlexTopicRetriever.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_topic_retriever import OpenAlexTopicRetriever


class TestOpenAlexTopicRetriever:
    """Test OpenAlexTopicRetriever functionality."""
    
    def test_init(self, api_client):
        """Test OpenAlexTopicRetriever initialization."""
        retriever = OpenAlexTopicRetriever(api_client)
        assert retriever.api_client == api_client
    
    def test_search_topics_basic(self, topic_retriever):
        """Test basic topic search."""
        mock_response = {
            'results': [
                {'id': 'https://openalex.org/T123', 'display_name': 'Machine Learning'},
                {'id': 'https://openalex.org/T456', 'display_name': 'Deep Learning'}
            ],
            'meta': {'count': 2}
        }
        
        with patch.object(topic_retriever.api_client, 'search_topics') as mock_search:
            with patch.object(topic_retriever, '_process_topic_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = topic_retriever.search_topics("Machine Learning", max_results=5)
                
                assert len(result) == 2
                mock_search.assert_called_once_with(
                    query="Machine Learning",
                    filters={},
                    per_page=5
                )
                assert mock_process.call_count == 2
    
    def test_search_topics_with_filters(self, topic_retriever):
        """Test topic search with domain and field filters."""
        mock_response = {'results': [{'id': 'T123', 'display_name': 'Machine Learning'}], 'meta': {'count': 1}}
        
        with patch.object(topic_retriever.api_client, 'search_topics') as mock_search:
            with patch.object(topic_retriever, '_process_topic_data') as mock_process:
                mock_search.return_value = mock_response
                mock_process.return_value = {'processed': True}
                
                result = topic_retriever.search_topics("AI", domain="D123", field="F456")
                
                mock_search.assert_called_once_with(
                    query="AI",
                    filters={'domain.id': 'D123', 'field.id': 'F456'},
                    per_page=10
                )
    
    def test_search_topics_max_results_limit(self, topic_retriever):
        """Test topic search respects max_results limit."""
        large_response = {
            'results': [{'id': f'T{i}', 'display_name': f'Topic {i}'} for i in range(100)],
            'meta': {'count': 100}
        }
        
        with patch.object(topic_retriever.api_client, 'search_topics') as mock_search:
            with patch.object(topic_retriever, '_process_topic_data') as mock_process:
                mock_search.return_value = large_response
                mock_process.side_effect = lambda x: {'processed': True, 'id': x['id']}
                
                result = topic_retriever.search_topics("test", max_results=5)
                
                assert len(result) == 5
                assert mock_process.call_count == 5
    
    def test_search_topics_api_limit(self, topic_retriever):
        """Test topic search respects API per_page limit of 50."""
        mock_response = {'results': [], 'meta': {'count': 0}}
        
        with patch.object(topic_retriever.api_client, 'search_topics') as mock_search:
            mock_search.return_value = mock_response
            
            result = topic_retriever.search_topics("test", max_results=100)
            
            mock_search.assert_called_once_with(
                query="test",
                filters={},
                per_page=50  # Should be limited to 50
            )
    
    def test_search_topics_error_handling(self, topic_retriever):
        """Test topic search error handling."""
        with patch.object(topic_retriever.api_client, 'search_topics') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                topic_retriever.search_topics("test")
    
    def test_get_by_openalex_id_success(self, topic_retriever, mock_topic_response):
        """Test getting topic by OpenAlex ID successfully."""
        with patch.object(topic_retriever.api_client, 'get_topic_by_id') as mock_get:
            with patch.object(topic_retriever, '_process_topic_data') as mock_process:
                mock_get.return_value = mock_topic_response
                mock_process.return_value = {'processed': True}
                
                result = topic_retriever.get_by_openalex_id("T123456789")
                
                assert result == {'processed': True}
                mock_get.assert_called_once_with("T123456789")
    
    def test_get_by_openalex_id_not_found(self, topic_retriever):
        """Test getting topic by OpenAlex ID when not found."""
        with patch.object(topic_retriever.api_client, 'get_topic_by_id') as mock_get:
            mock_get.return_value = None
            
            result = topic_retriever.get_by_openalex_id("T123456789")
            
            assert result is None
    
    def test_get_by_openalex_id_error_handling(self, topic_retriever):
        """Test getting topic by OpenAlex ID error handling."""
        with patch.object(topic_retriever.api_client, 'get_topic_by_id') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="API Error"):
                topic_retriever.get_by_openalex_id("T123456789")
    
    def test_process_topic_data_complete(self, topic_retriever):
        """Test processing complete topic data."""
        topic_data = {
            'id': 'https://openalex.org/T123456789',
            'display_name': 'Machine Learning',
            'description': 'A subset of artificial intelligence',
            'works_count': 150000,
            'cited_by_count': 2500000,
            'subfield_count': 12,
            'created_date': '2023-01-01',
            'domain': {
                'id': 'https://openalex.org/D123',
                'display_name': 'Computer Science'
            },
            'field': {
                'id': 'https://openalex.org/F456',
                'display_name': 'Artificial Intelligence'
            },
            'subfield': {
                'id': 'https://openalex.org/S789',
                'display_name': 'Machine Learning'
            },
            'keywords': ['neural networks', 'deep learning', 'supervised learning'],
            'counts_by_year': [
                {'year': 2022, 'works_count': 15000, 'cited_by_count': 250000},
                {'year': 2023, 'works_count': 20000, 'cited_by_count': 300000}
            ]
        }
        
        result = topic_retriever._process_topic_data(topic_data)
        
        assert result['display_name'] == 'Machine Learning'
        assert result['works_count'] == 150000
        assert result['cited_by_count'] == 2500000
        assert result['domain']['display_name'] == 'Computer Science'
        assert result['field']['display_name'] == 'Artificial Intelligence'
        assert result['subfield']['display_name'] == 'Machine Learning'
        assert 'neural networks' in result['keywords']
        assert 2022 in result['works_by_year']
        assert result['works_by_year'][2022] == 15000
    
    def test_process_topic_data_minimal(self, topic_retriever):
        """Test processing minimal topic data."""
        topic_data = {
            'id': 'https://openalex.org/T123456789',
            'display_name': 'Test Topic'
        }
        
        result = topic_retriever._process_topic_data(topic_data)
        
        assert result['display_name'] == 'Test Topic'
        assert result['works_count'] == 0
        assert result['cited_by_count'] == 0
    
    def test_process_topic_data_error_handling(self, topic_retriever):
        """Test processing topic data with error."""
        topic_data = {
            'display_name': 'Test Topic',
            'id': 'https://openalex.org/T123456789'
        }
        
        # Mock an exception during processing
        with patch.object(topic_retriever, '_calculate_topic_metrics', side_effect=Exception("Processing Error")):
            result = topic_retriever._process_topic_data(topic_data)
            
            assert result['display_name'] == 'Test Topic'
            assert 'error' in result
    
    def test_calculate_topic_metrics(self, topic_retriever):
        """Test calculating topic metrics."""
        topic_data = {
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
        
        metrics = topic_retriever._calculate_topic_metrics(topic_data)
        
        assert metrics['citations_per_work'] == 5.0  # 5000/1000
        assert metrics['recent_works_count'] == 900  # 2020-2023: 150+200+250+300
        assert metrics['recent_citations_count'] == 4500  # 2020-2023: 750+1000+1250+1500
        assert metrics['growth_rate'] == 83.33  # (250+300)/2 / (100+200)/2 = 275/150 = 1.83 = 83.33% growth


@pytest.fixture
def topic_retriever(api_client):
    """OpenAlexTopicRetriever fixture."""
    return OpenAlexTopicRetriever(api_client)


@pytest.fixture
def mock_topic_response():
    """Mock OpenAlex topic response."""
    return {
        "id": "https://openalex.org/T123456789",
        "display_name": "Machine Learning",
        "description": "A subset of artificial intelligence",
        "works_count": 150000,
        "cited_by_count": 2500000,
        "subfield_count": 12,
        "created_date": "2023-01-01",
        "domain": {
            "id": "https://openalex.org/D123",
            "display_name": "Computer Science"
        },
        "field": {
            "id": "https://openalex.org/F456",
            "display_name": "Artificial Intelligence"
        },
        "subfield": {
            "id": "https://openalex.org/S789",
            "display_name": "Machine Learning"
        },
        "keywords": ["neural networks", "deep learning", "supervised learning"],
        "counts_by_year": [
            {"year": 2022, "works_count": 15000, "cited_by_count": 250000},
            {"year": 2023, "works_count": 20000, "cited_by_count": 300000}
        ]
    }