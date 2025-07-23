"""Simple Cosmos DB service for vector search."""

import json
import sys
import os
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.memory_store import CosmosDBAIAgentStore


class CosmosService:
    """Simple service for Cosmos DB vector search operations."""

    def __init__(self, account_uri: str, account_key: str):
        """Initialize the Cosmos DB service."""
        self.memory_store = CosmosDBAIAgentStore(account_uri, account_key)
        self.memory_store.initialize()

    def upsert_item(self, item: dict) -> str:
        """Insert the item into the container."""
        try:
            result = self.memory_store.upsert_item(item)
            return json.dumps({"result": result})
        except Exception as e:
            return f"error: " + str(e)

    def vector_search_offers(self, vector: List[float], top_k: int = 5) -> str:
        """Search for offers using vector similarity."""
        try:
            results = self.memory_store.search_query(
                vector=vector,
                top_k=top_k
            )
            return json.dumps({"results": results, "count": len(results)})
        except Exception as e:
            return f"error " + str(e)

    def hybrid_search_offers(self, vector: List[float], user_prompt: str, top_k: int = 5) -> str:
        """Hybrid search offers using vector similarity."""
        try:
            results = self.memory_store.hybrid_search(
                vector=vector,
                user_prompt=user_prompt,
                top_k=top_k
            )
            return json.dumps({"results": results, "count": len(results)})
        except Exception as e:
            return f"error " + str(e)

    def query_product(self, city_name: str) -> str:
        try:
            results = self.memory_store.query_items(city_name)
            return json.dumps({"results": results, "count": len(results)})
        except Exception as e:
            return f"error " + str(e)
