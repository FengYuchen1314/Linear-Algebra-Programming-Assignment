"""Matrix library service."""

import json
from pathlib import Path

from app.utils.validator import validate_matrix_data

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class MatrixLibraryService:
    def __init__(self):
        with open(DATA_DIR / "square_matrices.json", encoding="utf-8") as f:
            self._square = json.load(f)
        with open(DATA_DIR / "rectangular_matrices.json", encoding="utf-8") as f:
            self._rect = json.load(f)
        self._by_id = {m["id"]: m for m in self._square + self._rect}

    def list_square(self):
        return self._square

    def list_rectangular(self):
        return self._rect

    def get_by_id(self, matrix_id):
        if matrix_id not in self._by_id:
            raise ValueError(f"矩阵 ID 不存在: {matrix_id}")
        item = self._by_id[matrix_id]
        validate_matrix_data(item["matrix"])
        return item

    def get_validated_matrix(self, matrix_id):
        item = self.get_by_id(matrix_id)
        arr, warnings = validate_matrix_data(item["matrix"])
        return arr, item, warnings
