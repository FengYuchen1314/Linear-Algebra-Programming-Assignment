"""Jordan normal form routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matrix_source_resolver import resolve_matrix
from app.services.jordan_service import compute_jordan
from app.utils.formatter import matrix_to_list
from app.utils.errors import error_response, success_response, NON_SQUARE_JORDON_MSG

router = APIRouter(prefix="/api/matrix", tags=["jordan"])


class MatrixSourceRequest(BaseModel):
    source: str
    matrix_id: Optional[str] = None
    requirement: Optional[str] = None
    matrix_type: str = "auto"


@router.post("/jordan")
async def jordan_form(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await resolve_matrix(
            req.source, req.matrix_id, req.requirement, req.matrix_type
        )
        if arr.shape[0] != arr.shape[1]:
            return error_response(NON_SQUARE_JORDON_MSG)
        result, steps, comp_warnings = compute_jordan(arr)
        return success_response(
            result=result,
            input_data=input_data,
            matrix=matrix_to_list(arr),
            steps=steps,
            warnings=warnings + comp_warnings,
        )
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"计算失败: {e}")
