"""Simple embedding service using Azure OpenAI."""

from typing import List
from openai import AzureOpenAI


class EmbeddingService:
    """Simple service for generating text embeddings."""

    def __init__(self, endpoint: str, api_key: str, deployment: str):
        """Initialize the embedding service."""
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01"
        )
        self.deployment = deployment

    def generate_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for text."""
        try:
            response = self.client.embeddings.create(
                model=self.deployment,
                input=text,
                dimensions=1536
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
