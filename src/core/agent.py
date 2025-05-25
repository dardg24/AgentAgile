from typing import TypedDict, Annotated, Optional, Dict, Any, List
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI


from utils import (
            GEMINI_API_KEY,
            LANGCHAIN_API_KEY,
            LANGCHAIN_TRACING,
            LANGSMITH_PROJECT
)
from core import tools, SlackResponseCoordinator


# State schema
class TrelloSlackState(TypedDict):
    channel_id: str
    messages: Annotated[list[AnyMessage], add_messages]
    thread_ts: Optional[str]
    conversation_state: Optional[str]
    conversation_context: Optional[Dict[str, Any]]
    last_tool_results: Optional[List[Dict[str, Any]]]
    response_sent: Optional[bool]

# Configure LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)
llm_with_tools = llm.bind_tools(tools)

def assistant(state: TrelloSlackState):
    """Assistant that processes messages and decides on tool usage"""
    system_message = """You are a helpful Trello assistant integrated with Slack.
You manage Trello boards, lists, and cards using the available tools.

IMPORTANT: 
1. Tools return structured data, not send messages
2. Be conversational and helpful
3. For simple greetings or questions, respond naturally without tools
4. For Trello operations, use the appropriate tool

Available tools:
- list_boards: Shows all Trello boards
- list_cards_in_list: Shows cards in a specific list
- create_new_card: Creates a new card
- move_card_between_lists: Moves cards between lists
- update_card_details: Updates card information
- generate_daily_stand_up: Creates a daily activity report
"""
    
    sys_msg = SystemMessage(content=system_message)
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]
    }

def extract_tool_results(state: TrelloSlackState) -> TrelloSlackState:
    """Extract and structure tool results"""
    tool_results = []
    
    for message in reversed(state["messages"][-5:]):
        if isinstance(message, ToolMessage):
            try:
                # Tool results should already be dictionaries
                result = message.content
                if isinstance(result, dict):
                    tool_results.append(result)
            except Exception as e:
                print(f"Error extracting tool result: {e}")
    
    return {"last_tool_results": tool_results}

def send_response_node(state: TrelloSlackState) -> TrelloSlackState:
    """Send formatted response to Slack using coordinator"""
    if state.get("response_sent", False):
        return {"response_sent": True}
    
    channel_id = state["channel_id"]
    thread_ts = state.get("thread_ts")
    
    # Check for tool results first
    tool_results = state.get("last_tool_results", [])
    
    if tool_results:
        # Send each tool result through coordinator
        for result in tool_results:
            SlackResponseCoordinator.send_response(result, channel_id, thread_ts)
    else:
        # No tools used, send AI message directly
        last_ai_message = None
        for message in reversed(state["messages"]):
            if isinstance(message, AIMessage):
                last_ai_message = message
                break
        
        if last_ai_message and last_ai_message.content:
            from core import send_to_slack
            send_to_slack(last_ai_message.content, channel_id, thread_ts=thread_ts)
    
    return {"response_sent": True}

def conversation_continuation_node(state: TrelloSlackState):
    """Handle multi-step conversations"""
    conversation_state = state.get("conversation_state")
    conversation_context = state.get("conversation_context", {})
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    if conversation_state == "awaiting_card_name":
        card_name = last_message
        list_name = conversation_context.get("list_name")
        
        system_prompt = f"""
        The user provided the card name: "{card_name}"
        Create this card in the list: "{list_name}"
        Use the create_new_card tool.
        """
        
        return {
            "messages": [SystemMessage(content=system_prompt), HumanMessage(content=card_name)],
            "conversation_state": None,
            "conversation_context": {},
            "response_sent": False
        }
    
    return state

def should_continue_after_assistant(state: TrelloSlackState) -> str:
    """Routing after assistant"""
    messages = state["messages"]
    last_message = messages[-1] if messages else None
    
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "send_response"

# Build graph
def build_trello_slack_graph():
    builder = StateGraph(TrelloSlackState)
    
    # Add nodes
    builder.add_node("check_continuation", conversation_continuation_node)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("extract_results", extract_tool_results)
    builder.add_node("send_response", send_response_node)
    
    # Initial routing
    def should_continue_from_start(state):
        if state.get("conversation_state"):
            return "check_continuation"
        return "assistant"
    
    # Define edges
    builder.add_conditional_edges(
        START,
        should_continue_from_start,
        {
            "check_continuation": "check_continuation",
            "assistant": "assistant"
        }
    )
    
    builder.add_edge("check_continuation", "assistant")
    
    builder.add_conditional_edges(
        "assistant",
        should_continue_after_assistant,
        {
            "tools": "tools",
            "send_response": "send_response"
        }
    )
    
    builder.add_edge("tools", "extract_results")
    builder.add_edge("extract_results", "assistant")
    builder.add_edge("send_response", END)
    
    return builder.compile()

# Process Slack messages
def process_slack_message(
    message: str, 
    channel_id: str,
    thread_ts: Optional[str] = None,
    previous_state: Optional[Dict[str, Any]] = None
):
    """Process a message from Slack"""
    # Send progress update for new conversations
    if not previous_state:
        SlackResponseCoordinator.send_progress_update(
            f"Processing: '{message}'",
            channel_id,
            thread_ts
        )
    
    graph = build_trello_slack_graph()
    
    if previous_state:
        # Continue conversation
        new_messages = [HumanMessage(content=message)]
        initial_state = {
            **previous_state,
            "messages": previous_state.get("messages", []) + new_messages,
            "response_sent": False
        }
    else:
        # New conversation
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "conversation_state": None,
            "conversation_context": {},
            "response_sent": False
        }
    
    # Invoke with recursion limit
    config = {"recursion_limit": 25}
    result = graph.invoke(initial_state, config=config)
    
    return result