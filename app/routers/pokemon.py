from fastapi import APIRouter, HTTPException, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlmodel import select, func
from app.database import SessionDep
from app.models import Pokemon, UserPokemon
from app.auth import AuthDep
from app.utilities.flash import flash, get_flashed_messages
from fastapi.templating import Jinja2Templates




pokemon_router = router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages


@router.get("/pokemon", response_class=HTMLResponse)
async def pokemon_dashboard(request: Request, user: AuthDep, db: SessionDep, q: str = None):
    statement = select(Pokemon)
    if q:
        statement = statement.where(Pokemon.name.ilike(f"%{q}%"))
    pokemon_list = db.exec(statement).all()
    for p in pokemon_list:
        p.name = p.name.title()
    
    return templates.TemplateResponse(request=request, name="pokemon.html", context={"request": request, "user": user, "pokemon_list": pokemon_list})




@router.post("/mypokemon")
async def capture_pokemon(request: Request, user: AuthDep, db: SessionDep, pokemon_id: int = Form(...), name: str = Form(None)):
    pokemon = db.get(Pokemon, pokemon_id)
    if not pokemon:
        return RedirectResponse(url="/pokemon", status_code=status.HTTP_303_SEE_OTHER)
    
    display_name = name.strip() if name and name.strip() else pokemon.name.title()
    new_capture = UserPokemon(user_id=user.id, pokemon_id=pokemon_id, name=display_name)
    db.add(new_capture)
    db.commit()

    flash(request, "Successfully captured Pokemon!", "success")
    return RedirectResponse(url="/mypokemon", status_code=status.HTTP_303_SEE_OTHER)




@router.get("/mypokemon", response_class=HTMLResponse)
async def my_pokemon_page(request: Request, user: AuthDep, db: SessionDep, q: str = None):
    statement = (
        select(UserPokemon, Pokemon)
        .join(Pokemon, UserPokemon.pokemon_id == Pokemon.pokemon_id)
        .where(UserPokemon.user_id == user.id)
    )
    if q:
        statement = statement.where((UserPokemon.name.ilike(f"%{q}%")) | (Pokemon.name.ilike(f"%{q}%")))
    
    results = db.exec(statement).all()
    captured_pokemon = []
    for user_poke, poke in results:
        captured_pokemon.append({
            "capture_id": user_poke.id,
            "pokemon_id": poke.pokemon_id,
            "nickname": user_poke.name,
            "species": poke.name.title(),
            "type": poke.type1,
            "weight": poke.weight,
            "height": poke.height
        })
    
    return templates.TemplateResponse(request=request, name="mypokemon.html", context={"request": request, "user": user, "captured_pokemon": captured_pokemon})



@router.put("/mypokemon/{capture_id}")
async def rename_pokemon(request: Request, capture_id: int, user: AuthDep, db: SessionDep, name: str = Form(...)):
    user_poke = db.get(UserPokemon, capture_id)
    if user_poke and user_poke.user_id == user.id:
        user_poke.name = name.strip()
        db.add(user_poke)
        db.commit()
        flash(request, "Successfully renamed Pokemon!", "success")
        return JSONResponse({"status": "success"})
    return JSONResponse({"status": "error"}, status_code=404)



@router.delete("/mypokemon/{capture_id}")
async def release_pokemon(request: Request, capture_id: int, user: AuthDep, db: SessionDep):
    user_poke = db.get(UserPokemon, capture_id)
    if user_poke and user_poke.user_id == user.id:
        db.delete(user_poke)
        db.commit()
        flash(request, "Bye bye", "success")
        return JSONResponse({"status": "success"})
    return JSONResponse({"status": "error"}, status_code=404)



@router.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request, user: AuthDep, db: SessionDep):
    statement = (
        select(Pokemon.type1, func.count(UserPokemon.id))
        .join(UserPokemon, UserPokemon.pokemon_id == Pokemon.pokemon_id)
        .where(UserPokemon.user_id == user.id)
        .group_by(Pokemon.type1)
    )

    results = db.exec(statement).all()
    

    return templates.TemplateResponse(request=request, name="stats.html", context={"request": request, "user": user, "labels": [r[0] for r in results], "counts": [r[1] for r in results]})