"""
models/step.py
Mô tả trạng thái bộ nhớ tại mỗi bước thực thi thuật toán.

  • Thêm trường hit_rate / fault_rate (tích lũy đến bước hiện tại)
  • Thêm next_use (dùng cho OPT visualization)
  • to_dict()  → dict   (dùng cho JSON export + batch compare)
  • to_csv_row() → list  (dùng thẳng cho csv.writer)
  • __eq__ / __hash__ để so sánh khi test

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import json
from typing import Optional


class Step:
    """
    Lưu trạng thái 1 bước trong quá trình thay thế trang.

    Attributes
    ----------
    page          : Số trang được tham chiếu tại bước này
    frames        : Snapshot frames sau khi xử lý bước này  (-1 = trống)
    is_fault      : True  → page fault,  False → page hit
    total_faults  : Tổng fault tích lũy từ bước 1 đến bước này
    total_hits    : Tổng hit  tích lũy từ bước 1 đến bước này
    evicted       : Trang bị đẩy ra  (-1 nếu không có hoặc hit)
    next_use      : Lần dùng tiếp theo (OPT) – None nếu không áp dụng
    step_index    : Chỉ số bước (0-based), gán bởi thuật toán
    """

    __slots__ = (
        "page", "frames", "is_fault",
        "total_faults", "total_hits",
        "evicted", "next_use", "step_index",
    )

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        page         : int,
        frames       : list[int],
        is_fault     : bool,
        total_faults : int,
        evicted      : int = -1,
        *,
        total_hits   : int = -1,        # -1 → tự tính từ step_index
        next_use     : Optional[int] = None,
        step_index   : int = -1,
    ):
        self.page         = page
        self.frames       = list(frames)        # deep-copy để tránh shared ref
        self.is_fault     = is_fault
        self.total_faults = total_faults
        self.evicted      = evicted
        self.next_use     = next_use
        self.step_index   = step_index

        # Tự tính total_hits nếu step_index được cung cấp
        if total_hits == -1 and step_index >= 0:
            self.total_hits = (step_index + 1) - total_faults
        else:
            self.total_hits = max(total_hits, 0)

    # ------------------------------------------------------------------ #
    #  Computed properties                                                 #
    # ------------------------------------------------------------------ #

    @property
    def hit_rate(self) -> float:
        """Hit rate tích lũy đến bước hiện tại (0.0 – 1.0)."""
        total = self.total_faults + self.total_hits
        return self.total_hits / total if total > 0 else 0.0

    @property
    def fault_rate(self) -> float:
        """Fault rate tích lũy (0.0 – 1.0)."""
        return 1.0 - self.hit_rate

    @property
    def frame_count(self) -> int:
        """Số frame đang chứa trang hợp lệ (khác -1)."""
        return sum(1 for f in self.frames if f != -1)

    # ------------------------------------------------------------------ #
    #  Serialization                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        """
        Chuyển sang dict – dùng cho JSON export hoặc batch compare.

        Format:
        {
            "step"         : 1,
            "page"         : 7,
            "fault_or_hit" : "FAULT",
            "evicted"      : -1,
            "frames"       : [7, -1, -1],
            "total_faults" : 1,
            "total_hits"   : 0,
            "hit_rate"     : 0.0,
            "fault_rate"   : 1.0,
            "next_use"     : null
        }
        """
        return {
            "step"         : self.step_index + 1,
            "page"         : self.page,
            "fault_or_hit" : "FAULT" if self.is_fault else "HIT",
            "evicted"      : self.evicted,
            "frames"       : list(self.frames),
            "total_faults" : self.total_faults,
            "total_hits"   : self.total_hits,
            "hit_rate"     : round(self.hit_rate,  4),
            "fault_rate"   : round(self.fault_rate, 4),
            "next_use"     : self.next_use,
        }

    def to_csv_row(self, frame_size: int) -> list:
        """
        Trả về 1 row list cho csv.writer.

        Columns (frame_size=3):
        Step | Page | Fault/Hit | Evicted |
        Frame_1 | Frame_2 | Frame_3 |
        Total_Faults | Total_Hits | Hit_Rate(%) | Fault_Rate(%) | Next_Use
        """
        row = [
            self.step_index + 1,
            self.page,
            "FAULT" if self.is_fault else "HIT",
            self.evicted if self.evicted != -1 else "-",
        ]
        for f in range(frame_size):
            v = self.frames[f] if f < len(self.frames) else -1
            row.append(v if v != -1 else "-")
        row += [
            self.total_faults,
            self.total_hits,
            f"{self.hit_rate * 100:.2f}",
            f"{self.fault_rate * 100:.2f}",
            self.next_use if self.next_use is not None else "-",
        ]
        return row

    @staticmethod
    def csv_header(frame_size: int) -> list:
        """Header row tương ứng với to_csv_row()."""
        cols = ["Step", "Page", "Fault/Hit", "Evicted"]
        cols += [f"Frame_{i+1}" for i in range(frame_size)]
        cols += ["Total_Faults", "Total_Hits",
                 "Hit_Rate(%)", "Fault_Rate(%)", "Next_Use"]
        return cols

    def to_json(self) -> str:
        """JSON string của bước này."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                      #
    # ------------------------------------------------------------------ #

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Step):
            return NotImplemented
        return (self.page == other.page
                and self.frames == other.frames
                and self.is_fault == other.is_fault
                and self.total_faults == other.total_faults)

    def __hash__(self) -> int:
        return hash((self.page, tuple(self.frames),
                     self.is_fault, self.total_faults))

    def __repr__(self) -> str:
        fh = "FAULT" if self.is_fault else "HIT"
        return (f"Step(idx={self.step_index}, page={self.page}, "
                f"{fh}, frames={self.frames}, "
                f"faults={self.total_faults}, hits={self.total_hits})")
