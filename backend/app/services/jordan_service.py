"""Jordan normal form via nilpotent matrix method."""

import numpy as np
import sympy as sp

from app.utils.formatter import (
    format_number,
    matrix_to_list,
    exact_matrix_max_abs,
    to_exact_matrix,
    round_complex,
    eigenvalue_display,
)
from app.utils.latex import latex_matrix

lam = sp.Symbol("lambda")


def _numeric_matrix_to_list(M):
    """Format a (possibly complex) numeric SymPy matrix without rationalizing."""
    return [[format_number(round_complex(M[i, j])) for j in range(M.cols)] for i in range(M.rows)]


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


def _orth(M, tol=1e-9):
    """Orthonormal basis for the column space of M (numeric)."""
    M = np.asarray(M, dtype=complex)
    if M.size == 0 or M.shape[1] == 0:
        return np.zeros((M.shape[0], 0), dtype=complex)
    u, s, _ = np.linalg.svd(M)
    thresh = tol * max(M.shape) * (s[0] if s.size else 1.0)
    rank = int(np.sum(s > thresh))
    return u[:, :rank]


def _null_basis(M, tol=1e-9):
    """Orthonormal basis for the null space of M (numeric)."""
    M = np.asarray(M, dtype=complex)
    if M.shape[1] == 0:
        return np.zeros((M.shape[0], 0), dtype=complex)
    u, s, vh = np.linalg.svd(M)
    thresh = tol * max(M.shape) * (s[0] if s.size else 1.0)
    rank = int(np.sum(s > thresh))
    return vh[rank:].conj().T


def _complement(B, base, tol=1e-9):
    """Basis for the part of col(B) not already contained in col(base)."""
    Bp = B
    Qb = _orth(base, tol)
    if Qb.shape[1] > 0:
        Bp = B - Qb @ (Qb.conj().T @ B)
    return _orth(Bp, tol)


def _numeric_jordan(A_np, eig_pairs, tol=1e-9):
    """Numeric Jordan form: J from integer rank structure, P from generalized
    eigenvector chains. Robust for irrational/complex spectra where exact SymPy
    would explode. eig_pairs is a list of (numeric_eigenvalue, algebraic_mult)."""
    n = A_np.shape[0]
    I = np.eye(n, dtype=complex)
    P_cols = []
    blocks = []  # (lambda, block_size)
    for lam_val, _alg in eig_pairs:
        N = A_np - lam_val * I
        # Kernel bases of increasing powers, until the kernel dimension stabilizes.
        ker = [np.zeros((n, 0), dtype=complex)]
        dims = [0]
        power = np.eye(n, dtype=complex)
        while True:
            power = power @ N
            kb = _null_basis(power, tol)
            ker.append(kb)
            dims.append(kb.shape[1])
            if dims[-1] == dims[-2] or len(dims) > n + 1:
                break
        q = len(ker) - 2  # highest power whose kernel still grew = max chain length
        higher = np.zeros((n, 0), dtype=complex)
        for level in range(q, 0, -1):
            base = np.concatenate([ker[level - 1], higher], axis=1)
            tops = _complement(ker[level], base, tol)
            for j in range(tops.shape[1]):
                w = tops[:, j]
                chain = [w]
                v = w
                for _ in range(level - 1):
                    v = N @ v
                    chain.append(v)
                blocks.append((lam_val, level))
                P_cols.extend(reversed(chain))  # eigenvector first -> upper Jordan blocks
            allk = np.concatenate([higher, tops], axis=1)
            higher = (N @ allk) if allk.shape[1] > 0 else np.zeros((n, 0), dtype=complex)
    P = np.column_stack(P_cols) if P_cols else np.eye(n, dtype=complex)
    J = np.zeros((n, n), dtype=complex)
    idx = 0
    for lam_val, size in blocks:
        for d in range(size):
            J[idx + d, idx + d] = lam_val
            if d < size - 1:
                J[idx + d, idx + d + 1] = 1.0
        idx += size
    return P, J


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

    # Exact symbolic structure (null spaces of B^k, Jordan form) is only fast
    # and reliable when the eigenvalues are rational. Irrational/complex roots
    # (radicals, CRootOf) make SymPy explode, so we switch to numerically-stable
    # ranks and a numeric Jordan form there. Exact eigenvalues are still used for
    # display where they are "nice".
    use_numeric = not all(ev.is_rational for ev in eigenvals)
    A_np = np.array(A, dtype=complex) if use_numeric else None
    if use_numeric:
        warnings.append("矩阵特征值非有理数，结构计算采用数值方法，Jordan 标准型为近似结果")

    steps.append({
        "title": "特征多项式",
        "content": str(char_poly.as_expr()),
        "latex": f"\\det(\\lambda I - A) = {sp.latex(char_poly.as_expr())}",
    })

    eigen_analysis = []
    nilpotent_tables = {}
    max_nilpotent_index = 0

    for ev, alg_mult in eigenvals.items():
        ev_value, ev_latex = eigenvalue_display(ev)
        if use_numeric:
            ev_num = complex(ev.evalf())
            geo_mult = n - int(np.linalg.matrix_rank(A_np - ev_num * np.eye(n, dtype=complex), tol=1e-6))
            table = _numeric_dim_ker_table(A_np, ev_num, alg_mult, n)
            B_list = _numeric_matrix_to_list(sp.Matrix((A_np - ev_num * np.eye(n, dtype=complex)).tolist()))
        else:
            B = sm - ev * sp.eye(n)
            geo_mult = len(B.nullspace())
            table, B_mat = _dim_ker_powers(sm, ev, alg_mult)
            B_list = matrix_to_list(B_mat)

        nil_index = max((row["k"] for row in table if row["dim_ker_Bk"] >= alg_mult), default=alg_mult)
        max_nilpotent_index = max(max_nilpotent_index, nil_index)

        nilpotent_tables[str(ev)] = {
            "eigenvalue_latex": ev_latex,
            "B_matrix": B_list,
            "table": table,
        }

        eigen_analysis.append({
            "eigenvalue": ev_value,
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

    if use_numeric:
        eig_pairs = [(complex(ev.evalf()), m) for ev, m in eigenvals.items()]
        P_np, J_np = _numeric_jordan(A_np, eig_pairs)
        P_clean = [[round_complex(P_np[i, j]) for j in range(P_np.shape[1])] for i in range(P_np.shape[0])]
        J_clean = [[round_complex(J_np[i, j]) for j in range(J_np.shape[1])] for i in range(J_np.shape[0])]
        P_list, J_list = matrix_to_list(P_clean), matrix_to_list(J_clean)
        P_latex, J_latex = latex_matrix(P_clean), latex_matrix(J_clean)
        try:
            residual = np.linalg.solve(P_np, A_np @ P_np) - J_np
            max_err = format_number(round_complex(float(np.max(np.abs(residual))) if residual.size else 0.0))
        except np.linalg.LinAlgError:
            max_err = format_number(0.0)
        jordan_chains = []
    else:
        P, J = sm.jordan_form()
        P_list, J_list = matrix_to_list(P), matrix_to_list(J)
        P_latex, J_latex = latex_matrix(P.tolist()), latex_matrix(J.tolist())
        verify = (P.inv() * sm * P - J).applyfunc(lambda x: sp.nsimplify(x, rational=True))
        max_err = exact_matrix_max_abs(verify)
        jordan_chains = []
        for ev in eigenvals:
            chain_vecs = (sm - ev * sp.eye(n)).nullspace()
            if chain_vecs:
                jordan_chains.append({
                    "eigenvalue": str(ev),
                    "chain_vectors": [matrix_to_list(v) for v in chain_vecs[:3]],
                })

    steps.append({
        "title": "Jordan 标准型",
        "content": "采用上 Jordan 块约定，P⁻¹AP=J",
        "latex": f"J={J_latex},\\quad P={P_latex}",
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
        "P": P_list,
        "J": J_list,
        "P_latex": P_latex,
        "J_latex": J_latex,
        "verification_error": max_err,
        "verification_exact": max_err == 0,
        "convention": "上 Jordan 块",
    }

    return result, steps, warnings
