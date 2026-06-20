"""Sturm sequence and root finding service."""

import sympy as sp

from app.utils.parser import X
from app.utils.formatter import format_number, poly_to_str, poly_to_latex
from app.utils.latex import latex_expr
from app.utils.errors import ZERO_POLY_MSG

PRECISION = 1e-8
ROOT_TOL = 1e-10
INTERIOR_OFFSET = 1e-8


def _fval(f, x):
    return float(sp.N(f.subs(X, x), 15))


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
    return [float(sp.N(g.subs(X, c), 15)) for g in sequence]


def _cauchy_bound(f):
    poly = sp.Poly(f, X)
    an = poly.LC()
    coeffs = [abs(float(c / an)) for c in poly.all_coeffs()[:-1]]
    B = 1 + max(coeffs) if coeffs else 1
    # Slightly pad so real roots lying exactly on the Cauchy circle are interior.
    pad = max(1e-4, 1e-9 * B)
    return -B - pad, B + pad


def _count_roots_in_interval(sequence, a, b):
    va = _sign_variations(_eval_sturm(sequence, a))
    vb = _sign_variations(_eval_sturm(sequence, b))
    return va - vb, va, vb


def _dedupe_intervals(intervals):
    """Merge isolation intervals that refer to the same root."""
    by_center = {}
    for lo, hi in intervals:
        center = (lo + hi) / 2
        key = round(center, 8)
        if key not in by_center:
            by_center[key] = [lo, hi]
    return [by_center[k] for k in sorted(by_center)]


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


def _bisect_root(f, left, right):
    a, b = left, right
    if abs(a - b) < PRECISION:
        return (a + b) / 2
    fa = float(sp.N(f.subs(X, a), 15))
    fb = float(sp.N(f.subs(X, b), 15))
    if fa * fb > 0:
        return (a + b) / 2
    while b - a > PRECISION:
        mid = (a + b) / 2
        fm = float(sp.N(f.subs(X, mid), 15))
        if abs(fm) < PRECISION:
            return mid
        if fa * fm <= 0:
            b = mid
        else:
            a = mid
            fa = fm
    return (a + b) / 2


def compute_sturm(f_expr):
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

    L, R = _cauchy_bound(work_f)
    steps.append({
        "title": "Cauchy 根界",
        "content": f"所有实根在 [{L:.6g}, {R:.6g}] 内",
        "latex": f"L={L},\\quad R={R}",
    })

    intervals = []
    _isolate_roots(work_f, sequence, L, R, intervals, steps)
    intervals = _dedupe_intervals(intervals)

    approx_roots = []
    for lo, hi in intervals:
        if abs(lo - hi) < 1e-14:
            root = lo
        else:
            root = _bisect_root(work_f, lo, hi)
        approx_roots.append({
            "interval": [format_number(lo), format_number(hi)],
            "approx_root": format_number(root),
            "precision": PRECISION,
        })

    steps.append({
        "title": "近似求根",
        "content": f"使用二分法，精度 {PRECISION}",
    })

    return {
        "polynomial": poly_to_str(f),
        "derivative": poly_to_str(f_prime),
        "gcd_f_fprime": poly_to_str(gcd_ff),
        "has_multiple_roots": has_multiple,
        "squarefree_polynomial": poly_to_str(work_f) if has_multiple else None,
        "sturm_sequence": seq_strs,
        "sturm_sequence_latex": seq_latex,
        "root_bounds": {"L": format_number(L), "R": format_number(R)},
        "isolated_intervals": [[format_number(a), format_number(b)] for a, b in intervals],
        "approx_roots": approx_roots,
    }, steps, warnings
