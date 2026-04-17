"""
GUI/compare.py  —  tkinter-only, no matplotlib
OS_VME_08 — Group 5 — HCMUTRANS
"""
from __future__ import annotations
import tkinter as tk
from GUI.widgets import C, F, HLine
from models.step import Step

NAMES = ["FIFO", "LRU", "OPT"]


class CompareTab(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C.BG, **kw)
        self._build()

    def _build(self):
        tk.Label(self, text="Algorithm Comparison",
                 font=F(13, bold=True), bg=C.BG, fg=C.WHITE).pack(pady=(14, 2))
        self._sub = tk.Label(self,
                              text='Click  "Run ALL & Compare"  to see results',
                              font=F(10), bg=C.BG, fg=C.TEXT2)
        self._sub.pack(pady=(0, 4))
        HLine(self).pack(fill="x", padx=14, pady=(0, 8))

        outer = tk.Canvas(self, bg=C.BG, highlightthickness=0)
        vbar  = tk.Scrollbar(self, orient="vertical", command=outer.yview)
        outer.configure(yscrollcommand=vbar.set)
        vbar.pack(side="right", fill="y")
        outer.pack(side="left", fill="both", expand=True)
        self._body = tk.Frame(outer, bg=C.BG)
        cwin = outer.create_window((0, 0), window=self._body, anchor="nw")

        def _resize(e):
            outer.configure(scrollregion=outer.bbox("all"))
            outer.itemconfig(cwin, width=outer.winfo_width())
        self._body.bind("<Configure>", _resize)
        outer.bind("<Configure>", lambda e: outer.itemconfig(cwin, width=e.width))

    def render(self, results: dict, times: dict, refs: list, frame_size: int):
        for w in self._body.winfo_children():
            w.destroy()

        n      = len(refs)
        faults = {nm: sum(1 for s in results[nm] if s.is_fault) for nm in NAMES}
        hits   = {nm: n - faults[nm] for nm in NAMES}
        rates  = {nm: hits[nm] / n * 100 for nm in NAMES}
        best   = min(faults, key=faults.get)

        self._sub.config(
            text=f"Input: {n} pages  |  {frame_size} frames  |  Best: {best} ({faults[best]} faults)")

        # ── Pill cards ────────────────────────────────────────────────
        pill_row = tk.Frame(self._body, bg=C.BG)
        pill_row.pack(fill="x", padx=24, pady=(4, 16))

        for nm in NAMES:
            col = C.ALGO[nm]
            crown = "  👑" if nm == best else ""
            card = tk.Frame(pill_row, bg=C.BG3, padx=18, pady=12)
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, text=nm + crown, font=F(15, bold=True),
                     bg=C.BG3, fg=col).pack()
            HLine(card).pack(fill="x", pady=5)
            for lbl, val, vc in [
                ("Faults",   str(faults[nm]),        C.FAULT),
                ("Hits",     str(hits[nm]),           C.HIT),
                ("Hit Rate", f"{rates[nm]:.1f}%",     C.ACCENT),
                ("Time",     f"{times[nm]:.3f} ms",   C.YELLOW),
            ]:
                r = tk.Frame(card, bg=C.BG3); r.pack(fill="x", pady=1)
                tk.Label(r, text=lbl + ":", width=10, anchor="w",
                         font=F(9), bg=C.BG3, fg=C.TEXT2).pack(side="left")
                tk.Label(r, text=val, font=F(11, bold=True),
                         bg=C.BG3, fg=vc).pack(side="left")

        # ── Bar chart (tkinter canvas) ────────────────────────────────
        tk.Label(self._body, text="Faults / Hits / Hit Rate (%)",
                 font=F(10, bold=True), bg=C.BG, fg=C.TEXT2
                 ).pack(anchor="w", padx=24, pady=(2, 2))
        self._bar_chart(faults, hits, rates)

        # ── Table ─────────────────────────────────────────────────────
        tk.Label(self._body, text="Summary Table",
                 font=F(10, bold=True), bg=C.BG, fg=C.TEXT2
                 ).pack(anchor="w", padx=24, pady=(14, 4))
        self._table(faults, hits, rates, times)

    # ── bar chart ─────────────────────────────────────────────────────
    def _bar_chart(self, faults, hits, rates):
        W, H   = 680, 210
        PAD_L  = 60; PAD_R = 20; PAD_T = 18; PAD_B = 44
        BW     = 26   # bar width
        GAP    = 6    # gap between bars in group
        GSPACE = 36   # space between groups

        c = tk.Canvas(self._body, bg=C.BG2, width=W, height=H,
                      highlightthickness=0)
        c.pack(padx=24, pady=(0, 4))

        datasets = [("Faults", faults, C.FAULT),
                    ("Hits",   hits,   C.HIT),
                    ("Rate%",  rates,  C.ACCENT)]

        max_val = max(
            max(faults.values()),
            max(hits.values()),
            max(v for v in rates.values())
        ) or 1

        chart_h = H - PAD_T - PAD_B

        def yp(v): return PAD_T + chart_h - int(v / max_val * chart_h)

        # grid lines
        for i in range(5):
            v = max_val * i / 4
            y = yp(v)
            c.create_line(PAD_L, y, W - PAD_R, y, fill=C.BORDER, dash=(3, 4))
            c.create_text(PAD_L - 4, y, text=f"{v:.0f}", anchor="e",
                          fill=C.TEXT2, font=("Consolas", 8))

        group_w = len(datasets) * (BW + GAP)
        total_w = len(NAMES) * (group_w + GSPACE)
        offset  = (W - PAD_L - PAD_R - total_w) // 2

        for gi, nm in enumerate(NAMES):
            gx = PAD_L + offset + gi * (group_w + GSPACE)
            for di, (label, ds, col) in enumerate(datasets):
                x0  = gx + di * (BW + GAP)
                val = ds[nm]
                y0  = yp(val)
                yb  = PAD_T + chart_h
                # gradient-ish: draw two rects
                c.create_rectangle(x0, y0, x0 + BW, yb,
                                   fill=col, outline="")
                # value above
                if val > 0:
                    c.create_text(x0 + BW // 2, y0 - 3,
                                  text=f"{val:.0f}", anchor="s",
                                  fill=C.TEXT, font=("Consolas", 8))
            # algo label
            mid = gx + group_w // 2
            c.create_text(mid, H - PAD_B + 14, text=nm,
                          fill=C.ALGO[nm], font=("Consolas", 10, "bold"))

        # legend
        lx = PAD_L + 4
        for lbl, _, col in datasets:
            c.create_rectangle(lx, H - 12, lx + 10, H - 2, fill=col, outline="")
            c.create_text(lx + 14, H - 7, text=lbl, anchor="w",
                          fill=C.TEXT2, font=("Consolas", 8))
            lx += 72

    # ── table ─────────────────────────────────────────────────────────
    def _table(self, faults, hits, rates, times):
        order     = sorted(NAMES, key=lambda n: faults[n])
        rank_icon = {order[0]: "🥇", order[1]: "🥈", order[2]: "🥉"}

        tbl = tk.Frame(self._body, bg=C.BG)
        tbl.pack(padx=24, pady=(0, 20), anchor="w")

        cols = [("Algorithm", 12), ("Faults", 8), ("Hits", 8),
                ("Hit Rate", 10), ("Time (ms)", 12), ("Rank", 6)]
        hdr  = tk.Frame(tbl, bg=C.BG)
        hdr.pack(fill="x")
        for col, w in cols:
            tk.Label(hdr, text=col, width=w, font=F(10, bold=True),
                     bg=C.BG3, fg=C.ACCENT, pady=6).pack(side="left", padx=1)

        for nm in NAMES:
            row = tk.Frame(tbl, bg=C.BG)
            row.pack(fill="x", pady=1)
            col = C.ALGO[nm]
            for val, w, fg, bold in [
                (nm,                    12, col,      True),
                (str(faults[nm]),       8,  C.FAULT,  False),
                (str(hits[nm]),         8,  C.HIT,    False),
                (f"{rates[nm]:.1f}%",   10, C.ACCENT, False),
                (f"{times[nm]:.3f}",    12, C.YELLOW, False),
                (rank_icon[nm],          6, C.TEXT,   False),
            ]:
                tk.Label(row, text=val, width=w, font=F(10, bold=bold),
                         bg=C.BG2, fg=fg, pady=6).pack(side="left", padx=1)