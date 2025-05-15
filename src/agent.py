from typing import TypedDict, Annotated, Optional, Dict, Any
from typing_extensions import NotRequired
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage

from config import GEMINI_API_KEY
from trello_tools import tools

class TrelloSlackState(TypedDict):
    """
    State passing between the nodes of the network.
    NotRequired means that these fields may not be present initially.
    """
    # Input source (Channel ID)
    channel_id: str
    messages: Annotated[list[AnyMessage], add_messages]
    # Procesed input answer
    intent: NotRequired[str]
    details: NotRequired[Dict[str, any]]
    # Trello return
    trello_result: NotRequired[Dict[str, Any]]
    # Answer message
    response: NotRequired[str]
    # Flow control
    error: NotRequired[str]
    next: NotRequired[str]

llm = ChatGoogleGenerativeAI(
    model='models/gemini-2.0-flash',
    google_api_key = GEMINI_API_KEY,
    temperature = 0.5,
    max_tokens = 8000
)