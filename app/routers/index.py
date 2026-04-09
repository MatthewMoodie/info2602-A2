from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import SessionDep
from app.auth import IsUserLoggedIn, get_current_user, is_admin

index_router = APIRouter()

@index_router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep
):
    
    if user_logged_in:
        user = await get_current_user(request, db)
        if await is_admin(user):
            return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
        


        return RedirectResponse(url="/pokemon", status_code=status.HTTP_303_SEE_OTHER)
    
    


    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)