from fastapi import APIRouter, status, Response, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.models import User
from app.database import SessionDep
from app.auth import encrypt_password, verify_password, create_access_token
from app.utilities.flash import flash, get_flashed_messages
from fastapi.templating import Jinja2Templates




auth_router = router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})




@router.post("/login")
async def login(request: Request, response: Response, db: SessionDep, username: str = Form(...), password: str = Form(...)):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password):
        flash(request, "Incorrect username or password", "danger")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    access_token = create_access_token(data={"sub": str(user.id)})
    redirect_response = RedirectResponse(url="/pokemon", status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return redirect_response



@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    
    return templates.TemplateResponse(request=request, name="signup.html", context={"request": request})




@router.post("/signup")
async def signup(request: Request, db: SessionDep, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    existing_user = db.exec(select(User).where((User.username == username) | (User.email == email))).first()
    if existing_user:
        flash(request, "Username or email already exists", "danger")
        return RedirectResponse(url="/signup", status_code=status.HTTP_303_SEE_OTHER)

    new_user = User(username=username, email=email, password=encrypt_password(password))
    db.add(new_user)
    db.commit()
    flash(request, "Registration completed! Sign in now!", "success")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)



@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    flash(request, "You have been successfully logged out.", "success")
    return response