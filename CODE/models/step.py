"""
models/step.py
Mo ta trang thai bo nho tai moi buoc thuc thi thuat toan.
"""


class Step:
    """
    Luu trang thai 1 buoc trong qua trinh thay the trang.

    Attributes:
        page         : So trang duoc tham chieu
        frames       : Trang thai cac frame (-1 = trong)
        is_fault     : True = page fault, False = page hit
        total_faults : Tong so fault tinh den buoc nay
        evicted      : Trang bi day ra (-1 neu khong co)
    """

    def __init__(self, page: int, frames: list,
                 is_fault: bool, total_faults: int, evicted: int = -1):
        self.page         = page
        self.frames       = list(frames)
        self.is_fault     = is_fault
        self.total_faults = total_faults
        self.evicted      = evicted

    def __repr__(self):
        fh = "FAULT" if self.is_fault else "HIT"
        return f"Step(page={self.page}, {fh}, frames={self.frames})"
