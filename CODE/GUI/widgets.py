"""
GUI/widgets.py
Shared reusable widgets và color palette dùng chung toàn bộ GUI.

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk


# =========================================================================
#  COLOR PALETTE  (Catppuccin Mocha)
# =========================================================================
class C:
    BG      = "#1a1a2e"
    BG2     = "#252538"
    BG3     = "#2e2e48"
    SURFACE = "#3a3a58"
    ACCENT  = "#818cf8"       # indigo bright
    FAULT   = "#fb7185"       # rose bright
    HIT     = "#4ade80"       # green bright
    NEW_PG  = "#60a5fa"       # blue bright
    TEXT    = "#e2e8f0"       # near white — rõ chính
    TEXT2   = "#94a3b8"       # slate — phụ nhưng vẫn đọc được
    MUTED   = "#64748b"       # chỉ dùng cho placeholder
    YELLOW  = "#fbbf24"       # amber bright
    PEACH   = "#fb923c"
    MAUVE   = "#c084fc"
    WHITE   = "#f8fafc"
    BORDER  = "#3f3f60"

    # Per-algo colours
    ALGO = {
        "FIFO" : "#60a5fa",   # blue
        "LRU"  : "#4ade80",   # green
        "OPT"  : "#c084fc",   # purple
    }


# =========================================================================
#  FONT HELPERS
# =========================================================================
def F(size: int = 10, bold: bool = False, italic: bool = False) -> tuple:
    style = ("bold" if bold else "") + (" italic" if italic else "")
    return ("Consolas", size, style.strip()) if style.strip() else ("Consolas", size)


# =========================================================================
#  REUSABLE WIDGETS
# =========================================================================

class HLine(tk.Frame):
    """Horizontal separator line."""
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.BORDER, height=1, **kw)


class SectionLabel(tk.Label):
    """Small uppercase section heading."""
    def __init__(self, parent, text: str, **kw):
        super().__init__(parent, text=text,
                         font=F(9, bold=True),
                         bg=C.BG2, fg=C.TEXT2, **kw)   # TEXT2 đã sáng hơn


class PillStat(tk.Frame):
    """
    Stat pill widget showing a large value + small label.

    Usage:
        p = PillStat(parent, "—", "Page Faults", C.FAULT)
        p.set("12")
    """

    def __init__(self, parent, value: str, label: str, color: str, **kw):
        super().__init__(parent, bg=C.BG3, padx=14, pady=8, **kw)
        self._val_lbl = tk.Label(self, text=value,
                                 font=F(20, bold=True),
                                 bg=C.BG3, fg=color)
        self._val_lbl.pack()
        tk.Label(self, text=label, font=F(9),
                 bg=C.BG3, fg=C.TEXT2).pack()
        self._color = color

    def set(self, value: str) -> None:
        self._val_lbl.config(text=value)


class IconButton(tk.Button):
    """Styled flat button."""

    def __init__(self, parent, text: str, command,
                 fg: str = C.ACCENT, size: int = 10, **kw):
        super().__init__(
            parent, text=text, command=command,
            font=F(size, bold=True),
            bg=C.BG3, fg=fg,
            relief="flat", cursor="hand2",
            activebackground=C.SURFACE,
            activeforeground=fg,
            pady=7, padx=10,
            **kw,
        )
        self.bind("<Enter>", lambda _: self.config(bg=C.SURFACE))
        self.bind("<Leave>", lambda _: self.config(bg=C.BG3))


class AccentButton(tk.Button):
    """Prominent accent-colored button."""

    def __init__(self, parent, text: str, command, **kw):
        super().__init__(
            parent, text=text, command=command,
            font=F(11, bold=True),
            bg=C.ACCENT, fg=C.BG,
            relief="flat", cursor="hand2",
            activebackground=C.MAUVE,
            activeforeground=C.BG,
            pady=9,
            **kw,
        )


class ScrollableCanvas(tk.Frame):
    """Canvas with horizontal + vertical scrollbars."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.BORDER, bd=1)
        self.canvas = tk.Canvas(self, bg=C.BG2,
                                highlightthickness=0, **kw)
        hbar = tk.Scrollbar(self, orient="horizontal",
                             command=self.canvas.xview)
        vbar = tk.Scrollbar(self, orient="vertical",
                             command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set,
                               yscrollcommand=vbar.set)
        hbar.pack(side="bottom", fill="x")
        vbar.pack(side="right",  fill="y")
        self.canvas.pack(fill="both", expand=True)

    def clear(self):
        self.canvas.delete("all")

    def set_scroll_region(self, w: int, h: int):
        self.canvas.configure(scrollregion=(0, 0, w, h))


class Tooltip:
    """
    Lightweight tooltip on mouse-hover.

    Usage:
        Tooltip(widget, "Some helpful text")
    """

    def __init__(self, widget: tk.Widget, text: str):
        self._widget  = widget
        self._text    = text
        self._tip_win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        if self._tip_win:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip_win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self._text,
                 font=F(9), bg=C.BG3, fg=C.YELLOW,
                 relief="flat", padx=10, pady=5,
                 bd=1).pack()

    def _hide(self, event=None):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None


class CanvasTooltip:
    """
    Tooltip that follows mouse over canvas items tagged with a given tag.

    Usage:
        ct = CanvasTooltip(canvas)
        ct.register(item_id, "Frame state: [7, 0, 1] — FAULT")
    """

    def __init__(self, canvas: tk.Canvas):
        self._canvas   = canvas
        self._texts    : dict[int, str] = {}
        self._tip_win  = None
        canvas.bind("<Motion>",  self._on_motion)
        canvas.bind("<Leave>",   self._hide)

    def register(self, item_id: int, text: str) -> None:
        self._texts[item_id] = text

    def _on_motion(self, event):
        items = self._canvas.find_overlapping(
            event.x - 2, event.y - 2, event.x + 2, event.y + 2)
        for item in reversed(items):
            if item in self._texts:
                self._show(event, self._texts[item])
                return
        self._hide()

    def _show(self, event, text: str):
        if self._tip_win:
            self._tip_win.destroy()
        x = self._canvas.winfo_rootx() + event.x + 15
        y = self._canvas.winfo_rooty() + event.y + 15
        self._tip_win = tw = tk.Toplevel(self._canvas)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=text,
                 font=F(9), bg=C.BG3, fg=C.YELLOW,
                 relief="flat", padx=10, pady=5,
                 justify="left").pack()

    def _hide(self, event=None):
        if self._tip_win:
            self._tip_win.destroy()
            self._tip_win = None


def build_notebook_style():
    """Apply themed ttk.Notebook style."""
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TNotebook",
                    background=C.BG, borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=C.BG3, foreground=C.TEXT,   # TEXT không phải TEXT2
                    font=F(10, bold=True), padding=[16, 7])
    style.map("TNotebook.Tab",
              background=[("selected", C.ACCENT)],
              foreground=[("selected", C.BG)])
    style.configure("TPanedwindow", background=C.BG)
    style.configure("TSeparator",   background=C.BORDER)