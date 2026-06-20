"""Matrix decomposition routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matrix_source_resolver import resolve_matrix
from app.services.decomposition_service import (
    full_rank_decomposition,
    lu_decomposition,
    ldu_decomposition,
    svd_decomposition,
)
from app.utils.formatter import matrix_to_list
from app.utils.errors import error_response, success_response

router = APIRouter(prefix="/api/matrix/decomposition", tags=["decomposition"])


class MatrixSourceRequest(BaseModel):
    source: str
    matrix_id: Optional[str] = None
    requirement: Optional[str] = None
    matrix_type: str = "auto"


async def _resolve(req):
    return await resolve_matrix(req.source, req.matrix_id, req.requirement, req.matrix_type)


@router.post("/full-rank")
async def full_rank(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await _resolve(req)
        result, steps = full_rank_decomposition(arr)
        return success_response(result=result, input_data=input_data, matrix=matrix_to_list(arr), steps=steps, warnings=warnings)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"计算失败: {e}")


@router.post("/lu")
async def lu(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await _resolve(req)
        result, steps = lu_decomposition(arr)
        return success_response(result=result, input_data=input_data, matrix=matrix_to_list(arr), steps=steps, warnings=warnings)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"计算失败: {e}")


@router.post("/ldu")
async def ldu(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await _resolve(req)
        result, steps = ldu_decomposition(arr)
        return success_response(result=result, input_data=input_data, matrix=matrix_to_list(arr), steps=steps, warnings=warnings)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"计算失败: {e}")


@router.post("/svd")
async def svd(req: MatrixSourceRequest):
    try:
        arr, input_data, warnings = await _resolve(req)
        result, steps, comp_warnings = svd_decomposition(arr)
        return success_response(result=result, input_data=input_data, matrix=matrix_to_list(arr), steps=steps, warnings=warnings + comp_warnings)
    except ValueError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(f"计算失败: {e}")
