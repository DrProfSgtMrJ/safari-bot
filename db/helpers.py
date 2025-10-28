import random
from sqlalchemy import func, select
from db.db import AsyncSessionLocal
from db.models import Pokemon, Rarity

RARITY_WEIGHTS = {
    Rarity.COMMON: 60,
    Rarity.UNCOMMON: 25,
    Rarity.RARE: 10,
    Rarity.LEGENDARY: 5
}

# Pokemon Selection
def get_rarity() -> Rarity:
    rarities = list(RARITY_WEIGHTS.keys())
    weights = list(RARITY_WEIGHTS.values())
    return random.choices(rarities, weights=weights, k=1)[0]

async def get_rand_pokemon_by_rarity(rarity: Rarity) -> Pokemon | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Pokemon)
            .where(Pokemon.rarity == rarity)
            .order_by(func.random())
            .limit(1)
        )

        return result.scalar_one_or_none()


# Use Safari Inventory

async def use_bait(discord_id: int):
    pass

