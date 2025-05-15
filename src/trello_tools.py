import requests
from config import (
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    BoardID,
    ListId,
    CardId,
    CardName
)
from typing import Dict, List, Optional, TypedDict, Any

# Trello API functions
def get_trello_boards() -> Dict[str, str]:
    """
    Gets all Trello boards accesible to the user.

    This tool allows the agent to retrieve and list all available Trello boards,
    providing tthe user with an overview of their Trello workspace.

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
            Returns None if the API call fails.
    
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
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        card_dict = {card['name']: card['id'] for card in response.json()}
        return card_dict
    else:
        print(f"Error: {response.status_code}")
        return None

def create_trello_card(list_id, name, desc=""):
    """
    Creates a new card in the specified list.
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
    
    response = requests.post(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def update_trello_card(card_id, list_id=None, name=None, desc=None):
    """
    Updates a Trello card. Any parameter that is None will not be updated.
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
    
    response = requests.put(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def get_trello_card(card_id):
    """
    Gets details of a specific Trello card.
    """
    url = f"https://api.trello.com/1/cards/{card_id}"
    
    headers = {
        "Accept": "application/json"
    }
    
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None