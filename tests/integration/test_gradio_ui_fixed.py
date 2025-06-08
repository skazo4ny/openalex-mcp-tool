"""
Integration tests for Gradio UI wrapper functions.
"""

import pytest
from unittest.mock import Mock, patch
from app import (
    search_papers_ui,
    get_paper_by_doi_ui,
    search_authors_ui,
    search_concepts_ui,
    format_paper_results,
    format_author_results,
    format_concept_results
)


class TestGradioUIIntegration:
    """Test Gradio UI wrapper functions."""
    
    def test_search_papers_ui_success(self, mock_publication_results):
        """Test search_papers_ui returns formatted string."""
        with patch('app.search_openalex_papers') as mock_search:
            mock_search.return_value = mock_publication_results
            
            result = search_papers_ui("machine learning", max_results=2)
            
            assert isinstance(result, str)
            assert "Test Paper 1" in result
            assert "Test Paper 2" in result
            assert "DOI:" in result
            assert "Year:" in result
            
            mock_search.assert_called_once_with("machine learning", 2, None, None)
    
    def test_search_papers_ui_with_year_filters(self, mock_publication_results):
        """Test search_papers_ui with year filters."""
        with patch('app.search_openalex_papers') as mock_search:
            mock_search.return_value = mock_publication_results
            
            result = search_papers_ui("machine learning", 5, 2020, 2024)
            
            assert isinstance(result, str)
            mock_search.assert_called_once_with("machine learning", 5, 2020, 2024)
    
    def test_search_papers_ui_no_results(self):
        """Test search_papers_ui with no results."""
        with patch('app.search_openalex_papers') as mock_search:
            mock_search.return_value = []
            
            result = search_papers_ui("nonexistent query")
            
            assert isinstance(result, str)
            assert "No papers found" in result
    
    def test_search_papers_ui_error_handling(self):
        """Test search_papers_ui error handling."""
        with patch('app.search_openalex_papers') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            result = search_papers_ui("test")
            
            assert isinstance(result, str)
            assert "Error searching papers" in result
            assert "API Error" in result
    
    def test_get_paper_by_doi_ui_success(self, mock_work_response):
        """Test get_paper_by_doi_ui returns formatted string."""
        with patch('app.get_publication_by_doi') as mock_get:
            mock_get.return_value = mock_work_response
            
            result = get_paper_by_doi_ui("10.1038/nature12373")
            
            assert isinstance(result, str)
            assert "Test Paper" in result
            assert "10.1038/nature12373" in result
            assert "DOI:" in result
            
            mock_get.assert_called_once_with("10.1038/nature12373")
    
    def test_get_paper_by_doi_ui_not_found(self):
        """Test get_paper_by_doi_ui when paper not found."""
        with patch('app.get_publication_by_doi') as mock_get:
            mock_get.return_value = None
            
            result = get_paper_by_doi_ui("10.1000/nonexistent")
            
            assert isinstance(result, str)
            assert "No publication found for DOI" in result
            assert "10.1000/nonexistent" in result
    
    def test_get_paper_by_doi_ui_error_handling(self):
        """Test get_paper_by_doi_ui error handling."""
        with patch('app.get_publication_by_doi') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            result = get_paper_by_doi_ui("10.1038/nature12373")
            
            assert isinstance(result, str)
            assert "Error retrieving publication" in result
            assert "API Error" in result
    
    def test_search_authors_ui_success(self, mock_author_results):
        """Test search_authors_ui returns formatted string."""
        with patch('app.search_openalex_authors') as mock_search:
            mock_search.return_value = mock_author_results
            
            result = search_authors_ui("John Doe", max_results=3)
            
            assert isinstance(result, str)
            assert "John Doe" in result
            assert "Jane Smith" in result
            assert "ORCID:" in result
            assert "Works count:" in result
            
            mock_search.assert_called_once_with("John Doe", 3)
    
    def test_search_authors_ui_no_results(self):
        """Test search_authors_ui with no results."""
        with patch('app.search_openalex_authors') as mock_search:
            mock_search.return_value = []
            
            result = search_authors_ui("Nonexistent Author")
            
            assert isinstance(result, str)
            assert "No authors found" in result
    
    def test_search_authors_ui_error_handling(self):
        """Test search_authors_ui error handling."""
        with patch('app.search_openalex_authors') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            result = search_authors_ui("John Doe")
            
            assert isinstance(result, str)
            assert "Error searching authors" in result
            assert "API Error" in result
    
    def test_search_concepts_ui_success(self, mock_concept_results):
        """Test search_concepts_ui returns formatted string."""
        with patch('app.search_openalex_concepts') as mock_search:
            mock_search.return_value = mock_concept_results
            
            result = search_concepts_ui("machine learning", max_results=3)
            
            assert isinstance(result, str)
            assert "Machine Learning" in result
            assert "Deep Learning" in result
            assert "Level:" in result
            assert "Works count:" in result
            
            mock_search.assert_called_once_with("machine learning", 3)
    
    def test_search_concepts_ui_no_results(self):
        """Test search_concepts_ui with no results."""
        with patch('app.search_openalex_concepts') as mock_search:
            mock_search.return_value = []
            
            result = search_concepts_ui("Nonexistent Concept")
            
            assert isinstance(result, str)
            assert "No concepts found" in result
    
    def test_search_concepts_ui_error_handling(self):
        """Test search_concepts_ui error handling."""
        with patch('app.search_openalex_concepts') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            result = search_concepts_ui("machine learning")
            
            assert isinstance(result, str)
            assert "Error searching concepts" in result
            assert "API Error" in result


class TestFormattingFunctions:
    """Test result formatting functions."""
    
    def test_format_paper_results_multiple_papers(self, mock_publication_results):
        """Test formatting multiple paper results."""
        result = format_paper_results(mock_publication_results)
        
        assert isinstance(result, str)
        assert "1. Test Paper 1" in result
        assert "2. Test Paper 2" in result
        assert "DOI:" in result
        assert "Year:" in result
        assert "Authors:" in result
        assert "Abstract:" in result
    
    def test_format_paper_results_empty(self):
        """Test formatting empty paper results."""
        result = format_paper_results([])
        
        assert result == "No papers found."
    
    def test_format_paper_results_long_abstract(self):
        """Test formatting paper with long abstract."""
        paper = {
            'title': 'Test Paper',
            'doi': '10.1000/test',
            'abstract': 'A' * 400,  # Long abstract
            'authors': [{'display_name': 'Test Author'}],
            'publication_year': 2023
        }
        
        result = format_paper_results([paper])
        
        assert isinstance(result, str)
        assert "..." in result  # Should be truncated
        assert len(result.split("Abstract: ")[1].split("\n")[0]) <= 304  # 300 + "..."
    
    def test_format_author_results_multiple_authors(self, mock_author_results):
        """Test formatting multiple author results."""
        result = format_author_results(mock_author_results)
        
        assert isinstance(result, str)
        assert "1. John Doe" in result
        assert "2. Jane Smith" in result
        assert "ORCID:" in result
        assert "Affiliation:" in result
        assert "Works count:" in result
    
    def test_format_author_results_empty(self):
        """Test formatting empty author results."""
        result = format_author_results([])
        
        assert result == "No authors found."
    
    def test_format_concept_results_multiple_concepts(self, mock_concept_results):
        """Test formatting multiple concept results."""
        result = format_concept_results(mock_concept_results)
        
        assert isinstance(result, str)
        assert "1. Machine Learning" in result
        assert "2. Deep Learning" in result
        assert "Level:" in result
        assert "Works count:" in result
        assert "Description:" in result
    
    def test_format_concept_results_empty(self):
        """Test formatting empty concept results."""
        result = format_concept_results([])
        
        assert result == "No concepts found."
    
    def test_format_paper_results_many_authors(self):
        """Test formatting paper with many authors."""
        paper = {
            'title': 'Test Paper',
            'doi': '10.1000/test',
            'abstract': 'Test abstract',
            'authors': [{'display_name': f'Author {i}'} for i in range(10)],
            'publication_year': 2023
        }
        
        result = format_paper_results([paper])
        
        assert isinstance(result, str)
        assert "Author 0, Author 1, Author 2 and 7 others" in result
    
    def test_format_results_handle_missing_fields(self):
        """Test formatting functions handle missing fields gracefully."""
        # Test paper with missing fields
        paper = {'title': 'Minimal Paper'}
        result = format_paper_results([paper])
        assert "No DOI" in result
        assert "Unknown year" in result
        assert "No abstract available" in result
        
        # Test author with missing fields
        author = {'display_name': 'Minimal Author'}
        result = format_author_results([author])
        assert "No ORCID" in result
        assert "No affiliation" in result
        assert "Works count: 0" in result
        
        # Test concept with missing fields
        concept = {'display_name': 'Minimal Concept'}
        result = format_concept_results([concept])
        assert "No description" in result
        assert "Unknown level" in result
        assert "Works count: 0" in result
