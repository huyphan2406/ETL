"""
Custom exceptions for the Data Engineering project.
Provides specific exception types for better error handling.
"""


class DEException(Exception):
    """Base exception for all Data Engineering exceptions."""
    pass


class DatabaseConnectionError(DEException):
    """Raised when database connection fails."""
    pass


class DatabaseOperationError(DEException):
    """Raised when database operation fails."""
    pass


class DataValidationError(DEException):
    """Raised when data validation fails."""
    pass


class CDCProcessingError(DEException):
    """Raised when CDC processing fails."""
    pass


class SparkJobError(DEException):
    """Raised when Spark job fails."""
    pass


class ConfigurationError(DEException):
    """Raised when configuration is invalid or missing."""
    pass


class KafkaError(DEException):
    """Raised when Kafka operation fails."""
    pass

