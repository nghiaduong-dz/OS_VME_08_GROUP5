"""
unit_tests/test_algorithms.py
Kiem tra tinh dung dan cua 3 thuat toan.
Ket qua doi chieu voi giao trinh OS Concepts 10th Edition.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.fifo import FIFO
from algorithms.lru  import LRU
from algorithms.opt  import OPT


class TestRunner:
    def __init__(self):
        self.results = []
        self.passed  = 0
        self.failed  = 0

    def check(self, name: str, condition: bool):
        ok = bool(condition)
        status = "PASS" if ok else "FAIL"
        self.results.append((status, name))
        if ok: self.passed += 1
        else:  self.failed  += 1

    def run_all(self):
        refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]
        n    = 3

        sF = FIFO.run(refs, n)
        sL = LRU.run(refs, n)
        sO = OPT.run(refs, n)

        fF = FIFO.count_faults(sF)
        fL = LRU.count_faults(sL)
        fO = OPT.count_faults(sO)

        # Logic correctness
        self.check("OPT <= LRU <= FIFO  (optimal property)",   fO <= fL <= fF)

        # Step count matches ref length
        self.check("FIFO step count = ref length",              len(sF) == len(refs))
        self.check("LRU  step count = ref length",              len(sL) == len(refs))
        self.check("OPT  step count = ref length",              len(sO) == len(refs))

        # First access always fault
        self.check("FIFO step 1 is fault (cold start)",         sF[0].is_fault)
        self.check("LRU  step 1 is fault (cold start)",         sL[0].is_fault)
        self.check("OPT  step 1 is fault (cold start)",         sO[0].is_fault)

        # Step 5 (page 0) = hit for all
        self.check("FIFO step 5 is hit  (page 0 in frames)",    not sF[4].is_fault)
        self.check("LRU  step 5 is hit  (page 0 in frames)",    not sL[4].is_fault)
        self.check("OPT  step 5 is hit  (page 0 in frames)",    not sO[4].is_fault)

        # Empty ref string
        self.check("FIFO: empty ref -> 0 steps",                len(FIFO.run([], 3)) == 0)
        self.check("LRU:  empty ref -> 0 steps",                len(LRU.run([], 3))  == 0)
        self.check("OPT:  empty ref -> 0 steps",                len(OPT.run([], 3))  == 0)

        # Single frame
        s1 = FIFO.run([1, 1, 1, 2, 2], 1)
        self.check("FIFO: frame=1, refs=1,1,1,2,2 -> 2 faults", FIFO.count_faults(s1) == 2)

        # Belady's Anomaly
        belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        f3 = FIFO.count_faults(FIFO.run(belady, 3))
        f4 = FIFO.count_faults(FIFO.run(belady, 4))
        self.check("Belady: FIFO 3 frames = 9 faults",           f3 == 9)
        self.check("Belady: FIFO 4 frames = 10 faults (anomaly!)",f4 == 10)
        self.check("Belady anomaly: more frames -> more faults",  f4 > f3)

        # OPT is always optimal
        self.check("OPT always <= FIFO on any input",            fO <= fF)
        self.check("OPT always <= LRU  on any input",            fO <= fL)

        return self.results, self.passed, self.failed


# Chay truc tiep
if __name__ == "__main__":
    tr = TestRunner()
    results, passed, failed = tr.run_all()
    print("=" * 55)
    print("  UNIT TEST RESULTS — OS_VME_08 Group 5")
    print("=" * 55)
    for status, name in results:
        mark = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {mark}  {name}")
    print("-" * 55)
    print(f"  Passed: {passed}  |  Failed: {failed}  |  Total: {passed+failed}")
    print("  ALL PASSED!" if failed == 0 else "  SOME TESTS FAILED.")
    print("=" * 55)
