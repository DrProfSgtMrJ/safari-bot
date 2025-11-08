from data_models.pokemon import Pokemon
from db.helpers import get_rarity, get_rand_pokemon_by_rarity, spawn_pokemon as spawn_db_pokemon

async def get_random_pokemon() -> Pokemon:
    # Pick rarities
    rarity = get_rarity()
    random_pokemon = await get_rand_pokemon_by_rarity(rarity=rarity)
    return Pokemon.from_db_pokemon(db_pokemon=random_pokemon)

async def spawn_pokemon(pokemon_identifier: str) -> Pokemon | None:
    pokemon = await spawn_db_pokemon(pokemon_identifier=pokemon_identifier)
    return Pokemon.from_db_pokemon(db_pokemon=pokemon)
