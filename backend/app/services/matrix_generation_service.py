"""DeepSeek API matrix generation."""

import json
import os
import re

import httpx
import numpy as np
import sympy as sp

from app.utils.parser import detect_complex_matrix_requirement
from app.utils.validator import validate_matrix_data
from app.utils.errors import COMPLEX_MATRIX_MSG

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def _build_prompt(requirement, matrix_type):
    type_hint = ""
    if matrix_type == "square":
        type_hint = "Must be a square matrix, size 3-6."
    elif matrix_type == "rectangular":
        type_hint = "Must be a non-square matrix, both dimensions 3-6."
    else:
        type_hint = "Square (3-6) or rectangular (both dims 3-6)."

    return f"""Generate a real matrix based on this requirement:
"{requirement}"

{type_hint}

Rules:
- Real numbers only, use integers or simple fractions
- Max dimension 6
- Return ONLY valid JSON (no markdown):
{{"matrix": [[1,2],[3,4]], "description": "brief Chinese description", "rows": 2, "cols": 2}}"""


def _check_matrix_requirement(arr, requirement):
    req = requirement
    warnings = []
    m, n = arr.shape
    sm = sp.Matrix(arr.tolist())

    if "方阵" in req or "n阶" in req or re.search(r"\d+\s*阶", req):
        if m != n:
            return False, "要求方阵但生成了非方阵"

    if "非方阵" in req and m == n:
        return False, "要求非方阵但生成了方阵"

    if "不可逆" in req or "奇异" in req:
        if m == n and abs(np.linalg.det(arr)) > 1e-10:
            return False, "要求不可逆矩阵但生成的矩阵可逆"

    if "可逆" in req and "不可逆" not in req:
        if m == n and abs(np.linalg.det(arr)) < 1e-10:
            return False, "要求可逆矩阵但生成的矩阵不可逆"

    if "满秩" in req:
        rank = np.linalg.matrix_rank(arr)
        if "行满秩" in req and rank != m:
            return False, f"要求行满秩但 rank={rank}, rows={m}"
        if "列满秩" in req and rank != n:
            return False, f"要求列满秩但 rank={rank}, cols={n}"
        if "行满秩" not in req and "列满秩" not in req and rank != min(m, n):
            return False, f"要求满秩但 rank={rank}"

    if "可对角化" in req and "不可" not in req and m == n:
        try:
            if not sm.is_diagonalizable(reals=False):
                return False, "要求可对角化但生成的矩阵不可对角化"
        except Exception:
            pass

    if "不可对角化" in req and m == n:
        try:
            if sm.is_diagonalizable(reals=False):
                return False, "要求不可对角化但生成的矩阵可对角化"
        except Exception:
            pass

    dim_match = re.search(r"(\d+)\s*[×x]\s*(\d+)", req)
    if dim_match:
        er, ec = int(dim_match.group(1)), int(dim_match.group(2))
        if (m, n) != (er, ec):
            return False, f"要求维度 {er}×{ec}，实际 {m}×{n}"

    order_match = re.search(r"(\d+)\s*阶", req)
    if order_match and "×" not in req:
        order = int(order_match.group(1))
        if m != order or n != order:
            return False, f"要求 {order} 阶矩阵，实际 {m}×{n}"

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


async def generate_matrix(requirement, matrix_type="auto"):
    if detect_complex_matrix_requirement(requirement):
        return {"success": False, "errors": [COMPLEX_MATRIX_MSG]}

    last_error = None
    for attempt in range(2):
        try:
            raw = await _call_deepseek(_build_prompt(requirement, matrix_type))
            matrix = raw.get("matrix", [])
            arr, val_warnings = validate_matrix_data(matrix)
            ok, check_result = _check_matrix_requirement(arr, requirement)
            warnings = list(val_warnings)
            if not ok:
                last_error = check_result
                continue
            if isinstance(check_result, list):
                warnings.extend(check_result)
            return {
                "success": True,
                "matrix": arr.tolist(),
                "description": raw.get("description", ""),
                "warnings": warnings,
            }
        except json.JSONDecodeError as e:
            last_error = f"DeepSeek 返回非 JSON 格式: {e}"
        except Exception as e:
            last_error = str(e)

    return {"success": False, "errors": [last_error or "生成矩阵失败"]}
