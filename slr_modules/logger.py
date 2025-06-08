"""
Enhanced logging module for OpenAlex MCP Server
Provides JSON and XML logging with daily rotation
"""

import logging
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry["extra_data"] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


class XMLFormatter(logging.Formatter):
    """Custom formatter for XML logging"""
    
    def format(self, record):
        root = ET.Element("log_entry")
        
        # Basic fields
        ET.SubElement(root, "timestamp").text = datetime.fromtimestamp(record.created).isoformat()
        ET.SubElement(root, "level").text = record.levelname
        ET.SubElement(root, "logger").text = record.name
        ET.SubElement(root, "message").text = record.getMessage()
        ET.SubElement(root, "module").text = record.module
        ET.SubElement(root, "function").text = record.funcName
        ET.SubElement(root, "line").text = str(record.lineno)
        ET.SubElement(root, "thread").text = str(record.thread)
        ET.SubElement(root, "process").text = str(record.process)
        
        # Add exception info if present
        if record.exc_info:
            exception_elem = ET.SubElement(root, "exception")
            ET.SubElement(exception_elem, "type").text = record.exc_info[0].__name__ if record.exc_info[0] else ""
            ET.SubElement(exception_elem, "message").text = str(record.exc_info[1]) if record.exc_info[1] else ""
            traceback_elem = ET.SubElement(exception_elem, "traceback")
            traceback_elem.text = ''.join(traceback.format_exception(*record.exc_info))
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            extra_elem = ET.SubElement(root, "extra_data")
            for key, value in record.extra_data.items():
                field_elem = ET.SubElement(extra_elem, key)
                field_elem.text = str(value)
        
        return ET.tostring(root, encoding='unicode')


class DailyRotatingLogger:
    """Logger with daily rotation for JSON and XML formats"""
    
    def __init__(self, name: str = "openalex_mcp", logs_dir: str = "logs"):
        self.name = name
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
        
        # Log startup
        self.logger.info("Logger initialized", extra={
            'extra_data': {
                'logs_directory': str(self.logs_dir.absolute()),
                'logger_name': name,
                'startup_time': datetime.now().isoformat()
            }
        })
    
    def _setup_handlers(self):
        """Setup console, JSON, and XML handlers"""
        today = datetime.now().strftime("%Y%m%d")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # JSON file handler
        json_file = self.logs_dir / f"{self.name}_{today}.json"
        json_handler = logging.FileHandler(json_file, mode='a', encoding='utf-8')
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_handler)
        
        # XML file handler
        xml_file = self.logs_dir / f"{self.name}_{today}.xml"
        xml_handler = logging.FileHandler(xml_file, mode='a', encoding='utf-8')
        xml_handler.setLevel(logging.DEBUG)
        xml_handler.setFormatter(XMLFormatter())
        
        # Write XML header if file is new
        if not xml_file.exists() or xml_file.stat().st_size == 0:
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n<logs>\n')
        
        self.logger.addHandler(xml_handler)
    
    def log_request(self, endpoint: str, method: str, params: Dict[str, Any], 
                   response_time: Optional[float] = None, status: str = "success"):
        """Log API request details"""
        self.logger.info(f"API Request: {method} {endpoint}", extra={
            'extra_data': {
                'endpoint': endpoint,
                'method': method,
                'parameters': params,
                'response_time_ms': response_time,
                'status': status,
                'request_type': 'api_request'
            }
        })
    
    def log_mcp_call(self, tool_name: str, args: Dict[str, Any], 
                     result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """Log MCP tool calls"""
        level = logging.ERROR if error else logging.INFO
        message = f"MCP Tool: {tool_name}"
        if error:
            message += f" - ERROR: {error}"
        
        extra_data = {
            'tool_name': tool_name,
            'arguments': args,
            'call_type': 'mcp_tool'
        }
        
        if result:
            extra_data['result_summary'] = {
                'success': True,
                'result_keys': list(result.keys()) if isinstance(result, dict) else None,
                'result_type': type(result).__name__
            }
        
        if error:
            extra_data['error'] = error
            extra_data['result_summary'] = {'success': False}
        
        self.logger.log(level, message, extra={'extra_data': extra_data})
    
    def log_startup(self, app_info: Dict[str, Any]):
        """Log application startup information"""
        self.logger.info("Application starting", extra={
            'extra_data': {
                **app_info,
                'event_type': 'startup'
            }
        })
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with full context"""
        self.logger.error(f"Error in {context}: {str(error)}", 
                         exc_info=True, 
                         extra={'extra_data': {
                             'error_context': context,
                             'error_type': type(error).__name__
                         }})
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        self.logger.info(f"Performance: {operation}", extra={
            'extra_data': {
                'operation': operation,
                'duration_ms': duration * 1000,
                'performance_type': 'timing',
                **kwargs
            }
        })
    
    def debug(self, message: str, **kwargs):
        """Debug level logging"""
        self.logger.debug(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def info(self, message: str, **kwargs):
        """Info level logging"""
        self.logger.info(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def warning(self, message: str, **kwargs):
        """Warning level logging"""
        self.logger.warning(message, extra={'extra_data': kwargs} if kwargs else None)
    
    def error(self, message: str, **kwargs):
        """Error level logging"""
        self.logger.error(message, extra={'extra_data': kwargs} if kwargs else None)


# Global logger instance
_global_logger = None

def get_logger() -> DailyRotatingLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = DailyRotatingLogger()
    return _global_logger

def setup_logging(name: str = "openalex_mcp", logs_dir: str = "logs") -> DailyRotatingLogger:
    """Setup and return a logger instance"""
    return DailyRotatingLogger(name, logs_dir)
