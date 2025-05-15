from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY
from trello_tools import tools

# Define state schema
class TrelloSlackState(TypedDict):
    channel_id: str
    messages: Annotated[list[AnyMessage], add_messages]

# Configure LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)
llm_with_tools = llm.bind_tools(tools)

# Assistant node handler
def assistant(state: TrelloSlackState):
    system_message = """You are a helpful Trello assistant integrated with Slack.
You can manage Trello boards, lists, and cards using the available tools.
Always take time to understand the user's request before selecting a tool.
Respond in a clear, professional manner.
"""
    sys_msg = SystemMessage(content=system_message)
    
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])],
        "channel_id": state["channel_id"]
    }

# Build graph
def build_trello_slack_graph():
    builder = StateGraph(TrelloSlackState)
    
    # Define nodes
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    
    # Define edges
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition
    )
    builder.add_edge("tools", "assistant")
    
    return builder.compile()

# Main function to process Slack messages
def process_slack_message(message: str, channel_id: str):
    """
    Process a message from Slack through the Trello agent.
    
    Args:
        message: User's message from Slack
        channel_id: Slack channel ID where message originated
    
    Returns:
        The final result from the agent
    """
    # Initialize graph
    graph = build_trello_slack_graph()
    
    # Prepare initial state
    messages = [HumanMessage(content=message)]
    
    # Invoke graph
    result = graph.invoke({
        "messages": messages, 
        "channel_id": channel_id
    })
    
    # For testing purposes, print the full conversation
    for i, msg in enumerate(result["messages"]):
        print(f"[{i}] {msg.type}: {msg.content}")
    
    # Return the last message content for sending to Slack
    return result["messages"][-1].content

# Test function
def test_agent():
    test_messages = [
        "Show me all cards in the 'To Do' list",
        "Move the card 'Fix login bug' from 'In Progress' to 'Done'",
        "Create a new card called 'Update documentation' in the 'To Do' list",
        "Generate an activity report"
    ]
    
    for message in test_messages:
        print("\n" + "="*50)
        print(f"USER REQUEST: {message}")
        print("="*50)
        
        response = process_slack_message(message, "test-channel")
        
        print("\nFINAL RESPONSE:")
        print(response)
        print("="*50)

if __name__ == "__main__":
    test_agent()