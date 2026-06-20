"""Polynomial library service."""

import json
from pathlib import Path

from app.utils.validator import validate_polynomial_expr

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "polynomial_library.json"


class PolynomialLibraryService:
    def __init__(self):
        with open(DATA_PATH, encoding="utf-8") as f:
            self._library = json.load(f)
        self._by_id = {item["id"]: item for item in self._library}

    def list_all(self):
        return self._library

    def get_by_id(self, poly_id):
        if poly_id not in self._by_id:
            raise ValueError(f"多项式 ID 不存在: {poly_id}")
        item = self._by_id[poly_id]
        validate_polynomial_expr(item["polynomial"])
        return item

    def get_validated_polynomial(self, poly_id):
        item = self.get_by_id(poly_id)
        expr, _ = validate_polynomial_expr(item["polynomial"])
        return expr, item
