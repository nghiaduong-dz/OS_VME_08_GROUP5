"""
GUI/gantt.py
Gantt Chart tab — vẽ bảng thay thế trang + animation step-by-step.

Features:
  • Canvas scrollable (ngang + dọc)
  • Tooltip hover: hiển thị frame state + lý do fault/hit
  • Animation: replay từng bước với delay tuỳ chỉnh
  • Highlight ô hiện tại khi animate

OS_VME_08 — Group 5 — HCMUTRANS
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from GUI.widgets import (
    C, F, HLine, PillStat, IconButton,
    ScrollableCanvas, CanvasTooltip,
)
from models.step import Step


class GanttTab(tk.Frame):
    """
    Full Gantt-chart tab.
    Gọi .render(algo_name, steps, frame_size, exec_ms) để vẽ lại.
    """

    CW = 46   # cell width
    CH = 38   # cell height
    LABEL_W = 92

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.BG, **kw)

        self._steps      : list[Step] = []
        self._frame_size : int        = 3
        self._algo_name  : str        = ""
        self._anim_job   = None        # after() handle
        self._anim_step  : int        = 0
        self._speed_var  = tk.IntVar(value=120)   # ms per step

        self._build()

    # ------------------------------------------------------------------ #
    #  Build UI                                                            #
    # ------------------------------------------------------------------ #

    def _build(self):
        # ---- top bar: title + pills ----------------------------------
        top = tk.Frame(self, bg=C.BG)
        top.pack(fill="x", padx=14, pady=(10, 4))

        self._title = tk.Label(top,
                               text="Select an algorithm and click Run",
                               font=F(13, bold=True),
                               bg=C.BG, fg=C.TEXT2)
        self._title.pack(side="left")

        # ---- pills ---------------------------------------------------
        pill_row = tk.Frame(self, bg=C.BG)
        pill_row.pack(pady=(0, 6))
        self.p_faults = PillStat(pill_row, "—", "Page Faults", C.FAULT)
        self.p_hits   = PillStat(pill_row, "—", "Page Hits",   C.HIT)
        self.p_rate   = PillStat(pill_row, "—", "Hit Rate",    C.ACCENT)
        self.p_time   = PillStat(pill_row, "—", "Exec Time",   C.YELLOW)
        for p in (self.p_faults, self.p_hits, self.p_rate, self.p_time):
            p.pack(side="left", padx=6)

        # ---- legend --------------------------------------------------
        leg = tk.Frame(self, bg=C.BG)
        leg.pack(pady=(0, 6))
        for color, lbl in [
            (C.FAULT,  "Page Fault"),
            (C.HIT,    "Page Hit"),
            (C.NEW_PG, "New Frame"),
            (C.BG3,    "Unchanged"),
        ]:
            tk.Frame(leg, bg=color, width=13, height=13
                     ).pack(side="left", padx=(10, 3))
            tk.Label(leg, text=lbl, font=F(9),
                     bg=C.BG, fg=C.TEXT2).pack(side="left", padx=(0, 8))

        # ---- animation controls --------------------------------------
        ctrl = tk.Frame(self, bg=C.BG2, pady=5)
        ctrl.pack(fill="x", padx=10, pady=(0, 6))

        IconButton(ctrl, "⏮ Reset",   self._anim_reset,  fg=C.TEXT2,  size=9).pack(side="left", padx=4)
        IconButton(ctrl, "▶ Play",    self._anim_play,   fg=C.HIT,    size=9).pack(side="left", padx=4)
        IconButton(ctrl, "⏸ Pause",   self._anim_pause,  fg=C.YELLOW, size=9).pack(side="left", padx=4)
        IconButton(ctrl, "⏭ End",     self._anim_end,    fg=C.TEXT2,  size=9).pack(side="left", padx=4)

        tk.Label(ctrl, text="Speed:", font=F(9),
                 bg=C.BG2, fg=C.TEXT2).pack(side="left", padx=(16, 4))
        tk.Scale(ctrl, from_=30, to=600,
                 variable=self._speed_var,
                 orient="horizontal", length=120,
                 bg=C.BG2, fg=C.TEXT,
                 troughcolor=C.BG3,
                 highlightthickness=0,
                 font=F(8)).pack(side="left")
        tk.Label(ctrl, text="ms/step", font=F(9),
                 bg=C.BG2, fg=C.TEXT2).pack(side="left", padx=4)

        self._anim_lbl = tk.Label(ctrl, text="Step: —",
                                   font=F(10, bold=True),
                                   bg=C.BG2, fg=C.ACCENT)
        self._anim_lbl.pack(side="right", padx=12)

        # ---- canvas --------------------------------------------------
        self._sc = ScrollableCanvas(self)
        self._sc.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._canvas = self._sc.canvas
        self._tooltip = CanvasTooltip(self._canvas)

    # ------------------------------------------------------------------ #
    #  Public render                                                       #
    # ------------------------------------------------------------------ #

    def render(self, algo_name: str, steps: list[Step],
               frame_size: int, exec_ms: float,
               algo_color: str | None = None) -> None:
        self._anim_pause()
        self._steps      = steps
        self._frame_size = frame_size
        self._algo_name  = algo_name
        self._exec_ms    = exec_ms
        self._anim_step  = 0

        color = algo_color or C.ALGO.get(algo_name, C.ACCENT)
        self._title.config(text=f"Algorithm: {algo_name}", fg=color)

        if not steps:
            return

        faults = sum(1 for s in steps if s.is_fault)
        hits   = len(steps) - faults
        hr     = hits / len(steps) * 100

        self.p_faults.set(str(faults))
        self.p_hits.set(str(hits))
        self.p_rate.set(f"{hr:.1f}%")
        self.p_time.set(f"{exec_ms:.2f}ms")

        self._draw_all(steps, frame_size, highlight=-1)

    # ------------------------------------------------------------------ #
    #  Drawing                                                             #
    # ------------------------------------------------------------------ #

    def _draw_all(self, steps: list[Step], n: int,
                  highlight: int = -1) -> None:
        """
        Vẽ toàn bộ Gantt grid.
        highlight: index bước đang được animate (-1 = tất cả)
        """
        CW, CH = self.CW, self.CH
        LABEL_W = self.LABEL_W
        PAD_TOP = 22
        PAD_L   = 10

        total_w = PAD_L + LABEL_W + len(steps) * CW + 30
        total_h = PAD_TOP + (n + 3) * CH + 20
        self._sc.clear()
        self._sc.set_scroll_region(total_w, total_h)

        c = self._canvas
        self._tooltip = CanvasTooltip(c)  # rebuild

        def cell(col, row, text, bg, fg=C.WHITE, bold=False,
                 outline=C.BORDER, border_w=1):
            x0 = PAD_L + LABEL_W + col * CW
            y0 = PAD_TOP + row * CH
            x1, y1 = x0 + CW - 1, y0 + CH - 1
            rid = c.create_rectangle(x0, y0, x1, y1,
                                     fill=bg, outline=outline, width=border_w)
            font = F(10, bold=bold)
            tid = c.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                                 text=str(text), fill=fg, font=font)
            return rid, tid

        def row_lbl(row, text):
            x0, y0 = PAD_L, PAD_TOP + row * CH
            x1, y1 = PAD_L + LABEL_W - 2, y0 + CH
            c.create_rectangle(x0, y0, x1, y1,
                                fill=C.BG3, outline=C.BORDER)
            c.create_text((x0 + x1) // 2, (y0 + y1) // 2,
                           text=text, fill=C.TEXT, font=F(9, bold=True))

        # Labels
        row_lbl(0, "Page Ref")
        for f in range(n):
            row_lbl(f + 1, f"Frame {f + 1}")
        row_lbl(n + 1, "F / H")

        # Cells
        for i, s in enumerate(steps):
            # Show only up to current anim step
            if highlight != -1 and i > highlight:
                break

            dim = (highlight != -1 and i < highlight)

            # Step number (top)
            x0 = PAD_L + LABEL_W + i * CW
            c.create_text(x0 + CW // 2, PAD_TOP // 2 + 4,
                           text=str(i + 1), fill=C.TEXT2, font=F(9))

            is_active = (i == highlight)
            bw        = 2 if is_active else 1
            bcolor    = C.YELLOW if is_active else C.BORDER
            alpha_fg  = C.BG if dim else C.BG   # ô page/FH: luôn dùng BG (chữ tối trên nền sáng)

            # Page row
            pg_bg = (C.FAULT if s.is_fault else C.HIT)
            rid, tid = cell(i, 0, s.page, pg_bg, alpha_fg,
                            bold=True, outline=bcolor, border_w=bw)

            # Tooltip text for page cell
            ttip = (
                f"Step {i+1}  |  Page: {s.page}\n"
                f"{'PAGE FAULT' if s.is_fault else 'PAGE HIT'}\n"
                f"Evicted: {s.evicted if s.evicted != -1 else '—'}\n"
                f"Frames: {s.frames}\n"
                f"Total faults: {s.total_faults}  hits: {s.total_hits}\n"
                f"Hit rate: {s.hit_rate*100:.1f}%"
                + (f"\nNext use: step {s.next_use+1}" if s.next_use is not None else "")
            )
            self._tooltip.register(rid, ttip)
            self._tooltip.register(tid, ttip)

            # Frame rows
            for f in range(n):
                v = s.frames[f] if f < len(s.frames) else -1
                if v == -1:
                    cell(i, f + 1, "·", C.BG2, C.TEXT2,
                         outline=bcolor, border_w=bw)
                else:
                    is_new = s.is_fault and v == s.page
                    fbg    = C.NEW_PG if is_new else C.BG3
                    ffg    = C.BG if is_new else C.TEXT   # không dim chữ frame nữa
                    cell(i, f + 1, v, fbg, ffg,
                         outline=bcolor, border_w=bw)

            # F/H row
            fh_bg = C.FAULT if s.is_fault else C.HIT
            cell(i, n + 1,
                 "F" if s.is_fault else "H",
                 fh_bg, alpha_fg, bold=True,
                 outline=bcolor, border_w=bw)

        # Scroll to highlight
        if highlight > 0 and steps:
            frac = highlight / max(len(steps), 1)
            self._canvas.xview_moveto(max(0, frac - 0.1))

    # ------------------------------------------------------------------ #
    #  Animation                                                           #
    # ------------------------------------------------------------------ #

    def _anim_play(self):
        if not self._steps:
            return
        if self._anim_step >= len(self._steps):
            self._anim_step = 0
        self._anim_tick()

    def _anim_tick(self):
        if self._anim_step >= len(self._steps):
            # Animation xong → vẽ lại toàn bộ không dim
            self._draw_all(self._steps, self._frame_size, highlight=-1)
            self._anim_lbl.config(text=f"Step: {len(self._steps)} ✓")
            return
        self._draw_all(self._steps, self._frame_size,
                       highlight=self._anim_step)
        self._anim_lbl.config(
            text=f"Step: {self._anim_step + 1} / {len(self._steps)}")
        self._anim_step += 1
        delay = self._speed_var.get()
        self._anim_job = self.after(delay, self._anim_tick)

    def _anim_pause(self):
        if self._anim_job:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    def _anim_reset(self):
        self._anim_pause()
        self._anim_step = 0
        if self._steps:
            self._draw_all(self._steps, self._frame_size, highlight=-1)
            self._anim_lbl.config(text="Step: —")

    def _anim_end(self):
        self._anim_pause()
        if self._steps:
            self._anim_step = len(self._steps) - 1
            self._draw_all(self._steps, self._frame_size,
                           highlight=self._anim_step)
            self._anim_lbl.config(
                text=f"Step: {len(self._steps)} ✓")