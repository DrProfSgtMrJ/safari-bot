from sqlalchemy import Column, Integer, BigInteger, String, Enum
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

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    sprite_url = Column(String, nullable=True)
    rarity = Column(rarity_enum, nullable=False, default=Rarity.COMMON)
