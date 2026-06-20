"""Resolve matrix from source (library or generated)."""

from app.services.matrix_library_service import MatrixLibraryService
from app.services.matrix_generation_service import generate_matrix

_matrix_lib = MatrixLibraryService()


async def resolve_matrix(source, matrix_id=None, requirement=None, matrix_type="auto"):
    if source == "library":
        if not matrix_id:
            raise ValueError("来自矩阵库时必须提供 matrix_id")
        arr, item, warnings = _matrix_lib.get_validated_matrix(matrix_id)
        return arr, {"source": "library", "matrix_id": matrix_id, "item": item}, warnings
    if source == "generated":
        if not requirement:
            raise ValueError("来自生成时必须提供 requirement")
        gen = await generate_matrix(requirement, matrix_type)
        if not gen.get("success"):
            raise ValueError(gen.get("errors", ["生成失败"])[0])
        from app.utils.validator import validate_matrix_data
        arr, warnings = validate_matrix_data(gen["matrix"])
        return arr, {"source": "generated", "requirement": requirement, "description": gen.get("description")}, gen.get("warnings", []) + warnings
    raise ValueError("source 必须是 library 或 generated")
