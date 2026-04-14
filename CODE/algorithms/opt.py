"""
algorithms/opt.py
OPT - Optimal Page Replacement Algorithm (Belady's Algorithm)
Thay the trang se khong duoc dung trong thoi gian dai nhat o tuong lai.
Day la thuat toan ly thuyet toi uu - can biet truoc chuoi tham chieu.

Tham khao: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne - p.401-402
"""

from models.step import Step


class OPT:

    @staticmethod
    def run(refs: list, frame_size: int) -> list:
        """
        Chay thuat toan OPT.

        Args:
            refs       : Chuoi tham chieu trang (can biet truoc)
            frame_size : So luong frame bo nho

        Returns:
            Danh sach Step mo ta tung buoc thuc thi
        """
        steps  = []
        frames = [-1] * frame_size
        faults = 0

        for i, page in enumerate(refs):
            hit     = page in frames
            evicted = -1

            if not hit:
                faults += 1
                if -1 in frames:
                    slot = frames.index(-1)
                else:
                    # Tim trang dung xa nhat trong tuong lai
                    farthest, slot = -1, 0
                    for f in range(frame_size):
                        next_use = next(
                            (j for j in range(i + 1, len(refs))
                             if refs[j] == frames[f]),
                            len(refs)   # khong con dung nua -> uu tien day ra
                        )
                        if next_use > farthest:
                            farthest, slot = next_use, f
                evicted      = frames[slot]
                frames[slot] = page

            steps.append(Step(page, frames, not hit, faults, evicted))

        return steps

    @staticmethod
    def count_faults(steps: list) -> int:
        return sum(1 for s in steps if s.is_fault)
