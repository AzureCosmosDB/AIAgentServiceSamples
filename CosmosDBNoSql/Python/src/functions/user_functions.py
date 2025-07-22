"""User functions for the AI Agent."""

import json
import sys
import os
import uuid

from dotenv import load_dotenv
from typing import Set, Callable, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.embedding_service import EmbeddingService
from services.cosmos_service import CosmosService

load_dotenv()

# Azure OpenAI settings
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Cosmos DB settings
cosmos_uri = os.getenv("COSMOS_ACCOUNT_URI")
cosmos_key = os.getenv("COSMOS_ACCOUNT_KEY")

# Initialize services
embedding_service = EmbeddingService(azure_openai_endpoint, azure_openai_key, azure_openai_deployment)
cosmos_service = CosmosService(cosmos_uri, cosmos_key)


def get_destinations_information(user_prompt: str) -> str:
    """Search for destinations information using vector similarity."""
    try:
        # Generate embeddings for the user prompt
        vectors = embedding_service.generate_embeddings(user_prompt)
        if not vectors:
            return json.dumps({"error": "Failed to generate embeddings", "results": []})

        if (os.getenv("COSMOS_SEARCH_TYPE")) == "vector":
            # Search for similar products using vector search
            return cosmos_service.vector_search_offers(vectors)
        elif (os.getenv("COSMOS_SEARCH_TYPE")) == "hybrid":
            # Search for similar products using hybrid search
            return cosmos_service.hybrid_search_offers(vectors, user_prompt)
    except Exception as e:
        json.dumps({"error": str(e), "results": []})
        raise e


def get_city_info(city_name: str) -> str:
    """Search for destination information using city name."""
    try:
        return cosmos_service.query_product(city_name)
    except Exception as e:
        json.dumps({"error": str(e), "results": []})
        raise e


def book_trip(start_date: str, end_date: str, city_name: str) -> str:
    """Book a trip."""
    try:
        item = {
            "id": str(uuid.uuid4()),
            "city_name": city_name,
            "start_date": start_date,
            "end_date": end_date,
        }
        return cosmos_service.upsert_item(item)
    except Exception as e:
        json.dumps({"error": str(e), "results": []})
        raise e


# Define the set of user functions available to the agent
# Only include the functions you want the agent to have access to
user_functions: Set[Callable[..., Any]] = {
    get_destinations_information,
    get_city_info,
    book_trip
}
