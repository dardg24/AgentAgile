from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from utils import GEMINI_API_KEY, SLACK_CHANNEL_ID
from core.tools import (
    tools,
    send_to_slack
)

# STEP 1: DEFINE THE STATE
# ========================
# The State acts as shared memory that travels between all graph nodes.
# Each node can read information from the state and write new information.
# This allows us to maintain conversation context and results throughout the process.

class TrelloAgentState(TypedDict):
    """
    State that flows between all nodes in the graph.
    
    Think of this as a clipboard that each worker in an assembly line can read from
    and write to, passing it along with new information added at each step.
    """
    # Initial user information
    user_query: str                    # What the user typed
    channel_id: str                    # Where to reply in Slack
    
    # Messages for the LLM (LangGraph handles this automatically)
    messages: Annotated[List[AnyMessage], add_messages]
    
    # Operation results
    tool_results: Optional[List[Dict[str, Any]]]  # Results from tools
    final_response: Optional[str]                 # Final formatted response


# STEP 2: CONFIGURE LLM WITH TOOLS
# =================================
# Here we give the LLM access to the tools you created.
# The LLM will automatically learn when and how to use each one.

# Configure the LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.1  # Low temperature for more consistent responses
)

# Bind tools to the LLM - this enables the ReAct "magic"
llm_with_tools = llm.bind_tools(tools)


# STEP 3: DEFINE THE NODES
# ========================
# Each node is a function that performs a specific task.
# It receives the current state and returns the modifications it wants to make.

def assistant(state: TrelloAgentState) -> TrelloAgentState:
    """
    MAIN NODE: THE AGENT'S "BRAIN"
    
    This node implements the "Reasoning" part of ReAct.
    The LLM analyzes the current situation and decides:
    1. Do I need to use a tool?
    2. Which tool should I use?
    3. Or can I respond directly?
    
    Your implementation is cleaner and more direct than my previous version,
    so I'm using your approach with the improved system message you provided.
    """
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


def format_response_node(state: TrelloAgentState) -> TrelloAgentState:
    """
    FORMATTING NODE: THE "PRESENTER"
    
    This node takes raw results and converts them into friendly messages for Slack.
    It's like a translator that converts technical jargon into understandable human language.
    
    The extract_tool_results function you mentioned could be useful here for more complex
    processing, but LangGraph's automatic tool handling works well for our current flow.
    If you need to extract specific tool results for custom formatting, we can add it later.
    """
    
    # Get the last message from the assistant
    last_message = state["messages"][-1] if state["messages"] else None
    
    if not last_message or not isinstance(last_message, AIMessage):
        # If something went wrong, create a friendly error response
        response = "❌ Sorry, something went wrong processing your request."
    elif hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # If the LLM still wants to use tools, don't format yet
        return {}  # Don't update anything, let the cycle continue
    else:
        # The LLM has decided it can respond directly
        response = last_message.content
    
    # Send the response to Slack
    channel_id = state.get("channel_id", SLACK_CHANNEL_ID)
    send_to_slack(response, channel_id)
    
    return {"final_response": response}


# STEP 4: DEFINE ROUTING LOGIC
# ============================
# This function decides where the flow goes after the assistant node.

def should_continue(state: TrelloAgentState) -> str:
    """
    DECISION FUNCTION: THE "TRAFFIC DIRECTOR"
    
    Examines the assistant's last response and decides:
    - If the LLM wants to use tools → go to "tools"
    - If the LLM has a final response → go to "format_response"
    
    This is like a traffic light that directs flow based on current conditions.
    """
    
    # Get the last message
    last_message = state["messages"][-1] if state["messages"] else None
    
    # If the message has tool_calls, it means the LLM wants to use tools
    if (last_message and 
        hasattr(last_message, 'tool_calls') and 
        last_message.tool_calls):
        return "tools"  # Go execute tools
    else:
        return "format_response"  # Go format the final response


# STEP 5: BUILD THE GRAPH
# =======================
# Here we connect all the nodes like creating a flowchart.

def create_trello_agent():
    """
    GRAPH BUILDER: THE "ARCHITECT"
    
    Takes all individual components and connects them in a logical flow.
    It's like creating a blueprint for a factory where each station has a specific function.
    
    The flow implements ReAct automatically:
    - assistant (Reasoning) → tools (Acting) → assistant (Observing) → repeat if needed
    - When satisfied, assistant → format_response → END
    """
    
    # Create the graph
    builder = StateGraph(TrelloAgentState)
    
    # ADD NODES
    # Each node is a "workstation" in our processing factory
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))  # LangGraph handles this automatically
    builder.add_node("format_response", format_response_node)
    
    # DEFINE THE FLOW
    # These are the "highways" that connect the stations
    
    # 1. Always start at the assistant
    builder.add_edge(START, "assistant")
    
    # 2. From assistant, use conditional logic to decide the next step
    builder.add_conditional_edges(
        "assistant",
        should_continue,  # This function decides
        {
            "tools": "tools",                    # If it needs tools
            "format_response": "format_response" # If it can respond
        }
    )
    
    # 3. After using tools, return to assistant to evaluate results
    # This is key for ReAct: the agent "observes" results and decides if it needs more actions
    builder.add_edge("tools", "assistant")
    
    # 4. After formatting, finish
    builder.add_edge("format_response", END)
    
    # Compile the graph into an executable function
    return builder.compile()


# STEP 6: MAIN PROCESSING FUNCTION
# ================================

def process_slack_message(user_message: str, channel_id: str) -> str:
    """
    MAIN FUNCTION: THE "FACTORY OPERATOR"
    
    This function takes a Slack message and processes it completely:
    1. Creates the initial state
    2. Executes the graph
    3. Returns the result
    
    It's like pressing the "START" button on a machine that does all the work.
    """
    
    # Create the graph
    agent = create_trello_agent()
    
    # Initial state - like filling out a work order
    initial_state = {
        "user_query": user_message,
        "channel_id": channel_id,
        "messages": [HumanMessage(content=user_message)],
        "tool_results": None,
        "final_response": None
    }
    
    # Execute the graph - here's where all the magic happens
    # The graph automatically:
    # 1. Analyzes the message (assistant)
    # 2. Executes tools if necessary (tools)
    # 3. Re-analyzes results (assistant)
    # 4. Repeats until satisfied
    # 5. Formats and sends response (format_response)
    
    try:
        result = agent.invoke(initial_state)
        return result.get("final_response", "Process completed")
    except Exception as e:
        error_msg = f"❌ Error processing request: {str(e)}"
        send_to_slack(error_msg, channel_id)
        return error_msg

"""
HOW EVERYTHING WORKS TOGETHER (Example: "move test-card to Done"):

This flow implements ReAct naturally:
- Reasoning: Assistant analyzes and plans
- Acting: Tools execute actions on Trello  
- Observing: Assistant evaluates results
- (Repeat if needed): Automatic cycle until complete
"""