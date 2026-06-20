"""Matrix source routes: library and generation."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.matrix_library_service import MatrixLibraryService
from app.services.matrix_generation_service import generate_matrix
from app.utils.errors import error_response

router = APIRouter(prefix="/api/matrix", tags=["matrix-source"])
_lib = MatrixLibraryService()


class GenerateMatrixRequest(BaseModel):
    requirement: str
    matrix_type: str = "auto"


@router.get("/library/square")
def list_square_matrices():
    return {"success": True, "matrices": _lib.list_square()}


@router.get("/library/rectangular")
def list_rectangular_matrices():
    return {"success": True, "matrices": _lib.list_rectangular()}


@router.get("/library/{matrix_id}")
def get_matrix(matrix_id: str):
    try:
        item = _lib.get_by_id(matrix_id)
        return {"success": True, "matrix": item}
    except ValueError as e:
        return error_response(str(e))


@router.post("/generate")
async def generate_mat(req: GenerateMatrixRequest):
    result = await generate_matrix(req.requirement, req.matrix_type)
    if not result.get("success"):
        return error_response(result.get("errors", ["生成失败"]))
    return result
