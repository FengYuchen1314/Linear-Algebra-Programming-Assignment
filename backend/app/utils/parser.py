"""Parse polynomials and matrices from strings or data."""

import re

import sympy as sp


X = sp.Symbol("x")


def parse_polynomial(expr_str):
    """Parse a polynomial string into a SymPy expression in x."""
    expr_str = expr_str.strip()
    expr_str = expr_str.replace("^", "**")
    if "=" in expr_str:
        expr_str = expr_str.split("=")[-1].strip()
    expr = sp.sympify(expr_str, locals={"x": X})
    poly = sp.Poly(expr, X)
    return poly.as_expr()


def parse_matrix(matrix_data):
    """Parse a 2D list into a SymPy Matrix."""
    return sp.Matrix(matrix_data)


def detect_complex_polynomial_requirement(text):
    patterns = [
        r"复系数",
        r"复数系数",
        r"虚系数",
        r"complex\s+coefficient",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def detect_complex_matrix_requirement(text):
    patterns = [
        r"复数矩阵",
        r"复矩阵",
        r"虚数矩阵",
        r"complex\s+matrix",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)
