import json

from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
import destinations_data

import os


def get_vector_indexing_policy():
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "vectorIndexes": [
            {"path": "/embedding", "type": "diskANN"}
        ],
        "fullTextIndexes": [
            {"path": "/description"}
        ]
    }


def get_vector_embedding_policy():
    return {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": "float32",
                "dimensions": 1536,
                "distanceFunction": "cosine"
            }
        ]
    }


def get_full_text_policy():
    return {
        "defaultLanguage": "en-US",
        "fullTextPaths": [
            {
                "path": "/description",
                "language": "en-US"
            }
        ]
    }


def main():
    load_dotenv()

    # Cosmos DB settings
    cosmos_uri = os.getenv("COSMOS_ACCOUNT_URI")
    cosmos_key = os.getenv("COSMOS_ACCOUNT_KEY")
    database_name = "travel_db"
    destinations_container_name = "destinations"
    trips_container_name = "trips"

    client = CosmosClient(cosmos_uri, cosmos_key)

    database = client.create_database_if_not_exists(database_name)
    destinations_container = database.create_container_if_not_exists(
        id=destinations_container_name,
        partition_key=PartitionKey(path="/pk"),
        offer_throughput=12000,
        indexing_policy=get_vector_indexing_policy(),
        vector_embedding_policy=get_vector_embedding_policy(),
        full_text_policy=get_full_text_policy()
    )

    trips_container = database.create_container_if_not_exists(
        id=trips_container_name,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=12000,
    )

    destinations = destinations_data.get_data()
    for index, item in enumerate(destinations):
        item["id"] = str(index)
        item['pk'] = str((index % 2) + 1)
        destinations_container.upsert_item(item)


if __name__ == '__main__':
    main()
