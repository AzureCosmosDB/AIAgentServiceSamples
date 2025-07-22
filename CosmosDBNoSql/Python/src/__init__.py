"""Main package initialization for the AI Agent application."""

from .services import EmbeddingService, CosmosService
from .functions import user_functions

__version__ = "1.0.0"
__all__ = ["EmbeddingService", "CosmosService", "user_functions"]
