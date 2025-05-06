import json
from enum import Enum
from typing import List, Optional

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential


class SearchType(Enum):
    VECTOR = "vector"
    FULL_TEXT_CONTAINS = "fulltextcontains"
    FULL_TEXT_CONTAINS_ALL = "fulltextcontainsall"
    FULL_TEXT_CONTAINS_ANY = "fulltextcontainsany"
    FULL_TEXT_SCORE = "fulltextscore"
    HYBRID = "hybrid"


class MemoryStore:
    def __init__(self, account_uri: str, database_name: str, container_name: str):
        self.account_uri = account_uri
        self.client: CosmosClient = None
        self.database = DatabaseProxy = None
        self.container = ContainerProxy = None
        self.database_name: str = database_name
        self.container_name: str = container_name

    async def initialize(self):
        credential = DefaultAzureCredential()
        self.client = CosmosClient(self.account_uri, credential)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)

    async def upsert_item(self, item: dict):
        if not self.container:
            raise RuntimeError("Cosmos container not initialized. Call initialize() first.")
        return await self.container.upsert_item(item)

    async def query_items(
            self,
            where_clause: str = "",
            parameters: Optional[List[dict]] = None,
            projection: Optional[List[str]] = None
    ) -> List[dict]:
        if not self.container:
            raise RuntimeError("Cosmos container not initialized. Call initialize() first.")

        # Build SELECT clause
        if projection:
            select_clause = "SELECT " + ", ".join([f"c.{field}" for field in projection])
        else:
            select_clause = "SELECT *"

        # Final query string
        query = f"{select_clause} FROM c"
        if where_clause:
            query += f" WHERE {where_clause}"

        items = []
        async for item in self.container.query_items(
                query=query,
                parameters=parameters or [],
                enable_cross_partition_query=True
        ):
            items.append(item)

        return items

    async def search_query(
            self,
            search_type: SearchType,
            vector_field: Optional[str] = None,
            vector: Optional[List[float]] = None,
            text_field: Optional[str] = None,
            keywords: Optional[List[str]] = None,
            projection: Optional[List[str]] = None,
            top_k: int = 10
    ) -> List[dict]:
        if not self.container:
            raise RuntimeError("Cosmos container not initialized.")

        # SELECT clause
        if projection:
            select_clause = f"SELECT TOP {top_k} " + ", ".join([f"c.{field}" for field in projection])
        else:
            select_clause = f"SELECT TOP {top_k} *"
        query = f"{select_clause} FROM c"
        parameters = []

        # Helper to inline keywords
        def format_keywords(keywords_list: List[str]) -> str:
            return ", ".join([json.dumps(k) for k in keywords_list])  # safely quote and escape

        # Search logic
        if search_type == SearchType.VECTOR:
            if not (vector_field and vector):
                raise ValueError("Vector field and vector must be provided for vector search.")
            query += f" ORDER BY VectorDistance(c.{vector_field}, @vector)"
            parameters.append({"name": "@vector", "value": vector})

        elif search_type == SearchType.FULL_TEXT_CONTAINS:
            if not (text_field and keywords):
                raise ValueError("Text field and at least one keyword must be provided.")
            query += f" WHERE FullTextContains(c.{text_field}, {json.dumps(keywords[0])})"

        elif search_type == SearchType.FULL_TEXT_CONTAINS_ALL:
            if not (text_field and keywords):
                raise ValueError("Text field and keywords must be provided.")
            query += f" WHERE FullTextContainsAll(c.{text_field}, {format_keywords(keywords)})"

        elif search_type == SearchType.FULL_TEXT_CONTAINS_ANY:
            if not (text_field and keywords):
                raise ValueError("Text field and keywords must be provided.")
            query += f" WHERE FullTextContainsAny(c.{text_field}, {format_keywords(keywords)})"

        elif search_type == SearchType.FULL_TEXT_SCORE:
            if not (text_field and keywords):
                raise ValueError("Text field and keywords must be provided.")
            query += f" ORDER BY RANK FullTextScore(c.{text_field}, {format_keywords(keywords)})"

        elif search_type == SearchType.HYBRID:
            if not (vector_field and vector and text_field and keywords):
                raise ValueError("Vector field, vector, text field, and keywords must be provided for hybrid search.")
            query += f" ORDER BY RANK RRF(VectorDistance(c.{vector_field}, @vector), FullTextScore(c.{text_field}, {format_keywords(keywords)}))"
            parameters.append({"name": "@vector", "value": vector})

        else:
            raise ValueError("Unsupported search type.")

        # Execute and collect results
        results = self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )
        result_list = [item async for item in results]
        return result_list
