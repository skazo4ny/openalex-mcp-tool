"""
Configuration Manager

Handles loading and managing configuration from YAML files
and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading from YAML files and environment variables."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        if config_path is None:
            # Default to config/slr_config.yaml relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "slr_config.yaml")
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    config = yaml.safe_load(file) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                logger.warning(f"Configuration file not found at {self.config_path}. Using defaults.")
                return {}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key, supporting nested keys with dot notation.
        
        Args:
            key: Configuration key (supports dot notation like 'openalex.base_url')
            default: Default value if key is not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_openalex_email(self) -> Optional[str]:
        """Get OpenAlex email from environment variable."""
        return os.getenv('OPENALEX_EMAIL')
    
    def get_openalex_config(self) -> Dict[str, Any]:
        """Get OpenAlex-specific configuration."""
        return self.get('openalex', {})
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search-specific configuration."""
        return self.get('search', {})
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application-specific configuration."""
        return self.get('app', {})
