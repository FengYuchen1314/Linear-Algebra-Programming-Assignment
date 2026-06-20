#!/usr/bin/env python3
"""一键运行线性代数全部功能，并生成文本报告。

单文件独立运行：复制本文件到任意位置即可执行，无需原项目 backend。
运行前会自动检查并安装缺失依赖；完成后自动打开 TXT 报告。

运行方式：
    python run_all.py

输出文件（生成于本目录）：
    线性代数计算报告.txt   — 简洁文本，不含复杂公式
"""

from __future__ import annotations

import importlib
import platform
import re
import subprocess
import sys
import textwrap
import traceback
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

REQUIRED_PACKAGES: list[tuple[str, str]] = [
    ("sympy", "sympy"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
]


def _show_alert(title: str, message: str) -> None:
    """跨平台弹窗提醒；失败时回退到终端输出。"""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except tk.TclError:
            pass
        messagebox.showinfo(title, message, parent=root)
        root.destroy()
        return
    except Exception:
        pass

    system = platform.system()
    safe_msg = message.replace('"', "'").replace("\\", "/")
    safe_title = title.replace('"', "'")
    try:
        if system == "Darwin":
            script = (
                f'display dialog "{safe_msg}" with title "{safe_title}" '
                f'buttons {{"确定"}} default button 1 with icon note'
            )
            subprocess.run(["osascript", "-e", script], check=False)
            return
        if system == "Windows":
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Add-Type -AssemblyName PresentationFramework;"
                    f'[System.Windows.MessageBox]::Show("{safe_msg}","{safe_title}")',
                ],
                check=False,
            )
            return
    except Exception:
        pass

    print(f"\n[{title}] {message}\n")


def _pip_install(packages: list[str]) -> None:
    print(f"正在安装: {', '.join(packages)}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        check=True,
    )


def ensure_dependencies() -> None:
    """检查第三方库，缺失则弹窗提醒并自动 pip 安装。"""
    missing_pip: list[str] = []
    for pip_name, import_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_pip.append(pip_name)

    if missing_pip:
        _show_alert(
            "缺少依赖库",
            "检测到未安装以下库：\n"
            + "\n".join(f"  · {name}" for name in missing_pip)
            + "\n\n即将自动安装，请稍候…",
        )
        _pip_install(missing_pip)


def open_txt(path: Path) -> None:
    """用系统默认程序打开文本报告。"""
    if not path.exists():
        return
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        elif system == "Windows":
            import os

            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception as exc:
        print(f"      无法自动打开 TXT: {exc}")


ensure_dependencies()

import numpy as np
import sympy as sp
from scipy.linalg import svd as scipy_svd
from sympy.polys.domains import QQ
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.normalforms import invariant_factors, smith_normal_form

# =============================================================================
# 计算核心（原 la_core，内联）
# =============================================================================

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





import sympy as sp


def latex_matrix(mat):
    return sp.latex(sp.Matrix(mat))


def latex_poly(poly):
    return sp.latex(sp.expand(poly))


def latex_expr(expr):
    return sp.latex(sp.simplify(expr))



import numpy as np
import sympy as sp


def _nsimplify_expr(val):
    if isinstance(val, sp.Basic):
        try:
            return sp.nsimplify(val, rational=True)
        except (TypeError, ValueError, AttributeError):
            return sp.simplify(val)
    return val


def eigenvalue_display(ev):
    """Return (numeric_value, latex) for a SymPy eigenvalue.

    Rationals stay exact; "nice" closed-form values (radicals, i) keep their
    exact LaTeX; CRootOf / opaque roots fall back to a rounded decimal so the
    UI never shows \\operatorname{CRootOf}(...).
    """
    if ev.is_rational:
        return format_number(ev), sp.latex(ev)
    num = round_complex(complex(ev.evalf()))
    value = format_number(num)
    nice = bool(ev.is_number) and not ev.has(sp.CRootOf)
    latex = sp.latex(ev) if nice else format_number_latex(value)
    return value, latex


def round_complex(z, ndigits=6):
    """Round a (possibly complex) number; collapse to real if imag ~ 0."""
    z = complex(z)
    re = round(z.real, ndigits)
    im = round(z.imag, ndigits)
    return re if abs(im) < 1e-9 else complex(re, im)


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
        if val.free_symbols:
            return {"latex": sp.latex(sp.expand(val))}
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
        # nsimplify(rational=True) on tiny floating residuals (e.g. 1e-16) is
        # pathologically slow, so only take the exact path for exact matrices.
        if any(getattr(e, "has", lambda *_: False)(sp.Float) for e in expr_mat):
            mx = max((abs(complex(e.evalf())) for e in expr_mat), default=0.0)
            return 0 if mx < 1e-9 else format_number(round(mx, 10))
        simplified = expr_mat.applyfunc(lambda x: sp.nsimplify(x, rational=True))
        if simplified.is_zero_matrix:
            return 0
        return format_number(max(abs(complex(x.evalf())) for x in simplified))
    return format_number(0)
"""Sturm sequence and root finding service."""

import sympy as sp


DEFAULT_PRECISION = 0.01
ROOT_TOL = 1e-10
INTERIOR_OFFSET = 1e-8


def _fval(f, x):
    return float(sp.N(f.subs(X, x), 50))


def _fprime(f):
    return sp.expand(sp.diff(f, X))


def _is_root(f, x):
    return abs(_fval(f, x)) < ROOT_TOL


def _poly_div_rem(f, g):
    q, r = sp.div(sp.expand(f), sp.expand(g), X)
    return sp.expand(q), sp.expand(r)


def _build_sturm_sequence(f):
    g0 = sp.expand(f)
    g1 = sp.expand(sp.diff(g0, X))
    sequence = [g0, g1]
    while True:
        if sp.Poly(sequence[-1], X).degree() == 0:
            break
        _, rem = _poly_div_rem(sequence[-2], sequence[-1])
        if sp.simplify(rem) == 0:
            break
        sequence.append(sp.expand(-rem))
        if sp.Poly(sequence[-1], X).degree() == 0:
            break
    return sequence


def _sign_variations(values):
    filtered = [v for v in values if abs(float(v)) > 1e-12]
    if len(filtered) <= 1:
        return 0
    count = 0
    for i in range(len(filtered) - 1):
        if filtered[i] * filtered[i + 1] < 0:
            count += 1
    return count


def _eval_sturm(sequence, c):
    return [float(sp.N(g.subs(X, c), 50)) for g in sequence]


def _positive_root_bound(f):
    """Upper bound for positive real roots.

    If a_n > 0 and some a_i < 0 (i < n), every positive root is < 1 + max|a_i/a_n|.
    If no such negative coefficient exists, there is no positive real root.
    """
    poly = sp.Poly(sp.expand(f), X)
    if poly.degree() <= 0:
        return 0.0
    coeffs = [float(c) for c in poly.all_coeffs()]
    an = coeffs[0]
    if abs(an) < 1e-15:
        return 0.0
    normalized = [coeffs[i] / an for i in range(1, len(coeffs))]
    negative = [abs(c) for c in normalized if c < -1e-15]
    if not negative:
        return 0.0
    return 1.0 + max(negative)


def _cauchy_radius(f):
    """Symmetric Cauchy radius: every complex root satisfies |z| <= B."""
    poly = sp.Poly(sp.expand(f), X)
    an = float(poly.LC())
    ratios = [abs(float(c / an)) for c in poly.all_coeffs()[1:]]
    return 1.0 + max(ratios) if ratios else 1.0


def _real_root_bounds(f):
    """Asymmetric interval [L, R] containing all real roots.

    Positive roots are bounded by _positive_root_bound(f); negative roots by
    negating the positive-root bound of f(-x).  Only when both sides collapse
    to 0 (e.g. no real roots) do we fall back to the symmetric Cauchy disk.
    """
    pos_R = _positive_root_bound(f)
    pos_L = _positive_root_bound(sp.expand(f.subs(X, -X)))
    L = -pos_L if pos_L > 1e-15 else 0.0
    R = pos_R if pos_R > 1e-15 else 0.0

    if R - L <= 1e-15:
        B = _cauchy_radius(f)
        L, R = -B, B

    pad = max(1e-4, 1e-9 * max(abs(L), abs(R), 1.0))
    return L - pad, R + pad


def _count_roots_in_interval(sequence, a, b):
    """Count distinct real roots in (a, b] via Sturm's theorem.

    Evaluate slightly inside the endpoints so zeros in the Sturm sequence at
    exact roots of f do not corrupt the variation count.
    """
    width = b - a
    eps = min(INTERIOR_OFFSET, width / 4) if width > 8 * INTERIOR_OFFSET else 0.0
    a_eval = a + eps
    b_eval = b - eps if width > 2 * eps else b
    if a_eval >= b_eval:
        a_eval, b_eval = a, b
    va = _sign_variations(_eval_sturm(sequence, a_eval))
    vb = _sign_variations(_eval_sturm(sequence, b_eval))
    return va - vb, va, vb


def _dedupe_intervals(intervals):
    """Merge isolation intervals that refer to the same root."""
    by_center = {}
    for lo, hi in intervals:
        center = (lo + hi) / 2
        key = round(center, 8)
        if key not in by_center:
            by_center[key] = [lo, hi]
        else:
            prev = by_center[key]
            by_center[key] = [min(prev[0], lo), max(prev[1], hi)]
    return [by_center[k] for k in sorted(by_center)]


def _refine_interval(f, sequence, left, right, max_width):
    """Shrink an interval known to contain one root to width <= max_width."""
    lo, hi = left, right
    flo, fhi = _fval(f, lo), _fval(f, hi)

    if abs(flo) < ROOT_TOL:
        return lo, min(hi, lo + max_width)
    if abs(fhi) < ROOT_TOL:
        return max(lo, hi - max_width), hi

    guard = 0
    while hi - lo > max_width and guard < 200:
        guard += 1
        mid = (lo + hi) / 2
        fmid = _fval(f, mid)

        if abs(fmid) < ROOT_TOL:
            if mid - lo <= hi - mid:
                hi = mid
                fhi = fmid
            else:
                lo = mid
                flo = fmid
            continue

        if flo * fhi <= 0:
            if flo * fmid <= 0:
                hi, fhi = mid, fmid
            else:
                lo, flo = mid, fmid
            continue

        count_left, _, _ = _count_roots_in_interval(sequence, lo, mid)
        if count_left >= 1:
            hi = mid
        else:
            lo = mid

    return lo, hi


def _best_sample(f, left, right, samples=24):
    if right - left < 1e-14:
        return left
    best_x = left
    best_v = abs(_fval(f, left))
    for i in range(samples + 1):
        x = left + (right - left) * i / samples
        v = abs(_fval(f, x))
        if v < best_v:
            best_v = v
            best_x = x
    return best_x


def _polish_newton(f, f_prime, x0, left, right, precision):
    """Refine a root estimate with damped Newton, clamped to the bracket."""
    x = x0
    tol = min(ROOT_TOL, precision / 10)
    for _ in range(40):
        fx = _fval(f, x)
        if abs(fx) < tol:
            return x
        fpx = _fval(f_prime, x)
        if abs(fpx) < 1e-15:
            break
        step = fx / fpx
        x_next = x - step
        if x_next <= left or x_next >= right:
            break
        if abs(x_next - x) < tol:
            return x_next
        x = x_next
    return _best_sample(f, left, right, 32)


def _isolate_roots(f, sequence, left, right, intervals, steps):
    # Record endpoint roots but keep searching the remaining open interval.
    if _is_root(f, left):
        intervals.append([left, left])
        steps.append({"title": "端点为根", "content": f"x={left:g} 是 f(x) 的根"})
        left += INTERIOR_OFFSET
    if _is_root(f, right):
        intervals.append([right, right])
        steps.append({"title": "端点为根", "content": f"x={right:g} 是 f(x) 的根"})
        right -= INTERIOR_OFFSET

    if right - left <= ROOT_TOL:
        return

    count, va, vb = _count_roots_in_interval(sequence, left, right)
    steps.append({
        "title": f"区间 [{left:.6g}, {right:.6g}]",
        "content": f"V({left:.6g})={va}, V({right:.6g})={vb}, V(a)-V(b)={count}",
        "latex": f"V({left}) - V({right}) = {va} - {vb} = {count}",
    })

    if count <= 0:
        return
    if count == 1:
        intervals.append([left, right])
        return

    mid = (left + right) / 2
    if _is_root(f, mid):
        intervals.append([mid, mid])
        steps.append({"title": "发现根", "content": f"x={mid:g} 是 f(x) 的根"})
        _isolate_roots(f, sequence, left, mid - INTERIOR_OFFSET, intervals, steps)
        _isolate_roots(f, sequence, mid + INTERIOR_OFFSET, right, intervals, steps)
    else:
        _isolate_roots(f, sequence, left, mid, intervals, steps)
        _isolate_roots(f, sequence, mid, right, intervals, steps)


def _bisect_root(f, left, right, precision):
    """Refine an isolated interval to a simple real root."""
    f_prime = _fprime(f)
    a, b = left, right
    tol = min(ROOT_TOL, precision / 10)

    if abs(b - a) < 1e-14:
        return a

    fa, fb = _fval(f, a), _fval(f, b)
    if abs(fa) < tol:
        return a
    if abs(fb) < tol:
        return b

    if fa * fb > 0:
        guess = _best_sample(f, a, b, 32)
        return _polish_newton(f, f_prime, guess, a, b, precision)

    while b - a > precision:
        mid = (a + b) / 2
        fm = _fval(f, mid)
        if abs(fm) < tol:
            return mid
        if fa * fm <= 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm

    guess = _best_sample(f, a, b, 16)
    return _polish_newton(f, f_prime, guess, a, b, precision)


def compute_sturm(f_expr, precision=DEFAULT_PRECISION):
    if precision <= 0:
        raise ValueError("精度必须为正数")
    steps = []
    warnings = []

    poly = sp.Poly(f_expr, X)
    if poly.degree() == 0 and poly.LC() == 0:
        raise ValueError(ZERO_POLY_MSG)

    f = sp.expand(f_expr)
    f_prime = sp.expand(sp.diff(f, X))
    gcd_ff = sp.expand(sp.gcd(f, f_prime))
    has_multiple = sp.Poly(gcd_ff, X).degree() > 0

    steps.append({
        "title": "多项式与导数",
        "content": f"f(x) = {poly_to_str(f)}, f'(x) = {poly_to_str(f_prime)}",
        "latex": f"f(x)={poly_to_latex(f)},\\quad f'(x)={poly_to_latex(f_prime)}",
    })

    work_f = f
    if has_multiple:
        squarefree = sp.expand(sp.div(f, gcd_ff)[0])
        warnings.append("多项式存在重根，使用 square-free 部分继续 Sturm 分析")
        work_f = squarefree
        steps.append({
            "title": "重根判别",
            "content": f"gcd(f, f')={poly_to_str(gcd_ff)}，存在重根。square-free: {poly_to_str(squarefree)}",
            "latex": f"\\gcd(f,f')={latex_expr(gcd_ff)} \\neq 1,\\quad f_{{\\mathrm{{sf}}}}={poly_to_latex(squarefree)}",
        })
    else:
        steps.append({
            "title": "重根判别",
            "content": "gcd(f, f')=1，无重根",
            "latex": "\\gcd(f,f')=1",
        })

    sequence = _build_sturm_sequence(work_f)
    seq_strs = [poly_to_str(g) for g in sequence]
    seq_latex = [poly_to_latex(g) for g in sequence]
    steps.append({
        "title": "Sturm 序列",
        "content": ", ".join(f"g{i}={s}" for i, s in enumerate(seq_strs)),
        "latex": ",\\quad ".join(f"g_{{{i}}}={l}" for i, l in enumerate(seq_latex)),
    })

    L, R = _real_root_bounds(work_f)
    steps.append({
        "title": "实根界",
        "content": f"正根上界 R={R:.6g}，负根下界 L={L:.6g}，所有实根在 [{L:.6g}, {R:.6g}] 内",
        "latex": f"L={L},\\quad R={R}",
    })

    intervals = []
    _isolate_roots(work_f, sequence, L, R, intervals, steps)
    intervals = _dedupe_intervals(intervals)

    bracket_width = max(precision * 4, 0.25)
    tightened = []
    for lo, hi in intervals:
        if abs(lo - hi) < 1e-14:
            tightened.append([lo, hi])
        else:
            rlo, rhi = _refine_interval(work_f, sequence, lo, hi, bracket_width)
            tightened.append([rlo, rhi])
    intervals = tightened

    approx_roots = []
    for lo, hi in intervals:
        if abs(lo - hi) < 1e-14:
            root = lo
        else:
            root = _bisect_root(work_f, lo, hi, precision)
        approx_roots.append({
            "interval": [format_number(lo), format_number(hi)],
            "approx_root": format_number(root),
            "precision": format_number(precision),
        })

    steps.append({
        "title": "近似求根",
        "content": f"使用二分法，精度 ε = {precision}",
        "latex": f"\\text{{二分法精度}}\\ \\varepsilon = {precision}",
    })

    return {
        "polynomial": poly_to_str(f),
        "derivative": poly_to_str(f_prime),
        "gcd_f_fprime": poly_to_str(gcd_ff),
        "has_multiple_roots": has_multiple,
        "squarefree_polynomial": poly_to_str(work_f) if has_multiple else None,
        "sturm_sequence": seq_strs,
        "sturm_sequence_latex": seq_latex,
        "precision": format_number(precision),
        "root_bounds": {"L": format_number(L), "R": format_number(R)},
        "isolated_intervals": [[format_number(a), format_number(b)] for a, b in intervals],
        "approx_roots": approx_roots,
    }, steps, warnings

"""Matrix basic properties computation."""

import numpy as np
import sympy as sp



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
        diag_tex = "\\text{是}" if is_diag else "\\text{否}"
        steps.append({
            "title": "可对角化判定",
            "content": reason,
            "latex": f"\\text{{可对角化：}}{diag_tex}",
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

"""Matrix decomposition services."""



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

"""Jordan normal form via nilpotent matrix method."""


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

"""Lambda-matrix method and Smith normal form."""


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


# ---------------------------------------------------------------------------
# 内置样例数据（无需外部 JSON）
# ---------------------------------------------------------------------------

SAMPLE_POLYNOMIALS = {
    "poly_001": {"name": "三次无重根多项式", "polynomial": "x^3 - 2*x + 1"},
    "poly_002": {"name": "三次有重根多项式", "polynomial": "x^3 - 3*x^2 + 3*x - 1"},
}

SAMPLE_MATRICES = {
    "square_001": {
        "name": "三阶可逆矩阵",
        "matrix": [[1, 2, 0], [0, 1, 3], [2, 0, 1]],
    },
    "square_004": {
        "name": "三阶不可对角化矩阵",
        "matrix": [[2, 1, 0], [0, 2, 1], [0, 0, 2]],
    },
    "square_007": {
        "name": "三阶幂零矩阵",
        "matrix": [[0, 1, 0], [0, 0, 1], [0, 0, 0]],
    },
    "square_009": {
        "name": "两个 Jordan 块",
        "matrix": [[2, 1, 0, 0], [0, 2, 0, 0], [0, 0, 3, 1], [0, 0, 0, 3]],
    },
    "rect_001": {
        "name": "3×4 行满秩矩阵",
        "matrix": [[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3]],
    },
    "rect_002": {
        "name": "4×3 列满秩矩阵",
        "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]],
    },
}


def get_polynomial(poly_id: str) -> dict:
    if poly_id not in SAMPLE_POLYNOMIALS:
        raise KeyError(f"未知多项式: {poly_id}")
    return {"id": poly_id, **SAMPLE_POLYNOMIALS[poly_id]}


def get_matrix(matrix_id: str) -> dict:
    if matrix_id not in SAMPLE_MATRICES:
        raise KeyError(f"未知矩阵: {matrix_id}")
    return {"id": matrix_id, **SAMPLE_MATRICES[matrix_id]}


# =============================================================================
# 报告生成与主入口
# =============================================================================

TXT_PATH = HERE / "线性代数计算报告.txt"

PRECISION = 0.01


def matrix_as_floats(mat) -> list[list[float]]:
    """SymPy 矩阵转纯 float 列表，避免 SciPy SVD 类型错误。"""
    return [[float(x) for x in row] for row in mat.tolist()]


def format_value_plain(val: Any) -> str:
    """将数值格式化为纯文本（含复数）。"""
    if isinstance(val, dict) and "re" in val and "im" in val:
        re, im = val["re"], val["im"]
        if abs(im) < 1e-9:
            return str(re)
        sign = "+" if im >= 0 else "-"
        return f"{re} {sign} {abs(im)}i"
    if isinstance(val, (list, tuple)):
        return str(val)
    return str(val)


# ---------------------------------------------------------------------------
# 报告数据结构
# ---------------------------------------------------------------------------

class ReportSection:
    def __init__(self, title: str, subtitle: str = "", subtitle_latex: str = ""):
        self.title = title
        self.subtitle = subtitle
        self.subtitle_latex = subtitle_latex
        self.steps: list[dict[str, str]] = []
        self.summary_items: list[dict[str, str]] = []
        self.warnings: list[str] = []
        self.error: str | None = None

    def add_step(self, step: dict) -> None:
        self.steps.append(step)

    def add_summary(self, text: str, latex: str = "") -> None:
        self.summary_items.append({"text": text, "latex": latex})


def run_all_computations() -> list[ReportSection]:
    sections: list[ReportSection] = []

    # ---- 1. Sturm 序列 ----
    for poly_id in ("poly_001", "poly_002"):
        item = get_polynomial(poly_id)
        expr = parse_polynomial(item["polynomial"])
        poly_latex = poly_to_latex(expr)
        sec = ReportSection(
            "Sturm 序列与求根",
            item["name"],
            subtitle_latex=poly_latex,
        )
        try:
            result, steps, warnings = compute_sturm(expr, precision=PRECISION)
            sec.warnings.extend(warnings)
            for st in steps:
                sec.add_step(st)
            sec.add_summary(f"多项式: {result['polynomial']}", latex=f"f(x)={poly_latex}")
            sec.add_summary(f"实根区间: {result['isolated_intervals']}")
            for r in result["approx_roots"]:
                sec.add_summary(
                    f"近似根 {r['approx_root']}（区间 {r['interval'][0]} ~ {r['interval'][1]}）"
                )
        except Exception as exc:
            sec.error = str(exc)
        sections.append(sec)

    # ---- 2. 矩阵性质 ----
    for matrix_id, label in (
        ("square_001", "三阶可逆方阵"),
        ("square_004", "三阶不可对角化方阵"),
        ("rect_001", "3×4 行满秩矩阵"),
    ):
        item = get_matrix(matrix_id)
        sec = ReportSection("矩阵基本性质", f"{item['name']} — {label}")
        try:
            mat = parse_matrix(item["matrix"])
            result, steps, warnings = compute_properties(mat.tolist())
            sec.warnings.extend(warnings)
            for st in steps:
                sec.add_step(st)
            sec.add_summary(f"尺寸: {result['rows']}×{result['cols']}, 秩: {result['rank']}")
            if result.get("is_square"):
                sec.add_summary(
                    f"行列式: {result.get('det')}, 迹: {result.get('trace')}",
                    latex=f"\\det(A)={result.get('det_latex', result.get('det'))},\\ "
                    f"\\mathrm{{tr}}(A)={result.get('trace_latex', result.get('trace'))}",
                )
                sec.add_summary(f"可逆: {result.get('is_invertible')}, 可对角化: {result.get('is_diagonalizable')}")
                if result.get("characteristic_polynomial_latex"):
                    sec.add_summary(
                        f"特征多项式: {result.get('characteristic_polynomial')}",
                        latex=result["characteristic_polynomial_latex"],
                    )
                if result.get("eigenvalues"):
                    for ev in result["eigenvalues"]:
                        sec.add_summary(
                            f"特征值 {format_value_plain(ev['eigenvalue'])}: "
                            f"代数重数 {ev['algebraic_multiplicity']}, "
                            f"几何重数 {ev['geometric_multiplicity']}",
                            latex=(
                                f"\\lambda={ev.get('eigenvalue_latex', ev['eigenvalue'])}:\\ "
                                f"n_a={ev['algebraic_multiplicity']},\\ "
                                f"n_g={ev['geometric_multiplicity']}"
                            ),
                        )
            else:
                sec.add_summary(f"有左逆: {result.get('has_left_inverse')}, 有右逆: {result.get('has_right_inverse')}")
        except Exception as exc:
            sec.error = str(exc)
        sections.append(sec)

    # ---- 3. 矩阵分解 ----
    decomp_jobs = [
        ("满秩分解 A=BC", full_rank_decomposition, "rect_002", False),
        ("LU / PLU 分解", lu_decomposition, "square_001", False),
        ("LDU 分解", ldu_decomposition, "square_001", False),
        ("SVD 分解", svd_decomposition, "square_001", True),
    ]
    for title, fn, matrix_id, has_warn in decomp_jobs:
        item = get_matrix(matrix_id)
        sec = ReportSection("矩阵分解", f"{title} — {item['name']}")
        try:
            mat = parse_matrix(item["matrix"])
            data = matrix_as_floats(mat) if has_warn else mat.tolist()
            if has_warn:
                result, steps, warnings = fn(data)
                sec.warnings.extend(warnings)
            else:
                result, steps = fn(data)
            for st in steps:
                sec.add_step(st)
            if title.startswith("满秩"):
                sec.add_summary(f"秩: {result['rank']}, 验证误差: {result['verification_error']}")
            elif title.startswith("SVD"):
                sec.add_summary(f"奇异值: {result['singular_values']}")
                sec.add_summary(f"Frobenius 误差: {result['verification_error']}")
            elif title.startswith("LDU"):
                if result.get("success"):
                    sec.add_summary(f"LDU 分解成功, 验证误差: {result['verification_error']}")
                else:
                    sec.add_summary(f"LDU 分解失败: {result.get('reason')}")
            else:
                kind = "PLU" if result.get("needs_permutation") else "LU"
                sec.add_summary(f"{kind} 分解, 验证误差: {result['verification_error']}")
        except Exception as exc:
            sec.error = str(exc)
        sections.append(sec)

    # ---- 4. Jordan 标准型 ----
    for matrix_id in ("square_004", "square_009"):
        item = get_matrix(matrix_id)
        sec = ReportSection("Jordan 标准型", item["name"])
        try:
            mat = parse_matrix(item["matrix"])
            result, steps, warnings = compute_jordan(mat.tolist())
            sec.warnings.extend(warnings)
            for st in steps:
                sec.add_step(st)
            sec.add_summary(f"特征多项式: {result['characteristic_polynomial']}",
                            latex=result.get("characteristic_polynomial_latex", ""))
            for ev in result["eigenvalues"]:
                sec.add_summary(
                    f"特征值 {format_value_plain(ev['eigenvalue'])}: "
                    f"代数重数={ev['algebraic_multiplicity']}, "
                    f"几何重数={ev['geometric_multiplicity']}, "
                    f"幂零指数={ev['nilpotent_index']}",
                    latex=(
                        f"\\lambda={ev.get('eigenvalue_latex', ev['eigenvalue'])}:\\ "
                        f"n_a={ev['algebraic_multiplicity']},\\ "
                        f"n_g={ev['geometric_multiplicity']},\\ "
                        f"t={ev['nilpotent_index']}"
                    ),
                )
            sec.add_summary(f"P⁻¹AP=J 验证误差: {result['verification_error']}")
        except Exception as exc:
            sec.error = str(exc)
        sections.append(sec)

    # ---- 5. λ-矩阵法 ----
    for matrix_id in ("square_004", "square_007"):
        item = get_matrix(matrix_id)
        sec = ReportSection("λ-矩阵法（Smith 标准型）", item["name"])
        try:
            mat = parse_matrix(item["matrix"])
            result, steps, warnings = compute_lambda_smith(mat.tolist())
            sec.warnings.extend(warnings)
            for st in steps:
                sec.add_step(st)
            inv_latex = ",\\quad ".join(result.get("invariant_factors_latex", []))
            sec.add_summary(f"不变因子: {result['invariant_factors']}", latex=inv_latex)
            elem_latex = ",\\quad ".join(e["factor_latex"] for e in result["elementary_divisors"])
            sec.add_summary(
                f"初等因子: {[e['factor'] for e in result['elementary_divisors']]}",
                latex=elem_latex or "1",
            )
            sec.add_summary(
                f"最小多项式: {result['minimal_polynomial']}",
                latex=result.get("minimal_polynomial_latex", ""),
            )
            sec.add_summary(f"可对角化: {result['is_diagonalizable']}")
        except Exception as exc:
            sec.error = str(exc)
        sections.append(sec)

    return sections


# ---------------------------------------------------------------------------
# 文本报告（简洁，避免复杂公式）
# ---------------------------------------------------------------------------

def _matrix_to_plain(rows: list[list[Any]], indent: str = "  ") -> str:
    lines = []
    for row in rows:
        cells = ", ".join(str(c) for c in row)
        lines.append(f"{indent}[{cells}]")
    return "\n".join(lines)


def _sanitize_text(s: str) -> str:
    """去掉 LaTeX 命令，保留可读文字与数字。"""
    if not s:
        return ""
    out = s
    for token in ("\\lambda", "\\det", "\\gcd", "\\text", "\\mathrm", "\\operatorname"):
        out = out.replace(token, "")
    out = out.replace("{", "").replace("}", "").replace("$", "")
    out = out.replace("\\\\", " ").replace("\\", "")
    return " ".join(out.split())


def write_txt_report(sections: list[ReportSection]) -> None:
    lines: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("线性代数编程作业 — 计算报告（简洁版）")
    lines.append(f"生成时间: {now}")
    lines.append("说明: 本文件为纯文本摘要，复杂公式已转为数值或文字描述。")
    lines.append("=" * 72)

    for idx, sec in enumerate(sections, 1):
        lines.append("")
        lines.append(f"[{idx}] {sec.title}")
        if sec.subtitle:
            lines.append(f"    样例: {sec.subtitle}")
        lines.append("-" * 72)

        if sec.error:
            lines.append(f"  [错误] {sec.error}")
            continue

        if sec.summary_items:
            lines.append("  【结果摘要】")
            for item in sec.summary_items:
                lines.append(f"    · {item['text']}")

        if sec.steps:
            lines.append("  【计算步骤】")
            for i, st in enumerate(sec.steps, 1):
                title = st.get("title", f"步骤 {i}")
                content = _sanitize_text(st.get("content", ""))
                lines.append(f"    {i}. {title}")
                if content:
                    wrapped = textwrap.fill(content, width=64, initial_indent="       ", subsequent_indent="       ")
                    lines.append(wrapped)

        if sec.warnings:
            lines.append("  【提示】")
            for w in sec.warnings:
                lines.append(f"    ! {w}")

    lines.append("")
    lines.append("=" * 72)
    lines.append("报告结束")

    TXT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 60)
    print("线性代数编程作业 — 一键运行全部功能")
    print("=" * 60)

    try:
        print("\n[1/2] 正在执行全部计算模块...")
        sections = run_all_computations()
        ok = sum(1 for s in sections if not s.error)
        print(f"      完成 {len(sections)} 项任务，成功 {ok} 项，失败 {len(sections) - ok} 项")

        print("\n[2/2] 正在生成文本报告...")
        write_txt_report(sections)
        print(f"      已写入: {TXT_PATH}")
        print("      正在打开 TXT…")
        open_txt(TXT_PATH)

        print("\n" + "=" * 60)
        print("全部完成！输出文件位于:")
        print(f"  · {TXT_PATH.name}")
        print("=" * 60)
        return 0

    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

