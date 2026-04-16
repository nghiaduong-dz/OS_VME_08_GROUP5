"""
utils/file_handler.py
Xử lý đọc/ghi file CSV + tạo sample inputs.

  • write_output() dùng Step.to_csv_row() (có hit_rate, fault_rate, next_use)
  • batch_export() — chạy 3 algo cùng lúc → 3 file output/FIFO.csv v.v.
  • create_stress_inputs() — tự tạo file stress_test_1/2/3.csv

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import csv
import os
import random

from models.step import Step


class FileHandler:

    # ------------------------------------------------------------------ #
    #  Read                                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def read_input(path: str) -> tuple[int, list[int]]:
        """
        Đọc file CSV đầu vào.

        Format:
            Dòng 1: frame_size (int, 1-20)
            Dòng 2: reference string (comma-separated ints)

        Returns:
            (frame_size, ref_string)

        Raises:
            FileNotFoundError, ValueError
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        with open(path, "r", encoding="utf-8-sig") as f:
            lines = [ln.strip() for ln in f if ln.strip()]

        if len(lines) < 2:
            raise ValueError("File CSV thiếu dữ liệu (cần ít nhất 2 dòng).")

        try:
            frame_size = int(lines[0])
        except ValueError:
            raise ValueError(f"Frame size không hợp lệ: '{lines[0]}'")

        if not (1 <= frame_size <= 20):
            raise ValueError(f"Frame size phải từ 1–20 (nhận {frame_size}).")

        ref_string : list[int] = []
        skipped    : int       = 0
        for tok in lines[1].split(","):
            tok = tok.strip()
            if not tok:
                continue
            try:
                v = int(tok)
                if v < 0:
                    skipped += 1
                    continue
                ref_string.append(v)
            except ValueError:
                skipped += 1

        if skipped:
            print(f"[FileHandler] WARNING: {skipped} token không hợp lệ bị bỏ qua.")

        if not ref_string:
            raise ValueError("Reference string trống hoặc không có giá trị hợp lệ.")

        return frame_size, ref_string

    # ------------------------------------------------------------------ #
    #  Write single                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def write_output(
        path      : str,
        algo_name : str,
        frame_size: int,
        ref_string: list[int],
        steps     : list[Step],
        exec_ms   : float,
    ) -> None:
        """
        Xuất kết quả ra file CSV chi tiết.
        Dùng Step.to_csv_row() → tự động gồm hit_rate, fault_rate, next_use.
        """
        faults     = sum(1 for s in steps if s.is_fault)
        hits       = len(steps) - faults
        hit_rate   = hits   / len(steps) * 100 if steps else 0
        fault_rate = faults / len(steps) * 100 if steps else 0

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)

            # ---- Header block ----------------------------------------
            w.writerow(["=== VIRTUAL MEMORY PAGE REPLACEMENT SIMULATOR ==="])
            w.writerow(["OS_VME_08 — Group 5 — HCMUTRANS"])
            w.writerow([])
            w.writerow(["Algorithm",        algo_name])
            w.writerow(["Frame Size",        frame_size])
            w.writerow(["Total References",  len(ref_string)])
            w.writerow(["Total Faults",      faults])
            w.writerow(["Total Hits",        hits])
            w.writerow(["Hit Rate (%)",      f"{hit_rate:.2f}"])
            w.writerow(["Fault Rate (%)",    f"{fault_rate:.2f}"])
            w.writerow(["Exec Time (ms)",    f"{exec_ms:.4f}"])
            w.writerow([])
            w.writerow(["Reference String"] + ref_string)
            w.writerow([])

            # ---- Data table ------------------------------------------
            w.writerow(Step.csv_header(frame_size))
            for s in steps:
                w.writerow(s.to_csv_row(frame_size))

    # ------------------------------------------------------------------ #
    #  Batch export                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def batch_export(
        out_dir   : str,
        frame_size: int,
        ref_string: list[int],
        results   : dict[str, tuple[list[Step], float]],
    ) -> list[str]:
        """
        Xuất cùng lúc nhiều thuật toán ra nhiều file.

        Args:
            out_dir  : Thư mục output
            results  : {algo_name: (steps, exec_ms)}

        Returns:
            Danh sách đường dẫn file đã tạo.
        """
        os.makedirs(out_dir, exist_ok=True)
        paths: list[str] = []
        for algo_name, (steps, exec_ms) in results.items():
            path = os.path.join(out_dir, f"{algo_name}.csv")
            FileHandler.write_output(
                path, algo_name, frame_size, ref_string, steps, exec_ms
            )
            paths.append(path)
        return paths

    # ------------------------------------------------------------------ #
    #  Sample creators                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create_sample(path: str) -> None:
        """Tạo file CSV mẫu (ví dụ giáo trình p.400)."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("3\n7,0,1,2,0,3,0,4,2,3,0,3\n")

    @staticmethod
    def create_belady(path: str) -> None:
        """Tạo file CSV kiểm tra Belady's Anomaly."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("4\n1,2,3,4,1,2,5,1,2,3,4,5\n")

    @staticmethod
    def create_stress_inputs(input_dir: str = "input") -> None:
        """
        Tạo 3 file stress test:
            stress_test_1.csv  — 1 000 refs, 3 frames
            stress_test_2.csv  — 10 000 refs, 5 frames
            stress_test_3.csv  — 50 000 refs, 10 frames
        """
        os.makedirs(input_dir, exist_ok=True)
        rng = random.Random(42)

        configs = [
            ("stress_test_1.csv", 3,  1_000,  10),
            ("stress_test_2.csv", 5,  10_000, 15),
            ("stress_test_3.csv", 10, 50_000, 20),
        ]

        for fname, frames, n, prange in configs:
            path = os.path.join(input_dir, fname)
            refs = [rng.randint(0, prange - 1) for _ in range(n)]
            with open(path, "w", newline="", encoding="utf-8") as f:
                f.write(f"{frames}\n")
                f.write(",".join(map(str, refs)) + "\n")

        # Edge-case inputs
        edge_cases = {
            "testcase_no_page_fault.csv"       : (5, [0,1,2,3,4,0,1,2,3,4]),
            "testcase_large_frames.csv"         : (20, list(range(20))*2),
            "testcase_extreme_page_fault.csv"   : (1, list(range(50))),
            "testcase_invalid_characters.csv"   : None,   # ký tự lạ
            "testcase_invalid_negative_frame.csv": None,  # frame âm
        }

        for fname, data in edge_cases.items():
            path = os.path.join(input_dir, fname)
            with open(path, "w", newline="", encoding="utf-8") as f:
                if data is None:
                    if "characters" in fname:
                        f.write("3\nabc,1,2,?,3,4\n")   # mix invalid
                    else:
                        f.write("-1\n1,2,3\n")           # frame âm
                else:
                    frames, refs = data
                    f.write(f"{frames}\n")
                    f.write(",".join(map(str, refs)) + "\n")

        print(f"[FileHandler] Tạo xong stress + edge-case inputs tại '{input_dir}/'")
