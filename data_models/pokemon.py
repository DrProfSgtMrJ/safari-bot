from dataclasses import dataclass
from enum import Enum
from discord import Embed, Color
from db.models import Pokemon as DbPokemon, Rarity as DbRarity


class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"

    def get_star(self) -> str:
        if self == Rarity.COMMON:
            return "⭐"
        elif self == Rarity.UNCOMMON:
            return "⭐⭐"
        elif self == Rarity.RARE:
            return "⭐⭐⭐"
        else:
            return "⭐⭐⭐⭐"

    def catch_chance(self) -> float:
        if self == Rarity.COMMON:
            return 0.6
        elif self == Rarity.UNCOMMON:
            return 0.45
        elif self == Rarity.RARE:
            return 0.3
        else:
            return 0.1

    def flee_chance(self) -> float:
        if self == Rarity.COMMON:
            return 0.05
        elif self == Rarity.UNCOMMON:
            return 0.1
        elif self == Rarity.RARE:
            return 0.2
        else:
            return 0.5

    @classmethod
    def from_db_rarity(cls, db_rarity: DbRarity) -> "Rarity":
        return cls(db_rarity.value)

class PokemonStatus(str, Enum):
    FLED = "FLED"
    CAUGHT = "CAUGHT"
    EMPTY = "EMPTY"

@dataclass
class Pokemon:
    id: int
    name: str
    sprite_url: str
    rarity: Rarity
    status: PokemonStatus = PokemonStatus.EMPTY
    catch_chance: float = 0
    flee_chance: float = 0

    @classmethod
    def from_db_pokemon(cls, db_pokemon: DbPokemon) -> "Pokemon":
        return cls(id=int(db_pokemon.id), name=str(db_pokemon.name), sprite_url=str(db_pokemon.sprite_url), rarity=Rarity.from_db_rarity(db_pokemon.rarity))

    def __post_init__(self):
        self.catch_chance = self.rarity.catch_chance()
        self.flee_chance = self.rarity.flee_chance()

    def to_embeded(self) -> Embed:
        embed = Embed(
            title=f"A wild {self.name} appeared!",
            description="What will you do?",
            color=Color.ash_embed()
        )
        embed.set_image(url=self.sprite_url)
        footer_str = f"Rarity: {self.rarity.get_star()}"
        if self.status == PokemonStatus.CAUGHT:
            footer_str += "\n✅ CAUGHT✅ "
        elif self.status == PokemonStatus.FLED:
            footer_str += "\n❌FLED❌"

        embed.set_footer(text=footer_str)

        return embed
