from sqlalchemy import Column, Integer, BigInteger, String
from .db import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(BigInteger, unique=True, nullable=False)
    discord_display_name = Column(String(255), nullable=False)
