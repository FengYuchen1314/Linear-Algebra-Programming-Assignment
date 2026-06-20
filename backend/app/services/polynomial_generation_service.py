"""DeepSeek API polynomial generation."""

import json
import os
import re

import httpx
import sympy as sp

from app.utils.parser import X, detect_complex_polynomial_requirement
from app.utils.validator import validate_polynomial_expr
from app.utils.errors import COMPLEX_POLY_MSG

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def _build_prompt(requirement):
    return f"""Generate a real-coefficient polynomial in variable x based on this requirement:
"{requirement}"

Rules:
- Use integer coefficients when possible
- Degree between 3 and 8 (default 3-6 if not specified)
- Variable must be x only
- Real coefficients only, no complex coefficients

Return ONLY valid JSON (no markdown):
{{"polynomial": "x^3 - 2*x + 1", "description": "brief Chinese description", "degree": 3}}"""


def _check_requirement(expr, requirement):
    """Basic semantic checks on generated polynomial."""
    req = requirement.lower()
    poly = sp.Poly(expr, X)
    degree = poly.degree()
    warnings = []

    deg_match = re.search(r"(\d+)\s*次", requirement)
    if deg_match:
        expected = int(deg_match.group(1))
        if degree != expected:
            return False, f"次数应为 {expected}，实际为 {degree}"

    if "重根" in requirement and "无重根" not in requirement and "没有重根" not in requirement:
        d = sp.gcd(poly.as_expr(), sp.diff(poly.as_expr(), X))
        if sp.degree(d, X) == 0:
            return False, "要求有重根但生成的多项式无重根"

    if "无重根" in requirement or "没有重根" in requirement or "不同实根" in requirement:
        d = sp.gcd(poly.as_expr(), sp.diff(poly.as_expr(), X))
        if sp.degree(d, X) > 0:
            return False, "要求无重根但生成的多项式有重根"

    if "只有一个实根" in requirement or "一个实根" in requirement:
        real_roots = sp.real_roots(poly.as_expr(), X)
        if len(real_roots) != 1:
            return False, f"要求只有一个实根，实际有 {len(real_roots)} 个"

    if "整系数" in requirement:
        for c in poly.all_coeffs():
            if not c.is_integer:
                warnings.append("未完全满足整系数要求")

    return True, warnings


async def _call_deepseek(prompt):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("未配置 DEEPSEEK_API_KEY 环境变量")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            DEEPSEEK_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)


async def generate_polynomial(requirement):
    if detect_complex_polynomial_requirement(requirement):
        return {"success": False, "errors": [COMPLEX_POLY_MSG]}

    last_error = None
    for attempt in range(2):
        try:
            raw = await _call_deepseek(_build_prompt(requirement))
            poly_str = raw.get("polynomial", "")
            expr, val_warnings = validate_polynomial_expr(poly_str)
            ok, check_result = _check_requirement(expr, requirement)
            warnings = list(val_warnings)
            if not ok:
                last_error = check_result
                continue
            if isinstance(check_result, list):
                warnings.extend(check_result)
            return {
                "success": True,
                "polynomial": str(sp.expand(expr)),
                "description": raw.get("description", ""),
                "warnings": warnings,
            }
        except json.JSONDecodeError as e:
            last_error = f"DeepSeek 返回非 JSON 格式: {e}"
        except Exception as e:
            last_error = str(e)

    return {"success": False, "errors": [last_error or "生成多项式失败"]}
