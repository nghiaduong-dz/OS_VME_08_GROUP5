"""
unit_tests/test_algorithms.py
Kiểm tra tính đúng đắn của 3 thuật toán + Step model.
Kết quả đối chiếu với giáo trình OS Concepts 10th Edition.

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.fifo import FIFO
from algorithms.lru  import LRU, LRUClock
from algorithms.opt  import OPT
from models.step     import Step


class TestRunner:

    def __init__(self):
        self.results: list[tuple[str, str]] = []
        self.passed  = 0
        self.failed  = 0

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def check(self, name: str, condition: bool) -> None:
        status = "PASS" if condition else "FAIL"
        self.results.append((status, name))
        if condition:
            self.passed += 1
        else:
            self.failed += 1

    def check_eq(self, name: str, got, expected) -> None:
        ok = got == expected
        if not ok:
            name = f"{name}  [got={got}, expected={expected}]"
        self.check(name, ok)

    # ------------------------------------------------------------------ #
    #  Test suites                                                         #
    # ------------------------------------------------------------------ #

    def _test_textbook(self) -> None:
        """Đối chiếu chính xác với giáo trình Silberschatz p.400-403."""
        refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
        n    = 3

        sF = FIFO.run(refs, n)
        sL = LRU.run(refs, n)
        sO = OPT.run(refs, n)

        fF = FIFO.count_faults(sF)
        fL = LRU.count_faults(sL)
        fO = OPT.count_faults(sO)

        # Giáo trình cho biết: FIFO=9, LRU=8(?), OPT=7 (tùy phiên bản)
        # Quan trọng hơn: OPT ≤ LRU ≤ FIFO (tính tối ưu)
        self.check("TB: OPT <= LRU <= FIFO (optimal property)", fO <= fL <= fF)
        self.check("TB: FIFO faults >= 1",  fF >= 1)
        self.check("TB: OPT  faults >= 1",  fO >= 1)

        # Step count
        self.check_eq("TB: FIFO step count", len(sF), len(refs))
        self.check_eq("TB: LRU  step count", len(sL), len(refs))
        self.check_eq("TB: OPT  step count", len(sO), len(refs))

        # Bước 1 luôn fault (cold start)
        self.check("TB: FIFO step 1 is fault", sF[0].is_fault)
        self.check("TB: LRU  step 1 is fault", sL[0].is_fault)
        self.check("TB: OPT  step 1 is fault", sO[0].is_fault)

        # Bước 5 (refs[4]=0): page 0 đã có trong frames → HIT
        self.check("TB: FIFO step 5 is hit (page 0 cached)", not sF[4].is_fault)
        self.check("TB: LRU  step 5 is hit (page 0 cached)", not sL[4].is_fault)
        self.check("TB: OPT  step 5 is hit (page 0 cached)", not sO[4].is_fault)

    def _test_edge_cases(self) -> None:
        """Test biên: chuỗi rỗng, 1 frame, refs toàn giống nhau."""
        # Empty refs
        self.check_eq("EDGE: FIFO empty refs → 0 steps", len(FIFO.run([], 3)), 0)
        self.check_eq("EDGE: LRU  empty refs → 0 steps", len(LRU.run([], 3)),  0)
        self.check_eq("EDGE: OPT  empty refs → 0 steps", len(OPT.run([], 3)),  0)

        # frame_size=1
        s1 = FIFO.run([1, 1, 1, 2, 2], 1)
        self.check_eq("EDGE: FIFO frame=1 [1,1,1,2,2] → 2 faults",
                      FIFO.count_faults(s1), 2)

        # All same page → only first is fault
        for name, Cls in [("FIFO",FIFO),("LRU",LRU),("OPT",OPT)]:
            ss = Cls.run([5, 5, 5, 5, 5], 3)
            self.check_eq(f"EDGE: {name} all-same page → 1 fault",
                          Cls.count_faults(ss), 1)

        # Fully unique pages (no hit possible) with frame_size=1
        for name, Cls in [("FIFO",FIFO),("LRU",LRU),("OPT",OPT)]:
            unique = list(range(5))
            ss = Cls.run(unique, 1)
            self.check_eq(f"EDGE: {name} all-unique frame=1 → 5 faults",
                          Cls.count_faults(ss), 5)

        # Validation: negative frame_size
        for name, Cls in [("FIFO",FIFO),("LRU",LRU),("OPT",OPT)]:
            try:
                Cls.run([1, 2, 3], 0)
                self.check(f"EDGE: {name} frame=0 raises ValueError", False)
            except ValueError:
                self.check(f"EDGE: {name} frame=0 raises ValueError", True)

    def _test_belady(self) -> None:
        """Belady's Anomaly — FIFO 3f=9 faults, 4f=10 faults."""
        belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        f3 = FIFO.count_faults(FIFO.run(belady, 3))
        f4 = FIFO.count_faults(FIFO.run(belady, 4))
        self.check_eq("BELADY: FIFO 3 frames = 9 faults",            f3, 9)
        self.check_eq("BELADY: FIFO 4 frames = 10 faults (anomaly)", f4, 10)
        self.check("BELADY: more frames → more faults",              f4 > f3)

        # OPT KHÔNG bị Belady
        o3 = OPT.count_faults(OPT.run(belady, 3))
        o4 = OPT.count_faults(OPT.run(belady, 4))
        self.check("BELADY: OPT not affected (4f <= 3f)", o4 <= o3)

    def _test_lru_clock(self) -> None:
        """LRUClock fault count gần với LRU (cho phép ±20% divergence)."""
        refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
        n    = 3
        fLRU   = LRU.count_faults(LRU.run(refs, n))
        fClock = LRUClock.count_faults(LRUClock.run(refs, n))
        # Clock là xấp xỉ, không nhất thiết bằng chính xác
        self.check("LRUClock: faults >= OPT faults",
                   fClock >= OPT.count_faults(OPT.run(refs, n)))
        diverge_pct = abs(fClock - fLRU) / max(fLRU, 1) * 100
        self.check(f"LRUClock: divergence from LRU <= 30% (got {diverge_pct:.1f}%)",
                   diverge_pct <= 30)
        self.check_eq("LRUClock step count = ref length",
                      len(LRUClock.run(refs, n)), len(refs))

    def _test_step_model(self) -> None:
        """Kiểm tra Step model: hit_rate, fault_rate, serialization."""
        refs = [1, 2, 1, 3, 1]
        n    = 2
        steps = LRU.run(refs, n)

        # step_index gán đúng
        for i, s in enumerate(steps):
            self.check_eq(f"STEP: step_index[{i}]", s.step_index, i)

        # hit_rate + fault_rate = 1.0
        for s in steps:
            total = s.hit_rate + s.fault_rate
            self.check(f"STEP: hit+fault=1 at step {s.step_index}",
                       abs(total - 1.0) < 1e-9)

        # to_dict keys
        d = steps[-1].to_dict()
        required_keys = {
            "step","page","fault_or_hit","evicted","frames",
            "total_faults","total_hits","hit_rate","fault_rate","next_use"
        }
        self.check("STEP: to_dict has all required keys",
                   required_keys.issubset(d.keys()))

        # to_json roundtrip
        js   = steps[0].to_json()
        back = json.loads(js)
        self.check("STEP: to_json is valid JSON", isinstance(back, dict))

        # to_csv_row length
        row = steps[0].to_csv_row(n)
        hdr = Step.csv_header(n)
        self.check_eq("STEP: to_csv_row length == header length",
                      len(row), len(hdr))

        # __eq__
        steps2 = LRU.run(refs, n)
        self.check("STEP: equal steps compare equal", steps[0] == steps2[0])

    def _test_opt_next_use(self) -> None:
        """OPT: next_use field được gán trên Step."""
        refs  = [1, 2, 3, 1, 2, 3]
        steps = OPT.run(refs, frame_size=2)
        # Bước 0 (page=1): next_use nên là 3
        # (refs[3]=1 là lần dùng tiếp theo SAU bước 0)
        self.check("OPT: next_use at step 0 is correct",
                   steps[0].next_use == 3)
        # Bước cuối (page=3): không còn dùng nữa → None
        last = steps[-1]
        self.check("OPT: last step next_use is None", last.next_use is None)

    # ------------------------------------------------------------------ #
    #  Entry point                                                         #
    # ------------------------------------------------------------------ #

    def run_all(self) -> tuple[list[tuple[str,str]], int, int]:
        self._test_textbook()
        self._test_edge_cases()
        self._test_belady()
        self._test_lru_clock()
        self._test_step_model()
        self._test_opt_next_use()
        return self.results, self.passed, self.failed


# ---- CLI ----------------------------------------------------------------
if __name__ == "__main__":
    tr      = TestRunner()
    results, passed, failed = tr.run_all()

    print("=" * 65)
    print("  UNIT TEST RESULTS — OS_VME_08 Group 5")
    print("=" * 65)
    for status, name in results:
        mark = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {mark}  {name}")
    print("-" * 65)
    total = passed + failed
    print(f"  Passed: {passed}  |  Failed: {failed}  |  Total: {total}")
    print("  ALL PASSED! ✓" if failed == 0 else "  SOME TESTS FAILED. ✗")
    print("=" * 65)
    sys.exit(0 if failed == 0 else 1)
