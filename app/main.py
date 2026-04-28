from fastapi import FastAPI

from app.api.router import api_router
from dotenv import load_dotenv

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="SmartEntry API", version="1.0.0")

    app.include_router(api_router)

    return app


app = create_app()
