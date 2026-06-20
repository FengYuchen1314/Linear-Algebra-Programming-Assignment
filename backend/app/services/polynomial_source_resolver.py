"""Resolve polynomial from source (library or generated)."""

from app.services.polynomial_library_service import PolynomialLibraryService
from app.services.polynomial_generation_service import generate_polynomial
from app.utils.formatter import poly_to_str

_poly_lib = PolynomialLibraryService()


async def resolve_polynomial(source, polynomial_id=None, requirement=None):
    if source == "library":
        if not polynomial_id:
            raise ValueError("来自多项式库时必须提供 polynomial_id")
        expr, item = _poly_lib.get_validated_polynomial(polynomial_id)
        return expr, {"source": "library", "polynomial_id": polynomial_id, "item": item}, []
    if source == "generated":
        if not requirement:
            raise ValueError("来自生成时必须提供 requirement")
        gen = await generate_polynomial(requirement)
        if not gen.get("success"):
            raise ValueError(gen.get("errors", ["生成失败"])[0])
        from app.utils.validator import validate_polynomial_expr
        expr, warnings = validate_polynomial_expr(gen["polynomial"])
        return expr, {"source": "generated", "requirement": requirement, "description": gen.get("description")}, gen.get("warnings", []) + warnings
    raise ValueError("source 必须是 library 或 generated")
