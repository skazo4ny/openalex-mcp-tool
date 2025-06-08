"""
Integration tests for MCP tool functions.
"""

import pytest
from unittest.mock import Mock, patch
from app import (
    search_openalex_papers,
    get_publication_by_doi,
    search_openalex_authors,
    search_openalex_concepts
)


class TestMCPToolIntegration:
    """Test MCP tool functions integration."""
    
    def test_search_openalex_papers_success(self, mock_publication_results):
        """Test search_openalex_papers returns JSON data."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.search_publications.return_value = mock_publication_results
            
            result = search_openalex_papers("machine learning", max_results=2)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['title'] == 'Test Paper 1'
            assert result[1]['title'] == 'Test Paper 2'
            
            mock_retriever.search_publications.assert_called_once_with(
                query="machine learning",
                max_results=2,
                start_year=None,
                end_year=None
            )
    
    def test_search_openalex_papers_with_year_filters(self, mock_publication_results):
        """Test search_openalex_papers with year filters."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.search_publications.return_value = mock_publication_results
            
            result = search_openalex_papers(
                "machine learning", 
                max_results=5,
                start_year=2020,
                end_year=2024
            )
            
            assert isinstance(result, list)
            mock_retriever.search_publications.assert_called_once_with(
                query="machine learning",
                max_results=5,
                start_year=2020,
                end_year=2024
            )
    
    def test_search_openalex_papers_empty_results(self):
        """Test search_openalex_papers with no results."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.search_publications.return_value = []
            
            result = search_openalex_papers("nonexistent query")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_papers_error_handling(self):
        """Test search_openalex_papers error handling."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.search_publications.side_effect = Exception("API Error")
            
            result = search_openalex_papers("test")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_get_publication_by_doi_success(self, mock_work_response):
        """Test get_publication_by_doi returns JSON data."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.get_by_doi.return_value = mock_work_response
            
            result = get_publication_by_doi("10.1038/nature12373")
            
            assert isinstance(result, dict)
            assert result['title'] == 'Test Paper'
            assert result['doi'] == '10.1038/nature12373'
            
            mock_retriever.get_by_doi.assert_called_once_with("10.1038/nature12373")
    
    def test_get_publication_by_doi_not_found(self):
        """Test get_publication_by_doi when paper not found."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.get_by_doi.return_value = None
            
            result = get_publication_by_doi("10.1000/nonexistent")
            
            assert result is None
    
    def test_get_publication_by_doi_error_handling(self):
        """Test get_publication_by_doi error handling."""
        with patch('app.publication_retriever') as mock_retriever:
            mock_retriever.get_by_doi.side_effect = Exception("API Error")
            
            result = get_publication_by_doi("10.1038/nature12373")
            
            assert result is None
    
    def test_search_openalex_authors_success(self, mock_author_results):
        """Test search_openalex_authors returns JSON data."""
        with patch('app.author_retriever') as mock_retriever:
            mock_retriever.search_authors.return_value = mock_author_results
            
            result = search_openalex_authors("John Doe", max_results=3)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['display_name'] == 'John Doe'
            assert result[1]['display_name'] == 'Jane Smith'
            
            mock_retriever.search_authors.assert_called_once_with(
                name="John Doe",
                max_results=3
            )
    
    def test_search_openalex_authors_empty_results(self):
        """Test search_openalex_authors with no results."""
        with patch('app.author_retriever') as mock_retriever:
            mock_retriever.search_authors.return_value = []
            
            result = search_openalex_authors("Nonexistent Author")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_authors_error_handling(self):
        """Test search_openalex_authors error handling."""
        with patch('app.author_retriever') as mock_retriever:
            mock_retriever.search_authors.side_effect = Exception("API Error")
            
            result = search_openalex_authors("John Doe")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_concepts_success(self, mock_concept_results):
        """Test search_openalex_concepts returns JSON data."""
        with patch('app.concept_retriever') as mock_retriever:
            mock_retriever.search_concepts.return_value = mock_concept_results
            
            result = search_openalex_concepts("machine learning", max_results=3)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, dict) for item in result)
            assert result[0]['display_name'] == 'Machine Learning'
            assert result[1]['display_name'] == 'Deep Learning'
            
            mock_retriever.search_concepts.assert_called_once_with(
                name="machine learning",
                max_results=3
            )
    
    def test_search_openalex_concepts_empty_results(self):
        """Test search_openalex_concepts with no results."""
        with patch('app.concept_retriever') as mock_retriever:
            mock_retriever.search_concepts.return_value = []
            
            result = search_openalex_concepts("Nonexistent Concept")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_search_openalex_concepts_error_handling(self):
        """Test search_openalex_concepts error handling."""
        with patch('app.concept_retriever') as mock_retriever:
            mock_retriever.search_concepts.side_effect = Exception("API Error")
            
            result = search_openalex_concepts("machine learning")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_mcp_functions_return_proper_json_structure(self):
        """Test that all MCP functions return proper JSON structures."""
        # Test data structures
        mock_paper = {
            'title': 'Test Paper',
            'doi': '10.1000/test',
            'authors': [{'display_name': 'Test Author'}],
            'abstract': 'Test abstract',
            'publication_year': 2023
        }
        
        mock_author = {
            'display_name': 'Test Author',
            'orcid': '0000-0000-0000-0000',
            'works_count': 10,
            'affiliation': {'display_name': 'Test University'}
        }
        
        mock_concept = {
            'display_name': 'Test Concept',
            'description': 'Test description',
            'level': 1,
            'works_count': 1000
        }
        
        with patch('app.publication_retriever') as mock_pub_retriever:
            with patch('app.author_retriever') as mock_auth_retriever:
                with patch('app.concept_retriever') as mock_concept_retriever:
                    
                    # Setup mocks
                    mock_pub_retriever.search_publications.return_value = [mock_paper]
                    mock_pub_retriever.get_by_doi.return_value = mock_paper
                    mock_auth_retriever.search_authors.return_value = [mock_author]
                    mock_concept_retriever.search_concepts.return_value = [mock_concept]
                    
                    # Test search_openalex_papers
                    papers_result = search_openalex_papers("test")
                    assert isinstance(papers_result, list)
                    assert isinstance(papers_result[0], dict)
                    assert 'title' in papers_result[0]
                    
                    # Test get_publication_by_doi
                    doi_result = get_publication_by_doi("10.1000/test")
                    assert isinstance(doi_result, dict)
                    assert 'title' in doi_result
                    
                    # Test search_openalex_authors
                    authors_result = search_openalex_authors("test")
                    assert isinstance(authors_result, list)
                    assert isinstance(authors_result[0], dict)
                    assert 'display_name' in authors_result[0]
                    
                    # Test search_openalex_concepts
                    concepts_result = search_openalex_concepts("test")
                    assert isinstance(concepts_result, list)
                    assert isinstance(concepts_result[0], dict)
                    assert 'display_name' in concepts_result[0]
