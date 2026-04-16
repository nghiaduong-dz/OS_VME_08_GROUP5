"""
algorithms/fifo.py
FIFO – First In First Out Page Replacement Algorithm
Trang được nạp vào bộ nhớ đầu tiên sẽ bị thay thế trước.

Tham khảo: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne — p.400-401

OS_VME_08 — Group 5 — HCMUTRANS
"""

from collections import deque
from algorithms.base import PageReplacementAlgorithm
from models.step     import Step


class FIFO(PageReplacementAlgorithm):

    NAME = "FIFO"

    @staticmethod
    def run(refs: list[int], frame_size: int) -> list[Step]:
        """
        Chạy thuật toán FIFO.

        Args:
            refs       : Chuỗi tham chiếu trang
            frame_size : Số frame bộ nhớ

        Returns:
            Danh sách Step mô tả từng bước thực thi.
        """
        FIFO._validate(refs, frame_size)

        steps  : list[Step] = []
        frames : list[int]  = [-1] * frame_size
        queue  : deque[int] = deque()   # thứ tự nạp vào (FIFO)
        faults : int        = 0

        for i, page in enumerate(refs):
            hit     = page in frames
            evicted = -1

            if not hit:
                faults += 1
                if -1 in frames:
                    slot = frames.index(-1)
                    frames[slot] = page
                else:
                    evict_page = queue.popleft()   # oldest → O(1)
                    slot       = frames.index(evict_page)
                    evicted    = evict_page
                    frames[slot] = page
                queue.append(page)

            steps.append(Step(
                page, frames, not hit, faults,
                evicted,
                step_index=i,
            ))

        return steps

    @staticmethod
    def count_faults(steps: list[Step]) -> int:
        return FIFO._base_count_faults(steps)
