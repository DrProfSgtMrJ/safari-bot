from sqlalchemy import Column, Integer, BigInteger, String, Enum, null
from data_models.pokemon import Rarity
from .db import Base


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
    rarity = Column(Enum(Rarity), nullable=False, default=Rarity.COMMON)
