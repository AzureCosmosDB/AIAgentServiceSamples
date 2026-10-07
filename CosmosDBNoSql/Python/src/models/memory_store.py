"""Cosmos DB AI Agent Store for vector and text search operations."""

import json
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential


class CosmosDBAIAgentStore:
    """
    A store for AI agent data using Cosmos DB with vector and full-text search capabilities.
    
    This class provides methods to perform various types of searches including:
    - Vector similarity search
    - Hybrid search combining vector and text
    """

    load_dotenv()
    database_name = "travel_db"
    destinations_container_name = "destinations"
    trips_container_name = "trips"

    def __init__(self, account_uri: str, account_key: str):
        """
        Initialize the Cosmos DB AI Agent Store.
        
        Args:
            account_uri: The URI of the Cosmos DB account
        """
        self.account_uri = account_uri
        self.account_key = account_key
        self.client: Optional[CosmosClient] = None
        self.database = None
        self.destinations_container = None
        self.trips_container = None

    def initialize(self):
        """Initialize the Cosmos DB client and container connections."""
        try:
            if os.getenv("COSMOS_AUTH_MODE") == "key":
                self.client = CosmosClient(self.account_uri, self.account_key)
            else:
                credential = DefaultAzureCredential()
                self.client = CosmosClient(self.account_uri, credential=credential)
            self.database = self.client.get_database_client(self.database_name)
            self.destinations_container = self.database.get_container_client(self.destinations_container_name)
            self.trips_container = self.database.get_container_client(self.trips_container_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Cosmos DB connection: {e}") from e

    def upsert_item(self, item: dict) -> dict:
        """
        Insert or update an item in the container.
        
        Args:
            item: The item to upsert
            
        Returns:
            The upserted item
        Raises:
            RuntimeError: If container is not initialized
        """
        if not self.trips_container:
            raise RuntimeError("Cosmos container not initialized. Call initialize() first.")
        return self.trips_container.upsert_item(item)

    def query_items(
            self,
            city_name: str,
    ) -> List[dict]:
        query = "SELECT c.city_name, c.country, c.description, c.top_attractions FROM c WHERE c.city_name = @city_name"

        try:
            results = self.trips_container.query_items(
                query=query,
                parameters=[{"name": "@city_name", "value": city_name}],
                enable_cross_partition_query=True
            )
            return list(results)
        except Exception as e:
            print(f"[Error] Error querying items from Cosmos DB: {e}")
            raise e

    def search_query(
            self,
            vector: List[float] = None,
            vector_field: str = "embedding",
            top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform various types of search queries on the container.
        
        Args:
            vector: Vector for similarity search
            vector_field: Field name containing vectors
            top_k: Maximum number of results to return
            
        Returns:
            List of search results
            
        Raises:
            RuntimeError: If container is not initialized
            ValueError: If required parameters are missing for the search type
        """
        parameters = []

        # Helper to format keywords safely
        def format_keywords(text: str) -> str:
            return ", ".join([json.dumps(k) for k in text.split(" ")])


        query = ("SELECT TOP {} c.city_name, c.country, c.description, c.top_attractions FROM c "
                 "ORDER BY VectorDistance(c.{}, @vector)".format(top_k, vector_field))
        parameters.append({"name": "@vector", "value": vector})

        # Execute query and return results
        try:
            results = self.destinations_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            results_list = list(results)
            print(f"Search completed. Found {len(results_list)} results.")
            return results_list
        except Exception as e:
            print(f"[Error] Error executing search query: {e}")
            raise e

    def hybrid_search(
            self,
            vector: Optional[List[float]] = None,
            user_prompt: Optional[str] = None,
            vector_field: str = "embedding",
            text_field: str = "description",
            top_k: int = 5
    ) -> List[Dict[str, Any]]:
        search_terms = ", ".join([json.dumps(k) for k in user_prompt.split(" ")])
        query = ("SELECT TOP {} c.city_name, c.country, c.description, c.top_attractions FROM c " \
                "ORDER BY RANK RRF(FullTextScore(c.{}, {}), VectorDistance(c.{}, {}))"
                 .format(top_k, text_field, search_terms, vector_field, vector))

        # Execute query and return results
        try:
            results = self.destinations_container.query_items(
                query=query,
                enable_cross_partition_query=True
            )
            results_list = list(results)
            print(f"Search completed. Found {len(results_list)} results.")
            return results_list
        except Exception as e:
            print(f"[Error] Error executing search query: {e}")
            raise e
