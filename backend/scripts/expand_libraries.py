#!/usr/bin/env python3
"""Generate and validate expanded polynomial / matrix libraries."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.utils.validator import validate_polynomial_expr, validate_matrix_data  # noqa: E402

DATA = ROOT / "app" / "data"

NEW_POLYNOMIALS = [
    {"id": "poly_013", "name": "一次多项式", "degree": 1, "polynomial": "x - 5", "tags": ["一次", "整系数", "单实根"], "description": "简单一次式，实根 x=5"},
    {"id": "poly_014", "name": "一次负斜率", "degree": 1, "polynomial": "-2*x + 7", "tags": ["一次", "整系数", "单实根"], "description": "实根 x=7/2"},
    {"id": "poly_015", "name": "二次两不同实根", "degree": 2, "polynomial": "x^2 - 1", "tags": ["二次", "整系数", "无重根", "全实根"], "description": "x^2-1=(x-1)(x+1)，两根 ±1"},
    {"id": "poly_016", "name": "二次无实根", "degree": 2, "polynomial": "x^2 + 1", "tags": ["二次", "整系数", "无实根"], "description": "判别式小于零，无实根"},
    {"id": "poly_017", "name": "二次二重实根", "degree": 2, "polynomial": "x^2 + 2*x + 1", "tags": ["二次", "整系数", "有重根"], "description": "(x+1)^2，重根 x=-1"},
    {"id": "poly_018", "name": "二次无理根", "degree": 2, "polynomial": "x^2 - 2", "tags": ["二次", "整系数", "无重根", "无理根"], "description": "两根 ±√2，适合 Sturm 隔离"},
    {"id": "poly_019", "name": "二次三系数", "degree": 2, "polynomial": "2*x^2 - 3*x + 1", "tags": ["二次", "整系数", "无重根", "全实根"], "description": "2(x-1/2)(x-1)，两根 1/2 与 1"},
    {"id": "poly_020", "name": "三次三不同实根", "degree": 3, "polynomial": "x^3 - 6*x^2 + 11*x - 6", "tags": ["三次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "(x-1)(x-2)(x-3)，三实根 1,2,3"},
    {"id": "poly_021", "name": "三次单位根", "degree": 3, "polynomial": "x^3 - 1", "tags": ["三次", "整系数", "单实根"], "description": "实根 x=1，另两根为复数"},
    {"id": "poly_022", "name": "三次三重负根", "degree": 3, "polynomial": "x^3 + 3*x^2 + 3*x + 1", "tags": ["三次", "整系数", "有重根"], "description": "(x+1)^3，三重根 x=-1"},
    {"id": "poly_023", "name": "三次一重二重混合", "degree": 3, "polynomial": "x^3 - x^2 - x + 1", "tags": ["三次", "整系数", "有重根", "多实根"], "description": "(x-1)^2(x+1)，根 1(二重) 与 -1"},
    {"id": "poly_024", "name": "三次卡丹诺型", "degree": 3, "polynomial": "x^3 - 7*x + 6", "tags": ["三次", "整系数", "无重根", "全实根"], "description": "(x-1)(x-2)(x+3)，三实根"},
    {"id": "poly_025", "name": "三次缺二次项", "degree": 3, "polynomial": "x^3 - 4*x", "tags": ["三次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "x(x-2)(x+2)，根 0,±2"},
    {"id": "poly_026", "name": "四次四不同实根", "degree": 4, "polynomial": "x**4 - 10*x**3 + 35*x**2 - 50*x + 24", "tags": ["四次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "(x-1)(x-2)(x-3)(x-4)，四实根"},
    {"id": "poly_027", "name": "四次单位根", "degree": 4, "polynomial": "x^4 - 1", "tags": ["四次", "整系数", "无重根", "全实根"], "description": "四实根 ±1（各二重？不，x^4-1=(x-1)(x+1)(x-i)(x+i) 仅 ±1 实根"},
    {"id": "poly_028", "name": "四次无实根", "degree": 4, "polynomial": "x^4 + 4", "tags": ["四次", "整系数", "无实根"], "description": "恒正，无实根"},
    {"id": "poly_029", "name": "四次二重实根对", "degree": 4, "polynomial": "x^4 - 2*x^2 + 1", "tags": ["四次", "整系数", "有重根"], "description": "(x^2-1)^2，±1 各二重"},
    {"id": "poly_030", "name": "四次两对实根", "degree": 4, "polynomial": "x^4 - 10*x^2 + 9", "tags": ["四次", "整系数", "无重根", "全实根"], "description": "(x^2-1)(x^2-9)，根 ±1,±3"},
    {"id": "poly_031", "name": "四次三实根含重根", "degree": 4, "polynomial": "x^4 - 3*x^3 + 2*x^2 + 3*x - 2", "tags": ["四次", "整系数", "有重根", "多实根"], "description": "含重根与单根的混合情形"},
    {"id": "poly_032", "name": "五次五实根", "degree": 5, "polynomial": "x^5 - 15*x^4 + 85*x^3 - 225*x^2 + 274*x - 120", "tags": ["五次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "(x-1)(x-2)(x-3)(x-4)(x-5)，五实根"},
    {"id": "poly_033", "name": "五次单位根", "degree": 5, "polynomial": "x^5 - 1", "tags": ["五次", "整系数", "单实根"], "description": "实根 x=1"},
    {"id": "poly_034", "name": "五次缺项", "degree": 5, "polynomial": "x^5 - 5*x^3 + 4*x", "tags": ["五次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "x(x^2-1)(x^2-4)，根 0,±1,±2"},
    {"id": "poly_035", "name": "五次有重根", "degree": 5, "polynomial": "x^5 - 5*x^4 + 10*x^3 - 10*x^2 + 5*x - 1", "tags": ["五次", "整系数", "有重根"], "description": "(x-1)^5，五重根"},
    {"id": "poly_036", "name": "六次六实根", "degree": 6, "polynomial": "x^6 - 15*x^5 + 85*x^4 - 225*x^3 + 274*x^2 - 120*x", "tags": ["六次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "x(x-1)(x-2)(x-3)(x-4)(x-5)，六实根含 0"},
    {"id": "poly_037", "name": "六次单位根", "degree": 6, "polynomial": "x^6 - 1", "tags": ["六次", "整系数", "无重根", "全实根"], "description": "实根 ±1"},
    {"id": "poly_038", "name": "六次三对重根", "degree": 6, "polynomial": "x^6 - 3*x^4 + 3*x^2 - 1", "tags": ["六次", "整系数", "有重根"], "description": "(x^2-1)^3，±1 各三重"},
    {"id": "poly_039", "name": "六次无实根", "degree": 6, "polynomial": "x^6 + x^2 + 1", "tags": ["六次", "整系数", "无实根"], "description": "恒正，无实根"},
    {"id": "poly_040", "name": "七次七实根", "degree": 7, "polynomial": "x^7 - 28*x^6 + 322*x^5 - 2240*x^4 + 9424*x^3 - 24976*x^2 + 38360*x - 25200", "tags": ["七次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "根 0,1,2,3,4,5,6 的乘积展开"},
    {"id": "poly_041", "name": "七次缺高次项", "degree": 7, "polynomial": "x^7 - 7*x^3 + 6*x", "tags": ["七次", "整系数", "适合Sturm", "全实根"], "description": "多实根，适合 Sturm 演示"},
    {"id": "poly_042", "name": "八次八实根", "degree": 8, "polynomial": "x^8 - 36*x^7 + 546*x^6 - 4536*x^5 + 22449*x^4 - 71280*x^3 + 140400*x^2 - 155520*x + 64800", "tags": ["八次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "根 0,1,…,7 的乘积展开"},
    {"id": "poly_043", "name": "八次对称型", "degree": 8, "polynomial": "x^8 - 5*x^4 + 4", "tags": ["八次", "整系数", "无重根", "全实根"], "description": "(x^2-1)(x^2-4)(x^2-9) 型，多实根"},
    {"id": "poly_044", "name": "Sturm根密集", "degree": 4, "polynomial": "x^4 - 4*x^3 + 6*x^2 - 4*x", "tags": ["四次", "整系数", "有重根", "适合Sturm"], "description": "x(x-2)^3，根 0 与 2(三重)"},
    {"id": "poly_045", "name": "Sturm正负交替", "degree": 5, "polynomial": "x^5 + x^4 - 6*x^3 - 4*x^2 + 8*x", "tags": ["五次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "多实根，符号变化明显"},
    {"id": "poly_046", "name": "gcd非平凡", "degree": 4, "polynomial": "x^4 - 5*x^2 + 4", "tags": ["四次", "整系数", "无重根", "全实根", "适合Sturm"], "description": "与 poly_004 相同经典例，四实根"},
    {"id": "poly_047", "name": "大系数三次", "degree": 3, "polynomial": "6*x^3 - 11*x^2 + 6*x - 1", "tags": ["三次", "整系数", "无重根", "全实根"], "description": "6(x-1/2)(x-1/3)(x-1)，三正有理根"},
    {"id": "poly_048", "name": "近零三重根", "degree": 4, "polynomial": "x^4 - 3*x^3 + 3*x^2 - x", "tags": ["四次", "整系数", "有重根"], "description": "x(x-1)^3，0 与 1(三重)"},
    {"id": "poly_049", "name": "六次Chebyshev型", "degree": 6, "polynomial": "64*x^6 - 192*x^4 + 180*x^2 - 31", "tags": ["六次", "整系数", "无重根", "全实根"], "description": "六实根，分布较均匀"},
    {"id": "poly_050", "name": "八次有重根", "degree": 8, "polynomial": "x^8 - 4*x^4 + 4", "tags": ["八次", "整系数", "有重根"], "description": "(x^4-2)^2，±√2 各二重"},
]

NEW_SQUARE = [
    {"id": "square_016", "name": "二阶单位阵", "type": "square", "rows": 2, "cols": 2, "matrix": [[1, 0], [0, 1]], "tags": ["方阵", "可逆", "二阶", "对角"], "description": "2×2 单位矩阵"},
    {"id": "square_017", "name": "二阶旋转45°", "type": "square", "rows": 2, "cols": 2, "matrix": [[0.7071, -0.7071], [0.7071, 0.7071]], "tags": ["方阵", "正交", "二阶"], "description": "平面旋转约 45°"},
    {"id": "square_018", "name": "二阶剪切", "type": "square", "rows": 2, "cols": 2, "matrix": [[1, 2], [0, 1]], "tags": ["方阵", "可逆", "二阶", "Jordan"], "description": "2 阶 Jordan 块 J_2(1)"},
    {"id": "square_019", "name": "二阶奇异", "type": "square", "rows": 2, "cols": 2, "matrix": [[1, 2], [2, 4]], "tags": ["方阵", "不可逆", "二阶"], "description": "秩 1，第二行为第一行两倍"},
    {"id": "square_020", "name": "二阶反对称", "type": "square", "rows": 2, "cols": 2, "matrix": [[0, 1], [-1, 0]], "tags": ["方阵", "正交", "二阶"], "description": "90° 旋转，A^T=-A"},
    {"id": "square_021", "name": "三阶伴随矩阵", "type": "square", "rows": 3, "cols": 3, "matrix": [[0, 0, 1], [1, 0, 0], [0, 1, 0]], "tags": ["方阵", "正交", "三阶", "置换"], "description": "循环置换矩阵，特征值为三次单位根"},
    {"id": "square_022", "name": "三阶Hilbert", "type": "square", "rows": 3, "cols": 3, "matrix": [[1, 0.5, 0.3333], [0.5, 0.3333, 0.25], [0.3333, 0.25, 0.2]], "tags": ["方阵", "对称", "三阶", "病态"], "description": "3 阶 Hilbert 矩阵，条件数大"},
    {"id": "square_023", "name": "三阶Companion", "type": "square", "rows": 3, "cols": 3, "matrix": [[0, 0, 1], [1, 0, -2], [0, 1, 1]], "tags": ["方阵", "可对角化", "三阶"], "description": "特征多项式 x^3-x^2-2x+1 的友矩阵"},
    {"id": "square_024", "name": "三阶下三角", "type": "square", "rows": 3, "cols": 3, "matrix": [[3, 0, 0], [1, 2, 0], [4, 5, 1]], "tags": ["方阵", "LU", "三阶", "可逆"], "description": "下三角可逆，LU 直接适用"},
    {"id": "square_025", "name": "三阶秩2", "type": "square", "rows": 3, "cols": 3, "matrix": [[1, 1, 1], [1, 1, 1], [2, 2, 2]], "tags": ["方阵", "不可逆", "三阶"], "description": "秩 1，三行成比例"},
    {"id": "square_026", "name": "三阶块对角", "type": "square", "rows": 3, "cols": 3, "matrix": [[2, 1, 0], [0, 2, 0], [0, 0, 5]], "tags": ["方阵", "Jordan", "三阶", "不可对角化"], "description": "J_2(2) 与标量块 5"},
    {"id": "square_027", "name": "三阶随机整数", "type": "square", "rows": 3, "cols": 3, "matrix": [[3, 1, 4], [1, 5, 9], [2, 6, 5]], "tags": ["方阵", "可逆", "三阶"], "description": "一般整系数可逆矩阵"},
    {"id": "square_028", "name": "四阶单位阵", "type": "square", "rows": 4, "cols": 4, "matrix": [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]], "tags": ["方阵", "可逆", "四阶", "对角"], "description": "4×4 单位矩阵"},
    {"id": "square_029", "name": "四阶Jordan大块", "type": "square", "rows": 4, "cols": 4, "matrix": [[5,1,0,0],[0,5,1,0],[0,0,5,1],[0,0,0,5]], "tags": ["方阵", "Jordan", "四阶", "不可对角化", "幂零"], "description": "单个 4 阶 Jordan 块 J_4(5)"},
    {"id": "square_030", "name": "四阶块对角Jordan", "type": "square", "rows": 4, "cols": 4, "matrix": [[1,1,0,0],[0,1,0,0],[0,0,2,1],[0,0,0,2]], "tags": ["方阵", "Jordan", "四阶"], "description": "J_2(1) 与 J_2(2)"},
    {"id": "square_031", "name": "四阶对称三对角", "type": "square", "rows": 4, "cols": 4, "matrix": [[2,1,0,0],[1,2,1,0],[0,1,2,1],[0,0,1,2]], "tags": ["方阵", "对称", "四阶", "可对角化"], "description": "三对角对称，特征值为 2+2cos(kπ/5)"},
    {"id": "square_032", "name": "四阶置换", "type": "square", "rows": 4, "cols": 4, "matrix": [[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,0]], "tags": ["方阵", "正交", "四阶"], "description": "4 循环置换矩阵"},
    {"id": "square_033", "name": "四阶奇异秩2", "type": "square", "rows": 4, "cols": 4, "matrix": [[1,0,1,0],[0,1,0,1],[1,0,1,0],[0,1,0,1]], "tags": ["方阵", "不可逆", "四阶"], "description": "秩 2，前两列重复"},
    {"id": "square_034", "name": "四阶LU友好", "type": "square", "rows": 4, "cols": 4, "matrix": [[2,1,0,0],[1,3,1,0],[0,1,4,1],[0,0,1,5]], "tags": ["方阵", "LU", "四阶", "对称", "可逆"], "description": "对称三对角，顺序主子式非零"},
    {"id": "square_035", "name": "四阶需PLU", "type": "square", "rows": 4, "cols": 4, "matrix": [[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]], "tags": ["方阵", "PLU", "四阶", "可逆"], "description": "首主元为零，需行交换"},
    {"id": "square_036", "name": "五阶对角", "type": "square", "rows": 5, "cols": 5, "matrix": [[-1,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,2,0],[0,0,0,0,3]], "tags": ["方阵", "可对角化", "五阶", "奇异"], "description": "对角阵含零特征值，不可逆"},
    {"id": "square_037", "name": "五阶Jordan双块", "type": "square", "rows": 5, "cols": 5, "matrix": [[2,1,0,0,0],[0,2,0,0,0],[0,0,3,1,0],[0,0,0,3,1],[0,0,0,0,3]], "tags": ["方阵", "Jordan", "五阶"], "description": "J_2(2) 与 J_3(3)"},
    {"id": "square_038", "name": "五阶循环矩阵", "type": "square", "rows": 5, "cols": 5, "matrix": [[1,1,0,0,0],[0,1,1,0,0],[0,0,1,1,0],[0,0,0,1,1],[1,0,0,0,1]], "tags": ["方阵", "可逆", "五阶"], "description": "循环结构，适合 λ-矩阵法"},
    {"id": "square_039", "name": "五阶Hilbert", "type": "square", "rows": 5, "cols": 5, "matrix": [[1,0.5,0.3333,0.25,0.2],[0.5,0.3333,0.25,0.2,0.1667],[0.3333,0.25,0.2,0.1667,0.1429],[0.25,0.2,0.1667,0.1429,0.125],[0.2,0.1667,0.1429,0.125,0.1111]], "tags": ["方阵", "对称", "五阶", "病态"], "description": "5 阶 Hilbert 矩阵"},
    {"id": "square_040", "name": "六阶单位阵", "type": "square", "rows": 6, "cols": 6, "matrix": [[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]], "tags": ["方阵", "可逆", "六阶", "对角"], "description": "6×6 单位矩阵"},
    {"id": "square_041", "name": "六阶Jordan", "type": "square", "rows": 6, "cols": 6, "matrix": [[0,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,0,0,0],[0,0,0,2,1,0],[0,0,0,0,2,1],[0,0,0,0,0,2]], "tags": ["方阵", "Jordan", "六阶"], "description": "J_3(0) 与 J_3(2) 块对角"},
    {"id": "square_042", "name": "六阶全1矩阵", "type": "square", "rows": 6, "cols": 6, "matrix": [[1]*6 for _ in range(6)], "tags": ["方阵", "不可逆", "六阶", "对称"], "description": "秩 1，最大特征值 6"},
    {"id": "square_043", "name": "三阶λ-矩阵经典", "type": "square", "rows": 3, "cols": 3, "matrix": [[4,1,0],[0,3,1],[0,0,2]], "tags": ["方阵", "λ-矩阵", "Jordan", "三阶", "可对角化"], "description": "上三角，三个不同特征值，Smith 型简单"},
    {"id": "square_044", "name": "三阶不可约Jordan", "type": "square", "rows": 3, "cols": 3, "matrix": [[1,1,0],[0,1,1],[0,0,1]], "tags": ["方阵", "λ-矩阵", "Jordan", "三阶", "不可对角化"], "description": "单一 J_3(1)，Smith 不变因子非线性"},
    {"id": "square_045", "name": "四阶SVD友好", "type": "square", "rows": 4, "cols": 4, "matrix": [[1,2,0,0],[2,1,0,0],[0,0,3,4],[0,0,4,3]], "tags": ["方阵", "对称", "四阶", "SVD", "可逆"], "description": "块对角对称，奇异值明显"},
    {"id": "square_046", "name": "二阶LDU", "type": "square", "rows": 2, "cols": 2, "matrix": [[4,2],[2,3]], "tags": ["方阵", "LDU", "对称", "二阶"], "description": "2×2 对称正定"},
    {"id": "square_047", "name": "四阶LDU对称", "type": "square", "rows": 4, "cols": 4, "matrix": [[4,1,0,0],[1,4,1,0],[0,1,4,1],[0,0,1,4]], "tags": ["方阵", "LDU", "对称", "四阶"], "description": "对称三对角正定"},
    {"id": "square_048", "name": "三阶负对角", "type": "square", "rows": 3, "cols": 3, "matrix": [[-1,0,0],[0,-2,0],[0,0,-3]], "tags": ["方阵", "可对角化", "三阶", "对角"], "description": "负特征值对角阵"},
    {"id": "square_049", "name": "四阶幂零", "type": "square", "rows": 4, "cols": 4, "matrix": [[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,0,0]], "tags": ["方阵", "幂零", "Jordan", "四阶"], "description": "4 阶幂零 Jordan 块"},
    {"id": "square_050", "name": "五阶三Jordan块", "type": "square", "rows": 5, "cols": 5, "matrix": [[1,1,0,0,0],[0,1,0,0,0],[0,0,2,0,0],[0,0,0,3,1],[0,0,0,0,3]], "tags": ["方阵", "Jordan", "五阶"], "description": "J_2(1), 标量 2, J_2(3)"},
]

NEW_RECT = [
    {"id": "rect_011", "name": "2×3 列满秩", "type": "rectangular", "rows": 2, "cols": 3, "matrix": [[1,0,0],[0,1,0]], "tags": ["非方阵", "列满秩", "2×3"], "description": "秩 2，有左逆"},
    {"id": "rect_012", "name": "3×2 行满秩", "type": "rectangular", "rows": 3, "cols": 2, "matrix": [[1,0],[0,1],[0,0]], "tags": ["非方阵", "行满秩", "3×2"], "description": "秩 2，有右逆"},
    {"id": "rect_013", "name": "2×2 嵌入2×4", "type": "rectangular", "rows": 2, "cols": 4, "matrix": [[1,2,0,0],[3,4,0,0]], "tags": ["非方阵", "行满秩", "2×4", "满秩分解"], "description": "秩 2，适合满秩分解"},
    {"id": "rect_014", "name": "4×2 满秩分解", "type": "rectangular", "rows": 4, "cols": 2, "matrix": [[1,0],[0,1],[1,1],[2,1]], "tags": ["非方阵", "列满秩", "4×2", "满秩分解"], "description": "秩 2，A=BC 演示"},
    {"id": "rect_015", "name": "3×6 行满秩", "type": "rectangular", "rows": 3, "cols": 6, "matrix": [[1,0,0,1,0,0],[0,1,0,0,1,0],[0,0,1,0,0,1]], "tags": ["非方阵", "行满秩", "3×6"], "description": "秩 3，宽矩阵有右逆"},
    {"id": "rect_016", "name": "6×3  tall列满秩", "type": "rectangular", "rows": 6, "cols": 3, "matrix": [[1,0,0],[0,1,0],[0,0,1],[2,0,0],[0,2,0],[0,0,2]], "tags": ["非方阵", "列满秩", "6×3"], "description": "高瘦矩阵，有左逆"},
    {"id": "rect_017", "name": "4×5 SVD", "type": "rectangular", "rows": 4, "cols": 5, "matrix": [[1,0,0,0,0],[0,2,0,0,0],[0,0,3,0,0],[0,0,0,4,0]], "tags": ["非方阵", "SVD", "4×5", "行满秩"], "description": "对角型嵌入，奇异值 1,2,3,4"},
    {"id": "rect_018", "name": "5×4 SVD", "type": "rectangular", "rows": 5, "cols": 4, "matrix": [[1,0,0,0],[0,2,0,0],[0,0,3,0],[0,0,0,4],[0,0,0,0]], "tags": ["非方阵", "SVD", "5×4", "列满秩"], "description": "秩 4 列满秩"},
    {"id": "rect_019", "name": "3×3 秩1", "type": "rectangular", "rows": 3, "cols": 3, "matrix": [[1,1,1],[2,2,2],[3,3,3]], "tags": ["非方阵", "不满秩", "3×3"], "description": "秩 1，各行成比例"},
    {"id": "rect_020", "name": "2×6 秩2", "type": "rectangular", "rows": 2, "cols": 6, "matrix": [[1,2,3,4,5,6],[2,4,6,8,10,12]], "tags": ["非方阵", "不满秩", "2×6"], "description": "秩 1 宽矩阵"},
    {"id": "rect_021", "name": "6×2 秩2", "type": "rectangular", "rows": 6, "cols": 2, "matrix": [[1,0],[2,0],[3,0],[0,1],[0,2],[0,3]], "tags": ["非方阵", "列满秩", "6×2", "满秩分解"], "description": "两列独立，适合满秩分解"},
    {"id": "rect_022", "name": "4×6 秩3", "type": "rectangular", "rows": 4, "cols": 6, "matrix": [[1,0,0,1,0,0],[0,1,0,0,1,0],[0,0,1,0,0,1],[1,1,1,0,0,0]], "tags": ["非方阵", "满秩分解", "4×6"], "description": "秩 3，适合 A=BC"},
    {"id": "rect_023", "name": "5×5 置换块", "type": "rectangular", "rows": 5, "cols": 5, "matrix": [[0,1,0,0,0],[1,0,0,0,0],[0,0,1,0,0],[0,0,0,0,1],[0,0,0,1,0]], "tags": ["非方阵", "可逆", "5×5", "SVD"], "description": "块置换，可逆方阵型"},
    {"id": "rect_024", "name": "3×4 整数满秩", "type": "rectangular", "rows": 3, "cols": 4, "matrix": [[1,2,3,4],[0,1,2,3],[0,0,1,2]], "tags": ["非方阵", "行满秩", "3×4", "LU"], "description": "上梯形，秩 3"},
    {"id": "rect_025", "name": "4×3 下梯形", "type": "rectangular", "rows": 4, "cols": 3, "matrix": [[1,0,0],[2,1,0],[3,2,1],[4,3,2]], "tags": ["非方阵", "列满秩", "4×3"], "description": "列满秩下梯形"},
    {"id": "rect_026", "name": "6×4 不满秩", "type": "rectangular", "rows": 6, "cols": 4, "matrix": [[1,0,1,0],[0,1,0,1],[1,0,1,0],[0,1,0,1],[1,0,1,0],[0,1,0,1]], "tags": ["非方阵", "不满秩", "6×4"], "description": "秩 2，列重复"},
    {"id": "rect_027", "name": "2×5 行满秩", "type": "rectangular", "rows": 2, "cols": 5, "matrix": [[1,0,0,0,0],[0,1,0,0,0]], "tags": ["非方阵", "行满秩", "2×5"], "description": "最宽行满秩，秩 2"},
    {"id": "rect_028", "name": "5×2 列满秩", "type": "rectangular", "rows": 5, "cols": 2, "matrix": [[1,0],[0,1],[1,1],[2,1],[1,2]], "tags": ["非方阵", "列满秩", "5×2"], "description": "最瘦列满秩，秩 2"},
    {"id": "rect_029", "name": "6×6 Hilbert长", "type": "rectangular", "rows": 6, "cols": 6, "matrix": [[1/(i+j+1) for j in range(6)] for i in range(6)], "tags": ["非方阵", "对称", "6×6", "病态", "SVD"], "description": "6×6 Hilbert，条件数极大"},
    {"id": "rect_030", "name": "4×4 反对角", "type": "rectangular", "rows": 4, "cols": 4, "matrix": [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]], "tags": ["非方阵", "可逆", "4×4", "SVD"], "description": "反对角置换，正交型"},
]


def merge_unique(existing, new_items, key="id"):
    seen = {item[key] for item in existing}
    out = list(existing)
    for item in new_items:
        if item[key] in seen:
            continue
        seen.add(item[key])
        out.append(item)
    return out


def validate_polys(items):
    for item in items:
        validate_polynomial_expr(item["polynomial"])


def validate_mats(items):
    for item in items:
        validate_matrix_data(item["matrix"])


def main():
    poly_path = DATA / "polynomial_library.json"
    square_path = DATA / "square_matrices.json"
    rect_path = DATA / "rectangular_matrices.json"

    polys = json.loads(poly_path.read_text(encoding="utf-8"))
    squares = json.loads(square_path.read_text(encoding="utf-8"))
    rects = json.loads(rect_path.read_text(encoding="utf-8"))

    polys = merge_unique(polys, NEW_POLYNOMIALS)
    squares = merge_unique(squares, NEW_SQUARE)
    rects = merge_unique(rects, NEW_RECT)

    validate_polys(polys)
    validate_mats(squares)
    validate_mats(rects)

    poly_path.write_text(json.dumps(polys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    square_path.write_text(json.dumps(squares, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rect_path.write_text(json.dumps(rects, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Polynomials: {len(polys)}")
    print(f"Square matrices: {len(squares)}")
    print(f"Rectangular matrices: {len(rects)}")


if __name__ == "__main__":
    main()
