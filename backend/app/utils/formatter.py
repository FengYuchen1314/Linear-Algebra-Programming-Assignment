"""Format SymPy objects and matrices for JSON responses."""

from fractions import Fraction

import numpy as np
import sympy as sp


def _nsimplify_expr(val):
    if isinstance(val, sp.Basic):
        try:
            return sp.nsimplify(val, rational=True)
        except (TypeError, ValueError, AttributeError):
            return sp.simplify(val)
    return val


def to_exact_matrix(arr):
    """Build an exact (rational) SymPy matrix from a float numpy array/list.

    Matrices coming from validation are cast to float, which forces SymPy to
    work in floating point (ugly float char-poly coefficients, numerically
    unreliable eigenvalues / null spaces). Converting each entry to its exact
    rational value restores exact symbolic arithmetic.
    """
    data = arr.tolist() if hasattr(arr, "tolist") else arr
    return sp.Matrix(data).applyfunc(lambda x: sp.nsimplify(x, rational=True))


def format_number(val):
    """Prefer exact values; fall back to numeric approximations."""
    if isinstance(val, (bool, np.bool_)):
        return bool(val)

    if isinstance(val, np.generic):
        val = val.item()

    if isinstance(val, sp.Basic):
        val = _nsimplify_expr(val)
        if val.is_Integer:
            return int(val)
        if val.is_Rational:
            return int(val.p) if val.q == 1 else f"{int(val.p)}/{int(val.q)}"
        if val.is_real:
            if val.is_Rational:
                return int(val.p) if val.q == 1 else f"{int(val.p)}/{int(val.q)}"
            f = float(val.evalf())
            if abs(f - round(f)) < 1e-10:
                return int(round(f))
            return round(f, 10)
        if val.is_complex or val.has(sp.I):
            re = sp.re(val)
            im = sp.im(val)
            re_fmt = format_number(re)
            im_fmt = format_number(im)
            if isinstance(im_fmt, str) and "/" in str(im_fmt):
                im_num = float(sp.Rational(im_fmt)) if "/" in str(im_fmt) else im_fmt
            else:
                im_num = float(im_fmt) if im_fmt is not None else 0
            if abs(im_num) < 1e-10:
                return re_fmt
            return {"re": re_fmt, "im": im_fmt, "latex": sp.latex(val)}
        return str(val)

    if isinstance(val, (int, np.integer)):
        return int(val)

    if isinstance(val, (float, np.floating)):
        f = float(val)
        if not np.isfinite(f):
            return str(f)
        if abs(f - round(f)) < 1e-10:
            return int(round(f))
        return round(f, 10)

    if isinstance(val, Fraction):
        return int(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"

    if isinstance(val, complex):
        if abs(val.imag) < 1e-12:
            return format_number(val.real)
        return {
            "re": format_number(val.real),
            "im": format_number(val.imag),
        }

    if isinstance(val, str) and "/" in val:
        try:
            return format_number(sp.Rational(val))
        except (ValueError, TypeError):
            return val

    return str(val)


def format_number_latex(val):
    if isinstance(val, dict) and val.get("latex"):
        return val["latex"]
    if isinstance(val, str) and "/" in val:
        p, q = val.split("/", 1)
        return f"\\frac{{{p}}}{{{q}}}"
    if isinstance(val, dict) and "re" in val:
        re = val["re"]
        im = val["im"]
        im_num = float(sp.Rational(str(im))) if isinstance(im, str) and "/" in str(im) else float(im)
        re_tex = format_number_latex(re)
        im_tex = format_number_latex(im)
        if abs(im_num) < 1e-10:
            return re_tex
        sign = "+" if im_num >= 0 else "-"
        im_abs = format_number_latex(abs(im_num) if not isinstance(im, str) else im)
        if abs(float(sp.Rational(str(re))) if isinstance(re, str) and "/" in str(re) else float(re or 0)) < 1e-10:
            return f"{im_tex}i" if im_num >= 0 else f"-{im_abs}i"
        return f"{re_tex}{sign}{im_abs}i"
    return str(val)


def matrix_to_list(mat):
    if isinstance(mat, np.ndarray):
        return [[format_number(x) for x in row] for row in mat.tolist()]
    if isinstance(mat, sp.Matrix):
        simplified = mat.applyfunc(lambda x: _nsimplify_expr(x))
        return [[format_number(simplified[i, j]) for j in range(simplified.cols)] for i in range(simplified.rows)]
    if isinstance(mat, list):
        return [[format_number(x) for x in row] for row in mat]
    raise TypeError("Unsupported matrix type")


def matrix_to_latex(mat):
    if isinstance(mat, sp.Matrix):
        return sp.latex(mat.applyfunc(lambda x: _nsimplify_expr(x)))
    return sp.latex(sp.Matrix(mat))


def poly_to_str(poly, var=sp.Symbol("x")):
    return str(sp.expand(poly))


def poly_to_latex(poly, var=sp.Symbol("x")):
    return sp.latex(sp.expand(poly))


def exact_matrix_max_abs(expr_mat):
    """Return exact 0 when verification matrix is zero; otherwise numeric max."""
    if isinstance(expr_mat, sp.Matrix):
        simplified = expr_mat.applyfunc(lambda x: sp.nsimplify(x, rational=True))
        if simplified.is_zero_matrix:
            return 0
        return format_number(max(abs(float(x.evalf())) for x in simplified))
    return format_number(0)
