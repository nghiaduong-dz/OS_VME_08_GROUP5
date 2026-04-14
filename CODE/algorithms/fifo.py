"""
algorithms/fifo.py
FIFO - First In First Out Page Replacement Algorithm
Trang nao duoc nap vao bo nho dau tien se bi thay the truoc.

Tham khao: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne - p.400-401
"""

from models.step import Step


class FIFO:

    @staticmethod
    def run(refs: list, frame_size: int) -> list:
        """
        Chay thuat toan FIFO.

        Args:
            refs       : Chuoi tham chieu trang
            frame_size : So luong frame bo nho

        Returns:
            Danh sach Step mo ta tung buoc thuc thi
        """
        steps   = []
        frames  = [-1] * frame_size
        queue   = []          # luu PAGE theo thu tu nap vao (FIFO)
        faults  = 0

        for page in refs:
            hit     = page in frames
            evicted = -1

            if not hit:
                faults += 1
                if -1 in frames:
                    # Con slot trong
                    slot = frames.index(-1)
                    frames[slot] = page
                else:
                    # Day trang vao truoc nhat
                    evict_page = queue.pop(0)
                    slot = frames.index(evict_page)
                    evicted = evict_page
                    frames[slot] = page
                queue.append(page)

            steps.append(Step(page, frames, not hit, faults, evicted))

        return steps

    @staticmethod
    def count_faults(steps: list) -> int:
        return sum(1 for s in steps if s.is_fault)
