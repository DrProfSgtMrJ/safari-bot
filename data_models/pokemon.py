from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from discord import Embed, Color
from db.models import CaughtPokemon, Pokemon as DbPokemon, Rarity as DbRarity


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
    WILD = "WILD"

@dataclass
class Pokemon:
    id: int
    name: str
    sprite_url: str
    rarity: Rarity
    status: PokemonStatus = PokemonStatus.WILD
    caught_at: datetime | None = None
    fled_at: datetime | None = None
    flee_modifier: float = 0.0 # increases with failed throws
    bait_modifier: float = 0.0 # increases/decreases with bait

    @classmethod
    def from_db_pokemon(cls, db_pokemon: DbPokemon, status: PokemonStatus = PokemonStatus.WILD) -> "Pokemon":
        return cls(
            id=int(db_pokemon.id),
            name=str(db_pokemon.name),
            sprite_url=str(db_pokemon.sprite_url),
            rarity=Rarity.from_db_rarity(db_pokemon.rarity),
            status=status,
        )

    @classmethod
    def from_db_caught_pokemon(cls, db_caught_pokemon: CaughtPokemon) -> "Pokemon":
        poke: DbPokemon = db_caught_pokemon.pokemon
        return cls(
            id=int(poke.id),
            name=str(poke.name),
            sprite_url=str(poke.sprite_url),
            rarity=Rarity.from_db_rarity(poke.rarity),
            status=PokemonStatus.CAUGHT,
            caught_at=db_caught_pokemon.caught_at
        )

    def __post_init__(self):
        self.catch_chance = self.rarity.catch_chance()
        self.flee_chance = self.rarity.flee_chance()
    
    @property
    def effective_catch_chance(self) -> float:
        """ base + bait bonus, capped at 0.95"""
        return min(self.rarity.catch_chance() + self.bait_modifier, 0.95)

    @property
    def effetive_flee_chance(self) -> float:
        """ base + flee mod, capped at [0.05, 1.0]"""
        return max(
            min(self.rarity.flee_chance() + self.flee_modifier - self.bait_modifier, 1.0)
            , 0.05
        )

    def flee(self, fled_at: datetime):
        self.status = PokemonStatus.FLED
        self.fled_at = fled_at

    def catch(self, caught_at: datetime):
        self.status = PokemonStatus.CAUGHT
        self.caught_at = caught_at

    def to_wild_embeded(self) -> Embed:
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
    
    def to_caught_embeded(self) -> Embed:
        embed = Embed(
            title=self.name,
            description=f"Rarity: {self.rarity.get_star()}",
            color=0x00BFFF # light blue
        )
        embed.set_image(url=self.sprite_url)
        embed.set_footer(text=f"Caught at {self.caught_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

        return embed

