import requests
from config import TRELLO_API_KEY, TRELLO_TOKEN
from typing import Dict, List, Optional, TypedDict, Any

# Trello API functions
def get_trello_boards():
    """
    Gets all Trello boards accesible to the user.

    This tool allows the agent to retrieve and list all available Trello boards,
    providing tthe user with an overview of their Trello workspace.

    Returns:
        Dict[str, str]: A dictionary mapping board names to their IDs.
        Example: {"Board Name": "12345abcdef"}
        Returns None if the API call fails.

    Raises:
        ConnectionError: If unable to connect to the Trello API.
    """
    url = "https://api.trello.com/1/members/me/boards"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        # Create a dictionary of board names to board IDs
        boards_dict = {board['name']: board['id'] for board in response.json()}
        return boards_dict
    else:
        print(f"Error: {response.status_code}")
        return None

def get_trello_lists(board_id):
    """
    Gets all lists on a specific Trello board.
    Returns a dictionary mapping list names to list IDs.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    
    params = {
        "key": TRELLO_API_KEY, 
        "token": TRELLO_TOKEN
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        lists_dict = {list_item['name']: list_item['id'] for list_item in response.json()}
        return lists_dict
    else:
        print(f"Error: {response.status_code}")
        return None

def get_cards_in_list(list_id):
    """
    Gets all cards in a specific Trello list.
    Returns a dictionary mapping card names to card IDs.
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