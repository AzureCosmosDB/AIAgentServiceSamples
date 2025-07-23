# AI Agent with Cosmos DB Vector Search - Travel Destinations Sample

This sample demonstrates how to create an AI Agent that can search for travel destination information using vector embeddings in Azure Cosmos DB. The agent can answer questions about destinations, cities, and travel recommendations using semantic search.

## 🏗️ Project Structure

```
CosmosDBNoSql/Python/src/
├── setup/
│   ├── destinations_data.py    # Travel destinations data with embeddings
│   ├── ingest_data.py          # Script to load data into Cosmos DB
│   └── __init__.py
├── services/
│   ├── embedding_service.py    # Generate embeddings with Azure OpenAI
│   ├── cosmos_service.py       # Search Cosmos DB with vectors
│   └── __init__.py
├── functions/
│   ├── user_functions.py       # Functions for the agent to call
│   └── __init__.py
├── models/
│   ├── memory_store.py         # Cosmos DB operations
│   └── __init__.py
├── agent_demo.py               # Main demo application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (copy from .env.example)
└── README.md                   # This file
```

## 🚀 Prerequisites

Before running this sample, you need:

1. **Azure Cosmos DB account** with vector search capabilities
   - [Create a Cosmos DB account](https://docs.microsoft.com/en-us/azure/cosmos-db/how-to-create-cosmosdb-account)
   - [Enable vector search](https://docs.microsoft.com/en-us/azure/cosmos-db/vector-search)

2. **Azure OpenAI service** with text embedding model deployed
   - [Create an Azure OpenAI resource](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource)
   - [Deploy text-embedding-3-large model](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource#deploy-a-model)

3. **Azure AI Studio project** for the AI Agent
   - [Create an Azure AI Studio project](https://docs.microsoft.com/en-us/azure/ai-studio/how-to/create-projects)
   - [Set up AI Agents](https://docs.microsoft.com/en-us/azure/ai-studio/how-to/develop/sdk-overview)

4. **Python 3.8+**

## 🛠️ Setup Instructions

### 1. Clone and Navigate to the Project

```bash
git clone https://github.com/aayush3011/AIAgentServiceSamples.git
cd AIAgentServiceSamples/CosmosDBNoSql/Python/src
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file based on the example below and update with your Azure credentials:

```properties
# Azure Cosmos DB Configuration
COSMOS_ACCOUNT_URI=https://your-cosmos-account.documents.azure.com:443/
COSMOS_ACCOUNT_KEY=your-cosmos-account-key
COSMOS_DATABASE_NAME=travel_db
COSMOS_CONTAINER_NAME=destinations
COSMOS_AUTH_MODE=key
COSMOS_SEARCH_TYPE=vector

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT=text-embedding-3-large
AZURE_OPENAI_DIMENSIONS=1536

# Azure AI Agent Configuration
PROJECT_ENDPOINT=https://your-ai-studio-project.services.ai.azure.com/api/projects/your-project-name
```

### 4. Set Up Cosmos DB and Load Data

First, create the Cosmos DB database and container with vector indexing, then load the travel destinations data:

```bash
# Load travel destinations data into Cosmos DB
python setup/ingest_data.py
```

This script will:
- Create a Cosmos DB database (`travel_db`) with two containers:
  - `destinations` container for travel destination data
  - `trips` container for trip bookings and management
- Configure vector indexing for embeddings
- Load travel destination data with pre-computed embeddings

### 5. Run the AI Agent Demo

```bash
python agent_demo.py
```

## 🎯 How It Works

1. **User asks a question** like "Tell me about romantic destinations in Europe"
2. **Agent calls the function** `get_destinations_information()` or `get_city_info()`
3. **Function generates embeddings** using Azure OpenAI
4. **Searches Cosmos DB** using vector similarity or direct queries
5. **Returns results** to the agent
6. **Agent responds** to the user with relevant travel information

## 🔧 Available Functions

The AI Agent has access to these functions:

### `get_destinations_information(user_prompt: str)`
- Searches for destinations using vector similarity search
- Supports hybrid search combining vector and text search
- Best for: "Find romantic destinations", "Beach vacation spots", "Cultural cities"

### `get_city_info(city_name: str)` 
- Searches for specific city information by name using direct queries
- Best for: "Tell me about Paris", "Information about Tokyo"

**Search Types Available:**
- **Vector Search**: Semantic similarity based on embeddings
- **Hybrid Search**: Combines vector search with text matching for more precise results
- **Direct Query**: Exact name-based lookups

## 📝 Example Queries

Try asking the agent:

- "What are some romantic destinations in Europe?"
- "Tell me about beach destinations"
- "Find cultural cities with great museums"
- "What do you know about Paris?"
- "Recommend destinations for adventure travel"
- "Best places to visit in spring"

## 🔧 Key Components

### Vector Search
The sample uses Azure Cosmos DB's vector search capabilities to find semantically similar destinations based on user queries.

### Hybrid Search
Combines vector similarity search with full-text search for enhanced accuracy and relevance in results.

### Embeddings
Travel destination data includes pre-computed embeddings generated using Azure OpenAI's text-embedding-3-large model.

### AI Agent
Built using Azure AI Studio, the agent can have natural conversations and call functions to retrieve relevant information.

## 📊 Data

The sample includes travel destination data with:
- **City names** and locations
- **Descriptions** of destinations
- **Tags** for categorization
- **Popular activities** and attractions
- **Best times to visit**
- **Vector embeddings** for semantic search

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the `src` directory
2. **Authentication Errors**: Verify your Azure credentials in the `.env` file
3. **Cosmos DB Errors**: Ensure your Cosmos DB account has vector search enabled
4. **Agent Errors**: Check that your Azure AI Studio project endpoint is correct

### Debugging

- Check the console output for detailed error messages
- Verify all environment variables are set correctly
- Ensure the Cosmos DB container has been created and populated with data

## 🔒 Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use Azure Managed Identity in production instead of API keys
- Regularly rotate your API keys and access tokens

## 🚀 Extending the Sample

You can extend this sample by:

1. **Adding more functions** like hotel search, restaurant recommendations
2. **Implementing different search types** (hybrid search, full-text search)
3. **Adding more sophisticated travel data** with images, prices, reviews
4. **Creating a web interface** for the chat experience

## 📚 Related Documentation

- [Azure Cosmos DB Vector Search](https://docs.microsoft.com/en-us/azure/cosmos-db/vector-search)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure AI Studio](https://docs.microsoft.com/en-us/azure/ai-studio/)
- [Azure AI Agents SDK](https://docs.microsoft.com/en-us/python/api/azure-ai-agents/)

## 🤝 Contributing

This is a sample project. Feel free to fork and adapt it for your own use cases!
