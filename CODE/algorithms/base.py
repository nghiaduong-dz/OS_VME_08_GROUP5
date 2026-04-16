"""
algorithms/base.py
Abstract Base Class (ABC) cho tất cả thuật toán thay thế trang.
Đảm bảo interface thống nhất: run() + count_faults()

OS_VME_08 — Group 5 — HCMUTRANS
"""

from abc import ABC, abstractmethod
from models.step import Step


class PageReplacementAlgorithm(ABC):
    """
    ABC buộc mọi thuật toán phải implement đủ interface.
    Dùng để registry + type-check an toàn.
    """

    # Subclass khai báo tên hiển thị
    NAME: str = "UNKNOWN"

    # ------------------------------------------------------------------ #
    #  Abstract interface                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    @abstractmethod
    def run(refs: list[int], frame_size: int) -> list[Step]:
        """
        Chạy thuật toán thay thế trang.

        Args:
            refs        : Chuỗi tham chiếu trang (list số nguyên không âm)
            frame_size  : Số frame bộ nhớ vật lý (>= 1)

        Returns:
            Danh sách Step – một phần tử mỗi bước tham chiếu.

        Raises:
            ValueError  : frame_size < 1 hoặc refs chứa giá trị âm
        """
        ...

    @staticmethod
    @abstractmethod
    def count_faults(steps: list[Step]) -> int:
        """Đếm tổng số page fault từ danh sách Step."""
        ...

    # ------------------------------------------------------------------ #
    #  Shared helpers (không override)                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate(refs: list[int], frame_size: int) -> None:
        """Kiểm tra đầu vào chung – gọi ở đầu run()."""
        if frame_size < 1:
            raise ValueError(f"frame_size phải >= 1, nhận: {frame_size}")
        for i, p in enumerate(refs):
            if p < 0:
                raise ValueError(f"Số trang âm tại vị trí {i}: {p}")

    @staticmethod
    def _base_count_faults(steps: list[Step]) -> int:
        return sum(1 for s in steps if s.is_fault)