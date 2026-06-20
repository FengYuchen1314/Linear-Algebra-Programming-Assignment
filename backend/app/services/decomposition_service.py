"""Matrix decomposition services."""

import numpy as np
import sympy as sp
from scipy.linalg import svd as scipy_svd

from app.utils.formatter import format_number, matrix_to_list, exact_matrix_max_abs, to_exact_matrix
from app.utils.latex import latex_matrix


def full_rank_decomposition(A):
    steps = []
    sm = to_exact_matrix(A)
    m, n = sm.shape
    rank = sm.rank()
    rref, pivot_cols = sm.rref()
    pivot_cols = list(pivot_cols)

    H = rref[:rank, :]
    B = sm[:, pivot_cols]
    C = H

    steps.append({
        "title": "Hermite 标准型 / RREF",
        "content": f"rank(A)={rank}，主元列: {pivot_cols}",
        "latex": f"H={latex_matrix(rref.tolist())}",
    })
    steps.append({
        "title": "满秩分解 A=BC",
        "content": f"B 为 {m}×{rank}，C 为 {rank}×{n}",
        "latex": f"B={latex_matrix(B.tolist())},\\quad C={latex_matrix(C.tolist())}",
    })

    product = B * C
    error = sm - product
    err = exact_matrix_max_abs(error)
    steps.append({
        "title": "验证 A=BC",
        "content": "误差矩阵为零" if err == 0 else f"误差矩阵最大元素: {err}",
        "latex": f"A-BC={latex_matrix(error.tolist())}",
    })

    return {
        "rank": rank,
        "rref": matrix_to_list(rref),
        "pivot_columns": pivot_cols,
        "B": matrix_to_list(B),
        "C": matrix_to_list(C),
        "verification_error": err,
        "verification_exact": err == 0,
    }, steps


def lu_decomposition(A):
    steps = []
    sm = to_exact_matrix(A)
    n = sm.rows

    if n != sm.cols:
        raise ValueError("LU 分解需要方阵")

    try:
        L, U, perm = sm.LUdecomposition()
        P = sp.eye(n)
        if perm:
            P = P.permute_rows(perm)
        needs_perm = not P.equals(sp.eye(n))

        if needs_perm:
            steps.append({
                "title": "PLU 分解",
                "content": "需要行交换",
                "latex": f"P={latex_matrix(P.tolist())},\\quad L={latex_matrix(L.tolist())},\\quad U={latex_matrix(U.tolist())}",
            })
        else:
            steps.append({
                "title": "LU 分解",
                "content": "顺序主子式非零，无需行交换",
                "latex": f"L={latex_matrix(L.tolist())},\\quad U={latex_matrix(U.tolist())}",
            })

        lhs = P * sm if needs_perm else sm
        LU = L * U
        error = lhs - LU
        err = exact_matrix_max_abs(error)

        result = {
            "needs_permutation": needs_perm,
            "can_plain_lu": not needs_perm,
            "L": matrix_to_list(L),
            "U": matrix_to_list(U),
            "verification_error": err,
            "verification_exact": err == 0,
        }
        if needs_perm:
            result["P"] = matrix_to_list(P)

        if needs_perm:
            steps.append({
                "title": "分解结果",
                "latex": f"P={latex_matrix(P.tolist())},\\quad L={latex_matrix(L.tolist())},\\quad U={latex_matrix(U.tolist())}",
            })
        else:
            steps.append({
                "title": "分解结果",
                "latex": f"L={latex_matrix(L.tolist())},\\quad U={latex_matrix(U.tolist())}",
            })

        verify_title = "验证 PA=LU" if needs_perm else "验证 A=LU"
        verify_lhs = "PA" if needs_perm else "A"
        steps.append({
            "title": verify_title,
            "content": "恒等" if err == 0 else f"最大误差: {err}",
            "latex": f"{verify_lhs}-LU={latex_matrix(error.tolist())}",
        })

        return result, steps
    except Exception as e:
        raise ValueError(f"LU 分解失败: {e}") from e


def ldu_decomposition(A):
    steps = []
    lu_result, lu_steps = lu_decomposition(A)
    steps.extend(lu_steps)

    if not lu_result.get("L"):
        return lu_result, steps

    L = sp.Matrix(lu_result["L"])
    U = sp.Matrix(lu_result["U"])
    sm = to_exact_matrix(A)
    needs_perm = lu_result.get("needs_permutation", False)
    P = sp.Matrix(lu_result["P"]) if needs_perm and lu_result.get("P") else sp.eye(sm.rows)

    diag_elems = [U[i, i] for i in range(U.rows)]
    if any(d == 0 for d in diag_elems):
        fail = {
            "success": False,
            "reason": "U 的对角元素存在零，无法进行 LDU 分解",
            "L": lu_result["L"],
            "U": lu_result["U"],
        }
        if needs_perm:
            fail["P"] = lu_result["P"]
        return fail, steps

    D = sp.diag(*diag_elems)
    # U = D · U1 with U1 unit upper-triangular, so divide each row by its pivot.
    U1 = U.copy()
    for i in range(U1.rows):
        for j in range(U1.cols):
            U1[i, j] = U1[i, j] / diag_elems[i]

    LDU = L * D * U1
    lhs = P * sm if needs_perm else sm
    error = lhs - LDU
    err = exact_matrix_max_abs(error)

    result = {
        "success": True,
        "needs_permutation": needs_perm,
        "L": lu_result["L"],
        "D": matrix_to_list(D),
        "U1": matrix_to_list(U1),
        "verification_error": err,
        "verification_exact": err == 0,
    }
    if needs_perm:
        result["P"] = lu_result["P"]

    steps.append({
        "title": "LDU 分解",
        "content": "U = D·U₁，其中 U₁ 为单位上三角矩阵",
        "latex": f"D={latex_matrix(D.tolist())},\\quad U_1={latex_matrix(U1.tolist())}",
    })
    verify_title = "验证 PA=LDU" if needs_perm else "验证 A=LDU"
    verify_lhs = "PA" if needs_perm else "A"
    steps.append({
        "title": verify_title,
        "content": "恒等" if err == 0 else f"最大误差: {err}",
        "latex": f"{verify_lhs}-LDU={latex_matrix(error.tolist())}",
    })

    return result, steps


def svd_decomposition(A):
    steps = []
    warnings = []
    sm = to_exact_matrix(A)
    m, n = sm.rows, sm.cols
    rank = sm.rank()
    AtA = sm.T * sm

    steps.append({
        "title": "SVD 方法",
        "content": "计算 B=AᵀA（精确），再求特征值与特征向量",
        "latex": f"A^T A={latex_matrix(AtA.tolist())}",
    })

    try:
        char_poly = AtA.charpoly()
        steps.append({
            "title": "AᵀA 特征多项式",
            "content": str(char_poly.as_expr()),
            "latex": sp.latex(char_poly.as_expr()),
        })
    except Exception:
        pass

    warnings.append("奇异值与 U、V 矩阵使用 SciPy 数值计算")
    U_np, s, Vt_np = scipy_svd(np.array(A, dtype=float), full_matrices=True)
    sigma = np.zeros((m, n))
    for i, sv in enumerate(s):
        if i < min(m, n):
            sigma[i, i] = sv

    reconstruction = U_np @ sigma @ Vt_np
    error = np.linalg.norm(A - reconstruction, ord="fro")

    steps.append({
        "title": "数值 SVD 分解",
        "content": "U、Σ、Vᵀ 由 SciPy 数值计算",
    })

    result = {
        "U": matrix_to_list(U_np),
        "Sigma": matrix_to_list(sigma),
        "V_transpose": matrix_to_list(Vt_np),
        "singular_values": [format_number(x) for x in s],
        "rank": int(rank),
        "verification_error": format_number(error),
        "verification_exact": False,
        "method": "numeric",
    }

    steps.append({
        "title": "验证 ||A - UΣVᵀ||",
        "content": f"Frobenius 范数误差: {format_number(error)}",
    })

    return result, steps, warnings
