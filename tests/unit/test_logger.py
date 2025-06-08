"""
Unit tests for DailyRotatingLogger.
"""

import pytest
import os
import json
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from slr_modules.logger import DailyRotatingLogger

class TestDailyRotatingLogger:
    """Test DailyRotatingLogger functionality."""
    
    @pytest.fixture
    def logger(self, tmp_path):
        """DailyRotatingLogger fixture with temporary directory."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return DailyRotatingLogger("test_logger", str(log_dir))
    
    def test_init_creates_log_directory(self, tmp_path):
        """Test DailyRotatingLogger initialization creates log directory."""
        log_dir = tmp_path / "new_logs"
        logger = DailyRotatingLogger("test", str(log_dir))
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_init_with_existing_directory(self, tmp_path):
        """Test DailyRotatingLogger initialization with existing directory."""
        log_dir = tmp_path / "existing_logs"
        log_dir.mkdir()
        
        logger = DailyRotatingLogger("test", str(log_dir))
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_debug_logging(self, logger):
        """Test debug level logging."""
        logger.debug("Test debug message", test_key="test_value")
        # Should not raise exception
    
    def test_info_logging(self, logger):
        """Test info level logging."""
        logger.info("Test info message", test_key="test_value")
        # Should not raise exception
    
    def test_warning_logging(self, logger):
        """Test warning level logging."""
        logger.warning("Test warning message", test_key="test_value")
        # Should not raise exception
    
    def test_error_logging(self, logger):
        """Test error level logging."""
        logger.error("Test error message", test_key="test_value")
        # Should not raise exception
    
    def test_log_startup(self, logger):
        """Test startup logging."""
        app_info = {
            "app_name": "test_app",
            "version": "1.0.0"
        }
        logger.log_startup(app_info)
        # Should not raise exception
    
    def test_log_error_with_exception(self, logger):
        """Test error logging with exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            logger.log_error(e, "test context")
        # Should not raise exception
    
    def test_log_performance(self, logger):
        """Test performance logging."""
        logger.log_performance("test_operation", 0.5, param1="value1")
        # Should not raise exception
    
    def test_log_request(self, logger):
        """Test request logging."""
        logger.log_request("/test/endpoint", "GET", {"param": "value"}, 100.0)
        # Should not raise exception
    
    def test_log_mcp_call_success(self, logger):
        """Test MCP call logging on success."""
        args = {"query": "test"}
        result = {"results": []}
        logger.log_mcp_call("test_tool", args, result)
        # Should not raise exception
    
    def test_log_mcp_call_error(self, logger):
        """Test MCP call logging on error."""
        args = {"query": "test"}
        logger.log_mcp_call("test_tool", args, error="Test error")
        # Should not raise exception
