from fastapi import FastAPI

from src.metrics.router import router as router_metrics


app = FastAPI(title="Parser Dashboard", debug=True)

app.include_router(router_metrics)
