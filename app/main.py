from fastapi import FastAPI
from app.core.config import settings
from app.routers import auth


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,

)
app.include_router(auth.router)