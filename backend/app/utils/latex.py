"""LaTeX formatting helpers."""

import sympy as sp


def latex_matrix(mat):
    return sp.latex(sp.Matrix(mat))


def latex_poly(poly):
    return sp.latex(sp.expand(poly))


def latex_expr(expr):
    return sp.latex(sp.simplify(expr))
