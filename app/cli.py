from app.models import Pokemon
import typer
import csv
from tabulate import tabulate
from sqlmodel import select
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from app.auth import encrypt_password
import subprocess
import platform
import os

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db:
        drop_all()
        create_db_and_tables()
        print("Tables created.")

        with open('pokemon.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            pokemon_list = []
            for row in reader:
                pokemon = Pokemon(
                    name=row['name'],
                    type1=row['type1'],
                    type2=row['type2'] if row['type2'] else None,
                    height=float(row['height_m']) if row['height_m'] else None,
                    weight=float(row['weight_kg']) if row['weight_kg'] else None,
                    hp=int(row['hp']),
                    attack=int(row['attack']),
                    defense=int(row['defense']),
                    sp_attack=int(row['sp_attack']),
                    sp_defense=int(row['sp_defense']),
                    speed=int(row['speed'])
                )
                pokemon_list.append(pokemon)
            
            db.add_all(pokemon_list)
            db.commit()
            print(f"Database initialized with {len(pokemon_list)} pokemon.")

@cli.command()
def test(base_url: str = "http://127.0.0.1:8000", headless: bool = True):
    try:
        subprocess.run(["npm", "install"], check=True, shell=platform.system() == "Windows")
    except subprocess.CalledProcessError:
        typer.secho("Installing test package failed. Install Node/npm on your PC to continue", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    try:
        env = os.environ.copy()
        env["BASE_URL"] = base_url
        env["HEADLESS"] = str(headless).lower()
        subprocess.run(["npm", "test"], check=True, shell=platform.system() == "Windows", env=env)
    except subprocess.CalledProcessError:
        typer.secho("Tests failed!", fg=typer.colors.RED)
        raise typer.Exit(code=1)
   
if __name__ == "__main__":
    cli()