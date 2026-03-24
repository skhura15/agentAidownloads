"""
Logging Service

Provides centralized logging with Azure Application Insights integration
and structured logging capabilities.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json

from opencensus.ext.azure.log_exporter import AzureLogHandler  # type: ignore


class LoggingService:
    """
    Centralized logging service with:
    - Console logging
    - File logging
    - Azure Application Insights integration
    - Structured logging support
    """
    
    _loggers = {}
    _app_insights_connection_string = None
    _log_level = logging.INFO
    
    @classmethod
    def configure(
        cls,
        log_level: int = logging.INFO,
        app_insights_connection_string: Optional[str] = None,
        log_file: Optional[str] = None
    ) -> None:
        """
        Configure global logging settings.
        
        Args:
            log_level: Logging level (e.g., logging.INFO)
            app_insights_connection_string: Azure Application Insights connection string
            log_file: Optional file path for logging
        """
        cls._log_level = log_level
        cls._app_insights_connection_string = app_insights_connection_string
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(console_formatter)
            root_logger.addHandler(file_handler)
        
        # Azure Application Insights handler
        if app_insights_connection_string:
            try:
                azure_handler = AzureLogHandler(
                    connection_string=app_insights_connection_string
                )
                azure_handler.setLevel(log_level)
                root_logger.addHandler(azure_handler)
                logging.info("Azure Application Insights logging enabled")
            except Exception as e:
                logging.warning(f"Failed to initialize Azure Application Insights: {str(e)}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance.
        
        Args:
            name: Logger name (typically module or class name)
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(cls._log_level)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @staticmethod
    def log_structured(
        logger: logging.Logger,
        level: int,
        message: str,
        **kwargs
    ) -> None:
        """
        Log a structured message with additional context.
        
        Args:
            logger: Logger instance
            level: Log level
            message: Log message
            **kwargs: Additional structured data
        """
        structured_data = {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.log(level, json.dumps(structured_data))
    
    @staticmethod
    def log_agent_activity(
        logger: logging.Logger,
        agent_id: str,
        agent_name: str,
        action: str,
        details: Optional[dict] = None
    ) -> None:
        """
        Log agent activity with structured format.
        
        Args:
            logger: Logger instance
            agent_id: Agent identifier
            agent_name: Agent name
            action: Action performed
            details: Additional details
        """
        LoggingService.log_structured(
            logger,
            logging.INFO,
            f"Agent activity: {action}",
            agent_id=agent_id,
            agent_name=agent_name,
            action=action,
            details=details or {}
        )
    
    @staticmethod
    def log_api_request(
        logger: logging.Logger,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log API request with structured format.
        
        Args:
            logger: Logger instance
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: Optional user identifier
        """
        LoggingService.log_structured(
            logger,
            logging.INFO,
            f"API request: {method} {endpoint}",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id
        )
