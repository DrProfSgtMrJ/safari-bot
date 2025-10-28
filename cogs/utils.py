import random
import pokebase as pb
from sqlalchemy import func, select
from data_models.pokemon import Rarity, Pokemon

from db.db import AsyncSessionLocal
from db.models import Pokemon as DbPokemon

RARITY_WEIGHTS = {
    Rarity.COMMON: 60,
    Rarity.UNCOMMON: 25,
    Rarity.RARE: 10,
    Rarity.LEGENDARY: 5
}

async def get_random_pokemon() -> Pokemon:
    # Pick rarities
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    chosen_rarity = random.choices(rarities, weights=weights, k=1)[0]

    # Pick random Pokemon of that rarity
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DbPokemon)
            .where(DbPokemon.rarity == chosen_rarity)
            .order_by(func.random())
            .limit(1)
        )
        pokemon = result.scalar_one_or_none()
        return Pokemon.from_db_pokemon(db_pokemon=pokemon)

