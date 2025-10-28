from dataclasses import dataclass
from enum import Enum
from discord import Embed, Color
from db.models import Pokemon as DbPokemon


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
    id: int
    name: str
    sprite_url: str
    rarity: Rarity

    @classmethod
    def from_db_pokemon(cls, db_pokemon: DbPokemon) -> "Pokemon":
        return cls(id=int(db_pokemon.id), name=str(db_pokemon.name), sprite_url=str(db_pokemon.sprite_url), rarity=Rarity(db_pokemon.rarity))

    def to_embeded(self) -> Embed:
        embed = Embed(
            title=f"A wild {self.name} appeared!",
            description="What will you do?",
            color=Color.ash_embed()
        )
        embed.set_image(url=self.sprite_url)
        embed.set_footer(text=f"Rarity: {self.rarity}: {self.rarity.get_star()}")

        return embed
