from sqlmodel import Field, SQLModel, Relationship
from typing import Optional

class UserPokemon(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    pokemon_id: int | None = Field(default=None, foreign_key="pokemon.pokemon_id")
    name: str = Field(default="")

class Pokemon(SQLModel, table=True):
    pokemon_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    hp: int
    type1: str
    type2: str | None = Field(default=None)
    height: float | None = Field(default=None)
    weight: float | None = Field(default=None)