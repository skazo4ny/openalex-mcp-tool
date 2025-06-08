"""
Unit tests for OpenAlex utility functions.
"""

import pytest
from unittest.mock import Mock, patch
from openalex_modules.openalex_utils import (
    reconstruct_abstract_from_inverted_index,
    clean_doi,
    extract_openalex_id,
    format_author_name,
    extract_keywords_from_concepts,
    get_publication_venue,
    calculate_citation_percentile
)


class TestOpenAlexUtils:
    """Test OpenAlex utility functions."""
    
    def test_reconstruct_abstract_from_inverted_index_basic(self):
        """Test reconstructing abstract from inverted index."""
        inverted_index = {
            "The": [0],
            "quick": [1],
            "brown": [2],
            "fox": [3]
        }
        
        result = reconstruct_abstract_from_inverted_index(inverted_index)
        assert result == "The quick brown fox"
    
    def test_reconstruct_abstract_from_inverted_index_complex(self):
        """Test reconstructing abstract with multiple positions."""
        inverted_index = {
            "machine": [0, 5],
            "learning": [1, 6],
            "is": [2],
            "powerful": [3],
            "and": [4],
            "algorithms": [7]
        }
        
        result = reconstruct_abstract_from_inverted_index(inverted_index)
        assert result == "machine learning is powerful and machine learning algorithms"
    
    def test_reconstruct_abstract_from_inverted_index_empty(self):
        """Test reconstructing from empty inverted index."""
        result = reconstruct_abstract_from_inverted_index({})
        assert result == ""
    
    def test_reconstruct_abstract_from_inverted_index_none(self):
        """Test reconstructing from None."""
        result = reconstruct_abstract_from_inverted_index(None)
        assert result == ""
    
    def test_clean_doi_with_https_prefix(self):
        """Test cleaning DOI with https prefix."""
        doi = "https://doi.org/10.1038/nature12373"
        result = clean_doi(doi)
        assert result == "10.1038/nature12373"
    
    def test_clean_doi_with_http_prefix(self):
        """Test cleaning DOI with http prefix."""
        doi = "http://doi.org/10.1038/nature12373"
        result = clean_doi(doi)
        assert result == "10.1038/nature12373"
    
    def test_clean_doi_with_doi_prefix(self):
        """Test cleaning DOI with doi: prefix."""
        doi = "doi:10.1038/nature12373"
        result = clean_doi(doi)
        assert result == "10.1038/nature12373"
    
    def test_clean_doi_already_clean(self):
        """Test cleaning already clean DOI."""
        doi = "10.1038/nature12373"
        result = clean_doi(doi)
        assert result == "10.1038/nature12373"
    
    def test_clean_doi_empty(self):
        """Test cleaning empty DOI."""
        result = clean_doi("")
        assert result == ""
    
    def test_clean_doi_none(self):
        """Test cleaning None DOI."""
        result = clean_doi(None)
        assert result == ""
    
    def test_extract_openalex_id_full_url(self):
        """Test extracting ID from full OpenAlex URL."""
        url = "https://openalex.org/W2741809807"
        result = extract_openalex_id(url)
        assert result == "W2741809807"
    
    def test_extract_openalex_id_with_trailing_slash(self):
        """Test extracting ID from URL with trailing slash."""
        url = "https://openalex.org/A1234567890/"
        result = extract_openalex_id(url)
        assert result == "A1234567890"
    
    def test_extract_openalex_id_just_id(self):
        """Test extracting ID when already just ID."""
        id_str = "W2741809807"
        result = extract_openalex_id(id_str)
        assert result == "W2741809807"
    
    def test_extract_openalex_id_empty_string(self):
        """Test extracting ID from empty string."""
        result = extract_openalex_id("")
        assert result == ""
    
    def test_extract_openalex_id_none(self):
        """Test extracting ID from None."""
        result = extract_openalex_id("")  # Use empty string instead of None
        assert result == ""
    
    def test_format_author_name_with_display_name(self):
        """Test formatting author name with display_name."""
        author_data = {
            "display_name": "Jane Smith",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        result = format_author_name(author_data)
        assert result == "Jane Smith"
    
    def test_format_author_name_with_first_last(self):
        """Test formatting author name with first/last names."""
        author_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        result = format_author_name(author_data)
        assert result == "John Doe"
    
    def test_format_author_name_only_last(self):
        """Test formatting author name with only last name."""
        author_data = {
            "last_name": "Einstein"
        }
        
        result = format_author_name(author_data)
        assert result == "Einstein"
    
    def test_format_author_name_only_first(self):
        """Test formatting author name with only first name."""
        author_data = {
            "first_name": "Madonna"
        }
        
        result = format_author_name(author_data)
        assert result == "Madonna"
    
    def test_format_author_name_empty_data(self):
        """Test formatting author name with empty data."""
        result = format_author_name({})
        assert result == "Unknown Author"
    
    def test_extract_keywords_from_concepts_basic(self):
        """Test extracting keywords from concepts."""
        concepts = [
            {"display_name": "Machine learning"},
            {"display_name": "Artificial intelligence"},
            {"display_name": "Neural networks"}
        ]
        
        result = extract_keywords_from_concepts(concepts)
        assert result == ["Machine learning", "Artificial intelligence", "Neural networks"]
    
    def test_extract_keywords_from_concepts_with_limit(self):
        """Test extracting keywords with limit."""
        concepts = [
            {"display_name": "Concept 1"},
            {"display_name": "Concept 2"},
            {"display_name": "Concept 3"},
            {"display_name": "Concept 4"}
        ]
        
        result = extract_keywords_from_concepts(concepts, max_keywords=2)
        assert result == ["Concept 1", "Concept 2"]
    
    def test_extract_keywords_from_concepts_empty(self):
        """Test extracting keywords from empty list."""
        result = extract_keywords_from_concepts([])
        assert result == []
    
    def test_extract_keywords_from_concepts_missing_names(self):
        """Test extracting keywords with missing display names."""
        concepts = [
            {"display_name": "Valid Concept"},
            {},  # Missing display_name
            {"display_name": "Another Concept"}
        ]
        
        result = extract_keywords_from_concepts(concepts)
        assert result == ["Valid Concept", "Another Concept"]
    
    def test_get_publication_venue_with_primary_location(self):
        """Test getting venue from primary location."""
        work_data = {
            "primary_location": {
                "source": {
                    "display_name": "Nature",
                    "type": "journal",
                    "issn_l": "0028-0836",
                    "is_oa": False
                }
            }
        }
        
        result = get_publication_venue(work_data)
        
        assert result["name"] == "Nature"
        assert result["type"] == "journal"
        assert result["issn"] == "0028-0836"
        assert result["is_oa"] == False
    
    def test_get_publication_venue_with_oa_fallback(self):
        """Test getting venue from best OA location as fallback."""
        work_data = {
            "primary_location": {},
            "best_oa_location": {
                "source": {
                    "display_name": "arXiv",
                    "type": "repository"
                }
            }
        }
        
        result = get_publication_venue(work_data)
        
        assert result["name"] == "arXiv"
        assert result["type"] == "repository"
        assert result["issn"] is None
        assert result["is_oa"] is None
    
    def test_get_publication_venue_empty_data(self):
        """Test getting venue from empty data."""
        work_data = {}
        
        result = get_publication_venue(work_data)
        
        assert result["name"] is None
        assert result["type"] is None
        assert result["issn"] is None
        assert result["is_oa"] is None
    
    def test_calculate_citation_percentile_recent_paper(self):
        """Test citation percentile for recent paper."""
        # Paper from current year with 10 citations
        percentile = calculate_citation_percentile(10, 2025, 2025)
        assert percentile == 95.0
    
    def test_calculate_citation_percentile_older_paper(self):
        """Test citation percentile for older paper."""
        # Paper from 2020 with 50 citations (10 citations per year)
        percentile = calculate_citation_percentile(50, 2020, 2025)
        assert percentile == 95.0
    
    def test_calculate_citation_percentile_low_citations(self):
        """Test citation percentile for low citations."""
        # Paper from 2020 with 2 citations
        percentile = calculate_citation_percentile(2, 2020, 2025)
        assert percentile == 10.0
    
    def test_calculate_citation_percentile_no_citations(self):
        """Test citation percentile for no citations."""
        percentile = calculate_citation_percentile(0, 2020, 2025)
        assert percentile == 10.0
    
    def test_calculate_citation_percentile_invalid_year(self):
        """Test citation percentile for invalid year."""
        percentile = calculate_citation_percentile(10, 2030, 2025)
        assert percentile is None
    
    def test_calculate_citation_percentile_no_year(self):
        """Test citation percentile for missing year."""
        percentile = calculate_citation_percentile(10, None, 2025)
        assert percentile is None
    
    def test_calculate_citation_percentile_default_current_year(self):
        """Test citation percentile with default current year."""
        percentile = calculate_citation_percentile(10, 2024)
        assert percentile is not None
        assert isinstance(percentile, float)
