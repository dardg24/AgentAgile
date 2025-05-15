import requests
from config import (
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    BOARD_ID,
    SLACK_CHANNEL_ID,
    BoardID,
    ListId,
    CardId,
    CardName,
    DescriptionCard,
    ChannelId,
    ListName
)
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta

# --- Low-Level API Functions ---

def get_trello_boards() -> Dict[str, str]:
    """
    Gets all Trello boards accessible to the user.

    This tool allows the agent to retrieve and list all available Trello boards,
    providing the user with an overview of their Trello workspace.

    Returns:
        Dict[str, str]: A dictionary mapping board names to their IDs.
        Example: {"Board Name": "12345abcdef", "Another Board" : "567890ghijk"}
        Returns None if the API call fails (network error, HTTP error).
    """
    url = "https://api.trello.com/1/members/me/boards"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        boards_dict = {board['name']: board['id'] for board in response.json()}
        return boards_dict
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_trello_lists(board_id: BoardID) -> Dict[str, str]:
    """Gets all lists on a specific Trello board.
    
    This tool enables the agent to retrieve all lists within a specified board,
    allowing users to see how their tasks are organized.
    
    Args:
        board_id (BoardID): The ID of the Trello board to get lists from.
    
    Returns:
        Dict[str, str]: A dictionary mapping list names to their IDs.
            Example: {"To Do": "list123", "In Progress": "list456", "Done": "list789"}
            Returns None if the API call fails (network error, HTTP error).
    
    """
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        lists_dict = {list_item['name']: list_item['id'] for list_item in response.json()}
        return lists_dict
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_cards_in_list(list_id: ListId) -> Dict[str, str]:
    """Gets all cards in a specific Trello list.

       This tool allows the agent to retrieve all cards within a specified list,
       enabling users to see the task within a particular status category
    
       Args: list_id (ListId): The ID of the Trello List to get cards from.

       Returns:
            Dict [str, str]: A dictionary mapping card names to their IDs.
            Example: {"Implement login" : "card123", "Fix bug" : "drac456"}
            Return an empty dictionary if the list has no cards.
            Returns None if the API call fails (network error, HTTP error).
    
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        card_dict = {card['name']: card['id'] for card in response.json()}
        return card_dict

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def create_trello_card(
    list_id: ListId,
    name:CardName,
    desc:DescriptionCard
    ) -> Dict[str, str]:
    """Creates a new card in the specified Trello list.

       This tool enables the agent to create new tasks when requested by users,
        placing them in the appropriate list with optional description.

        Args:
            list_id (ListId): The ID of the list where the card will be created.
            name (CardName): The name/tittle of the card to create.
            desc (DescriptionCard): The description of the card to create.

        Returns:
            Dict[str, str]: The complete card data as returned by the Trello API.
            Return None if the API Call fails (network error, HTTP error).
    """
    url = "https://api.trello.com/1/cards"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "idList": list_id,
        "name": name,
        "desc": desc,
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "pos": "top"
    }
    
    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None
   
def update_trello_card(
            card_id: CardId,
            list_id: Optional[ListId] = None,
            name: Optional[CardName] = None,
            desc:Optional[DescriptionCard] =None
            )-> Dict[str,Any]:
    """Updates an existing Trello card with new values.
        
        This tool allows the agent to modify cards by moving them between lists,
        renaming them, or updating their description based on user requests.
        
        Args:
            card_id (CardId): The ID of the card to update.
            list_id (ListId, optional): The ID of the list to move the card to.
            name (CardName, optional): The new name for the card.
            desc (DescriptionCard, optional): The new description for the card.
        
        Returns:
            Dict[str,Any]: The updated card data as returned by the Trello API.
                Returns None if the API call fails (network error, HTTP error).
    """
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    headers = {
        "Accept": "application/json"
    }
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    # Only add parameters that are not None
    if list_id:
        params["idList"] = list_id
    if name:
        params["name"] = name
    if desc:
        params["desc"] = desc
    
    try:
        response = requests.put(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_trello_card(card_id:CardId):
    """Gets detailed information about a specific Trello card.
    
    This tool enables the agent to retrieve comprehensive information about a card,
    including its metadata, description, and other properties.
    
    Args:
        card_id (CardId): The ID of the card to retrieve details for.
    
    Returns:
        Dict[str, Any]: The complete card data as returned by the Trello API.
            Returns None if the API call fails (network error, HTTP error).
    """
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def send_to_slack(message: str, channel_id: ChannelId) -> bool:
    """
    Envía un mensaje a un canal específico de Slack.
    
    Args:
        message (str): El mensaje a enviar
        channel_id (str): ID del canal de Slack
        
    Returns:
        bool: True si el mensaje se envió correctamente, False en caso contrario
    """
    try:
        # Importamos aquí para evitar la dependencia circular
        from config import SLACK_BOT_TOKEN
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        payload = {"channel": channel_id, "text": message}
        
        slack_response = requests.post(url, headers=headers, json=payload)
        
        if slack_response.status_code == 200 and slack_response.json().get("ok"):
            print(f"Mensaje enviado exitosamente a Slack canal {channel_id}")
            return True
        else:
            print(f"Error enviando mensaje a Slack: {slack_response.json()}")
            return False
    
    except Exception as e:
        print(f"Excepción enviando mensaje a Slack: {str(e)}")
        return False

# --- High-Level Tools for the Agent ---

def list_boards() -> str:
    """
    Retrieves and formats all available Trello boards for the user.
    
    This high-level tool provides a user-friendly list of all boards
    accessible to the user's Trello account.
    
    Returns:
        str: A formatted string listing all boards.
             Returns an error message if the operation fails.
    """
    boards = get_trello_boards()
    
    if not boards:
        return "⚠️ Unable to retrieve your Trello boards. Please try again later."
    
    if len(boards) == 0:
        return "You don't have any Trello boards. Would you like to create one?"
    
    response = "📋 **Your Trello Boards:**\n\n"
    for board_name in boards.keys():
        response += f"• {board_name}\n"
    
    return response

def list_cards_in_list(
        list_name: ListName,
        board_id: Optional[BoardID] = BOARD_ID,
        channel_id: Optional[ChannelId] = SLACK_CHANNEL_ID) -> str:
    """
    Retrieves and formats all cards in a specific list by name.
    
    Args:
        list_name (str): The name of the list to get cards from.
        board_id (str, optional): The ID of the board. If not provided, uses the default.
        channel_id (str, optional): Slack channel ID for notifications.
    
    Returns:
        str: A formatted string listing all cards in the specified list.
             Returns an error message if the operation fails.
    """
    board_id = board_id or BOARD_ID
    
    # Enviar mensaje de progreso a Slack si se proporciona un channel_id
    if channel_id:
        send_to_slack(f"🔍 Buscando tarjetas en la lista '{list_name}'...", channel_id)
    
    # Get lists on the board
    lists = get_trello_lists(board_id)
    if not lists:
        error_msg = "⚠️ Unable to retrieve lists from the board. Please try again later."
        if channel_id:
            send_to_slack(error_msg, channel_id)
        return error_msg
    
    # Check if the requested list exists
    if list_name not in lists:
        similar_lists = [name for name in lists.keys() if list_name.lower() in name.lower()]
        suggestion = f"\n\nDid you mean one of these lists? {', '.join(similar_lists)}" if similar_lists else ""
        error_msg = f"❌ List '{list_name}' not found on the board.{suggestion}"
        if channel_id:
            send_to_slack(error_msg, channel_id)
        return error_msg
    
    # Get cards in the list
    cards = get_cards_in_list(lists[list_name])
    if cards is None:
        error_msg = f"⚠️ Unable to retrieve cards from the '{list_name}' list. Please try again later."
        if channel_id:
            send_to_slack(error_msg, channel_id)
        return error_msg
    
    if len(cards) == 0:
        empty_msg = f"📋 The list '{list_name}' has no cards."
        if channel_id:
            send_to_slack(empty_msg, channel_id)
        return empty_msg
    
    response = f"📋 **Cards in '{list_name}':**\n\n"
    for card_name in cards.keys():
        response += f"• {card_name}\n"
    
    # Enviar resultado a Slack si se proporciona un channel_id
    if channel_id:
        send_to_slack(response, channel_id)
    
    return response

def create_new_card(
        card_name: CardName,
        list_name: ListName,
        description: DescriptionCard = "",
        board_id: Optional[BoardID] = BOARD_ID) -> str:
    """
    Creates a new card in the specified list using list name instead of ID.
    
    This high-level tool simplifies card creation by using natural language references
    to lists and handling all the necessary API calls behind the scenes.
    
    Args:
        card_name (str): The name/title for the new card.
        list_name (str): The name of the list where the card will be created.
        description (str, optional): The description for the new card.
        board_id (str, optional): The ID of the board. If not provided, uses the default.
    
    Returns:
        str: A success or error message describing the result of the operation.
    """
    board_id = board_id or BOARD_ID
    
    # Get lists on the board
    lists = get_trello_lists(board_id)
    if not lists:
        return "⚠️ Unable to retrieve lists from the board. Please try again later."
    
    # Check if the requested list exists
    if list_name not in lists:
        similar_lists = [name for name in lists.keys() if list_name.lower() in name.lower()]
        suggestion = f"\n\nDid you mean one of these lists? {', '.join(similar_lists)}" if similar_lists else ""
        return f"❌ List '{list_name}' not found on the board.{suggestion}"
    
    # Create the card
    result = create_trello_card(lists[list_name], card_name, description)
    
    if result:
        return f"✅ Successfully created card '{card_name}' in list '{list_name}'."
    else:
        return f"❌ Failed to create card '{card_name}'. Please try again later."

def move_card_between_lists(
        card_name: str,
        source_list_name: str,
        target_list_name: str,
        board_id: Optional[str] = None) -> str:
    """
    Moves a card from one list to another using list names instead of IDs.
    
    This high-level tool simplifies card movement by using natural language references
    to cards and lists, handling all the necessary lookups and API calls.
    
    Args:
        card_name (str): The name of the card to move.
        source_list_name (str): The name of the list where the card is currently.
        target_list_name (str): The name of the list where the card should be moved.
        board_id (str, optional): The ID of the board. If not provided, uses the default.
    
    Returns:
        str: A success or error message describing the result of the operation.
    """
    board_id = board_id or BOARD_ID
    
    # Get lists on the board
    lists = get_trello_lists(board_id)
    if not lists:
        return "⚠️ Unable to retrieve lists from the board. Please try again later."
    
    # Check if both lists exist
    if source_list_name not in lists:
        return f"❌ Source list '{source_list_name}' not found on the board."
    
    if target_list_name not in lists:
        return f"❌ Target list '{target_list_name}' not found on the board."
    
    # Get cards in the source list
    cards = get_cards_in_list(lists[source_list_name])
    if cards is None:
        return f"⚠️ Unable to retrieve cards from '{source_list_name}'. Please try again later."
    
    # Check if the card exists in the source list
    if card_name not in cards:
        return f"❌ Card '{card_name}' not found in list '{source_list_name}'."
    
    # Move the card
    result = update_trello_card(cards[card_name], lists[target_list_name])
    
    if result:
        return f"✅ Successfully moved card '{card_name}' from '{source_list_name}' to '{target_list_name}'."
    else:
        return f"❌ Failed to move card '{card_name}'. Please try again later."

def update_card_details(
        card_name: str,
        list_name: str,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        board_id: Optional[str] = None) -> str:
    """
    Updates the details of an existing card using list and card names.
    
    This high-level tool allows for updating card details using natural language
    references rather than technical IDs.
    
    Args:
        card_name (str): The current name of the card to update.
        list_name (str): The name of the list containing the card.
        new_name (str, optional): The new name for the card.
        new_description (str, optional): The new description for the card.
        board_id (str, optional): The ID of the board. If not provided, uses the default.
    
    Returns:
        str: A success or error message describing the result of the operation.
    """
    if not new_name and not new_description:
        return "⚠️ No updates specified. Please provide a new name or description."
    
    board_id = board_id or BOARD_ID
    
    # Get lists on the board
    lists = get_trello_lists(board_id)
    if not lists:
        return "⚠️ Unable to retrieve lists from the board. Please try again later."
    
    # Check if the list exists
    if list_name not in lists:
        return f"❌ List '{list_name}' not found on the board."
    
    # Get cards in the list
    cards = get_cards_in_list(lists[list_name])
    if cards is None:
        return f"⚠️ Unable to retrieve cards from '{list_name}'. Please try again later."
    
    # Check if the card exists
    if card_name not in cards:
        return f"❌ Card '{card_name}' not found in list '{list_name}'."
    
    # Update the card
    result = update_trello_card(cards[card_name], name=new_name, desc=new_description)
    
    if result:
        updates = []
        if new_name:
            updates.append("name")
        if new_description:
            updates.append("description")
        
        return f"✅ Successfully updated {' and '.join(updates)} of card '{card_name}'."
    else:
        return f"❌ Failed to update card '{card_name}'. Please try again later."

def generate_daily_stand_up(
        board_id: Optional[BoardID] = BOARD_ID,
        channel_id: Optional[ChannelId] = SLACK_CHANNEL_ID) -> str:
    """
    Generates a detailed stand-up report of today's Trello activity.
    
    This targeted report focuses specifically on cards updated today,
    making it perfect for daily stand-up meetings and progress updates.
    
    Args:
        board_id (str, optional): The ID of the board. If not provided, uses the default.
        channel_id (str, optional): Slack channel ID for notifications.
    
    Returns:
        str: A formatted stand-up report showing today's activity.
    """
    if channel_id:
        send_to_slack("🔍 Generando reporte de actividad diaria...", channel_id)
    
    board_id = board_id or BOARD_ID
    
    # Get lists on the board
    lists = get_trello_lists(board_id)
    if not lists:
        error_msg = "⚠️ Unable to retrieve lists from the board. Please try again later."
        if channel_id:
            send_to_slack(error_msg, channel_id)
        return error_msg
    
    # Collect all cards with details
    all_cards = []
    for list_name, list_id in lists.items():
        cards_dict = get_cards_in_list(list_id)
        if cards_dict:
            for card_name, card_id in cards_dict.items():
                card_details = get_trello_card(card_id)
                if card_details:
                    card_details["list_name"] = list_name
                    all_cards.append(card_details)
    
    # Get current date
    today = datetime.now().date()
    
    summary = "# Daily Stand-Up Summary\n\n"
    summary += f"Date: {today.strftime('%d/%m/%Y')}\n\n"
    
    # Filter cards updated today
    today_cards = []
    for card in all_cards:
        # Safely parse the date with proper timezone handling
        try:
            last_activity = datetime.fromisoformat(card['dateLastActivity'].replace('Z', '+00:00'))
            # Compare only the date portions
            if last_activity.date() == today:
                today_cards.append(card)
        except (ValueError, TypeError):
            # Skip cards with unparseable dates
            continue
    
    if not today_cards:
        no_cards_msg = "No cards were updated today.\n"
        summary += no_cards_msg
        if channel_id:
            send_to_slack(summary, channel_id)
        return summary
    
    summary += f"## Cards Updated Today ({len(today_cards)})\n\n"
    
    for card in today_cards:
        # Extract relevant information
        name = card['name']
        description = card['desc'] if card['desc'] else "No description"
        status = "Open" if not card['closed'] else "Closed"
        url = card['url']
        
        # Add to summary
        summary += f"### {name}\n"
        summary += f"- **Status:** {status}\n"
        summary += f"- **Description:** {description}\n"
        summary += f"- **Last Updated:** {card['dateLastActivity']}\n"
        summary += f"- **URL:** {url}\n\n"
    
    if channel_id:
        send_to_slack(summary, channel_id)
    
    return summary


# Full set of tools - both low-level and high-level
tools = [
    # Low-level API tools
    get_trello_boards,
    get_trello_lists,
    get_cards_in_list,
    create_trello_card,
    update_trello_card,
    get_trello_card,
    
    # High-level tools optimized for agent use
    list_boards,
    list_cards_in_list,
    create_new_card,
    move_card_between_lists,
    update_card_details,
    generate_daily_stand_up,

    send_to_slack
]