import random
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload
from db.db import AsyncSessionLocal
from db.models import CaughtPokemon, Pokemon, Rarity, SafariInventory, TriviaQuestion, Users
from enum import Enum

class UseBaitResult(str, Enum):
    NoInventoryFound = "NoInventoryFound"
    NoBaitLeft = "NoBaitLeft"
    BaitUsed = "BaitUsed"

class UseBallResult(str, Enum):
    NoInventoryFound = "NoInventoryFound"
    NoBallsLeft = "NoBallsLeft"
    BallUsed = "BallUsed"

class GiveItemResult(str, Enum):
    GiverNotRegistered = "GiverNotRegistered"
    ReceiverNotRegistered = "ReceiverNotRegistered"
    NoInventoryFound = "NoInventoryFound"
    InvalidItemType  = "InvalidItemType"
    InsufficientAmount = "InsufficientAmount"

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

async def get_inventory(discord_user_id: int) -> SafariInventory | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Users)
            .options(selectinload(Users.inventory))
            .where(Users.discord_id == discord_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            print(f"User is None for ID: {discord_user_id}")
            return None
        
        return user.inventory

async def give_from_inventory(from_user_id: int, to_user_id: int, item_type: str, amount: int) -> GiveItemResult:
    valid_items = ["bait", "pokeballs", "pokeball"]
    item_type = item_type.lower()
    if item_type not in valid_items:
        return GiveItemResult.InvalidItemType

    async with AsyncSessionLocal() as session:
        giver_result = await session.execute(
            select(Users)
            .options(selectinload(Users.inventory))
            .where(Users.discord_id == from_user_id))
        giver_user = giver_result.scalar_one_or_none() 

        if giver_user is None:
            return GiveItemResult.GiverNotRegistered

        receiver_result = await session.execute(
            select(Users)
            .options(selectinload(Users.inventory))
            .where(Users.discord_id == to_user_id))
        receiver_user = receiver_result.scalar_one_or_none() 

        if receiver_user is None:
            return GiveItemResult.ReceiverNotRegistered

        giver_inv = giver_user.inventory
        recv_inv = receiver_user.inventory

        if giver_inv is None or recv_inv is None:
            return GiveItemResult.NoInventoryFound
        
        if item_type in ["pokeball", "pokeballs"]:
            if giver_inv.pokeballs < amount:
                return GiveItemResult.InsufficientAmount
            else:
                giver_inv.pokeballs -= amount
                recv_inv.pokeballs += amount
        
        if item_type in ["bait"]:
            if giver_inv.bait < amount:
                return GiveItemResult.InsufficientAmount
            else:
                giver_inv.bait -= amount
                recv_inv.bait += amount

        await session.commit()
        
        
    
async def get_caught(discord_user_id: int) -> list[CaughtPokemon]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Users)
            .options(
                joinedload(Users.caught_pokemon)
                .joinedload(CaughtPokemon.pokemon)
            )
            .filter_by(discord_id=discord_user_id)
        )

        user = result.unique().scalars().first() 
        
        if user:
            return user.caught_pokemon
    return []

async def show(discord_user_id: int, item_type: str) -> str | list[CaughtPokemon] | SafariInventory | None:
    valid_items = ["bait", "pokeballs", "pokeball", "caught", "inventory", "balls"]
    item_type = item_type.lower()
    if item_type not in valid_items:
        return f"Invalid item: {item_type}."
    elif item_type == "caught":
        return await get_caught(discord_user_id=discord_user_id)
    elif item_type == "inventory":
        return await get_inventory(discord_user_id=discord_user_id)
    elif item_type == "bait":
        inv = await get_inventory(discord_user_id=discord_user_id)
        if inv:
            return f"Bait: {inv.bait}"
        else:
            return "Inventory not found"
    elif item_type in ["pokeballs", "pokeball", "balls"]:
        inv = await get_inventory(discord_user_id=discord_user_id)
        if inv:
            return f"Pokeballs: {inv.pokeballs}"
        else:
            return "Inventory not found"

    return None

async def get_random_trivia_question(mark_used: bool = True) -> str | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TriviaQuestion)
            .where(TriviaQuestion.used == False)
            .order_by(func.random())
            .limit(1)
        )
        
        question: TriviaQuestion = result.scalar_one_or_none()

        if question:
            # Mark it as used
            if mark_used:
                question.used = True
                await session.commit()
            return str(question.question)

        return None

async def spawn_pokemon(pokemon_identifier: str) -> Pokemon | None:
    try:
        pokemon_id = int(pokemon_identifier)
        return await get_pokemon_by_id(id=pokemon_id)
    except ValueError:
        return await get_pokemon_by_name(name=pokemon_identifier)
    


async def get_pokemon_by_id(id: int) -> Pokemon | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Pokemon).where(Pokemon.id == id))
        return result.scalar_one_or_none()

async def get_pokemon_by_name(name: str) -> Pokemon | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Pokemon).where(Pokemon.name.ilike(name)))
        return result.scalar_one_or_none()

         


