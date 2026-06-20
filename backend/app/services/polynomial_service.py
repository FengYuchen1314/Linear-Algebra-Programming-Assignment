"""Sturm sequence and root finding service."""

import sympy as sp

from app.utils.parser import X
from app.utils.formatter import format_number, poly_to_str, poly_to_latex
from app.utils.latex import latex_expr
from app.utils.errors import ZERO_POLY_MSG

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
