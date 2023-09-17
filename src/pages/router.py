from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from settings import TEMPLATES_PATH


router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory=TEMPLATES_PATH)


@router.get("/")
async def get_home_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/new")
async def get_home_page2(request: Request):
    return templates.TemplateResponse("dashboard2.html", {"request": request})
