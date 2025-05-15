import requests
from config import (
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    BoardID,
    ListId,
    CardId,
    CardName,
    DescriptionCard
)
from typing import Dict, Optional, Any

# Trello API functions
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

tools = [
    get_trello_boards,
    get_trello_lists,
    get_cards_in_list,
    create_trello_card,
    update_trello_card,
    get_trello_card
 ]