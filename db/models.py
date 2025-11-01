from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, BigInteger, String, Enum
from sqlalchemy.orm import relationship
from .db import Base
import enum

class Rarity(enum.Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"

rarity_enum = Enum(Rarity, name="rarity_enum", create_type=True)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    discord_display_name = Column(String(255), nullable=False)

    inventory = relationship("SafariInventory", back_populates="user", uselist=False, cascade="all, delete-orphan")
    caught_pokemon = relationship("CaughtPokemon", back_populates="user", cascade="all, delete-orphan")

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    sprite_url = Column(String, nullable=True)
    rarity = Column(rarity_enum, nullable=False, default=Rarity.COMMON)

class SafariInventory(Base):
    __tablename__ = "safari_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bait = Column(Integer, nullable=False, default=10)
    pokeballs = Column(Integer, nullable=False, default=8)

    user = relationship("Users", back_populates="inventory")

class CaughtPokemon(Base):
    __tablename__ = "caught_pokemon"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pokemon_id = Column(ForeignKey("pokemon.id", ondelete="CASCADE"), nullable=False)
    caught_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("Users", back_populates="caught_pokemon")
    pokemon = relationship("Pokemon")
