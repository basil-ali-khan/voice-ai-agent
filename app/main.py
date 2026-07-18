import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database import Base, engine
from app.errors import DomainError
from app.patients import model  # noqa: F401
from app.patients.routes import router as patients_router
from app.voice.routes import router as voice_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app() -> FastAPI:
    app = FastAPI(title="CareCloud Patient Registration", version="0.1.0")
    app.include_router(patients_router)
    app.include_router(voice_router)

    @app.on_event("startup")
    def create_schema() -> None:
        Base.metadata.create_all(bind=engine)

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"data": None, "error": {"code": error.code, "message": error.message, "details": error.details}})

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"data": None, "error": {"code": "validation_error", "message": "Request validation failed.", "details": jsonable_encoder(error.errors())}})

    @app.get("/health", tags=["operational"])
    def health() -> dict:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"data": {"status": "ok"}, "error": None}

    return app


app = create_app()
