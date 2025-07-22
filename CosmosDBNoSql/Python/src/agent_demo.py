"""Simple test script for the AI Agent."""
import os
import time
from dotenv import load_dotenv
from azure.ai.agents.models import FunctionTool
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from functions.user_functions import user_functions


def agent_demo():
    """Simple test of the AI Agent with vector search."""

    load_dotenv()
    
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    
    # Initialize client and functions
    project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
    functions = FunctionTool(functions=user_functions)

    with project_client:
        agent_client = project_client.agents
        
        # Create agent
        agent = agent_client.create_agent(
            model="gpt-4o",
            name="travel-agent",
            instructions="You are a helpful banking assistant that can search for product information.",
            tools=functions.definitions,
        )
        print(f"Created agent: {agent.name}")

        # Create conversation
        thread = agent_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        # Examples of some user prompts for this agent
        message = "What are some adventure locations for a guys trip?"
        # message = "Book a trip for Paris from June 10th to June 20th."
        # message = "What cities are good to travel during June to July."
        # message = "Tell me something about new york city?"
        agent_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )
        print(f"Created message: {message}")

        # Run agent
        run = agent_client.runs.create(thread_id=thread.id, agent_id=agent.id)
        print(f"Created run, ID: {run.id}")
        
        # Handle the conversation
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = agent_client.runs.get(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    print(f"🔧 Executing: {tool_call.function.name}")
                    output = functions.execute(tool_call)
                    tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                
                agent_client.runs.submit_tool_outputs(
                    thread_id=thread.id, 
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

        # Show results
        print(f"\n✅ Conversation completed!")
        messages = agent_client.messages.list(thread_id=thread.id)
        
        for message in reversed(list(messages)):
            role = message.role
            content = message.content[0].text.value if hasattr(message.content[0], 'text') else str(message.content)
            print(f"\n{role.upper()}: {content}")

        # agent_client.delete_agent(agent.id)
        # print(f"Deleted agent: {agent.id}")


if __name__ == "__main__":
    agent_demo()
