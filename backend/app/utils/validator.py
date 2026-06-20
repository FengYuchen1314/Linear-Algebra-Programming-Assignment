"""Validation for polynomials and matrices."""

import re

import numpy as np
import sympy as sp

from app.utils.parser import X, parse_polynomial
from app.utils.errors import COMPLEX_POLY_MSG, COMPLEX_MATRIX_MSG


def is_real_number(val):
    if isinstance(val, (int, float)):
        return np.isfinite(val) and not isinstance(val, bool)
    if isinstance(val, complex):
        return abs(val.imag) < 1e-12
    return False


def validate_polynomial_expr(expr_str):
    """Validate and return (expr, warnings) or raise ValueError."""
    warnings = []
    try:
        expr = parse_polynomial(expr_str)
    except Exception as e:
        raise ValueError(f"多项式无法被 SymPy 解析: {e}") from e

    poly = sp.Poly(expr, X)
    if poly.degree() == 0 and poly.LC() == 0:
        raise ValueError("零多项式无效")

    if poly.degree() > 8:
        raise ValueError("多项式次数不能超过 8")

    coeffs = poly.all_coeffs()
    for c in coeffs:
        if not sp.im(c).equals(0):
            raise ValueError(COMPLEX_POLY_MSG)

    free = expr.free_symbols
    if free - {X}:
        raise ValueError("多项式只能包含变量 x")

    return expr, warnings


def validate_matrix_data(matrix_data):
    """Validate matrix data. Returns (np.ndarray, warnings) or raises ValueError."""
    warnings = []
    if not isinstance(matrix_data, list) or not matrix_data:
        raise ValueError("矩阵必须是二维数组")

    if not all(isinstance(row, list) for row in matrix_data):
        raise ValueError("矩阵必须是二维数组")

    row_len = len(matrix_data[0])
    if row_len == 0:
        raise ValueError("矩阵不能为空")

    for row in matrix_data:
        if len(row) != row_len:
            raise ValueError("矩阵各行长度必须一致")

    rows, cols = len(matrix_data), row_len
    if rows > 6 or cols > 6:
        raise ValueError("矩阵维度不能超过 6")

    arr = []
    for row in matrix_data:
        parsed_row = []
        for val in row:
            if isinstance(val, str):
                if re.search(r"[ij]|I\b", val):
                    raise ValueError(COMPLEX_MATRIX_MSG)
                try:
                    val = float(sp.sympify(val))
                except Exception:
                    raise ValueError(f"矩阵元素无法解析: {val}")
            if not is_real_number(val):
                raise ValueError(COMPLEX_MATRIX_MSG)
            parsed_row.append(float(val))
        arr.append(parsed_row)

    return np.array(arr, dtype=float), warnings


def validate_square_matrix(matrix_data):
    arr, warnings = validate_matrix_data(matrix_data)
    if arr.shape[0] != arr.shape[1]:
        raise ValueError("该功能需要方阵")
    return arr, warnings
