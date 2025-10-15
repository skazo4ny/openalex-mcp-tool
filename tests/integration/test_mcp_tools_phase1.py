"""
Integration tests for Phase 1 MCP tool functions.
"""

import pytest
from unittest.mock import Mock, patch
from app import (
    search_openalex_topics,
    search_openalex_institutions,
    search_openalex_sources
)


class TestPhase1MCPToolIntegration:
    """Test Phase 1 MCP tool functions integration."""
    
    def test_search_openalex_topics_success(self, mock_topic_results):
        """Test search_openalex_topics returns JSON data."""
        with patch('app.topic_retriever') as mock_retriever:
            mock_retriever.search_topics.return_value = mock_topic_results
            
            result = search_openalex_topics("machine learning", max_results=2)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['display_name'] == 'Machine Learning'
            assert result[1]['display_name'] == 'Deep Learning'
            
            mock_retriever.search_topics.assert_called_once_with(
                name="machine learning",
                max_results=2
            )
    
    def test_search_openalex_topics_empty_results(self):
        """Test search_openalex_topics with no results."""
        with patch('app.topic_retriever') as mock_retriever:
            mock_retriever.search_topics.return_value = []
            
            result = search_openalex_topics("nonexistent topic")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_topics_error_handling(self):
        """Test search_openalex_topics error handling."""
        with patch('app.topic_retriever') as mock_retriever:
            mock_retriever.search_topics.side_effect = Exception("API Error")
            
            result = search_openalex_topics("test")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_institutions_success(self, mock_institution_results):
        """Test search_openalex_institutions returns JSON data."""
        with patch('app.institution_retriever') as mock_retriever:
            mock_retriever.search_institutions.return_value = mock_institution_results
            
            result = search_openalex_institutions("Harvard", max_results=3)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['display_name'] == 'Harvard University'
            assert result[1]['display_name'] == 'MIT'
            
            mock_retriever.search_institutions.assert_called_once_with(
                name="Harvard",
                max_results=3,
                country_code=None
            )
    
    def test_search_openalex_institutions_with_country_filter(self, mock_institution_results):
        """Test search_openalex_institutions with country filter."""
        with patch('app.institution_retriever') as mock_retriever:
            mock_retriever.search_institutions.return_value = mock_institution_results
            
            result = search_openalex_institutions("University", max_results=5, country_code="US")
            
            assert isinstance(result, list)
            mock_retriever.search_institutions.assert_called_once_with(
                name="University",
                max_results=5,
                country_code="US"
            )
    
    def test_search_openalex_institutions_empty_results(self):
        """Test search_openalex_institutions with no results."""
        with patch('app.institution_retriever') as mock_retriever:
            mock_retriever.search_institutions.return_value = []
            
            result = search_openalex_institutions("Nonexistent Institution")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_institutions_error_handling(self):
        """Test search_openalex_institutions error handling."""
        with patch('app.institution_retriever') as mock_retriever:
            mock_retriever.search_institutions.side_effect = Exception("API Error")
            
            result = search_openalex_institutions("Harvard")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_sources_success(self, mock_source_results):
        """Test search_openalex_sources returns JSON data."""
        with patch('app.source_retriever') as mock_retriever:
            mock_retriever.search_sources.return_value = mock_source_results
            
            result = search_openalex_sources("Nature", max_results=3)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['display_name'] == 'Nature'
            assert result[1]['display_name'] == 'Science'
            
            mock_retriever.search_sources.assert_called_once_with(
                name="Nature",
                max_results=3,
                source_type=None
            )
    
    def test_search_openalex_sources_with_type_filter(self, mock_source_results):
        """Test search_openalex_sources with type filter."""
        with patch('app.source_retriever') as mock_retriever:
            mock_retriever.search_sources.return_value = mock_source_results
            
            result = search_openalex_sources("conference", max_results=5, source_type="conference")
            
            assert isinstance(result, list)
            mock_retriever.search_sources.assert_called_once_with(
                name="conference",
                max_results=5,
                source_type="conference"
            )
    
    def test_search_openalex_sources_empty_results(self):
        """Test search_openalex_sources with no results."""
        with patch('app.source_retriever') as mock_retriever:
            mock_retriever.search_sources.return_value = []
            
            result = search_openalex_sources("Nonexistent Source")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_sources_error_handling(self):
        """Test search_openalex_sources error handling."""
        with patch('app.source_retriever') as mock_retriever:
            mock_retriever.search_sources.side_effect = Exception("API Error")
            
            result = search_openalex_sources("Nature")
            
            assert isinstance(result, list)
            assert len(result) == 0


@pytest.fixture
def mock_topic_results():
    """Mock topic search results."""
    return [
        {
            'display_name': 'Machine Learning',
            'description': 'A subset of artificial intelligence',
            'domain': {'display_name': 'Computer Science'},
            'field': {'display_name': 'Artificial Intelligence'},
            'works_count': 100000,
            'cited_by_count': 2000000,
            'openalex_id': 'T123456789'
        },
        {
            'display_name': 'Deep Learning',
            'description': 'A subset of machine learning',
            'domain': {'display_name': 'Computer Science'},
            'field': {'display_name': 'Artificial Intelligence'},
            'works_count': 50000,
            'cited_by_count': 1000000,
            'openalex_id': 'T987654321'
        }
    ]


@pytest.fixture
def mock_institution_results():
    """Mock institution search results."""
    return [
        {
            'display_name': 'Harvard University',
            'country_code': 'US',
            'type': 'education',
            'works_count': 150000,
            'cited_by_count': 2500000,
            'openalex_id': 'I123456789'
        },
        {
            'display_name': 'MIT',
            'country_code': 'US',
            'type': 'education',
            'works_count': 100000,
            'cited_by_count': 2000000,
            'openalex_id': 'I987654321'
        }
    ]


@pytest.fixture
def mock_source_results():
    """Mock source search results."""
    return [
        {
            'display_name': 'Nature',
            'issn_l': '1234-5678',
            'type': 'journal',
            'publisher': 'Nature Publishing Group',
            'works_count': 150000,
            'cited_by_count': 2500000,
            'openalex_id': 'S123456789'
        },
        {
            'display_name': 'Science',
            'issn_l': '9876-5432',
            'type': 'journal',
            'publisher': 'American Association for the Advancement of Science',
            'works_count': 100000,
            'cited_by_count': 2000000,
            'openalex_id': 'S987654321'
        }
    ]