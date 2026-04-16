"""
utils/file_handler.py
Xu ly doc/ghi file CSV.

Input CSV format:
    Dong 1: Frame size (so nguyen duong, 1-20)
    Dong 2: Reference string (so nguyen cach nhau dau phay)

Output CSV format:
    Header thong tin + bang chi tiet tung buoc
"""

import csv
import os


class FileHandler:

    @staticmethod
    def read_input(path: str):
        """
        Doc file CSV dau vao.

        Returns:
            (frame_size: int, ref_string: list)

        Raises:
            ValueError: Neu du lieu khong hop le
            FileNotFoundError: Neu file khong ton tai
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Khong tim thay file: {path}")

        with open(path, "r", encoding="utf-8-sig") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        if len(lines) < 2:
            raise ValueError("File CSV thieu du lieu (can it nhat 2 dong).")

        # Dong 1: frame size
        try:
            frame_size = int(lines[0])
        except ValueError:
            raise ValueError(f"Frame size khong hop le: '{lines[0]}'")

        if not (1 <= frame_size <= 20):
            raise ValueError(f"Frame size phai tu 1-20 (got {frame_size}).")

        # Dong 2: reference string
        tokens = lines[1].split(",")
        ref_string = []
        skipped = 0
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            try:
                val = int(t)
                if val < 0:
                    skipped += 1
                    continue
                ref_string.append(val)
            except ValueError:
                skipped += 1

        if skipped > 0:
            print(f"[FileHandler] WARNING: {skipped} token khong hop le bi bo qua.")

        if not ref_string:
            raise ValueError("Reference string trong hoac khong co gia tri hop le.")

        return frame_size, ref_string

    @staticmethod
    def write_output(path: str, algo_name: str, frame_size: int,
                     ref_string: list, steps: list, exec_ms: float):
        """
        Xuat ket qua ra file CSV.
        Format: Header + bang chi tiet tung buoc
        """
        faults    = sum(1 for s in steps if s.is_fault)
        hits      = len(steps) - faults
        hit_rate  = hits   / len(steps) * 100 if steps else 0
        fault_rate= faults / len(steps) * 100 if steps else 0

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)

            # Header
            w.writerow(["=== VIRTUAL MEMORY PAGE REPLACEMENT SIMULATOR ==="])
            w.writerow(["OS_VME_08 - Group 5 - HCMUTRANS"])
            w.writerow([])
            w.writerow(["Algorithm",       algo_name])
            w.writerow(["Frame Size",       frame_size])
            w.writerow(["Total References", len(ref_string)])
            w.writerow(["Total Faults",     faults])
            w.writerow(["Total Hits",       hits])
            w.writerow(["Hit Rate (%)",     f"{hit_rate:.2f}"])
            w.writerow(["Fault Rate (%)",   f"{fault_rate:.2f}"])
            w.writerow(["Exec Time (ms)",   f"{exec_ms:.3f}"])
            w.writerow([])
            w.writerow(["Reference String"] + ref_string)
            w.writerow([])

            # Column header
            header = ["Step", "Page", "Fault/Hit", "Evicted"]
            header += [f"Frame_{i+1}" for i in range(frame_size)]
            header += ["Total_Faults", "Total_Hits"]
            w.writerow(header)

            # Data rows
            if len(steps) > 1000:
                w.writerow(["[STRESS TEST DEFENSE PROTOCOL ACTIVATED]"])
                w.writerow([f"Skipped rendering {len(steps)} detailed steps to protect memory overhead during Export."])
                w.writerow(["Algorithm Analytics generated successfully in the header above."])
            else:
                tf, th = 0, 0
                for i, s in enumerate(steps):
                    if s.is_fault: tf += 1
                    else:          th += 1
                    row = [
                        i + 1,
                        s.page,
                        "FAULT" if s.is_fault else "HIT",
                        s.evicted if s.evicted != -1 else "-"
                    ]
                    row += [
                        s.frames[f] if f < len(s.frames) and s.frames[f] != -1 else "-"
                        for f in range(frame_size)
                    ]
                    row += [tf, th]
                    w.writerow(row)

    @staticmethod
    def create_sample(path: str):
        """Tao file CSV mau (vi du giao trinh)."""
        with open(path, "w", newline="") as f:
            f.write("3\n7,0,1,2,0,3,0,4,2,3,0,3\n")

    @staticmethod
    def create_belady(path: str):
        """Tao file CSV kiem tra Belady's Anomaly."""
        with open(path, "w", newline="") as f:
            f.write("4\n1,2,3,4,1,2,5,1,2,3,4,5\n")
