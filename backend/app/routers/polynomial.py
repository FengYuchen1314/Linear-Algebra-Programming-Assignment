"""Polynomial computation routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.polynomial_source_resolver import resolve_polynomial
from app.services.polynomial_service import compute_sturm
from app.utils.formatter import poly_to_str
from app.utils.errors import error_response, success_response

router = APIRouter(prefix="/api/polynomial", tags=["polynomial"])


class SturmRequest(BaseModel):
    source: str
    polynomial_id: Optional[str] = None
    requirement: Optional[str] = None


@router.post("/sturm")
async def sturm_roots(req: SturmRequest):
    try:
        expr, input_data, resolve_warnings = await resolve_polynomial(
            req.source, req.polynomial_id, req.requirement
        )
        result, steps, warnings = compute_sturm(expr)
        warnings = resolve_warnings + warnings
        return success_response(
            result=result,
            input_data=input_data,
            polynomial=poly_to_str(expr),
            steps=steps,
            warnings=warnings,
        )
    except ValueError as e:
        return error_response(str(e), {"source": req.source})
    except Exception as e:
        return error_response(f"计算失败: {e}", {"source": req.source})
