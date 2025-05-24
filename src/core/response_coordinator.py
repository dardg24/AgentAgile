import json

from typing import Dict, Any, List, Optional

from utils import (
    SLACK_CHANNEL_ID,
    ListName,
    Cards_dict,
    ChannelId
    )


class SlackResponseCoordinator:
    """
    Coordinates all responses to Slack, ensuring that only one message is
    sent per operation and with the appropriate formatting.
    """
    
    @staticmethod
    def format_cards_list(list_name: ListName, cards: Cards_dict) -> List[Dict]:
        """
        Formats a list of cards for Slack blocks.
        
        Args:
            list_name: Name of the Trello list
            cards: A dictionary where keys are card names and values are card IDs 
            
        Returns:
            A list of Slack block elements
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type" : "plain_text",
                    "text" : f"📋 Cards in '{list_name}'",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add each card as a section
        if cards:
            for card_name, card_id in cards.items(): # card_id is not used in the original code, but kept for consistency
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• {card_name}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Move Card",
                            "emoji": True
                        },
                        "value": json.dumps({
                            "action": "move_card",
                            "source_list": list_name,
                            "card_name": card_name
                        })
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

        # Add button to create new card
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create New Card",
                        "emoji": True
                    },
                    "value": json.dumps({
                        "action": "create_card",
                        "list_name": list_name
                    })
                }
            ]
        })

        return blocks

    @staticmethod
    def format_success_message(message: str) -> List[Dict]:
        """Formats a success message as Slack blocks.

        Args:
            message: The success message string.

        Returns:
            A list of Slack block elements for a success message.
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
        """Formats an error message as Slack blocks.

        Args:
            error: The error message string.
            suggestions: An optional list of string suggestions.

        Returns:
            A list of Slack block elements for an error message.
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

        # Add suggestions if present
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
        """Formats a daily report as Slack blocks.

        Args:
            report_content: The string content of the daily report.

        Returns:
            A list of Slack block elements for the daily report.
        """
        # Extract sections from the report
        title = "Daily Stand-Up Summary"

        # Split the report into sections for a friendlier format
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

        # Add the date (assuming it's in the first section)
        if len(sections) > 0:
            date_section = sections[0]
            date_lines = [line for line in date_section.split("\n") if "Date:" in line]
            if date_lines:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": date_lines[0].strip()
                    }
                })

        blocks.append({"type": "divider"})

        # Add each main section
        for i, section in enumerate(sections[1:], 1): # Start from the second element as the first might be the date or empty
            lines = section.strip().split("\n")
            if lines:
                # Section title
                section_title = lines[0].strip()
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{section_title}*"
                    }
                })

                # Section content
                content = "\n".join(lines[1:]).strip()
                if content:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": content
                        }
                    })

                if i < len(sections[1:]): # Add divider if not the last section
                    blocks.append({"type": "divider"})

        return blocks

    @staticmethod
    def send_response(
        result: Dict[str, Any],
        channel_id: ChannelId = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a formatted response to Slack based on the operation result.

        Args:
            result: A dictionary containing the operation result.
                    Expected keys:
                        "type" (str): The type of result (e.g., "cards_list", "card_created", "error").
                        "status" (str, optional): "success" or "error". Defaults to "success".
                        "message" (str, optional): A general message.
                        "suggestions" (List[str], optional): Suggestions for errors.
                        "list_name" (str, optional): Name of the Trello list.
                        "cards" (Dict[str, str], optional): Dictionary of cards.
                        "card_name" (str, optional): Name of the Trello card.
                        "source_list" (str, optional): Source list name for moved card.
                        "target_list" (str, optional): Target list name for moved card.
                        "updates" (List[str], optional): List of updated fields for a card.
                        "boards" (Dict[str, str], optional): Dictionary of Trello boards.
                        "summary" (str, optional): Content for daily summary.
            channel_id: The ID of the Slack channel. Uses SLACK_CHANNEL_ID from config if None.
            thread_ts: The thread timestamp for replies in threads.

        Returns:
            A dictionary with the result of sending the message to Slack.
        """
        # Import here to avoid circular imports
        from core.tools import send_to_slack # Assuming this function exists and handles actual Slack API calls

        channel_id = channel_id or SLACK_CHANNEL_ID

        # Determine the result type
        result_type = result.get("type")
        status = result.get("status", "success") # Default to success if status is not provided

        # If there's an error, handle it first
        if status == "error":
            error_msg = result.get("message", "An unknown error occurred")
            suggestions = result.get("suggestions", [])
            blocks = SlackResponseCoordinator.format_error_message(error_msg, suggestions)
            return send_to_slack(f"❌ {error_msg}", channel_id, blocks, thread_ts)

        # Handle different types of successful results
        if result_type == "cards_list":
            list_name = result.get("list_name", "Unknown list")
            cards = result.get("cards", {})

            if not cards:
                text = f"📋 The list '{list_name}' has no cards."
            else:
                text = f"📋 Found {len(cards)} cards in '{list_name}'"

            blocks = SlackResponseCoordinator.format_cards_list(list_name, cards)
            return send_to_slack(text, channel_id, blocks, thread_ts)

        elif result_type == "card_created":
            card_name = result.get("card_name", "Unknown card")
            list_name = result.get("list_name", "Unknown list")

            text = f"✅ Successfully created card '{card_name}' in list '{list_name}'."
            blocks = SlackResponseCoordinator.format_success_message(text)
            return send_to_slack(text, channel_id, blocks, thread_ts)

        elif result_type == "card_moved":
            card_name = result.get("card_name", "Unknown card")
            source_list = result.get("source_list", "Unknown source list")
            target_list = result.get("target_list", "Unknown target list")

            text = f"✅ Successfully moved card '{card_name}' from '{source_list}' to '{target_list}'."
            blocks = SlackResponseCoordinator.format_success_message(text)
            return send_to_slack(text, channel_id, blocks, thread_ts)

        elif result_type == "card_updated":
            card_name = result.get("card_name", "Unknown card")
            updates = result.get("updates", []) # e.g. ["description", "due date"]

            updates_text = " and ".join(updates) if updates else "details"
            text = f"✅ Successfully updated {updates_text} of card '{card_name}'."
            blocks = SlackResponseCoordinator.format_success_message(text)
            return send_to_slack(text, channel_id, blocks, thread_ts)

        elif result_type == "boards_list":
            boards = result.get("boards", {}) # Expects a dict like {"Board Name 1": "id1", "Board Name 2": "id2"}

            if not boards:
                text = "📋 No Trello boards found."
                blocks = [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                }]
            else:
                text = f"📋 Found {len(boards)} Trello boards"
                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📋 Your Trello Boards",
                            "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]

                for board_name in boards.keys():
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"• {board_name}"
                        }
                    })

            return send_to_slack(text, channel_id, blocks, thread_ts)

        elif result_type == "daily_summary":
            summary_text = result.get("summary", "")

            # If the summary is long, use formatted blocks
            if len(summary_text) > 500: # Arbitrary length for using blocks
                blocks = SlackResponseCoordinator.format_daily_report(summary_text)
                return send_to_slack("📊 Daily Stand-Up Summary", channel_id, blocks, thread_ts)
            else:
                # For shorter summaries, a simple text message might suffice
                # or use a simple block structure if preferred
                blocks = SlackResponseCoordinator.format_success_message(summary_text) # Or a custom simple block
                return send_to_slack(summary_text, channel_id, blocks=blocks, thread_ts=thread_ts)


        else:
            # Generic response for unrecognized successful types or simple messages
            message = result.get("message", "Operation completed successfully.")
            # Optionally, format even generic messages for consistency
            blocks = SlackResponseCoordinator.format_success_message(message)
            return send_to_slack(message, channel_id, blocks=blocks, thread_ts=thread_ts)

    @staticmethod
    def send_progress_update(
        message: str,
        channel_id: ChannelId = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a progress update while an operation is being processed.

        Args:
            message: The progress message.
            channel_id: The ID of the Slack channel. Uses SLACK_CHANNEL_ID from config if None.
            thread_ts: The thread timestamp for replies in threads.

        Returns:
            A dictionary with the result of sending the message to Slack.
        """
        from core.tools import send_to_slack 

        channel_id = channel_id or SLACK_CHANNEL_ID

        blocks = [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⏳ {message}"
            }
        }]

        return send_to_slack(f"⏳ {message}", channel_id, blocks, thread_ts)
