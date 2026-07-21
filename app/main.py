from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.exceptions import AppException
from app.routers import auth, users, task


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(task.router)