import random
import pokebase as pb
from data_models.pokemon import Rarity, Pokemon


POKEMON_BY_RARITY = {
     Rarity.COMMON:    ["Pidgey", "Rattata", "Zubat", "Caterpie"],
     Rarity.UNCOMMON:  ["Pikachu", "Eevee", "Vulpix", "Growlithe"],
     Rarity.RARE:      ["Dratini", "Larvitar", "Beldum"],
     Rarity.LEGENDARY: ["Mewtwo", "Articuno", "Zapdos", "Moltres"]
}

RARITY_WEIGHTS = {
    Rarity.COMMON: 60,
    Rarity.UNCOMMON: 25,
    Rarity.RARE: 10,
    Rarity.LEGENDARY: 5
}

def get_random_pokemon() -> Pokemon:
    rarity = random.choices(list(POKEMON_BY_RARITY.keys()), weights=RARITY_WEIGHTS.values(), k=1)[0]
    pokemon_name = random.choice(POKEMON_BY_RARITY[rarity])
    pb_pokemon = pb.pokemon(pokemon_name.lower())
    print(f"Got Pokemon: {pb_pokemon.name}")
    return Pokemon(name=pb_pokemon.name, sprite_url=pb_pokemon.sprites.front_default, rarity=rarity)
