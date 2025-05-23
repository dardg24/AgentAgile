from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


from utils.config import (
            GEMINI_API_KEY,
            LANGCHAIN_API_KEY,
            LANGCHAIN_TRACING_V2,
            LANGSMITH_PROJECT
)
from core.tools import tools


# Define state schema
class TrelloSlackState(TypedDict):
    channel_id: str
    messages: Annotated[list[AnyMessage], add_messages]
    thread_ts: Optional[str]
    conversation_state: Optional[bool] = None
    conversation_context: Optional[Dict[str, Any]]
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
You have access to a default Trello board that the user is working with.

IMPORTANT: Before selecting any tool, always think step-by-step about what the user is asking.

Follow this reasoning structure for each request:
1. ANALYZE REQUEST: What is the user trying to accomplish? Identify the specific task and entities involved.
2. IDENTIFY TOOL: Which tool is most appropriate for this task? Consider all available options.
3. PLAN PARAMETERS: What parameters will you need? Consider potential issues like case sensitivity or ambiguity.
4. EXPLAIN REASONING: Clearly articulate your reasoning process before executing any tool.

For example:
ANALYZE REQUEST: The user wants to create a new card named "Update docs" in the to-do list.
IDENTIFY TOOL: I should use create_new_card for this task.
PLAN PARAMETERS: I'll need the list_name="To Do" and card_name="Update docs".
EXPLAIN REASONING: Creating a new card requires the create_new_card tool with the specific list and card name parameters.

When the user asks for a "report", "activity report", "daily report", "stand-up report", or similar phrases,
automatically use the generate_daily_stand_up tool with the default board.

Remember that all high-level tools now can send messages directly to Slack, so users
will receive real-time updates about the progress of their requests.

Respond in a clear, professional manner after your reasoning process.
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
    builder.add_node("check_continuation", conversation_continuation_node)  # NUEVO
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    
    # Define el flujo condicional desde START
    def should_continue(state):
        """Decide si es una continuación o una nueva conversación"""
        if state.get("conversation_state"):
            return "check_continuation"
        return "assistant"
    
    # Define edges
    builder.add_conditional_edges(
        START,
        should_continue,
        {
            "check_continuation": "check_continuation",
            "assistant": "assistant"
        }
    )
    
    # Desde check_continuation siempre va a assistant
    builder.add_edge("check_continuation", "assistant")
    
    # El resto permanece igual
    builder.add_conditional_edges(
        "assistant",
        tools_condition
    )
    builder.add_edge("tools", "assistant")
    
    return builder.compile()

def conversation_continuation_node(state: TrelloSlackState):
    """
    Nodo que maneja continuaciones de conversaciones multi-paso.
    """
    conversation_state = state.get("conversation_state")
    conversation_context = state.get("conversation_context", {})
    
    # Obtener el último mensaje del usuario
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    print(f"🔄 Procesando continuación: {conversation_state}")
    print(f"📝 Contexto: {conversation_context}")
    print(f"💬 Mensaje: {last_message}")
    
    if conversation_state == "awaiting_card_name":
        # El usuario está respondiendo con el nombre de la tarjeta
        card_name = last_message
        list_name = conversation_context.get("list_name")
        
        # Crear mensaje para el LLM indicando que debe crear la tarjeta
        system_prompt = f"""
        The user has provided the card name: "{card_name}"
        You need to create this card in the list: "{list_name}"
        Use the create_new_card tool with these parameters.
        """
        
        return {
            "messages": [SystemMessage(content=system_prompt), HumanMessage(content=card_name)],
            "conversation_state": None,  # Limpiar el estado de conversación
            "conversation_context": {}   # Limpiar el contexto
        }
    
    # Si no reconocemos el estado, pasar al assistant normal
    return state

# Main function to process Slack messages
def process_slack_message(
    message: str, 
    channel_id: str,
    thread_ts: Optional[str] = None,
    previous_state: Optional[Dict[str, Any]] = None
):
    """
    Process a message from Slack through the Trello agent.
    
    Args:
        message: User's message from Slack
        channel_id: Slack channel ID
        thread_ts: Thread timestamp for threaded conversations
        previous_state: Estado de una conversación previa
    """
    # Si no hay estado previo, enviar mensaje de procesamiento
    if not previous_state:
        from core.tools import send_to_slack
        send_to_slack(f"🔍 Procesando: '{message}'", channel_id)
    
    # Initialize graph
    graph = build_trello_slack_graph()
    
    # Preparar estado inicial o continuar con el previo
    if previous_state:
        # Continuamos una conversación existente
        new_messages = [HumanMessage(content=message)]
        initial_state = {
            **previous_state,
            "messages": previous_state.get("messages", []) + new_messages
        }
    else:
        # Nueva conversación
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "conversation_state": None,
            "conversation_context": {}
        }
    
    # Invoke graph
    result = graph.invoke(initial_state)
    
    return result  # Retornamos el estado completo, no solo el mensaje

def test_agent():
    test_messages = [
        "Create a new card in Testing called testing new Jetson ",
        # "Move the card 'Fix login bug' from 'In Progress' to 'Done'",
        # "Create a new card called 'Update documentation' in the 'To Do' list",
        # "Generate an activity report",
        # "Genere a python function to replicate Fibonacci",
        # "Say Hi to Jesus and tell him to move to the new trello board"  # Esta prueba debería funcionar ahora
    ]
    
    for message in test_messages:
        print("\n" + "="*50)
        print(f"USER REQUEST: {message}")
        print("="*50)
        
        # Usamos el canal de prueba definido en la configuración
        from utils.config import SLACK_CHANNEL_ID
        response = process_slack_message(message, SLACK_CHANNEL_ID)
        
        print("\nFINAL RESPONSE:")
        print(response)
        print("="*50)
        
if __name__ == "__main__":
    test_agent()