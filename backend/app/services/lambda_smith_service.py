"""Lambda-matrix method and Smith normal form."""

import numpy as np
import sympy as sp
from sympy.polys.domains import QQ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.normalforms import smith_normal_form, invariant_factors

from app.utils.formatter import format_number, matrix_to_list, to_exact_matrix, round_complex, poly_to_latex, poly_to_str
from app.utils.latex import latex_matrix
from app.services.jordan_service import _numeric_jordan

lam = sp.Symbol("lambda")


def _to_domain_matrix(poly_matrix, n):
    K = QQ[lam]
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            p = sp.Poly(poly_matrix[i, j], lam, domain=QQ)
            row.append(K.from_sympy(p.as_expr()))
        rows.append(row)
    return DomainMatrix(rows, (n, n), K)


def _factorize_elementary_divisors(invariant_factor_list):
    elementary = []
    jordan_blocks = []
    for factor in invariant_factor_list:
        if factor == 1 or factor is None:
            continue
        expr = sp.expand(factor.as_expr() if hasattr(factor, "as_expr") else factor)
        if expr == 1:
            continue
        facs = sp.factor_list(expr, lam)
        for base, exp in facs[1]:
            elem_expr = sp.expand(base ** exp)
            elem_str = str(elem_expr)
            elementary.append({
                "factor": elem_str,
                "factor_latex": sp.latex(elem_expr),
                "base": str(base),
                "exponent": exp,
            })
            root = None
            base_poly = sp.Poly(base, lam) if not isinstance(base, sp.Poly) else base
            if base_poly.degree() == 1:
                root = -base_poly.all_coeffs()[1] / base_poly.all_coeffs()[0]
            jordan_blocks.append({
                "elementary_divisor": elem_str,
                "elementary_divisor_latex": sp.latex(elem_expr),
                "eigenvalue": format_number(complex(root.evalf())) if root is not None else str(base),
                "block_size": exp,
            })
    return elementary, jordan_blocks


def _compute_determinant_factors(lambda_matrix, n, invs):
    det_factors = {"D_0": "1"}
    product = sp.Integer(1)
    inv_exprs = []
    for inv in invs:
        if inv == 1:
            inv_exprs.append(sp.Integer(1))
        else:
            inv_exprs.append(sp.expand(inv.as_expr() if hasattr(inv, "as_expr") else inv))

    non_trivial_count = sum(1 for f in inv_exprs if f != 1)
    idx = 0
    for k in range(1, n + 1):
        if idx < len(inv_exprs) and inv_exprs[idx] != 1:
            product = sp.expand(product * inv_exprs[idx])
            idx += 1
        det_factors[f"D_{k}"] = str(product) if k <= non_trivial_count + (n - len(invs)) else ("0" if k > non_trivial_count else str(product))
    return det_factors


def compute_lambda_smith(A):
    steps = []
    warnings = []
    sm = to_exact_matrix(A)
    n = sm.rows

    if n != sm.cols:
        raise ValueError("λ-矩阵法只支持方阵")

    char_poly = sm.charpoly()
    lambda_I_minus_A = lam * sp.eye(n) - sm

    steps.append({
        "title": "特征矩阵 λI-A",
        "content": "构造多项式矩阵",
        "latex": f"\\lambda I - A = {latex_matrix(lambda_I_minus_A.tolist())}",
    })

    dm = _to_domain_matrix(lambda_I_minus_A, n)
    snf_dm = smith_normal_form(dm)
    snf_matrix = snf_dm.to_Matrix()
    invs = invariant_factors(dm)

    inv_exprs = []
    for inv in invs:
        if inv == 1:
            inv_exprs.append(sp.Integer(1))
        else:
            inv_exprs.append(sp.expand(inv.as_expr()))

    steps.append({
        "title": "Smith 标准型",
        "content": "经 λ-初等变换得到对角型",
        "latex": f"S={latex_matrix(snf_matrix.tolist())}",
    })

    non_trivial = [f for f in inv_exprs if f != 1]
    elementary, jordan_blocks = _factorize_elementary_divisors(non_trivial)

    min_poly = non_trivial[-1] if non_trivial else char_poly.as_expr()
    is_diag = all(sp.degree(f, lam) == 1 for f in non_trivial)

    det_factor_exprs = {"D_0": sp.Integer(1)}
    product = sp.Integer(1)
    inv_idx = 0
    for k in range(1, n + 1):
        if inv_idx < len(inv_exprs):
            product = sp.expand(product * inv_exprs[inv_idx])
            inv_idx += 1
        det_factor_exprs[f"D_{k}"] = product

    det_factors = {k: poly_to_str(v) for k, v in det_factor_exprs.items()}
    det_factors_latex = {
        k: poly_to_latex(v) if v not in (0, 1, sp.Integer(0), sp.Integer(1)) else str(v)
        for k, v in det_factor_exprs.items()
    }

    eigenvals = sm.eigenvals()
    if not all(e.is_rational for e in eigenvals):
        warnings.append("矩阵特征值非有理数，Jordan 标准型采用数值近似")
        eig_pairs = [(complex(e.evalf()), m) for e, m in eigenvals.items()]
        _P_np, J_np = _numeric_jordan(np.array(A, dtype=complex), eig_pairs)
        jordan_J_list = [[format_number(round_complex(J_np[i, j])) for j in range(J_np.shape[1])] for i in range(J_np.shape[0])]
    else:
        P, J = sm.jordan_form()
        jordan_J_list = matrix_to_list(J)

    inv_latex = [poly_to_latex(f) for f in inv_exprs]

    steps.append({
        "title": "不变因子",
        "content": f"d_k(λ): {[str(f) for f in inv_exprs]}",
        "latex": ",\\quad ".join(
            f"d_{{{i + 1}}}(\\lambda)={poly_to_latex(f)}" for i, f in enumerate(inv_exprs)
        ),
    })
    steps.append({
        "title": "初等因子组",
        "content": str([e["factor"] for e in elementary]),
        "latex": ",\\quad ".join(e["factor_latex"] for e in elementary) if elementary else "1",
    })
    steps.append({
        "title": "Jordan 块（由初等因子）",
        "content": str(jordan_blocks),
        "latex": ",\\quad ".join(
            f"{b['elementary_divisor_latex']} \\rightarrow J_{{{b['block_size']}}}"
            for b in jordan_blocks
        ) if jordan_blocks else "",
    })

    result = {
        "lambda_I_minus_A": matrix_to_list(lambda_I_minus_A),
        "smith_form": matrix_to_list(snf_matrix),
        "determinant_factors": det_factors,
        "determinant_factors_latex": det_factors_latex,
        "invariant_factors": [str(f) for f in inv_exprs],
        "invariant_factors_latex": inv_latex,
        "elementary_divisors": elementary,
        "jordan_blocks_from_elementary": jordan_blocks,
        "jordan_form_J": jordan_J_list,
        "is_diagonalizable": is_diag,
        "minimal_polynomial": str(min_poly),
        "minimal_polynomial_latex": poly_to_latex(min_poly),
        "characteristic_polynomial": str(char_poly.as_expr()),
        "characteristic_polynomial_latex": poly_to_latex(char_poly.as_expr()),
    }

    return result, steps, warnings
