"""Polynomial source routes: library and generation."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.polynomial_library_service import PolynomialLibraryService
from app.services.polynomial_generation_service import generate_polynomial
from app.utils.errors import error_response

router = APIRouter(prefix="/api/polynomial", tags=["polynomial-source"])
_lib = PolynomialLibraryService()


class GenerateRequest(BaseModel):
    requirement: str


@router.get("/library")
def list_polynomial_library():
    return {"success": True, "polynomials": _lib.list_all()}


@router.get("/library/{poly_id}")
def get_polynomial(poly_id: str):
    try:
        item = _lib.get_by_id(poly_id)
        return {"success": True, "polynomial": item}
    except ValueError as e:
        return error_response(str(e))


@router.post("/generate")
async def generate_poly(req: GenerateRequest):
    result = await generate_polynomial(req.requirement)
    if not result.get("success"):
        return error_response(result.get("errors", ["生成失败"]))
    return result
