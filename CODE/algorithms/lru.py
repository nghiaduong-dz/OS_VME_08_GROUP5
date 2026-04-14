"""
algorithms/lru.py
LRU - Least Recently Used Page Replacement Algorithm
Trang nao it duoc truy cap gan day nhat se bi thay the.

Tham khao: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne - p.402-403
"""

from models.step import Step


class LRU:

    @staticmethod
    def run(refs: list, frame_size: int) -> list:
        """
        Chay thuat toan LRU.

        Args:
            refs       : Chuoi tham chieu trang
            frame_size : So luong frame bo nho

        Returns:
            Danh sach Step mo ta tung buoc thuc thi
        """
        steps     = []
        frames    = [-1] * frame_size
        last_used = [-1] * frame_size   # buoc cuoi moi slot duoc dung
        faults    = 0

        for i, page in enumerate(refs):
            hit_slot = next((f for f in range(frame_size)
                             if frames[f] == page), -1)
            hit     = hit_slot != -1
            evicted = -1

            if hit:
                last_used[hit_slot] = i
            else:
                faults += 1
                if -1 in frames:
                    slot = frames.index(-1)
                else:
                    # Tim slot it duoc dung nhat
                    slot = last_used.index(min(last_used))
                evicted       = frames[slot]
                frames[slot]  = page
                last_used[slot] = i

            steps.append(Step(page, frames, not hit, faults, evicted))

        return steps

    @staticmethod
    def count_faults(steps: list) -> int:
        return sum(1 for s in steps if s.is_fault)
