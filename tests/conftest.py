"""
Pytest configuration and shared fixtures for OpenAlex MCP Server tests.
"""

import pytest
import os
import yaml
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from slr_modules.config_manager import ConfigManager
from slr_modules.api_clients import OpenAlexAPIClient

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return {
        'openalex': {
            'base_url': 'https://api.openalex.org',
            'timeout': 30,
            'retries': 2,
            'default_per_page': 10,
            'max_per_page': 50
        },
        'app': {
            'name': 'OpenAlex Explorer MCP Server',
            'version': '1.0.0'
        }
    }

@pytest.fixture
def config_manager(test_config, tmp_path):
    """ConfigManager fixture with test configuration."""
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(test_config, f)
    
    with patch.dict(os.environ, {'OPENALEX_EMAIL': 'test@example.com'}):
        return ConfigManager(str(config_file))

@pytest.fixture
def api_client(config_manager):
    """OpenAlexAPIClient fixture."""
    return OpenAlexAPIClient(config_manager)

@pytest.fixture
def mock_work_response():
    """Mock OpenAlex work response."""
    return {
        "id": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.1038/nature12373",
        "title": "Test Paper",
        "publication_year": 2023,
        "publication_date": "2023-06-15",
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A1234567890",
                    "display_name": "Test Author",
                    "orcid": "https://orcid.org/0000-0000-0000-0000"
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I1234567890",
                        "display_name": "Stanford University"
                    }
                ]
            }
        ],
        "abstract_inverted_index": {
            "This": [0],
            "is": [1], 
            "a": [2],
            "comprehensive": [3],
            "test": [4],
            "abstract": [5]
        },
        "cited_by_count": 100,
        "concepts": [
            {
                "id": "https://openalex.org/C41008148",
                "display_name": "Machine learning",
                "level": 1,
                "score": 0.95
            }
        ]
    }

@pytest.fixture
def mock_author_response():
    """Mock OpenAlex author response."""
    return {
        "id": "https://openalex.org/A1234567890",
        "display_name": "Jane Smith",
        "orcid": "https://orcid.org/0000-0000-0000-0000",
        "works_count": 42,
        "cited_by_count": 1250,
        "last_known_institution": {
            "id": "https://openalex.org/I1234567890",
            "display_name": "Stanford University"
        },
        "concepts": [
            {
                "id": "https://openalex.org/C41008148",
                "display_name": "Machine learning",
                "score": 0.95
            }
        ]
    }

@pytest.fixture
def mock_concept_response():
    """Mock OpenAlex concept response."""
    return {
        "id": "https://openalex.org/C41008148",
        "display_name": "Machine learning",
        "description": "A subset of artificial intelligence",
        "level": 1,
        "works_count": 125000,
        "cited_by_count": 2500000,
        "ancestors": [
            {
                "id": "https://openalex.org/C154945302",
                "display_name": "Artificial intelligence"
            }
        ]
    }

@pytest.fixture
def mock_search_response(mock_work_response):
    """Mock OpenAlex search response."""
    return {
        "results": [mock_work_response],
        "count": 1,
        "meta": {
            "count": 1,
            "page": 1,
            "per_page": 10
        }
    }

@pytest.fixture
def publication_retriever(api_client):
    """OpenAlexPublicationRetriever fixture."""
    from openalex_modules.openalex_publication_retriever import OpenAlexPublicationRetriever
    return OpenAlexPublicationRetriever(api_client)

@pytest.fixture
def author_retriever(api_client):
    """OpenAlexAuthorRetriever fixture."""
    from openalex_modules.openalex_author_retriever import OpenAlexAuthorRetriever
    return OpenAlexAuthorRetriever(api_client)

@pytest.fixture
def concept_retriever(api_client):
    """OpenAlexConceptRetriever fixture."""
    from openalex_modules.openalex_concept_retriever import OpenAlexConceptRetriever
    return OpenAlexConceptRetriever(api_client)

@pytest.fixture
def mock_publication_results():
    """Mock publication search results."""
    return [
        {
            'title': 'Test Paper 1',
            'doi': '10.1000/test1',
            'abstract': 'This is a test abstract for paper 1',
            'authors': [{'display_name': 'John Doe'}, {'display_name': 'Jane Smith'}],
            'publication_year': 2023,
            'cited_by_count': 50,
            'openalex_id': 'W123456789'
        },
        {
            'title': 'Test Paper 2',
            'doi': '10.1000/test2',
            'abstract': 'This is a test abstract for paper 2',
            'authors': [{'display_name': 'Alice Johnson'}],
            'publication_year': 2022,
            'cited_by_count': 25,
            'openalex_id': 'W987654321'
        }
    ]

@pytest.fixture
def mock_author_results():
    """Mock author search results."""
    return [
        {
            'display_name': 'John Doe',
            'orcid': 'https://orcid.org/0000-0000-0000-0001',
            'works_count': 50,
            'cited_by_count': 1000,
            'affiliation': {'display_name': 'Test University'},
            'openalex_id': 'A123456789'
        },
        {
            'display_name': 'Jane Smith',
            'orcid': 'https://orcid.org/0000-0000-0000-0002',
            'works_count': 75,
            'cited_by_count': 1500,
            'affiliation': {'display_name': 'Another University'},
            'openalex_id': 'A987654321'
        }
    ]

@pytest.fixture
def mock_concept_results():
    """Mock concept search results."""
    return [
        {
            'display_name': 'Machine Learning',
            'description': 'A subset of artificial intelligence',
            'level': 1,
            'works_count': 100000,
            'cited_by_count': 2000000,
            'openalex_id': 'C123456789'
        },
        {
            'display_name': 'Deep Learning',
            'description': 'A subset of machine learning',
            'level': 2,
            'works_count': 50000,
            'cited_by_count': 1000000,
            'openalex_id': 'C987654321'
        }
    ]

@pytest.fixture 
def mock_work_response():
    """Mock single work response with complete data."""
    return {
        'title': 'Test Paper',
        'doi': '10.1038/nature12373',
        'abstract': 'This is a comprehensive test abstract for the paper',
        'authors': [
            {'display_name': 'Test Author', 'orcid': '0000-0000-0000-0000'}
        ],
        'publication_year': 2023,
        'cited_by_count': 100,
        'openalex_id': 'W2741809807',
        'venue': {'display_name': 'Nature'},
        'open_access': {'is_oa': True}
    }
