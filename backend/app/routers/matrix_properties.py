"""Matrix properties routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matrix_source_resolver import resolve_matrix
from app.services.matrix_properties_service import compute_properties
from app.utils.formatter import matrix_to_list
from app.utils.errors import error_response, success_response

router = APIRouter(prefix="/api/matrix", tags=["matrix-properties"])


class MatrixSourceRequest(BaseModel):
    source: str
    matrix_id: Optional[str] = None
    requirement: Optional[str] = None
    matrix_type: str = "auto"


@router.post("/properties")
async def matrix_properties(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await resolve_matrix(
            req.source, req.matrix_id, req.requirement, req.matrix_type
        )
        result, steps, comp_warnings = compute_properties(arr)
        return success_response(
            result=result,
            input_data=input_data,
            matrix=matrix_to_list(arr),
            steps=steps,
            warnings=warnings + comp_warnings,
        )
    except ValueError as e:
        return error_response(str(e), {"source": req.source})
    except Exception as e:
        return error_response(f"计算失败: {e}", {"source": req.source})
