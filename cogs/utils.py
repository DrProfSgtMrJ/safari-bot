from data_models.pokemon import Pokemon
from db.helpers import get_rarity, get_rand_pokemon_by_rarity

async def get_random_pokemon() -> Pokemon:
    # Pick rarities
    rarity = get_rarity()
    random_pokemon = await get_rand_pokemon_by_rarity(rarity=rarity)
    return Pokemon.from_db_pokemon(db_pokemon=random_pokemon)

