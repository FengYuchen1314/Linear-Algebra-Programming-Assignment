"""Matrix basic properties computation."""

import numpy as np
import sympy as sp

from app.utils.formatter import format_number, matrix_to_list, exact_matrix_max_abs, format_number_latex, to_exact_matrix, eigenvalue_display
from app.utils.latex import latex_matrix


def _eigenvalue_analysis(sm, A):
    n = sm.rows
    char_poly = sm.charpoly()
    eigenvals = sm.eigenvals()
    warnings = []
    use_numeric = not all(lam.is_rational for lam in eigenvals)
    A_np = np.array(A, dtype=complex) if use_numeric else None
    if use_numeric:
        warnings.append("矩阵特征值非有理数，几何重数采用数值方法计算")
    analysis = []
    for ev, alg_mult in eigenvals.items():
        ev_value, ev_latex = eigenvalue_display(ev)
        if use_numeric:
            ev_num = complex(ev.evalf())
            geo_mult = n - int(np.linalg.matrix_rank(A_np - ev_num * np.eye(n, dtype=complex), tol=1e-6))
        else:
            geo_mult = len((sm - ev * sp.eye(n)).nullspace())
        analysis.append({
            "eigenvalue": ev_value,
            "eigenvalue_latex": ev_latex,
            "algebraic_multiplicity": alg_mult,
            "geometric_multiplicity": geo_mult,
        })
    total_geo = sum(a["geometric_multiplicity"] for a in analysis)
    is_diag = total_geo == n
    reason = "每个特征值的几何重数等于代数重数" if is_diag else "存在特征值的几何重数小于代数重数"
    return char_poly, analysis, is_diag, reason, warnings


def compute_properties(A):
    steps = []
    warnings = []
    sm = to_exact_matrix(A)
    m, n = sm.rows, sm.cols
    rank = sm.rank()
    rref = sm.rref()[0]

    steps.append({
        "title": "行化简 (RREF)",
        "content": f"rank(A) = {rank}",
        "latex": f"\\text{{RREF}}(A)={latex_matrix(rref.tolist())}",
    })

    result = {
        "rows": m,
        "cols": n,
        "is_square": m == n,
        "rank": rank,
        "rref": matrix_to_list(rref),
    }

    if m == n:
        det_val = sp.nsimplify(sm.det(), rational=True)
        trace_val = sp.nsimplify(sm.trace(), rational=True)
        is_invertible = det_val != 0
        result.update({
            "det": format_number(det_val),
            "det_latex": sp.latex(det_val),
            "trace": format_number(trace_val),
            "trace_latex": sp.latex(trace_val),
            "is_invertible": is_invertible,
        })

        if is_invertible:
            inv = sm.inv().applyfunc(lambda x: sp.nsimplify(x, rational=True))
            result["inverse"] = matrix_to_list(inv)
            steps.append({
                "title": "逆矩阵验证",
                "content": "A·A⁻¹ = I 且 A⁻¹·A = I",
                "latex": f"A^{{-1}}={latex_matrix(inv.tolist())}",
            })
        else:
            result["inverse"] = None
            steps.append({"title": "不可逆", "content": "det(A)=0，矩阵不可逆", "latex": "\\det(A)=0"})

        char_poly, eigen_analysis, is_diag, reason, eig_warnings = _eigenvalue_analysis(sm, A)
        warnings.extend(eig_warnings)
        result["characteristic_polynomial"] = str(char_poly.as_expr())
        result["characteristic_polynomial_latex"] = sp.latex(char_poly.as_expr())
        result["eigenvalues"] = eigen_analysis
        result["is_diagonalizable"] = is_diag
        result["diagonalizable_reason"] = reason

        steps.append({
            "title": "特征多项式",
            "content": f"det(λI-A) = {char_poly.as_expr()}",
            "latex": f"\\det(\\lambda I - A)={sp.latex(char_poly.as_expr())}",
        })
        steps.append({
            "title": "可对角化判定",
            "content": reason,
        })

        eigvals = [a["eigenvalue"] for a in eigen_analysis for _ in range(a["algebraic_multiplicity"])]
        if eigvals:
            tr_parts = []
            for v in eigvals:
                tr_parts.append(format_number_latex(v))
            steps.append({
                "title": "迹与行列式验证",
                "content": f"Σλᵢ 与 tr(A)、Πλᵢ 与 det(A) 一致",
                "latex": f"\\sum \\lambda_i = {result['trace_latex']},\\quad \\prod \\lambda_i = {result['det_latex']}",
            })
    else:
        has_left = rank == n
        has_right = rank == m
        result["has_left_inverse"] = has_left
        result["has_right_inverse"] = has_right

        if has_left:
            ata = sm.T * sm
            left_inv = (ata.inv() * sm.T).applyfunc(lambda x: sp.nsimplify(x, rational=True))
            result["left_inverse"] = matrix_to_list(left_inv)
            steps.append({
                "title": "左逆",
                "content": "rank(A)=n，列满秩，L=(AᵀA)⁻¹Aᵀ",
                "latex": f"L={latex_matrix(left_inv.tolist())}",
            })
        else:
            result["left_inverse"] = None

        if has_right:
            aat = sm * sm.T
            right_inv = (sm.T * aat.inv()).applyfunc(lambda x: sp.nsimplify(x, rational=True))
            result["right_inverse"] = matrix_to_list(right_inv)
            steps.append({
                "title": "右逆",
                "content": "rank(A)=m，行满秩，R=Aᵀ(AAᵀ)⁻¹",
                "latex": f"R={latex_matrix(right_inv.tolist())}",
            })
        else:
            result["right_inverse"] = None

        if not has_left and not has_right:
            steps.append({"title": "无广义逆", "content": "矩阵既无左逆也无右逆"})

    return result, steps, warnings
