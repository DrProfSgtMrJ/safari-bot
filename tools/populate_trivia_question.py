import asyncio
from db.db import AsyncSessionLocal
from db.models import TriviaQuestion


pokemon_trivia_questions = [
    "What is the only Pokemon that can naturally learn the move Sketch?",
    "Which Pokemon has the ability Wonder Guard?",
    "Which item doubles a Pokemon's speed but only allows one move?",
    "What Pokemon evolves from Eevee with high friendship at night?",
    "What Pokémon was the very first to be created by the developers?",
    "What is the name of the ferry service found in Pokémon games and anime?",
    "What item is needed to evolve Sneasel into Weavile?",
    "What is the name of the first Pokémon Ash Ketchum catches in the anime?",
    "What Pokémon is known as the “Time Travel Pokémon”?",
    "What is the name of the cruise liner in the Kanto region?",
    "Who do you have to help in order to obtain an S.S Ticket? (Please give me the name of the person)",
    "Which Pokemon game first removed the need for HMs to navigate?",
    "Which region did players transport to in Pokemon Legends: Arceus?",
    "What region does Hisui refer to in the 'modern' era of Pokemon?",
    "In the animated series, which region did Team Rocket finally defeat Ash and his Pikachu?",
    "Which Pokemon did Ash trade for a Raticate?",
    "Which Pokemon did Ash catch an abundance of in the Safari Zone?",
    "Which Pokemon passes away in the anime series Pokemon Sun and Moon?",
    "True or False, in the Pokemon anime, James, from Team Rocket, owned a Charizard?",
    "What is the name of the group of extradimensional Pokemon introduced in Pokemon Sun and Moon?",
    "What special type of move was introduced in Generation VII?",
    "What special form change was introduced in Generation VI?",
    "What type of moves were introduced in Generation VIII?",
    "True or False, Dynamax Pokemon are immune to flinching?",
    "True or False, Stakataka is Ground and Steel?",
    "What is the name of the Pokemon that Goodra evolves from?",
    "Which move is turned into Supersonic Skystrike when using Z-Power?",
    "What is Pikachu's exclusive Z-Move?",
    "True or False, Garbodor can learn the move Baneful Bunker?",
    "Which electric move inflicts more damage the faster the user is compared to the opponent?",
    "True or False, all Special Attack type moves use the target's Sepcial Defense?",
    "What is the name of the method introduced in Pokemon Sun and Moon used to maximize IVs?",
    "True or False, Steady is one of 25 Natures?",
    "Which flavor do Relaxed Natured pokemon prefer?",
    "Which flavor do Naive Natured pokemon dislike?",
    "What can be used within the Hoenn Safari Zone to increase your chances of acquiring a Pokemon of a certain Nature?",
]



async def populate_trivia_question():
    async with AsyncSessionLocal() as session:
        for i, question in enumerate(pokemon_trivia_questions):
            try:
                question_entry = TriviaQuestion(
                    id=i, 
                    question=question,
                    used=False
                )
                session.add(question_entry)
            except Exception as e:
                print(f"Failed to add question: {question}, {e}")
                continue
        await session.commit()

def main():
    asyncio.run(populate_trivia_question())

if __name__ == "__main__":
    main()
