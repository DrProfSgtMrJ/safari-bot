import asyncio
import pokebase as pb
from data_models.pokemon import Rarity
from db.db import AsyncSessionLocal, Base, AsyncSessionLocal, engine
from db.models import Pokemon

def determine_rarity(species) -> Rarity:
    print(f"species: {species}")
    if species.is_legendary or species.is_mythical:
        return Rarity.LEGENDARY
    elif species.is_baby:
        return Rarity.COMMON
    elif species.capture_rate >= 150:
        return Rarity.COMMON
    elif species.capture_rate >= 100:
        return Rarity.UNCOMMON
    else:
        return Rarity.RARE


async def populate_gen1_pokemon():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    async with AsyncSessionLocal() as session:
        for i in range(1, 152): # Gen 1 IDs
            # Skip if already existing
            existing = await session.get(Pokemon, i)
            if existing:
                print(f"Skipping {existing.name} (already in DB)")
                continue

            try:
                poke = pb.pokemon(i)
                species = pb.pokemon_species(i)
                rarity = determine_rarity(species)

                poke_entry = Pokemon(
                    id=i,
                    name=poke.name.capitalize(),
                    sprite_url=poke.sprites.front_default,
                    rarity=rarity
                )
                session.add(poke_entry)
                print(f"Added {poke_entry.name} ({rarity.value})")
            except Exception as e:
                print(f"Failed to add Pokemon ID {i}: {e}")
        await session.commit()


def main():
    asyncio.run(populate_gen1_pokemon())

if __name__ == "__main__":
    main()




