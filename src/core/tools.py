import requests

from typing import Dict, Optional, Any, List
from datetime import datetime

from utils import (
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    BOARD_ID,
    SLACK_CHANNEL_ID,
    SLACK_BOT_TOKEN,
    BoardID,
    ListId,
    CardId,
    CardName,
    DescriptionCard,
    ChannelId,
    ListName
)


# --- Low-Level API Functions ---

def get_trello_boards() -> Optional[Dict[str, str]]:
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
    headers = {"Accept": "application/json"}
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        boards_dict = {board['name']: board['id'] for board in response.json()}
        return boards_dict
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_trello_lists(board_id: BoardID) -> Optional[Dict[str, str]]:
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
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        lists_dict = {list_item['name']: list_item['id'] for list_item in response.json()}
        return lists_dict
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_cards_in_list(list_id: ListId) -> Optional[Dict[str, str]]:
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
    headers = {"Accept": "application/json"}
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        card_dict = {card['name']: card['id'] for card in response.json()}
        return card_dict
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def create_trello_card(
        list_id: ListId,
        name:CardName, desc:DescriptionCard = ''
        ) -> Optional[Dict[str, str]]:
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
    headers = {"Accept": "application/json"}
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
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None
   
def update_trello_card(
            card_id: CardId,
            list_id: Optional[ListId] = None,
            name: Optional[CardName] = None,
            desc:Optional[DescriptionCard] = None)-> Optional[Dict[str, Any]]:
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
    headers = {"Accept": "application/json"}
    params = {"key": TRELLO_API_KEY,"token": TRELLO_TOKEN}
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
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None

def get_trello_card(card_id:CardId) -> Optional[Dict[str,Any]]:
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
    headers = {"Accept": "application/json"}
    params = {"key": TRELLO_API_KEY,"token": TRELLO_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Request failed (e.g., network issue): {e}')
        return None


# --- High-Level Tools for the Agent ---

def list_boards() -> Dict[str, Any]:
    """
    Retrieves all available Trello boards and returns structured data.
    """
    boards = get_trello_boards()
    
    if  boards is None:
        return {
            "type": "boards_list",
            "status": "error",
            "message": "Unable to retrieve your Trello boards. Please try again later."
        }
    
    if len(boards) == 0:
        return {
            "type": "boards_list",
            "status": "success",
            "boards": {},
            "message": "You don't have any Trello boards."
        }
    
    return {
        "type": "boards_list",
        "status": "success",
        "boards": boards
    }
    
def list_cards_in_list(
        list_name: ListName,
        board_id: Optional[BoardID] = None) -> Dict[str, Any]:
    """Retrieves all cards in a specific list and returns structured data."""
    board_id = board_id or BOARD_ID
   
    lists = get_trello_lists(board_id)
    if not lists:
        return {
            "type": "cards_list",
            "status": "error",
            "message": "Unable to retrieve list from the board."
        }
    
    lists_lower = {name.lower(): (name, id) for name, id in lists.items()}

    if list_name.lower() in lists_lower:
        actual_list_name, list_id = lists_lower[list_name.lower()]
        cards = get_cards_in_list(list_id)

        if cards is None:
            return {
            "type": "cards_list",
            "status": "error",
            "message": f"Unable to retrieve cards from '{actual_list_name}'."
            }
        
        return {
            "type": "cards_list",
            "status": "success",
            "list_name": actual_list_name,
            "cards": cards
        }
        
    else:
        suggestions = [name for name in lists.keys() if list_name.lower() in name.lower()]
        return {
            "type": "cards_list",
            "status": "error",
            "message": f"List '{list_name}' not found on the board.",
            "suggestions": suggestions if suggestions else None
        }
 
def create_new_card(
        card_name: CardName,
        list_name: ListName,
        description: DescriptionCard = "",
        board_id: Optional[BoardID] = None) -> Dict[str, Any]:
    """Creates a new card in the specified list and returns structured data."""
    board_id = board_id or BOARD_ID
    
    lists = get_trello_lists(board_id)
    if not lists:
        return {
            "type": "create_card",
            "status": "error",
            "message": "Unable to retrieve lists from the board."
        }
    
    lists_lower = {name.lower(): (name, id) for name, id in lists.items()}

    if list_name.lower() in lists_lower:
        actual_list_name, list_id = lists_lower[list_name.lower()]
        result = create_trello_card(list_id, card_name, description)

        if result:
            return {
                "type": "card_created",
                "status": "success",
                "card_name": card_name,
                "list_name": actual_list_name,
                "card_data": result
            }
        else:
            return {
                "type": "card_created",
                "status": "error",
                "message": f"Failed to create card '{card_name}'."
            }
    else:
        suggestions = [name for name in lists.keys() if list_name.lower() in name.lower()]
        return {
            "type": "card_created",
            "status": "error",
            "message": f"List '{list_name}' not found.",
            "suggestions": suggestions
        }

def move_card_between_lists(
        card_name: str,
        source_list_name: str,
        target_list_name: str,
        board_id: Optional[str] = BOARD_ID) -> Dict[str, Any]:
    """Moves a card between lists and returns structured data."""
    board_id = board_id or BOARD_ID
    
    lists = get_trello_lists(board_id)
    if not lists:
        return {
            "type": "card_moved",
            "status": "error",
            "message": "Unable to retrieve lists from the board."
        }
    
    lists_lower = {name.lower(): (name, id) for name, id in lists.items()}
    
    # Verify source list
    if source_list_name.lower() not in lists_lower:
        suggestions = [name for name in lists.keys() if source_list_name.lower() in name.lower()]
        return {
            "type": "card_moved",
            "status": "error",
            "message": f"Source list '{source_list_name}' not found.",
            "suggestions": suggestions
        }
    
    # Verify target list
    if target_list_name.lower() not in lists_lower:
        suggestions = [name for name in lists.keys() if target_list_name.lower() in name.lower()]
        return {
            "type": "card_moved",
            "status": "error",
            "message": f"Target list '{target_list_name}' not found.",
            "suggestions": suggestions
        }
    
    source_list_actual, source_list_id = lists_lower[source_list_name.lower()]
    target_list_actual, target_list_id = lists_lower[target_list_name.lower()]
    
    # Get cards in source list
    cards = get_cards_in_list(source_list_id)
    if cards is None:
        return {
            "type": "card_moved",
            "status": "error",
            "message": f"Unable to retrieve cards from '{source_list_actual}'."
        }
    
    # Case-insensitive card search
    cards_lower = {name.lower(): (name, id) for name, id in cards.items()}
    
    if card_name.lower() in cards_lower:
        card_actual_name, card_id = cards_lower[card_name.lower()]
        result = update_trello_card(card_id, target_list_id)
        
        if result:
            return {
                "type": "card_moved",
                "status": "success",
                "card_name": card_actual_name,
                "source_list": source_list_actual,
                "target_list": target_list_actual,
                "card_data": result
            }
        else:
            return {
                "type": "card_moved",
                "status": "error",
                "message": f"Failed to move card '{card_actual_name}'."
            }
    else:
        suggestions = [name for name in cards.keys() if card_name.lower() in name.lower()]
        return {
            "type": "card_moved",
            "status": "error",
            "message": f"Card '{card_name}' not found in '{source_list_actual}'.",
            "suggestions": suggestions
        }

def update_card_details(
        card_name: str,
        list_name: str,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        board_id: Optional[str] = None) -> Dict[str, Any]:
    """Updates card details and returns structured data."""
    if not new_name and not new_description:
        return {
            "type": "card_updated",
            "status": "error",
            "message": "No updates specified."
        }
    
    board_id = board_id or BOARD_ID
    
    lists = get_trello_lists(board_id)
    if not lists:
        return {
            "type": "card_updated",
            "status": "error",
            "message": "Unable to retrieve lists from the board."
        }
    
    if list_name not in lists:
        return {
            "type": "card_updated",
            "status": "error",
            "message": f"List '{list_name}' not found."
        }
    
    cards = get_cards_in_list(lists[list_name])
    if cards is None:
        return {
            "type": "card_updated",
            "status": "error",
            "message": f"Unable to retrieve cards from '{list_name}'."
        }
    
    if card_name not in cards:
        return {
            "type": "card_updated",
            "status": "error",
            "message": f"Card '{card_name}' not found in '{list_name}'."
        }
    
    result = update_trello_card(cards[card_name], name=new_name, desc=new_description)
    
    if result:
        updates = []
        if new_name:
            updates.append("name")
        if new_description:
            updates.append("description")
        
        return {
            "type": "card_updated",
            "status": "success",
            "card_name": card_name,
            "updates": updates,
            "card_data": result
        }
    else:
        return {
            "type": "card_updated",
            "status": "error",
            "message": f"Failed to update card '{card_name}'."
        }

def generate_daily_stand_up(board_id: Optional[BoardID] = None) -> Dict[str, Any]:
    """Generates a daily stand-up report and returns structured data."""
    board_id = board_id or BOARD_ID
    
    lists = get_trello_lists(board_id)
    if not lists:
        return {
            "type": "daily_summary",
            "status": "error",
            "message": "Unable to retrieve lists from the board."
        }
    
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
        try:
            last_activity = datetime.fromisoformat(card['dateLastActivity'].replace('Z', '+00:00'))
            if last_activity.date() == today:
                today_cards.append(card)
        except (ValueError, TypeError):
            continue
    
    if not today_cards:
        summary += "No cards were updated today.\n"
        return {
            "type": "daily_summary",
            "status": "success",
            "summary": summary,
            "cards_count": 0
        }
    
    summary += f"## Cards Updated Today ({len(today_cards)})\n\n"
    
    for card in today_cards:
        name = card['name']
        description = card['desc'] if card['desc'] else "No description"
        status = "Open" if not card['closed'] else "Closed"
        url = card['url']
        
        summary += f"### {name}\n"
        summary += f"- **Status:** {status}\n"
        summary += f"- **Description:** {description}\n"
        summary += f"- **Last Updated:** {card['dateLastActivity']}\n"
        summary += f"- **URL:** {url}\n\n"
    
    return {
        "type": "daily_summary",
        "status": "success",
        "summary": summary,
        "cards_count": len(today_cards),
        "cards": today_cards
    }

# --- Slack Comunication Function ---

def send_to_slack(
    message: str, 
    channel_id: ChannelId, 
    blocks: Optional[List[Dict]] = None,
    thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """Direct function to send messages to Slack. Used only by the coordinator."""
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": channel_id,
        "text": message
    }
    
    if blocks:
        payload["blocks"] = blocks
    if thread_ts:
        payload["thread_ts"] = thread_ts
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("ok"):
            return response_data
        else:
            print(f"Error sending to Slack: {response_data}")
            return {"ok": False, "error": response_data.get("error", "Unknown error")}
    except Exception as e:
        print(f"Exception sending to Slack: {str(e)}")
        return {"ok": False, "error": str(e)}


# Export tools list for the agent
tools = [
    # Low-level API tools
    get_trello_boards,
    get_trello_lists,
    get_cards_in_list,
    create_trello_card,
    update_trello_card,
    get_trello_card,
    
    # High-level tools that return structured data
    list_boards,
    list_cards_in_list,
    create_new_card,
    move_card_between_lists,
    update_card_details,
    generate_daily_stand_up
]