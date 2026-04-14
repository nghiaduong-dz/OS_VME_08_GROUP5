"""
GUI/display.py
Giao dien do hoa chinh cua ung dung (tkinter).
Hien thi: Gantt chart, so sanh thuat toan, proof vs giao trinh.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os

from algorithms.fifo      import FIFO
from algorithms.lru       import LRU
from algorithms.opt       import OPT
from utils.file_handler   import FileHandler
from unit_tests.test_algorithms import TestRunner


class App(tk.Tk):
    # ---- Color palette ----------------------------------------
    BG      = "#1e1e2e"
    BG2     = "#2a2a3e"
    BG3     = "#313145"
    ACCENT  = "#7c8cf8"
    FAULT   = "#f38ba8"
    HIT     = "#a6e3a1"
    NEW_PG  = "#89b4fa"
    TEXT    = "#cdd6f4"
    TEXT2   = "#6c7086"
    YELLOW  = "#f9e2af"
    BORDER  = "#45475a"
    WHITE   = "#ffffff"

    def __init__(self):
        super().__init__()
        self.title("Virtual Memory Page Replacement Simulator — OS_VME_08 Group 5")
        self.geometry("1280x820")
        self.minsize(1100, 700)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        # State
        self.frame_size = tk.IntVar(value=3)
        self.ref_string = []
        self.last_steps = []
        self.last_algo  = ""
        self.last_exec  = 0.0

        # Init sample files
        os.makedirs("input",  exist_ok=True)
        os.makedirs("output", exist_ok=True)
        if not os.path.exists("input/input.csv"):
            FileHandler.create_sample("input/input.csv")
        if not os.path.exists("input/belady_test.csv"):
            FileHandler.create_belady("input/belady_test.csv")

        self._load_default()
        self._build_ui()

    # ---- Load default input ------------------------------------
    def _load_default(self):
        try:
            fs, rs = FileHandler.read_input("input/input.csv")
            self.frame_size.set(fs)
            self.ref_string = rs
        except Exception:
            self.frame_size.set(3)
            self.ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3]

    # ============================================================
    #  BUILD UI
    # ============================================================
    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        hf = tk.Frame(self, bg=self.BG2, pady=10)
        hf.pack(fill="x")
        tk.Label(hf,
                 text="Virtual Memory Page Replacement Simulator",
                 font=("Consolas", 18, "bold"),
                 bg=self.BG2, fg=self.ACCENT).pack()
        tk.Label(hf,
                 text="OS_VME_08  ·  Group 5  ·  HCMUTRANS  ·  FIFO | LRU | OPT",
                 font=("Consolas", 10),
                 bg=self.BG2, fg=self.TEXT2).pack()

    def _build_body(self):
        body = tk.Frame(self, bg=self.BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        left = tk.Frame(body, bg=self.BG2, width=300)
        left.pack(side="left", fill="y", padx=(10,5), pady=10)
        left.pack_propagate(False)
        self._build_left(left)

        right = tk.Frame(body, bg=self.BG)
        right.pack(side="left", fill="both", expand=True, padx=(5,10), pady=10)
        self._build_right(right)

    # ---- LEFT PANEL --------------------------------------------
    def _build_left(self, parent):
        def sec(txt):
            tk.Label(parent, text=txt,
                     font=("Consolas", 9, "bold"),
                     bg=self.BG2, fg=self.TEXT2).pack(anchor="w", padx=12, pady=(12,2))

        def hline():
            tk.Frame(parent, bg=self.BORDER, height=1).pack(fill="x", padx=8, pady=3)

        tk.Label(parent, text="⚙  Configuration",
                 font=("Consolas", 12, "bold"),
                 bg=self.BG2, fg=self.WHITE).pack(pady=(14,4))
        hline()

        # Input file
        sec("INPUT FILE")
        self.file_lbl = tk.Label(parent, text="input/input.csv",
                                 font=("Consolas", 9), bg=self.BG3,
                                 fg=self.YELLOW, wraplength=260,
                                 justify="left", padx=8, pady=4)
        self.file_lbl.pack(fill="x", padx=8, pady=2)
        tk.Button(parent, text="Load CSV file",
                  command=self._load_csv,
                  font=("Consolas", 10), bg=self.BG3,
                  fg=self.ACCENT, relief="flat",
                  cursor="hand2", pady=5).pack(fill="x", padx=8, pady=2)

        # Frame size
        sec("FRAME SIZE")
        row = tk.Frame(parent, bg=self.BG2)
        row.pack(fill="x", padx=8)
        tk.Scale(row, from_=1, to=10,
                 variable=self.frame_size,
                 orient="horizontal",
                 bg=self.BG2, fg=self.TEXT,
                 highlightthickness=0,
                 troughcolor=self.BG3,
                 font=("Consolas", 9)).pack(side="left", fill="x", expand=True)
        tk.Label(row, textvariable=self.frame_size,
                 width=3, font=("Consolas", 12, "bold"),
                 bg=self.BG2, fg=self.YELLOW).pack(side="left", padx=4)

        # Reference string
        sec("REFERENCE STRING")
        self.ref_entry = tk.Text(parent, height=3, width=28,
                                 font=("Consolas", 10), bg=self.BG3,
                                 fg=self.TEXT, insertbackground=self.TEXT,
                                 relief="flat", padx=6, pady=4)
        self.ref_entry.pack(fill="x", padx=8, pady=2)
        self.ref_entry.insert("1.0", ",".join(map(str, self.ref_string)))
        tk.Label(parent, text="Comma-separated page numbers",
                 font=("Consolas", 8),
                 bg=self.BG2, fg=self.TEXT2).pack(anchor="w", padx=12)

        hline()

        # Run buttons
        sec("RUN ALGORITHM")
        for label, algo, color in [
            ("▶  Run FIFO",  "FIFO",  "#89b4fa"),
            ("▶  Run LRU",   "LRU",   "#a6e3a1"),
            ("▶  Run OPT",   "OPT",   "#cba6f7"),
        ]:
            tk.Button(parent, text=label,
                      command=lambda a=algo: self._run(a),
                      font=("Consolas", 11, "bold"),
                      bg=self.BG3, fg=color,
                      relief="flat", cursor="hand2", pady=7
                      ).pack(fill="x", padx=8, pady=3)

        tk.Button(parent, text="⚡  Run ALL & Compare",
                  command=self._run_all,
                  font=("Consolas", 11, "bold"),
                  bg=self.ACCENT, fg=self.BG,
                  relief="flat", cursor="hand2", pady=8
                  ).pack(fill="x", padx=8, pady=4)

        hline()

        tk.Button(parent, text="💾  Export output.csv",
                  command=self._export,
                  font=("Consolas", 10), bg=self.BG3,
                  fg=self.YELLOW, relief="flat",
                  cursor="hand2", pady=6).pack(fill="x", padx=8, pady=2)

        tk.Button(parent, text="🧪  Run Unit Tests",
                  command=self._run_tests,
                  font=("Consolas", 10), bg=self.BG3,
                  fg=self.YELLOW, relief="flat",
                  cursor="hand2", pady=6).pack(fill="x", padx=8, pady=2)

        tk.Button(parent, text="👥  Team Info",
                  command=self._show_team,
                  font=("Consolas", 10), bg=self.BG3,
                  fg=self.TEXT2, relief="flat",
                  cursor="hand2", pady=6).pack(fill="x", padx=8, pady=2)

    # ---- RIGHT PANEL -------------------------------------------
    def _build_right(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                         background=self.BG3, foreground=self.TEXT2,
                         font=("Consolas", 10, "bold"), padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", self.ACCENT)],
                  foreground=[("selected", self.BG)])

        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill="both", expand=True)

        self.tab_gantt   = tk.Frame(self.nb, bg=self.BG)
        self.tab_compare = tk.Frame(self.nb, bg=self.BG)
        self.tab_stats   = tk.Frame(self.nb, bg=self.BG)

        self.nb.add(self.tab_gantt,   text="  Gantt Chart  ")
        self.nb.add(self.tab_compare, text="  Comparison  ")
        self.nb.add(self.tab_stats,   text="  Statistics  ")

        self._build_gantt_tab(self.tab_gantt)
        self._build_compare_tab(self.tab_compare)
        self._build_stats_tab(self.tab_stats)

    def _build_gantt_tab(self, parent):
        self.gantt_title = tk.Label(parent,
                                    text="Select an algorithm and click Run",
                                    font=("Consolas", 12, "bold"),
                                    bg=self.BG, fg=self.TEXT2)
        self.gantt_title.pack(pady=(10, 4))

        pills = tk.Frame(parent, bg=self.BG)
        pills.pack(pady=(0, 8))
        self.lbl_faults = self._pill(pills, "—", "Page Faults", self.FAULT)
        self.lbl_hits   = self._pill(pills, "—", "Page Hits",   self.HIT)
        self.lbl_rate   = self._pill(pills, "—", "Hit Rate",    self.ACCENT)
        self.lbl_time   = self._pill(pills, "—", "Exec Time",   self.YELLOW)

        leg = tk.Frame(parent, bg=self.BG)
        leg.pack(pady=(0, 6))
        for color, label in [
            (self.FAULT,  "Page Fault"),
            (self.HIT,    "Page Hit"),
            (self.NEW_PG, "New Frame"),
            (self.BG3,    "Unchanged"),
        ]:
            tk.Frame(leg, bg=color, width=12, height=12).pack(side="left", padx=(10,3))
            tk.Label(leg, text=label, font=("Consolas", 9),
                     bg=self.BG, fg=self.TEXT2).pack(side="left", padx=(0,8))

        wrap = tk.Frame(parent, bg=self.BORDER, bd=1)
        wrap.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.gantt_canvas = tk.Canvas(wrap, bg=self.BG2, highlightthickness=0)
        hbar = tk.Scrollbar(wrap, orient="horizontal", command=self.gantt_canvas.xview)
        vbar = tk.Scrollbar(wrap, orient="vertical",   command=self.gantt_canvas.yview)
        self.gantt_canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side="bottom", fill="x")
        vbar.pack(side="right",  fill="y")
        self.gantt_canvas.pack(fill="both", expand=True)

    def _build_compare_tab(self, parent):
        tk.Label(parent, text="Algorithm Comparison",
                 font=("Consolas", 13, "bold"),
                 bg=self.BG, fg=self.WHITE).pack(pady=(14, 4))
        tk.Label(parent, text='Click "Run ALL & Compare" to see results',
                 font=("Consolas", 10),
                 bg=self.BG, fg=self.TEXT2).pack()
        self.compare_frame = tk.Frame(parent, bg=self.BG)
        self.compare_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _build_stats_tab(self, parent):
        tk.Label(parent, text="Proof of Correctness",
                 font=("Consolas", 13, "bold"),
                 bg=self.BG, fg=self.WHITE).pack(pady=(14, 2))
        tk.Label(parent,
                 text="Compared with OS Concepts 10th Edition — Silberschatz et al.",
                 font=("Consolas", 9),
                 bg=self.BG, fg=self.TEXT2).pack()
        self.stats_frame = tk.Frame(parent, bg=self.BG)
        self.stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _pill(self, parent, val, label, color):
        f = tk.Frame(parent, bg=self.BG3, padx=14, pady=6)
        f.pack(side="left", padx=6)
        v = tk.Label(f, text=val, font=("Consolas", 18, "bold"),
                     bg=self.BG3, fg=color)
        v.pack()
        tk.Label(f, text=label, font=("Consolas", 9),
                 bg=self.BG3, fg=self.TEXT2).pack()
        return v

    def _build_statusbar(self):
        self.status_var = tk.StringVar(
            value="Ready  |  OS_VME_08 Group 5  |  HCMUTRANS")
        tk.Label(self, textvariable=self.status_var,
                 font=("Consolas", 9), bg=self.BG3,
                 fg=self.TEXT2, anchor="w",
                 padx=12, pady=4).pack(fill="x", side="bottom")

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.update_idletasks()

    # ============================================================
    #  ACTIONS
    # ============================================================
    def _load_csv(self):
        path = filedialog.askopenfilename(
            title="Select input CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            fs, rs = FileHandler.read_input(path)
            self.frame_size.set(fs)
            self.ref_string = rs
            self.file_lbl.config(text=os.path.basename(path))
            self.ref_entry.delete("1.0", "end")
            self.ref_entry.insert("1.0", ",".join(map(str, rs)))
            self._set_status(f"Loaded: {path}  |  {len(rs)} pages  |  {fs} frames")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _parse_ref(self):
        raw    = self.ref_entry.get("1.0", "end").strip()
        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        result = []
        for t in tokens:
            try:
                v = int(t)
                if v < 0:
                    raise ValueError(f"So trang am: {v}")
                result.append(v)
            except ValueError as e:
                raise ValueError(f"Reference string khong hop le: {e}")
        if not result:
            raise ValueError("Reference string trong.")
        return result

    def _run(self, algo_name):
        try:
            refs = self._parse_ref()
            n    = self.frame_size.get()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e)); return

        self.ref_string = refs
        self._set_status(f"Running {algo_name}...")

        algos  = {"FIFO": FIFO, "LRU": LRU, "OPT": OPT}
        colors = {"FIFO": self.NEW_PG, "LRU": self.HIT, "OPT": "#cba6f7"}

        t0    = time.perf_counter()
        steps = algos[algo_name].run(refs, n)
        ms    = (time.perf_counter() - t0) * 1000

        self.last_steps = steps
        self.last_algo  = algo_name
        self.last_exec  = ms

        self._draw_gantt(algo_name, steps, n, colors[algo_name])
        self._update_stats(algo_name, steps, refs, n)
        self.nb.select(0)
        faults = sum(1 for s in steps if s.is_fault)
        self._set_status(
            f"{algo_name}  |  {faults} faults  "
            f"|  {len(steps)-faults} hits  |  {ms:.3f} ms"
        )

    def _run_all(self):
        try:
            refs = self._parse_ref()
            n    = self.frame_size.get()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e)); return

        self.ref_string = refs
        self._set_status("Running all algorithms...")

        results, times = {}, {}
        for Cls, name in [(FIFO,"FIFO"),(LRU,"LRU"),(OPT,"OPT")]:
            t0 = time.perf_counter()
            results[name] = Cls.run(refs, n)
            times[name]   = (time.perf_counter() - t0) * 1000

        self.last_steps = results["OPT"]
        self.last_algo  = "OPT"
        self.last_exec  = times["OPT"]

        self._draw_gantt("ALL (showing OPT)", results["OPT"], n, "#cba6f7")
        self._draw_comparison(results, times, refs, n)
        self._update_stats("ALL", results["OPT"], refs, n)
        self.nb.select(1)
        self._set_status("All algorithms done. See Comparison tab.")

    # ============================================================
    #  DRAW GANTT
    # ============================================================
    def _draw_gantt(self, algo_name, steps, n, header_color):
        c = self.gantt_canvas
        c.delete("all")
        if not steps:
            c.create_text(300, 100, text="No data",
                          fill=self.TEXT2, font=("Consolas", 12))
            return

        CW, CH   = 44, 36
        LABEL_W  = 90
        PAD_TOP  = 20
        PAD_LEFT = 10

        total_w = PAD_LEFT + LABEL_W + len(steps) * CW + 20
        total_h = PAD_TOP  + (n + 3) * CH + 20
        c.configure(scrollregion=(0, 0, total_w, total_h))

        faults = sum(1 for s in steps if s.is_fault)
        hits   = len(steps) - faults
        hr     = hits / len(steps) * 100
        self.lbl_faults.config(text=str(faults))
        self.lbl_hits.config(text=str(hits))
        self.lbl_rate.config(text=f"{hr:.1f}%")
        self.lbl_time.config(text=f"{self.last_exec:.2f}ms")
        self.gantt_title.config(text=f"Algorithm: {algo_name}", fg=header_color)

        def cell(col, row, text, bg, fg="#ffffff", bold=False):
            x0 = PAD_LEFT + LABEL_W + col * CW
            y0 = PAD_TOP  + row * CH
            x1, y1 = x0+CW-1, y0+CH-1
            c.create_rectangle(x0, y0, x1, y1,
                                fill=bg, outline=self.BORDER, width=1)
            font = ("Consolas", 10, "bold") if bold else ("Consolas", 10)
            c.create_text((x0+x1)//2, (y0+y1)//2,
                          text=str(text), fill=fg, font=font)

        def row_lbl(row, text):
            y0 = PAD_TOP + row * CH
            y1 = y0 + CH
            c.create_rectangle(PAD_LEFT, y0, PAD_LEFT+LABEL_W-1, y1,
                                fill=self.BG3, outline=self.BORDER)
            c.create_text(PAD_LEFT+LABEL_W//2, (y0+y1)//2,
                          text=text, fill=self.TEXT2,
                          font=("Consolas", 9))

        row_lbl(0, "Page Ref")
        for f in range(n):
            row_lbl(f+1, f"Frame {f+1}")
        row_lbl(n+1, "Fault / Hit")

        for i, s in enumerate(steps):
            # Step numbers
            x0 = PAD_LEFT + LABEL_W + i * CW
            c.create_text(x0+CW//2, PAD_TOP//2+4,
                          text=str(i+1), fill=self.TEXT2,
                          font=("Consolas", 8))
            # Page row
            cell(i, 0, s.page,
                 self.FAULT if s.is_fault else self.HIT,
                 self.BG, bold=True)
            # Frame rows
            for f in range(n):
                if f < len(s.frames) and s.frames[f] != -1:
                    is_new = s.is_fault and s.frames[f] == s.page
                    cell(i, f+1, s.frames[f],
                         self.NEW_PG if is_new else self.BG3,
                         self.BG    if is_new else self.TEXT)
                else:
                    cell(i, f+1, "·", self.BG2, self.TEXT2)
            # F/H row
            cell(i, n+1,
                 "F" if s.is_fault else "H",
                 self.FAULT if s.is_fault else self.HIT,
                 self.BG, bold=True)

    # ============================================================
    #  DRAW COMPARISON
    # ============================================================
    def _draw_comparison(self, results, times, refs, n):
        for w in self.compare_frame.winfo_children():
            w.destroy()

        faults = {nm: sum(1 for s in st if s.is_fault)
                  for nm, st in results.items()}
        hits   = {nm: len(refs) - faults[nm] for nm in faults}
        rates  = {nm: hits[nm] / len(refs) * 100 for nm in faults}
        max_f  = max(faults.values()) or 1
        colors = {"FIFO": self.NEW_PG, "LRU": self.HIT, "OPT": "#cba6f7"}

        tk.Label(self.compare_frame,
                 text=f"Input: {len(refs)} pages  |  {n} frames",
                 font=("Consolas", 11),
                 bg=self.BG, fg=self.TEXT2).pack(pady=(0,14))

        for name in ["FIFO","LRU","OPT"]:
            row = tk.Frame(self.compare_frame, bg=self.BG)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=name, width=6,
                     font=("Consolas", 13, "bold"),
                     bg=self.BG, fg=colors[name]).pack(side="left")
            bar_f = tk.Frame(row, bg=self.BORDER, height=32, width=500)
            bar_f.pack(side="left", padx=10)
            bar_f.pack_propagate(False)
            fill_w = int(faults[name] / max_f * 498)
            tk.Frame(bar_f, bg=colors[name],
                     width=fill_w, height=30).place(x=1, y=1)
            info = (f"  {faults[name]} faults  |  {hits[name]} hits  |  "
                    f"{rates[name]:.1f}% hit rate  |  {times[name]:.3f} ms")
            tk.Label(row, text=info, font=("Consolas", 10),
                     bg=self.BG, fg=self.TEXT).pack(side="left")

        best = min(faults, key=faults.get)
        tk.Frame(self.compare_frame, bg=self.BORDER,
                 height=1).pack(fill="x", pady=14)
        tk.Label(self.compare_frame,
                 text=f"✓  Best: {best}  ({faults[best]} faults)",
                 font=("Consolas", 13, "bold"),
                 bg=self.BG, fg=colors[best]).pack()

        if faults["FIFO"] > faults["OPT"]:
            tk.Label(self.compare_frame,
                     text="⚠  FIFO may exhibit Belady's Anomaly",
                     font=("Consolas", 10),
                     bg=self.BG, fg=self.YELLOW).pack(pady=4)

        # Table
        tk.Frame(self.compare_frame, bg=self.BORDER,
                 height=1).pack(fill="x", pady=10)
        hdr = tk.Frame(self.compare_frame, bg=self.BG)
        hdr.pack(fill="x")
        for col, w in [("Algorithm",14),("Faults",10),
                       ("Hits",10),("Hit Rate",12),("Exec (ms)",12)]:
            tk.Label(hdr, text=col, width=w,
                     font=("Consolas", 10, "bold"),
                     bg=self.BG3, fg=self.ACCENT,
                     relief="flat", pady=4).pack(side="left", padx=1)
        for name in ["FIFO","LRU","OPT"]:
            row2 = tk.Frame(self.compare_frame, bg=self.BG)
            row2.pack(fill="x", pady=1)
            for val, w in [
                (name,14),(faults[name],10),(hits[name],10),
                (f"{rates[name]:.1f}%",12),(f"{times[name]:.3f}",12)
            ]:
                tk.Label(row2, text=str(val), width=w,
                         font=("Consolas", 10),
                         bg=self.BG2, fg=colors[name],
                         relief="flat", pady=4).pack(side="left", padx=1)

    # ============================================================
    #  STATS TAB
    # ============================================================
    def _update_stats(self, algo_name, steps, refs, n):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        # Proof section
        pf = tk.LabelFrame(self.stats_frame,
                            text="  Proof vs OS Concepts 10th Edition  ",
                            font=("Consolas", 10, "bold"),
                            bg=self.BG, fg=self.ACCENT,
                            labelanchor="nw", relief="flat", bd=1)
        pf.pack(fill="x", pady=(0,10))

        tb_refs = [7,0,1,2,0,3,0,4,2,3,0,3]
        tb_n    = 3
        algos_map = {"FIFO": FIFO, "LRU": LRU, "OPT": OPT}

        hdr = tk.Frame(pf, bg=self.BG)
        hdr.pack(fill="x", padx=8, pady=(8,2))
        for col, wid in [("Algorithm",12),("Got",8),("Status",10)]:
            tk.Label(hdr, text=col, width=wid,
                     font=("Consolas", 10, "bold"),
                     bg=self.BG3, fg=self.TEXT2,
                     pady=3).pack(side="left", padx=1)

        for name in ["FIFO","LRU","OPT"]:
            got = algos_map[name].count_faults(
                algos_map[name].run(tb_refs, tb_n))
            row = tk.Frame(pf, bg=self.BG)
            row.pack(fill="x", padx=8, pady=1)
            for val, wid in [(name,12),(str(got),8)]:
                tk.Label(row, text=val, width=wid,
                         font=("Consolas", 10),
                         bg=self.BG2, fg=self.TEXT,
                         pady=3).pack(side="left", padx=1)
            tk.Label(row, text=f"{got} faults", width=10,
                     font=("Consolas", 10, "bold"),
                     bg=self.BG2, fg=self.HIT,
                     pady=3).pack(side="left", padx=1)

        tk.Label(pf,
                 text="Reference: 7,0,1,2,0,3,0,4,2,3,0,3  |  3 frames",
                 font=("Consolas", 8),
                 bg=self.BG, fg=self.TEXT2).pack(padx=8, pady=(2,8))

        # Current run
        if steps:
            faults = sum(1 for s in steps if s.is_fault)
            hits   = len(steps) - faults
            cur = tk.LabelFrame(self.stats_frame,
                                text=f"  Current Run: {algo_name}  ",
                                font=("Consolas", 10, "bold"),
                                bg=self.BG, fg=self.YELLOW,
                                labelanchor="nw", relief="flat", bd=1)
            cur.pack(fill="x")
            for lbl, val, color in [
                ("Total References", len(steps),            self.TEXT),
                ("Frame Size",       n,                     self.TEXT),
                ("Page Faults",      faults,                self.FAULT),
                ("Page Hits",        hits,                  self.HIT),
                ("Hit Rate",         f"{hits/len(steps)*100:.2f}%", self.ACCENT),
                ("Fault Rate",       f"{faults/len(steps)*100:.2f}%", self.FAULT),
                ("Exec Time",        f"{self.last_exec:.3f} ms",    self.YELLOW),
            ]:
                r = tk.Frame(cur, bg=self.BG)
                r.pack(fill="x", padx=8, pady=1)
                tk.Label(r, text=lbl, width=20, anchor="w",
                         font=("Consolas", 10),
                         bg=self.BG, fg=self.TEXT2).pack(side="left")
                tk.Label(r, text=str(val),
                         font=("Consolas", 10, "bold"),
                         bg=self.BG, fg=color).pack(side="left")

    # ============================================================
    #  EXPORT
    # ============================================================
    def _export(self):
        if not self.last_steps:
            messagebox.showwarning("Export", "No results. Run an algorithm first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"output_{self.last_algo}.csv",
            filetypes=[("CSV files","*.csv")]
        )
        if not path:
            return
        try:
            refs = self._parse_ref()
            FileHandler.write_output(path, self.last_algo,
                                     self.frame_size.get(),
                                     refs, self.last_steps, self.last_exec)
            messagebox.showinfo("Export", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ============================================================
    #  UNIT TESTS WINDOW
    # ============================================================
    def _run_tests(self):
        win = tk.Toplevel(self)
        win.title("Unit Tests — OS_VME_08 Group 5")
        win.geometry("600x520")
        win.configure(bg=self.BG)
        tk.Label(win, text="Unit Test Results",
                 font=("Consolas", 13, "bold"),
                 bg=self.BG, fg=self.ACCENT).pack(pady=(14,4))
        tk.Label(win, text="Verified against OS Concepts 10th Ed.",
                 font=("Consolas", 9),
                 bg=self.BG, fg=self.TEXT2).pack()

        frame = tk.Frame(win, bg=self.BG)
        frame.pack(fill="both", expand=True, padx=16, pady=10)

        results, passed, failed = TestRunner().run_all()
        for status, name in results:
            row = tk.Frame(frame, bg=self.BG)
            row.pack(fill="x", pady=2)
            color = self.HIT if status == "PASS" else self.FAULT
            tk.Label(row, text=f"[{status}]", width=7,
                     font=("Consolas", 10, "bold"),
                     bg=self.BG2, fg=color).pack(side="left", padx=(0,6))
            tk.Label(row, text=name, font=("Consolas", 10),
                     bg=self.BG, fg=self.TEXT).pack(side="left")

        tk.Frame(win, bg=self.BORDER, height=1).pack(fill="x", padx=16)
        sc = self.HIT if failed == 0 else self.FAULT
        tk.Label(win,
                 text=f"Passed: {passed}  |  Failed: {failed}  |  Total: {passed+failed}",
                 font=("Consolas", 11, "bold"),
                 bg=self.BG, fg=sc).pack(pady=10)

    # ============================================================
    #  TEAM INFO WINDOW
    # ============================================================
    def _show_team(self):
        win = tk.Toplevel(self)
        win.title("Team Info — OS_VME_08 Group 5")
        win.geometry("560x400")
        win.configure(bg=self.BG)
        tk.Label(win, text="OS_VME_08 — Nhóm 5",
                 font=("Consolas", 14, "bold"),
                 bg=self.BG, fg=self.ACCENT).pack(pady=(14,2))
        tk.Label(win,
                 text="Đại học Giao thông Vận tải TP.HCM  |  Mã lớp: 7480201390613",
                 font=("Consolas", 9),
                 bg=self.BG, fg=self.TEXT2).pack()
        tk.Frame(win, bg=self.BORDER, height=1).pack(fill="x", padx=16, pady=10)
        members = [
            ("Phan Đình Phát",        "060206002816", "Algorithm Developer"),
            ("Nguyễn Thị Xuân Tuyền", "054306001845", "Data & File Handler"),
            ("Nguyễn Thanh Tuấn",     "051206002660", "GUI Developer"),
            ("Dương Trọng Nghĩa",     "066206008908", "Tester & Integrator"),
            ("Kim Nhựt Hoàng",        "084206006510", "Documentation"),
        ]
        for i, (name, sid, role) in enumerate(members, 1):
            row = tk.Frame(win, bg=self.BG2 if i%2==0 else self.BG)
            row.pack(fill="x", padx=16, pady=1)
            tk.Label(row, text=f"{i}.", width=3,
                     font=("Consolas", 10, "bold"),
                     bg=row["bg"], fg=self.ACCENT).pack(side="left", padx=(8,0))
            tk.Label(row, text=name, width=24, anchor="w",
                     font=("Consolas", 10, "bold"),
                     bg=row["bg"], fg=self.YELLOW).pack(side="left")
            tk.Label(row, text=sid, width=14,
                     font=("Consolas", 9),
                     bg=row["bg"], fg=self.TEXT2).pack(side="left")
            tk.Label(row, text=role, font=("Consolas", 9),
                     bg=row["bg"], fg=self.HIT).pack(side="left", padx=8)
        tk.Frame(win, bg=self.BORDER, height=1).pack(fill="x", padx=16, pady=10)
        tk.Label(win,
                 text="Ref: OS Concepts 10th Ed. — Silberschatz, Galvin, Gagne",
                 font=("Consolas", 9),
                 bg=self.BG, fg=self.TEXT2).pack()
