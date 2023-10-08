from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.metrics.router import router as router_metrics
from src.pages.router import router as router_pages


app = FastAPI(title="Parser Dashboard", debug=True)

app.include_router(router_metrics)
app.include_router(router_pages)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "http://loginovpavel.ru",
    "https://loginovpavel.ru",
    "https://kmetrics.loginovpavel.ru",
    "http://kmetrics.loginovpavel.ru",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
