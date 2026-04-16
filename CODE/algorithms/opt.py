"""
algorithms/opt.py
OPT – Optimal Page Replacement Algorithm (Belady's Algorithm)
Thay thế trang sẽ không được dùng trong thời gian dài nhất ở tương lai.
Đây là thuật toán lý thuyết tối ưu — cần biết trước chuỗi tham chiếu.

NewNew: next_use cache dict — O(n) precompute
  • Phiên bản cũ: mỗi bước scan O(n) → tổng O(n²)
  • Phiên bản mới:
      - Precompute next_use_map[i][page] = vị trí tiếp theo của page
        từ bước i trở đi → dùng dict + scan từ sau ra trước → O(n)
      - Mỗi bước evict tra O(frame_size) → tổng O(n·f)
  • Step.next_use được gán để GUI có thể hiển thị tooltip

Tham khảo: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne — p.401-402

OS_VME_08 — Group 5 — HCMUTRANS
"""

from algorithms.base import PageReplacementAlgorithm
from models.step     import Step


class OPT(PageReplacementAlgorithm):

    NAME = "OPT"

    # ------------------------------------------------------------------ #
    #  Precompute                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _build_next_use(refs: list[int]) -> list[dict[int, int]]:
        """
        Xây dựng bảng next_use[i] → dict {page: next_index_after_i}.

        Độ phức tạp: O(n)
            - Quét refs từ cuối → đầu, cập nhật dict hiện tại.
            - Mỗi bước i, dict lưu lần dùng tiếp theo của mọi page
              từ vị trí i+1 trở đi.

        Trả về: list có len = len(refs)+1
            next_use[i] = next use AFTER step i
            Nếu page không xuất hiện nữa → không có trong dict
              (coi như ∞ khi evict).
        """
        n          = len(refs)
        next_use   : list[dict[int, int]] = [dict() for _ in range(n + 1)]
        # next_use[n] = {} (không còn bước nào sau bước cuối)

        for i in range(n - 1, -1, -1):
            # Kế thừa từ bước sau
            next_use[i] = dict(next_use[i + 1])
            # Bước i+1 trở đi: page refs[i] xuất hiện tại i
            # Nhưng ta muốn next_use[i] = "sau bước i", nên:
            # refs[i] sẽ được dùng tại i, nên next_use sau bước i-1
            # Cách dễ hơn: next_use[i] là dict "nhìn từ bước i+1 trở đi"
            # Gán sau khi copy: refs[i] xuất hiện tại i → ghi vào [i-1..0]
            next_use[i][refs[i]] = i   # tại bước i, page này sẽ dùng

        # Sửa lại: next_use[i] nên = "lần dùng tiếp theo SAU bước i"
        # Rebuild đúng chiều
        result: list[dict[int, int]] = [dict() for _ in range(n + 1)]
        future: dict[int, int]       = {}   # page → next index từ cuối

        for i in range(n - 1, -1, -1):
            future[refs[i]] = i             # page refs[i] sẽ dùng tại i
            result[i]       = dict(future)  # bước i nhìn về tương lai từ i

        return result   # result[i] = next use TẠI hoặc SAU bước i

    # ------------------------------------------------------------------ #
    #  Main                                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def run(refs: list[int], frame_size: int) -> list[Step]:
        """
        Chạy OPT với next_use cache — O(n·frame_size).

        Với mỗi bước cần evict:
            Với mỗi frame f:
                next_f = next_use_after_i.get(frames[f], INF)
            Evict frame có next_f lớn nhất.
        """
        OPT._validate(refs, frame_size)
        if not refs:
            return []

        n            = len(refs)
        INF          = n + 1           # lớn hơn mọi index hợp lệ

        # Precompute next_use[i][page] = lần dùng tiếp theo tại/sau bước i
        next_use_tbl = OPT._build_next_use(refs)

        steps  : list[Step] = []
        frames : list[int]  = [-1] * frame_size
        faults : int        = 0

        for i, page in enumerate(refs):
            hit     = page in frames
            evicted = -1
            # next_use AFTER step i = next_use_tbl[i+1]
            future  = next_use_tbl[i + 1] if i + 1 <= n else {}

            if not hit:
                faults += 1
                if -1 in frames:
                    slot = frames.index(-1)
                else:
                    # Tìm frame sẽ dùng xa nhất / không dùng nữa
                    farthest, slot = -1, 0
                    for f in range(frame_size):
                        nxt = future.get(frames[f], INF)
                        if nxt > farthest:
                            farthest, slot = nxt, f
                evicted      = frames[slot]
                frames[slot] = page

            # next_use của trang vừa nạp (cho tooltip)
            this_next = future.get(page)

            steps.append(Step(
                page, frames, not hit, faults,
                evicted,
                next_use=this_next,
                step_index=i,
            ))

        return steps

    @staticmethod
    def count_faults(steps: list[Step]) -> int:
        return OPT._base_count_faults(steps)
