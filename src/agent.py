from typing import TypedDict, Annotated, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage