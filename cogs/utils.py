import random
import pokebase as pb


POKEMON_BY_RARITY = {
    "common" : ["Pidgey", "Rattata", "Zubat", "Caterpie"],
    "uncommon": ["Pikachu", "Eevee", "Vulpix", "Growlithe"],
    "rare": ["Dratini", "Larvitar", "Beldum"],
    "legendary": ["Mewtwo", "Articuno", "Zapdos", "Moltres"]
}

RARITY_WEIGHTS = {
    "common": 60,
    "uncommon": 25,
    "rare": 10,
    "legendary": 5
}

def get_random_pokemon() -> tuple[str, str]:
    rarity = random.choices(list(POKEMON_BY_RARITY.keys()), weights=RARITY_WEIGHTS.values(), k=1)[0]
    pokemon_name = random.choice(POKEMON_BY_RARITY[rarity])
    pokemon = pb.pokemon(pokemon_name.lower())
    print(f"Got Pokemon: {pokemon.name}")
    return pokemon.name, pokemon.sprites.front_default
