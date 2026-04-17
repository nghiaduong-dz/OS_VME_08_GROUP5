"""
unit_tests/stress_runner.py
Stress test & Performance benchmark tự động.

Chạy:
    python unit_tests/stress_runner.py

Kết quả ghi ra:
    output/stress_results.csv   — dữ liệu thô
    output/stress_summary.txt   — tóm tắt

Spec theo kế hoạch Big Update:
    • ref_size: 1k, 5k, 10k, 50k, 100k
    • frame_size: 3, 5, 10, 20
    • 3 thuật toán FIFO, LRU, OPT
    • Dùng timeit (repeat=3, lấy min)
    • Ghi chart data cho GUI (ref_size vs exec_time)

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import csv
import os
import random
import time
import sys

# Đảm bảo import từ root project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.fifo import FIFO
from algorithms.lru  import LRU
from algorithms.opt  import OPT

# ---- Cấu hình -------------------------------------------------------
REF_SIZES   = [1_000, 5_000, 10_000, 50_000, 100_000]
FRAME_SIZES = [3, 5, 10, 20]
ALGOS       = [("FIFO", FIFO), ("LRU", LRU), ("OPT", OPT)]
PAGE_RANGE  = 10          # trang 0–9 (tạo nhiều fault để test thực tế)
REPEAT      = 3           # lấy min của N lần đo
SEED        = 42


def _gen_refs(n: int, page_range: int, seed: int) -> list[int]:
    rng = random.Random(seed)
    return [rng.randint(0, page_range - 1) for _ in range(n)]


def run_stress(
    out_dir: str = "output",
    verbose: bool = True,
) -> list[dict]:
    """
    Chạy toàn bộ stress test.

    Returns:
        Danh sách kết quả dict, mỗi dict là 1 dòng CSV.
    """
    os.makedirs(out_dir, exist_ok=True)
    results: list[dict] = []

    total = len(REF_SIZES) * len(FRAME_SIZES) * len(ALGOS)
    done  = 0

    if verbose:
        print("=" * 65)
        print("  STRESS & PERFORMANCE TEST — OS_VME_08 Group 5")
        print(f"  {total} cases  |  repeat={REPEAT}  |  page_range={PAGE_RANGE}")
        print("=" * 65)

    for ref_size in REF_SIZES:
        refs = _gen_refs(ref_size, PAGE_RANGE, SEED)

        for frame_size in FRAME_SIZES:
            for algo_name, AlgoCls in ALGOS:
                times_ms: list[float] = []
                fault_count = 0

                for _ in range(REPEAT):
                    t0     = time.perf_counter()
                    steps  = AlgoCls.run(refs, frame_size)
                    elapsed= (time.perf_counter() - t0) * 1000
                    times_ms.append(elapsed)
                    fault_count = sum(1 for s in steps if s.is_fault)

                min_ms = min(times_ms)
                avg_ms = sum(times_ms) / REPEAT
                max_ms = max(times_ms)
                hits   = ref_size - fault_count
                hr     = hits / ref_size * 100

                row = {
                    "algo"        : algo_name,
                    "ref_size"    : ref_size,
                    "frame_size"  : frame_size,
                    "faults"      : fault_count,
                    "hits"        : hits,
                    "hit_rate_pct": round(hr, 2),
                    "min_ms"      : round(min_ms, 4),
                    "avg_ms"      : round(avg_ms, 4),
                    "max_ms"      : round(max_ms, 4),
                }
                results.append(row)
                done += 1

                if verbose:
                    print(
                        f"  [{done:3d}/{total}] "
                        f"{algo_name:<5} refs={ref_size:>7,}  "
                        f"frames={frame_size:>2}  "
                        f"faults={fault_count:>6}  "
                        f"min={min_ms:>8.3f}ms  avg={avg_ms:>8.3f}ms"
                    )

    # ---- Ghi CSV --------------------------------------------------------
    csv_path = os.path.join(out_dir, "stress_results.csv")
    _write_csv(csv_path, results)

    # ---- Ghi summary ----------------------------------------------------
    txt_path = os.path.join(out_dir, "stress_summary.txt")
    _write_summary(txt_path, results)

    if verbose:
        print("=" * 65)
        print(f"  ✓ CSV  → {csv_path}")
        print(f"  ✓ TXT  → {txt_path}")
        print("=" * 65)

    return results


# ---- IO helpers ---------------------------------------------------------

def _write_csv(path: str, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _write_summary(path: str, rows: list[dict]) -> None:
    lines: list[str] = []
    lines.append("=" * 65)
    lines.append("  STRESS RESULTS SUMMARY — OS_VME_08 Group 5")
    lines.append("=" * 65)

    # Fastest / slowest per algo
    from collections import defaultdict
    by_algo: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_algo[r["algo"]].append(r)

    for algo, algo_rows in by_algo.items():
        fastest = min(algo_rows, key=lambda x: x["min_ms"])
        slowest = max(algo_rows, key=lambda x: x["max_ms"])
        lines.append(f"\n  {algo}")
        lines.append(
            f"    Fastest: refs={fastest['ref_size']:>7,}  "
            f"frames={fastest['frame_size']}  "
            f"→ {fastest['min_ms']:.3f} ms"
        )
        lines.append(
            f"    Slowest: refs={slowest['ref_size']:>7,}  "
            f"frames={slowest['frame_size']}  "
            f"→ {slowest['max_ms']:.3f} ms"
        )

    # 100k comparison
    lines.append("\n  Performance @ 100k references:")
    lines.append(f"  {'Algo':<6} {'Frames':>6} {'Min(ms)':>10} {'Avg(ms)':>10}")
    lines.append("  " + "-" * 40)
    for r in rows:
        if r["ref_size"] == 100_000:
            lines.append(
                f"  {r['algo']:<6} {r['frame_size']:>6} "
                f"{r['min_ms']:>10.3f} {r['avg_ms']:>10.3f}"
            )

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---- Entry point --------------------------------------------------------
if __name__ == "__main__":
    run_stress(verbose=True)