from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from settings import API_BASE_URL, TEMPLATES_PATH


router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory=TEMPLATES_PATH)


@router.get("/")
async def get_home_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "api_base_url": API_BASE_URL}
    )
