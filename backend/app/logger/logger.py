"""
This module initializes the logging configuration for the FastAPI application
and provides a logging middleware class. The logging configuration is loaded
from a JSON file and applied using the logging configuration dictionary. The
LoggerMiddleware class logs details of each incoming HTTP request and the
corresponding response, including the request method, URL, and response status
code. This module is essential for monitoring and debugging the application by
capturing detailed logs.
"""

# Standard Libraries
from logging import getLogger
from logging.config import dictConfig
from json import load

# External Libraries
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Read logging configuration
with open(file="app/logger/config.json", mode="r", encoding="utf-8") as f:
    logging_config: dict = load(f)
f.close()

# Configure logging
dictConfig(logging_config)
logger = getLogger("altron_api")


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Logging middleware for the FastAPI application.
    """

    async def dispatch(self, request: Request, call_next):
        """
        This method is invoked for every incoming request and is responsible
        for logging the request and response details. The request details
        include the request method and URL, while the response details include
        the response status code. This method is an implementation of the
        abstract method from the BaseHTTPMiddleware class provided by
        the Starlette framework.
        """
        logger.info("Request: %s %s", request.method, request.url)
        response = await call_next(request)
        logger.info("Response: %s", response.status_code)
        return response
