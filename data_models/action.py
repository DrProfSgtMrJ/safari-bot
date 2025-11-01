from dataclasses import dataclass
from discord import Interaction
from enum import Enum

class ActionType(str, Enum):
    BAIT = "BAIT"
    POKEBALL = "POKEBALL"



@dataclass
class UserAction:
    discord_user_id: int
    interaction: Interaction
    action_type: ActionType

