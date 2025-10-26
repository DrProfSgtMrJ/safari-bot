from dataclasses import dataclass
from enum import Enum
from discord import Embed, Color


class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "lengendary"

    def get_star(self) -> str:
        if self == Rarity.COMMON:
            return "⭐"
        elif self == Rarity.UNCOMMON:
            return "⭐⭐"
        elif self == Rarity.RARE:
            return "⭐⭐⭐"
        else:
            return "⭐⭐⭐⭐"

@dataclass
class Pokemon:
    name: str
    sprite_url: str
    rarity: Rarity

    def to_embeded(self) -> Embed:
        embed = Embed(
            title=f"A wild {self.name} appeared!",
            description="What will you do?",
            color=Color.ash_embed()
        )
        embed.set_image(url=self.sprite_url)
        embed.set_footer(text=f"Rarity: {self.rarity}: {self.rarity.get_star()}")

        return embed
