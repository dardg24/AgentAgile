# NewTypeHints for functions
from typing import NewType, Dict, Any

CardId = NewType('CardId', str)
ListId = NewType('ListId', str)
BoardID = NewType('BoardID', str)
CardName = NewType('CardName', str)
ListName = NewType('ListName', str)
PositionCard = NewType('PositionCard', float)
DescriptionCard = NewType('DescriptionCard', str)
ChannelId = NewType('ChannelId', str)
CardsDict = NewType('CardsDict', Dict[str, Any])