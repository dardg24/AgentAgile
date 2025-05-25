from typing import Dict, Any, List, Optional
from utils import (
    SLACK_CHANNEL_ID,
    ListName,
    CardsDict,
    ChannelId
    )


class SlackResponseCoordinator:
    """
    Coordinates all responses to Slack, ensuring that only one message is
    sent per operation and with the appropriate formatting.

    This class provides static methods to format various types of messages
    (e.g., lists of cards, success messages, error messages, daily reports)
    into Slack's block kit format and then send them to a specified Slack channel.
    It aims to centralize Slack communication logic.
    """

    @staticmethod
    def format_cards_list(list_name: ListName, cards: CardsDict) -> List[Dict]:
        """
        Formats a list of Trello cards into Slack block kit elements.

        This method creates a header with the list name and then lists each card.
        If there are no cards, it displays a message indicating that the list is empty.

        Args:
            list_name: The name of the Trello list from which the cards are sourced.
            cards: A dictionary where keys are card names (str) and values are card IDs (str).

        Returns:
            A list of dictionaries, where each dictionary represents a Slack block element,
            suitable for use in a Slack message payload.
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Cards in '{list_name}'",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]

        # Add each card as a section
        if cards:
            for card_name, card_id in cards.items():
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {card_name}" # card_id is available if needed later: f"• {card_name} (ID: {card_id})"
                    }
                })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_No cards in this list_"
                }
            })

        return blocks

    @staticmethod
    def format_success_message(message: str) -> List[Dict]:
        """Formats a generic success message as Slack blocks.

        This method creates a Slack message block indicating a successful operation,
        displaying a custom message string.

        Args:
            message: The success message string to display.

        Returns:
            A list of Slack block elements representing the success message.
        """
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Success*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ]

    @staticmethod
    def format_error_message(error: str, suggestions: Optional[List[str]] = None) -> List[Dict]:
        """Formats an error message as Slack blocks, optionally including suggestions.

        This method creates a Slack message block indicating an error,
        displaying the error message and any provided suggestions for correction.

        Args:
            error: The error message string to display.
            suggestions: An optional list of string suggestions to help the user.
                         If provided, these will be formatted and included in the message.

        Returns:
            A list of Slack block elements representing the error message.
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *Error*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": error
                }
            }
        ]

        if suggestions:
            suggestion_text = "Did you mean one of these? " + ", ".join([f"`{s}`" for s in suggestions])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": suggestion_text
                }
            })

        return blocks

    @staticmethod
    def format_daily_report(report_content: str) -> List[Dict]:
        """Formats a daily stand-up report string into Slack blocks for better readability.

        The method expects the `report_content` to be a string where sections are
        delimited by "##". It extracts a title, date (if present in the first section),
        and then formats each subsequent section with a title and its content.

        Args:
            report_content: The string content of the daily report.
                            It's expected to have a structure like:
                            "Date: YYYY-MM-DD\n[Optional other info]\n## Section Title 1\nContent1...\n## Section Title 2\nContent2..."

        Returns:
            A list of Slack block elements formatted for displaying the daily report.
        """
        title = "Daily Stand-Up Summary"

        # Split the report into sections for more user-friendly formatting
        sections = report_content.split("##")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title,
                    "emoji": True
                }
            }
        ]

        # Add the date (we assume it's in the first section before the first "##")
        if len(sections) > 0:
            date_section_content = sections[0]
            # Attempt to find a line containing "Date:"
            date_lines = [line for line in date_section_content.split("\n") if "Date:" in line]
            if date_lines:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": date_lines[0].strip() # Display the first line that contains "Date:"
                    }
                })

        blocks.append({"type": "divider"})

        # Add each main section (skipping the first part which might contain the date or be empty if report starts with ##)
        for i, section_content in enumerate(sections[1:], 1): # Start from the first actual section after "##"
            lines = section_content.strip().split("\n")
            if lines:
                # Section Title
                section_title = lines[0].strip() # First line of the section is its title
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{section_title}*"
                    }
                })

                # Section Content
                content = "\n".join(lines[1:]).strip() # The rest of the lines form the content
                if content:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": content
                        }
                    })

                # Add a divider after each section's content, unless it's the very last block
                blocks.append({"type": "divider"})
        
        # Remove last divider if it exists to prevent trailing divider
        if blocks and blocks[-1].get("type") == "divider":
            blocks.pop()

        return blocks

    @staticmethod
    def send_response(
        result: Dict[str, Any],
        channel_id: ChannelId = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a formatted response to Slack based on the operation result.

        This method determines the type of message to send (error, cards list,
        card creation confirmation, etc.) based on the `result` dictionary.
        It then formats the message accordingly using other static methods in this class
        and sends it to the specified Slack channel and thread (if applicable).

        Args:
            result: A dictionary containing the details of the operation's outcome.
                    Expected keys vary based on `result["type"]` and `result["status"]`:
                    - "type" (str): REQUIRED. The type of result, e.g., "cards_list",
                      "card_created", "card_moved", "card_updated", "boards_list",
                      "daily_summary", or a generic type for simple messages.
                    - "status" (str, optional): "success" or "error". Defaults to "success"
                      if not provided. If "error", "message" is used for the error text.
                    - "message" (str, optional): A general message. Used for success messages
                      of unknown types or as the error message if status is "error".
                    - "suggestions" (List[str], optional): A list of suggestions if an error
                      occurred. Used if `status` is "error".
                    - "list_name" (str, optional): Name of the Trello list. Used for "cards_list"
                      and "card_created" types.
                    - "cards" (Dict[str, str], optional): A dictionary of cards (name: id).
                      Used for "cards_list" type.
                    - "card_name" (str, optional): Name of the Trello card. Used for
                      "card_created", "card_moved", "card_updated" types.
                    - "source_list" (str, optional): Source list name for a moved card.
                      Used for "card_moved" type.
                    - "target_list" (str, optional): Target list name for a moved card.
                      Used for "card_moved" type.
                    - "updates" (List[str], optional): List of updated fields for a card
                      (e.g., ["name", "description"]). Used for "card_updated" type.
                    - "boards" (Dict[str, str], optional): Dictionary of Trello boards (name: id).
                      Used for "boards_list" type.
                    - "summary" (str, optional): Content for a daily summary.
                      Used for "daily_summary" type.
            channel_id: The ID of the Slack channel to send the message to.
                        If None, `SLACK_CHANNEL_ID` from the utils/config will be used.
            thread_ts: The timestamp of a parent message to reply in a thread.
                       If None, the message is sent as a new message in the channel.

        Returns:
            A dictionary containing the response from the `send_to_slack` utility,
            which typically includes information about the message posting status.
        """

        from tools import send_to_slack

        final_channel_id: ChannelId = channel_id or SLACK_CHANNEL_ID # Ensure type consistency

        result_type = result.get("type")
        status = result.get("status", "success") # Default to success if status is not provided

        blocks: Optional[List[Dict[str, Any]]] = None # Initialize blocks as None
        text: str = "" # Fallback text for Slack notification

        # Handle error status first, as it overrides other types
        if status == "error":
            error_msg = result.get("message", "An unknown error occurred.")
            suggestions = result.get("suggestions") # Can be None
            blocks = SlackResponseCoordinator.format_error_message(error_msg, suggestions)
            text = f"❌ {error_msg}"
            return send_to_slack(message=text, channel_id=final_channel_id, blocks=blocks, thread_ts=thread_ts)

        # Handle different types of successful results
        if result_type == "cards_list":
            list_name: ListName = result.get("list_name", "Unknown List")
            cards: CardsDict = result.get("cards", {})

            if not cards:
                text = f"📋 The list '{list_name}' has no cards."
            else:
                text = f"📋 Found {len(cards)} card(s) in '{list_name}'."
            blocks = SlackResponseCoordinator.format_cards_list(list_name, cards)

        elif result_type == "card_created":
            card_name = result.get("card_name", "Unknown Card")
            list_name = result.get("list_name", "Unknown List")
            text = f"✅ Successfully created card '{card_name}' in list '{list_name}'."
            blocks = SlackResponseCoordinator.format_success_message(text)

        elif result_type == "card_moved":
            card_name = result.get("card_name", "Unknown Card")
            source_list = result.get("source_list", "Unknown Source List")
            target_list = result.get("target_list", "Unknown Target List")
            text = f"✅ Successfully moved card '{card_name}' from '{source_list}' to '{target_list}'."
            blocks = SlackResponseCoordinator.format_success_message(text)

        elif result_type == "card_updated":
            card_name = result.get("card_name", "Unknown Card")
            updates: List[str] = result.get("updates", [])
            updates_text = " and ".join(updates) if updates else "details"
            text = f"✅ Successfully updated {updates_text} of card '{card_name}'."
            blocks = SlackResponseCoordinator.format_success_message(text)

        elif result_type == "boards_list":
            boards: Dict[str, str] = result.get("boards", {})
            if not boards:
                text = "📋 No Trello boards found."
                blocks = [{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": text}
                }]
            else:
                text = f"📋 Found {len(boards)} Trello board(s)."
                board_blocks: List[Dict[str, Any]] = [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "📋 Your Trello Boards", "emoji": True}
                    },
                    {"type": "divider"}
                ]
                for board_name in boards.keys(): # Assuming boards is Dict[name, id]
                    board_blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"• {board_name}"}
                    })
                blocks = board_blocks

        elif result_type == "daily_summary":
            summary_text = result.get("summary", "")
            text = "📊 Daily Stand-Up Summary" # Short text for notification
            # If the summary is long or needs complex formatting, use blocks.
            # The threshold of 500 is arbitrary and can be adjusted.
            if len(summary_text) > 500 or "##" in summary_text: # "##" indicates sections
                blocks = SlackResponseCoordinator.format_daily_report(summary_text)
            else:
                # For short or simple summaries, send as plain text or a simple block
                text = summary_text # Overwrite the generic summary text if it's short
                blocks = [{
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": summary_text}
                }]


        else:
            # Generic success response for unrecognized types or if no specific formatting is needed
            text = result.get("message", "Operation completed successfully.")
            # For generic messages, we can use format_success_message or just a simple section
            blocks = SlackResponseCoordinator.format_success_message(text) if status == "success" else [{
                 "type": "section",
                 "text": {"type": "mrkdwn", "text": text}
            }]


        return send_to_slack(message=text, channel_id=final_channel_id, blocks=blocks, thread_ts=thread_ts)

    @staticmethod
    def send_progress_update(
        message: str,
        channel_id: Optional[ChannelId] = None, 
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a progress update message to Slack while a longer operation is processing.

        This is useful for providing feedback to the user during tasks that may take some time,
        indicating that the system is still working on their request.

        Args:
            message: The progress message to display (e.g., "Processing your request...").
            channel_id: The ID of the Slack channel to send the update to.
                        If None, `SLACK_CHANNEL_ID` from utils/config will be used.
            thread_ts: The timestamp of a parent message, to send the update as a reply in a thread.
                       If None, the update is sent as a new message in the channel.

        Returns:
            A dictionary containing the response from the `send_to_slack` utility,
            which typically includes information about the message posting status.
        """
        # Import here to avoid circular imports

        from tools import send_to_slack 

        final_channel_id: ChannelId = channel_id or SLACK_CHANNEL_ID # Ensure type consistency

        blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⏳ {message}"
            }
        }]
        text_summary = f"⏳ {message}"

        return send_to_slack(message=text_summary, channel_id=final_channel_id, blocks=blocks, thread_ts=thread_ts)