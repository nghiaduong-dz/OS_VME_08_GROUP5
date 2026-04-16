"""
algorithms/lru.py
LRU – Least Recently Used Page Replacement Algorithm
Trang ít được truy cập gần đây nhất sẽ bị thay thế.

Clock Approximation (Second-Chance) — O(1) amortized
  • Dùng deque làm "kim đồng hồ" thay vì linear scan O(n)
  • Mỗi frame có reference bit; khi cần evict: quét kim,
    nếu bit=1 → clear về 0 và bỏ qua, nếu bit=0 → evict.
  • Amortized O(1) vì mỗi frame bị set bit tối đa 1 lần giữa
    hai lần evict liên tiếp.

Tham khảo: Operating System Concepts 10th Edition
           Silberschatz, Galvin, Gagne — p.402-403, p.409-410

OS_VME_08 — Group 5 — HCMUTRANS
"""

from collections import OrderedDict
from algorithms.base import PageReplacementAlgorithm
from models.step     import Step


class LRU(PageReplacementAlgorithm):

    NAME = "LRU"

    @staticmethod
    def run(refs: list[int], frame_size: int) -> list[Step]:
        """
        Chạy LRU dùng OrderedDict làm LRU cache.

        OrderedDict.move_to_end() → O(1).
        popitem(last=False)       → lấy oldest → O(1).
        Clock approximation được implement thêm ở
        LRUClock.run() trong cùng file 
        """
        LRU._validate(refs, frame_size)

        steps : list[Step]          = []
        cache : OrderedDict[int,int]= OrderedDict()   # page → dummy val
        faults: int                 = 0

        # Giữ parallel list frames để snapshot
        frames: list[int] = [-1] * frame_size

        for i, page in enumerate(refs):
            hit     = page in cache
            evicted = -1

            if hit:
                cache.move_to_end(page)          # O(1) – mark as MRU
                frames = _cache_to_frames(cache, frame_size)
            else:
                faults += 1
                if len(cache) < frame_size:
                    cache[page] = 0
                else:
                    lru_page, _ = cache.popitem(last=False)   # O(1) – evict LRU
                    evicted      = lru_page
                    cache[page]  = 0
                frames = _cache_to_frames(cache, frame_size)

            steps.append(Step(
                page, frames, not hit, faults,
                evicted,
                step_index=i,
            ))

        return steps

    @staticmethod
    def count_faults(steps: list[Step]) -> int:
        return LRU._base_count_faults(steps)


# =========================================================================
#  LRU Clock Approximation  (O(1) amortized )
# =========================================================================

class LRUClock(PageReplacementAlgorithm):
    """
    Second-Chance (Clock) Page Replacement – xấp xỉ LRU.

    Dùng một vòng đồng hồ (deque) và reference bits.
    Khi page được truy cập:  ref_bit[page] = 1
    Khi cần evict:
        while ref_bit[hand] == 1:
            ref_bit[hand] = 0
            hand = hand.next
        evict hand
    """

    NAME = "LRU_CLOCK"

    @staticmethod
    def run(refs: list[int], frame_size: int) -> list[Step]:
        LRUClock._validate(refs, frame_size)

        steps   : list[Step]    = []
        clock   : list[int]     = []          # clock ring (pages)
        ref_bit : dict[int, int]= {}          # page → reference bit
        faults  : int           = 0
        hand    : int           = 0           # kim đồng hồ (index)

        for i, page in enumerate(refs):
            hit     = page in clock
            evicted = -1

            if hit:
                ref_bit[page] = 1             # set reference bit
            else:
                faults += 1
                if len(clock) < frame_size:
                    clock.append(page)
                    ref_bit[page] = 0
                else:
                    # Quét kim đồng hồ
                    while ref_bit[clock[hand]] == 1:
                        ref_bit[clock[hand]] = 0
                        hand = (hand + 1) % frame_size
                    evicted              = clock[hand]
                    ref_bit.pop(evicted)
                    clock[hand]          = page
                    ref_bit[page]        = 0
                    hand = (hand + 1) % frame_size

            # Snapshot frames
            frames = list(clock) + [-1] * (frame_size - len(clock))
            steps.append(Step(
                page, frames, not hit, faults,
                evicted,
                step_index=i,
            ))

        return steps

    @staticmethod
    def count_faults(steps: list[Step]) -> int:
        return LRUClock._base_count_faults(steps)


# ---- Helper -------------------------------------------------------------

def _cache_to_frames(cache: OrderedDict, frame_size: int) -> list[int]:
    """Chuyển OrderedDict keys → list frames, pad bằng -1."""
    keys = list(cache.keys())
    return (keys + [-1] * frame_size)[:frame_size]
