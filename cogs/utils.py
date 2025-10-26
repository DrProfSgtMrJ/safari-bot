import random
import pokebase as pb


def get_random_pokemon() -> tuple[str, str]:
    pokemon_id = random.randint(1, 1025)
    pokemon = pb.pokemon(pokemon_id)
    print(f"Got Pokemon: {pokemon.name} with id: {pokemon_id}")
    return pokemon.name, pokemon.sprites.front_default
