"""Custom error helpers for API responses."""

COMPLEX_POLY_MSG = "当前程序不支持输入为复系数多项式"
COMPLEX_MATRIX_MSG = "当前程序不支持输入为复数矩阵"
ZERO_POLY_MSG = "零多项式不能用于 Sturm 求根"
NON_SQUARE_JORDON_MSG = "Jordan 标准型功能只支持方阵"
NON_SQUARE_LAMBDA_MSG = "λ-矩阵法功能只支持方阵"


def error_response(errors, input_data=None):
    return {
        "success": False,
        "input": input_data or {},
        "polynomial": None,
        "matrix": None,
        "result": None,
        "steps": [],
        "warnings": [],
        "errors": errors if isinstance(errors, list) else [errors],
    }


def success_response(
    result,
    input_data=None,
    polynomial=None,
    matrix=None,
    steps=None,
    warnings=None,
):
    return {
        "success": True,
        "input": input_data or {},
        "polynomial": polynomial,
        "matrix": matrix,
        "result": result,
        "steps": steps or [],
        "warnings": warnings or [],
        "errors": [],
    }
