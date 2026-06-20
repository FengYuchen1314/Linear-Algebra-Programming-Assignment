"""Jordan normal form via nilpotent matrix method."""

import numpy as np
import sympy as sp

from app.utils.formatter import (
    format_number,
    matrix_to_list,
    matrix_to_latex,
    exact_matrix_max_abs,
    to_exact_matrix,
)
from app.utils.latex import latex_matrix

lam = sp.Symbol("lambda")


def _round_complex(z, ndigits=6):
    z = complex(z)
    re = round(z.real, ndigits)
    im = round(z.imag, ndigits)
    return re if abs(im) < 1e-9 else complex(re, im)


def _numeric_matrix_to_list(M):
    """Format a (possibly complex) numeric SymPy matrix without rationalizing."""
    return [[format_number(_round_complex(M[i, j])) for j in range(M.cols)] for i in range(M.rows)]


def _numeric_dim_ker_table(A_np, ev_num, alg_mult, n, tol=1e-6):
    """dim ker(B^k) table computed via numerically-stable matrix ranks."""
    B = A_np - ev_num * np.eye(n, dtype=complex)
    table = []
    d_prev = 0
    k = 0
    while True:
        d_k = 0 if k == 0 else n - int(np.linalg.matrix_rank(np.linalg.matrix_power(B, k), tol=tol))
        diff = d_k - d_prev
        block_info = ""
        if k >= 1:
            if d_k < alg_mult:
                d_next = n - int(np.linalg.matrix_rank(np.linalg.matrix_power(B, k + 1), tol=tol))
            else:
                d_next = d_k
            num_blocks = 2 * d_k - d_prev - d_next
            block_info = f"至少大小 {k} 的块: {diff}, 恰好大小 {k} 的块: {num_blocks}"
        table.append({"k": k, "dim_ker_Bk": d_k, "dk_diff": diff, "jordan_block_info": block_info})
        if d_k >= alg_mult:
            break
        d_prev = d_k
        k += 1
        if k > alg_mult + 2:
            break
    return table


def _nullity(B, k):
    return (B ** k).nullspace()


def _dim_ker_powers(A, eigenvalue, alg_mult):
    n = A.rows
    B = A - eigenvalue * sp.eye(n)
    table = []
    d_prev = 0
    k = 0
    while True:
        nk = len(_nullity(B, k)) if k > 0 else 0
        if k == 0:
            d_k = 0
        else:
            d_k = len(_nullity(B, k))
        diff = d_k - d_prev
        block_info = ""
        if k >= 1:
            d_next = len(_nullity(B, k + 1)) if d_k < alg_mult else d_k
            num_blocks = 2 * d_k - d_prev - d_next if k >= 1 else 0
            if k >= 1 and d_k < alg_mult:
                d_next_val = len(_nullity(B, k + 1))
                num_blocks = 2 * d_k - d_prev - d_next_val
            elif k >= 1:
                num_blocks = d_k - d_prev
            block_info = f"至少大小 {k} 的块: {diff}" + (f", 恰好大小 {k} 的块: {num_blocks}" if k >= 1 else "")
        table.append({
            "k": k,
            "dim_ker_Bk": d_k,
            "dk_diff": diff,
            "jordan_block_info": block_info,
        })
        if d_k >= alg_mult:
            break
        d_prev = d_k
        k += 1
        if k > alg_mult + 2:
            break
    return table, B


def _jordan_block(size, eigenval):
    J = sp.zeros(size, size)
    for i in range(size):
        J[i, i] = eigenval
        if i < size - 1:
            J[i, i + 1] = 1
    return J


def compute_jordan(A):
    steps = []
    warnings = []
    sm = to_exact_matrix(A)
    n = sm.rows

    if n != sm.cols:
        raise ValueError("Jordan 标准型只支持方阵")

    char_poly = sm.charpoly()
    eigenvals = sm.eigenvals()

    # Exact symbolic computation is fast for real spectra (rational or
    # irrational), but explodes for complex eigenvalues (nested radicals with i).
    # Fall back to a numeric matrix in that case to stay responsive.
    numeric = any(not ev.is_real for ev in eigenvals)
    if numeric:
        warnings.append("矩阵存在复特征值，已改用数值方法近似计算 Jordan 标准型，结果为近似值")
        sm_calc = sp.Matrix(A.tolist())
        eigenvals = sm_calc.eigenvals()
    else:
        sm_calc = sm

    def _ev_latex(value):
        return format_number_latex(format_number(value)) if numeric else sp.latex(value)

    steps.append({
        "title": "特征多项式",
        "content": str(char_poly.as_expr()),
        "latex": f"\\det(\\lambda I - A) = {sp.latex(char_poly.as_expr())}",
    })

    eigen_analysis = []
    nilpotent_tables = {}
    max_nilpotent_index = 0

    for ev, alg_mult in eigenvals.items():
        ev_latex = _ev_latex(ev)
        B = sm_calc - ev * sp.eye(n)
        geo_mult = len(B.nullspace())
        table, B_mat = _dim_ker_powers(sm_calc, ev, alg_mult)
        nil_index = max((row["k"] for row in table if row["dim_ker_Bk"] >= alg_mult), default=alg_mult)
        max_nilpotent_index = max(max_nilpotent_index, nil_index)

        nilpotent_tables[str(ev)] = {
            "eigenvalue_latex": ev_latex,
            "B_matrix": matrix_to_list(B_mat),
            "B_matrix_latex": matrix_to_latex(B_mat),
            "table": table,
        }

        eigen_analysis.append({
            "eigenvalue": format_number(ev),
            "eigenvalue_latex": ev_latex,
            "algebraic_multiplicity": alg_mult,
            "geometric_multiplicity": geo_mult,
            "nilpotent_index": nil_index,
        })

        steps.append({
            "title": "特征值分析",
            "latex": (
                f"\\lambda = {ev_latex}:\\quad n_a = {alg_mult},\\ "
                f"n_g = {geo_mult},\\ t = {nil_index},\\quad B = A - \\lambda I"
            ),
        })

    P, J = sm_calc.jordan_form()
    P_inv = P.inv()

    verify = (P_inv * sm_calc * P - J).applyfunc(lambda x: sp.nsimplify(x, rational=True))
    max_err = exact_matrix_max_abs(verify)

    jordan_chains = []
    for ev in eigenvals:
        B = sm_calc - ev * sp.eye(n)
        chain_vecs = B.nullspace()
        if chain_vecs:
            jordan_chains.append({
                "eigenvalue": str(ev),
                "chain_vectors": [matrix_to_list(v) for v in chain_vecs[:3]],
            })

    steps.append({
        "title": "Jordan 标准型",
        "content": "采用上 Jordan 块约定，P⁻¹AP=J",
        "latex": f"J={latex_matrix(J.tolist())},\\quad P={latex_matrix(P.tolist())}",
    })
    steps.append({
        "title": "验证 P⁻¹AP=J",
        "content": f"最大误差: {format_number(max_err)}",
    })

    result = {
        "A": matrix_to_list(sm),
        "characteristic_polynomial": str(char_poly.as_expr()),
        "characteristic_polynomial_latex": sp.latex(char_poly.as_expr()),
        "eigenvalues": eigen_analysis,
        "nilpotent_tables": nilpotent_tables,
        "nilpotent_index": max_nilpotent_index,
        "jordan_chains": jordan_chains,
        "P": matrix_to_list(P),
        "J": matrix_to_list(J),
        "P_latex": matrix_to_latex(P),
        "J_latex": matrix_to_latex(J),
        "verification_error": max_err,
        "verification_exact": max_err == 0,
        "convention": "上 Jordan 块",
    }

    return result, steps, warnings
