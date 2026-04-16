"""
algorithms/registry.py
Registry: tra cứu thuật toán theo tên chuỗi.

Dùng trong GUI / batch export để tránh if/elif chain dài.

Ví dụ:
    from algorithms.registry import AlgoRegistry
    cls   = AlgoRegistry.get("LRU")       # → class LRU
    steps = cls.run(refs, frame_size)

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from algorithms.base import PageReplacementAlgorithm


class _Registry:
    """Singleton registry ánh xạ tên → class thuật toán."""

    def __init__(self):
        self._table: dict[str, type] = {}

    # ------------------------------------------------------------------ #
    #  Registration                                                        #
    # ------------------------------------------------------------------ #

    def register(self, name: str, cls: type) -> None:
        """Đăng ký một thuật toán.  name phải unique (case-insensitive key)."""
        key = name.upper()
        if key in self._table:
            raise KeyError(f"Algorithm '{key}' đã được đăng ký.")
        self._table[key] = cls

    # ------------------------------------------------------------------ #
    #  Lookup                                                              #
    # ------------------------------------------------------------------ #

    def get(self, name: str) -> type:
        """
        Trả về class thuật toán.

        Raises:
            KeyError: nếu không tìm thấy.
        """
        key = name.upper()
        if key not in self._table:
            available = ", ".join(sorted(self._table))
            raise KeyError(
                f"Thuật toán '{name}' không tồn tại. "
                f"Có sẵn: {available}"
            )
        return self._table[key]

    def all_names(self) -> list[str]:
        """Danh sách tên đã đăng ký, sắp xếp theo alphabet."""
        return sorted(self._table.keys())

    def all_classes(self) -> list[type]:
        """Danh sách class theo thứ tự tên alphabet."""
        return [self._table[k] for k in self.all_names()]

    def __repr__(self) -> str:
        return f"AlgoRegistry({self.all_names()})"


# ---- Singleton toàn cục ------------------------------------------------
AlgoRegistry = _Registry()

# ---- Đăng ký 3 thuật toán mặc định ------------------------------------
# Import ở đây để tránh circular import (base không import registry)
from algorithms.fifo import FIFO   # noqa: E402
from algorithms.lru  import LRU    # noqa: E402
from algorithms.opt  import OPT    # noqa: E402

AlgoRegistry.register("FIFO", FIFO)
AlgoRegistry.register("LRU",  LRU)
AlgoRegistry.register("OPT",  OPT)