"""
Unit tests for ConfigManager.
"""

import pytest
import os
import yaml
from unittest.mock import patch, mock_open
from slr_modules.config_manager import ConfigManager

class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_init_with_config_file(self, tmp_path):
        """Test ConfigManager initialization with config file."""
        config_data = {'test': {'key': 'value'}}
        config_file = tmp_path / "test_config.yaml"
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config_manager = ConfigManager(str(config_file))
        assert config_manager.get('test.key') == 'value'
    
    def test_init_without_config_file(self):
        """Test ConfigManager initialization without config file."""
        # Use a non-existent path to test empty config
        config_manager = ConfigManager("nonexistent_config.yaml")
        assert config_manager.config == {}
    
    def test_get_existing_key(self, config_manager):
        """Test getting existing configuration key."""
        result = config_manager.get('openalex.timeout')
        assert result == 30
    
    def test_get_nonexistent_key_with_default(self, config_manager):
        """Test getting non-existent key with default value."""
        result = config_manager.get('nonexistent.key', 'default')
        assert result == 'default'
    
    def test_get_nested_key(self, config_manager):
        """Test getting nested configuration key."""
        result = config_manager.get('openalex.base_url')
        assert result == 'https://api.openalex.org'
    
    @patch.dict(os.environ, {'OPENALEX_EMAIL': 'test@example.com'})
    def test_get_openalex_email_from_env(self):
        """Test getting OpenAlex email from environment variable."""
        config_manager = ConfigManager()
        result = config_manager.get_openalex_email()
        assert result == 'test@example.com'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_openalex_email_missing(self):
        """Test getting OpenAlex email when not set."""
        config_manager = ConfigManager()
        result = config_manager.get_openalex_email()
        assert result is None
    
    def test_get_with_dot_notation(self, config_manager):
        """Test getting values with dot notation."""
        result = config_manager.get('app.name')
        assert result == 'OpenAlex Explorer MCP Server'
    
    def test_get_invalid_dot_notation(self, config_manager):
        """Test getting values with invalid dot notation."""
        result = config_manager.get('invalid.deep.key', 'fallback')
        assert result == 'fallback'
