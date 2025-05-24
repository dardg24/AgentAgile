import os
from dotenv import load_dotenv

# Constants for the application
# Loading enviroments constants
load_dotenv()
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_TOKEN = os.getenv("APP_TOKEN")
BOARD_ID = os.getenv('BOARD_ID')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

# Langchain constants
LANGCHAIN_API_KEY =  os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING = os.getenv('LANGCHAIN_TRACING')
LANGSMITH_PROJECT= os.getenv('LANGSMITH_PROJECT')

# NewTypeHints for functions
from typing import NewType

CardId = NewType('CardId', str)
ListId = NewType('ListId', str)
BoardID = NewType('BoardID', str)
CardName = NewType('CardName', str)
ListName = NewType('ListName', str)
PositionCard = NewType('PositionCard', float)
DescriptionCard = NewType('DescriptionCard', str)
ChannelId = NewType('ChannelId', str)

