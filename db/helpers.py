import random
from sqlalchemy import func, select
from db.db import AsyncSessionLocal
from db.models import CaughtPokemon, Pokemon, Rarity, SafariInventory, Users
from enum import Enum

class UseBaitResult(str, Enum):
    NoInventoryFound = "NoInventoryFound"
    NoBaitLeft = "NoBaitLeft"
    BaitUsed = "BaitUsed"

class UseBallResult(str, Enum):
    NoInventoryFound = "NoInventoryFound"
    NoBallsLeft = "NoBallsLeft"
    BallUsed = "BallUsed"

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
async def use_bait(discord_id: int) -> UseBaitResult:
    """ 
    Will lower the bait number in the user's safari inventory
    """
    # Get the User
    print(f"Using bait for: {discord_id}")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SafariInventory).join(Users).where(Users.discord_id == discord_id)
        )
        safari_inventory = result.scalar_one_or_none()

        if not safari_inventory:
            return UseBaitResult.NoInventoryFound
        if safari_inventory.bait <= 0:
            return UseBaitResult.NoBaitLeft

        safari_inventory.bait -= 1
        session.add(safari_inventory)
        await session.commit()

    return UseBaitResult.BaitUsed

async def use_ball(discord_id: int) -> UseBallResult:
    """ 
    Will lower the ball number in the user's safari inventory
    """
    # Get the User
    print(f"Using ball for: {discord_id}")
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SafariInventory).join(Users).where(Users.discord_id == discord_id)
        )
        safari_inventory = result.scalar_one_or_none()

        if not safari_inventory:
            return UseBallResult.NoInventoryFound
        if safari_inventory.pokeballs<= 0:
            return UseBallResult.NoBallsLeft

        safari_inventory.pokeballs -= 1
        session.add(safari_inventory)
        await session.commit()

    return UseBallResult.BallUsed

async def catch_pokemon(discord_user_id: int, pokemon_id: int):
    print(f"Catching pokemon: {pokemon_id}")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Users).where(Users.discord_id == discord_user_id))
        user = result.scalar_one_or_none()

        if not user:
            print(f"User {discord_user_id} not found")
            return

        caught_pokemon = CaughtPokemon(
            user_id=user.id,
            pokemon_id=pokemon_id,
        )
        session.add(caught_pokemon)
        await session.commit()
    

