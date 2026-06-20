"""FastAPI application entry point."""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    polynomial_source,
    polynomial,
    matrix_source,
    matrix_properties,
    decomposition,
    jordan,
    lambda_smith,
)

load_dotenv()

app = FastAPI(title="Linear Algebra Programming Assignment", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(polynomial_source.router)
app.include_router(polynomial.router)
app.include_router(matrix_source.router)
app.include_router(matrix_properties.router)
app.include_router(decomposition.router)
app.include_router(jordan.router)
app.include_router(lambda_smith.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
