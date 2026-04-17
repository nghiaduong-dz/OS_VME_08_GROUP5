"""
GUI/display.py  
OS_VME_08 — Group 5 — HCMUTRANS
"""
from __future__ import annotations
import os, sys, time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from GUI.widgets    import C, F, HLine, build_notebook_style
from GUI.gantt      import GanttTab
from GUI.compare    import CompareTab

from algorithms.fifo     import FIFO
from algorithms.lru      import LRU
from algorithms.opt      import OPT
from algorithms.registry import AlgoRegistry
from utils.file_handler  import FileHandler
from models.step         import Step
from unit_tests.test_algorithms import TestRunner


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Virtual Memory Page Replacement Simulator — OS_VME_08 Group 5")
        self.geometry("1280x800")
        self.minsize(1050, 650)
        self.configure(bg=C.BG)
        self.resizable(True, True)

        self.frame_size  = tk.IntVar(value=3)
        self.ref_string  : list[int] = []
        self.last_steps  : list[Step] = []
        self.last_algo   : str = ""
        self.last_exec   : float = 0.0
        self._all_results: dict = {}

        os.makedirs("input",  exist_ok=True)
        os.makedirs("output", exist_ok=True)
        FileHandler.create_sample("input/input.csv")
        FileHandler.create_belady("input/belady_test.csv")
        self._load_default()

        build_notebook_style()
        self._build_ui()
        self._style_ttk()

    # ── ttk extra styling ──────────────────────────────────────
    def _style_ttk(self):
        s = ttk.Style()
        # General scrollbar (used in tabs)
        s.configure("TScrollbar",
                     troughcolor=C.BG2, background=C.SURFACE,
                     arrowcolor=C.TEXT2, borderwidth=0,
                     relief="flat")
        s.map("TScrollbar",
              background=[("active", C.ACCENT), ("!active", C.SURFACE)])

        # Slim dark scrollbar for the left sidebar
        s.configure("Left.Vertical.TScrollbar",
                     troughcolor=C.BG2,
                     background=C.BG3,
                     arrowcolor=C.BG2,       # hide arrows (same as trough)
                     arrowsize=0,
                     borderwidth=0,
                     relief="flat",
                     width=6)               # thin strip
        s.map("Left.Vertical.TScrollbar",
              background=[("active", C.ACCENT), ("!active", C.SURFACE)])

    # ── Default load ───────────────────────────────────────────────────
    def _load_default(self):
        try:
            fs, rs = FileHandler.read_input("input/input.csv")
            self.frame_size.set(fs)
            self.ref_string = rs
        except Exception:
            self.frame_size.set(3)
            self.ref_string = [7,0,1,2,0,3,0,4,2,3,0,3]

    # ── Build UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        hf = tk.Frame(self, bg=C.BG2, pady=10)
        hf.pack(fill="x")

        # Info button — top right corner
        info_btn = tk.Button(hf, text="👥  Nhóm 5 - Info",
                              font=F(9, bold=True),
                              bg=C.SURFACE, fg=C.YELLOW,
                              relief="flat", cursor="hand2",
                              padx=12, pady=5,
                              activebackground=C.BG3,
                              activeforeground=C.YELLOW,
                              command=self._show_team)
        info_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=8)
        self._hover(info_btn, C.BG3, C.SURFACE, C.YELLOW)

        tk.Label(hf, text="Virtual Memory Page Replacement Simulator",
                 font=F(17, bold=True), bg=C.BG2, fg=C.ACCENT).pack()
        tk.Label(hf,
                 text="OS_VME_08  ·  Group 5  ·  HCMUTRANS  ·  FIFO | LRU | OPT",
                 font=F(9), bg=C.BG2, fg=C.TEXT2).pack()

    def _build_body(self):
        pane = tk.PanedWindow(self, orient="horizontal",
                               bg=C.BORDER, sashwidth=4, sashrelief="flat")
        pane.pack(fill="both", expand=True, padx=6, pady=6)

        left = tk.Frame(pane, bg=C.BG2, width=268)
        left.pack_propagate(False)
        self._build_left(left)
        pane.add(left, minsize=230)

        right = tk.Frame(pane, bg=C.BG)
        self._build_right(right)
        pane.add(right, minsize=680)

    # ── LEFT PANEL (scrollable) ────────────────────────────────────
    def _build_left(self, outer_frame):
        """Wrap nội dung trong Canvas → cuộn được khi nội dung dài."""
        # Canvas + scrollbar
        cv  = tk.Canvas(outer_frame, bg=C.BG2, highlightthickness=0)
        vsb = ttk.Scrollbar(outer_frame, orient="vertical",
                             command=cv.yview,
                             style="Left.Vertical.TScrollbar")
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        # Inner frame that actually holds widgets
        p   = tk.Frame(cv, bg=C.BG2)
        cw  = cv.create_window((0, 0), window=p, anchor="nw")

        def _on_frame_cfg(e):
            cv.configure(scrollregion=cv.bbox("all"))
        def _on_canvas_cfg(e):
            cv.itemconfig(cw, width=e.width)
        p.bind("<Configure>", _on_frame_cfg)
        cv.bind("<Configure>", _on_canvas_cfg)

        # Mousewheel scrolling
        def _mw(e):
            cv.yview_scroll(int(-1 * (e.delta / 120)), "units")
        cv.bind_all("<MouseWheel>", _mw)

        self._left_build(p)

    def _left_build(self, p):
        """Actual left-panel widgets, placed into the scrollable inner frame."""

        def sec(txt):
            tk.Label(p, text=txt, font=F(8, bold=True),
                     bg=C.BG2, fg=C.TEXT2).pack(
                anchor="w", padx=14, pady=(12, 2))

        def hline():
            HLine(p).pack(fill="x", padx=10, pady=4)

        # Title
        tk.Label(p, text="⚙  Configuration",
                 font=F(12, bold=True), bg=C.BG2, fg=C.WHITE
                 ).pack(pady=(14, 4))
        hline()

        # ── Input file ──
        sec("INPUT FILE")
        self._file_lbl = tk.Label(p, text="input/input.csv",
                                   font=F(9), bg=C.BG3, fg=C.YELLOW,
                                   wraplength=240, justify="left",
                                   padx=8, pady=5)
        self._file_lbl.pack(fill="x", padx=10, pady=(0, 3))
        self._lbtn(p, "📂  Load CSV file", self._load_csv, C.ACCENT)

        # ── Frame size slider (custom) ──
        sec("FRAME SIZE")
        self._build_frame_slider(p)

        # ── Reference string ──
        sec("REFERENCE STRING")
        self._ref_entry = tk.Text(p, height=3, width=26,
                                   font=F(10), bg=C.BG3, fg=C.TEXT,
                                   insertbackground=C.TEXT,
                                   relief="flat", padx=6, pady=5,
                                   selectbackground=C.SURFACE)
        self._ref_entry.pack(fill="x", padx=10, pady=(0, 2))
        self._ref_entry.insert("1.0", ",".join(map(str, self.ref_string)))
        tk.Label(p, text="Comma-separated page numbers",
                 font=F(8), bg=C.BG2, fg=C.TEXT2
                 ).pack(anchor="w", padx=14, pady=(0, 2))

        hline()

        # ── Run buttons ──
        sec("RUN ALGORITHM")
        for label, algo, col in [
            ("▶  Run FIFO", "FIFO", C.ALGO["FIFO"]),
            ("▶  Run LRU",  "LRU",  C.ALGO["LRU"]),
            ("▶  Run OPT",  "OPT",  C.ALGO["OPT"]),
        ]:
            self._lbtn(p, label, lambda a=algo: self._run(a), col, size=11)

        # Run ALL
        run_all = tk.Button(p, text="⚡  Run ALL & Compare",
                             command=self._run_all,
                             font=F(11, bold=True),
                             bg=C.ACCENT, fg=C.BG,
                             relief="flat", cursor="hand2", pady=9,
                             activebackground=C.MAUVE,
                             activeforeground=C.BG)
        run_all.pack(fill="x", padx=10, pady=5)
        self._hover(run_all, C.MAUVE, C.ACCENT, C.BG)

        hline()

        # ── Export ──
        sec("EXPORT  —  Chế độ 1: từng file")
        for nm, col in [("FIFO", C.ALGO["FIFO"]),
                        ("LRU",  C.ALGO["LRU"]),
                        ("OPT",  C.ALGO["OPT"])]:
            self._lbtn(p, f"💾  Export {nm} CSV",
                       lambda n=nm: self._export_single(n), col, size=9)

        sec("EXPORT  —  Chế độ 2: cả 3 file")
        batch_btn = tk.Button(p, text="📦  Xuất 3 CSV (FIFO · LRU · OPT)",
                               command=self._batch_csv,
                               font=F(10, bold=True),
                               bg=C.BG3, fg=C.YELLOW,
                               relief="flat", cursor="hand2",
                               pady=9, padx=8,
                               activebackground=C.SURFACE,
                               activeforeground=C.YELLOW)
        batch_btn.pack(fill="x", padx=10, pady=3)
        self._hover(batch_btn, C.SURFACE, C.BG3, C.YELLOW)

        hline()

        # ── Tools ──
        sec("TOOLS")
        self._lbtn(p, "🧪  Run Unit Tests", self._open_tests, C.TEXT2, size=9)

    # ── Custom frame-size slider ────────────────────────────────────────
    def _build_frame_slider(self, parent):
        """Slider row với số hiển thị lớn và rõ."""
        outer = tk.Frame(parent, bg=C.BG2)
        outer.pack(fill="x", padx=10, pady=(0, 4))

        # Value badge (left)
        badge = tk.Frame(outer, bg=C.ACCENT, padx=10, pady=4)
        badge.pack(side="left")
        self._fs_lbl = tk.Label(badge, textvariable=self.frame_size,
                                 font=F(14, bold=True),
                                 bg=C.ACCENT, fg=C.BG, width=2)
        self._fs_lbl.pack()

        # Slider
        slider = tk.Scale(outer, from_=1, to=10,
                          variable=self.frame_size,
                          orient="horizontal",
                          showvalue=False,
                          bg=C.BG2, fg=C.TEXT,
                          troughcolor=C.BG3,
                          activebackground=C.ACCENT,
                          highlightthickness=0,
                          sliderlength=22,
                          width=12,
                          font=F(8))
        slider.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Tick labels
        tick_row = tk.Frame(parent, bg=C.BG2)
        tick_row.pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(tick_row, text="1", font=F(8),
                 bg=C.BG2, fg=C.TEXT2).pack(side="left")
        tk.Label(tick_row, text="10", font=F(8),
                 bg=C.BG2, fg=C.TEXT2).pack(side="right")

        # Update badge bg on change
        def _on_change(*_):
            self._fs_lbl.config(bg=C.ACCENT)
            badge.config(bg=C.ACCENT)
        self.frame_size.trace_add("write", _on_change)

    # ── helpers ────────────────────────────────────────────────────────
    def _lbtn(self, parent, text, cmd, fg, size=10):
        b = tk.Button(parent, text=text, command=cmd,
                      font=F(size, bold=True),
                      bg=C.BG3, fg=fg,
                      relief="flat", cursor="hand2",
                      pady=7, padx=8,
                      activebackground=C.SURFACE,
                      activeforeground=fg)
        b.pack(fill="x", padx=10, pady=2)
        self._hover(b, C.SURFACE, C.BG3, fg)
        return b

    @staticmethod
    def _hover(btn, enter_bg, leave_bg, fg):
        btn.bind("<Enter>", lambda _: btn.config(bg=enter_bg))
        btn.bind("<Leave>", lambda _: btn.config(bg=leave_bg))

    # ── RIGHT PANEL (3 tabs) ────────────────────────────────────
    def _build_right(self, parent):
        self._nb = ttk.Notebook(parent)
        self._nb.pack(fill="both", expand=True)

        self._tab_gantt   = GanttTab(self._nb)
        self._tab_compare = CompareTab(self._nb)
        self._tab_tests   = tk.Frame(self._nb, bg=C.BG)

        self._nb.add(self._tab_gantt,   text="  Gantt Chart  ")
        self._nb.add(self._tab_compare, text="  Comparison  ")
        self._nb.add(self._tab_tests,   text="  Unit Tests  ")

        self._build_tests_tab(self._tab_tests)

    # ── Status bar ──────────────────────────────────────────────────────
    def _build_statusbar(self):
        self._status_var = tk.StringVar(value="Ready  |  OS_VME_08 Group 5  |  HCMUTRANS")
        bar = tk.Label(self, textvariable=self._status_var,
                        font=F(9), bg=C.BG3, fg=C.TEXT2,
                        anchor="w", padx=14, pady=5)
        bar.pack(fill="x", side="bottom")

    def _set_status(self, msg):
        self._status_var.set(msg)
        self.update_idletasks()

    # ── Actions ────────────────────────────────────────────────────────
    def _load_csv(self):
        path = filedialog.askopenfilename(
            title="Select input CSV",
            filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path: return
        try:
            fs, rs = FileHandler.read_input(path)
            self.frame_size.set(fs)
            self.ref_string = rs
            self._file_lbl.config(text=os.path.basename(path))
            self._ref_entry.delete("1.0", "end")
            self._ref_entry.insert("1.0", ",".join(map(str, rs)))
            self._set_status(f"Loaded: {path}  |  {len(rs)} pages  |  {fs} frames")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _parse_ref(self):
        raw = self._ref_entry.get("1.0", "end").strip()
        result = []
        for t in raw.split(","):
            t = t.strip()
            if not t: continue
            try:
                v = int(t)
                if v < 0: raise ValueError(f"Âm: {v}")
                result.append(v)
            except ValueError as e:
                raise ValueError(f"Reference string không hợp lệ: {e}")
        if not result: raise ValueError("Reference string trống.")
        return result

    def _run(self, algo_name: str):
        try:
            refs = self._parse_ref()
            n    = self.frame_size.get()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e)); return

        self.ref_string = refs
        self._set_status(f"Running {algo_name}...")
        Cls   = AlgoRegistry.get(algo_name)
        color = C.ALGO.get(algo_name, C.ACCENT)
        t0    = time.perf_counter()
        steps = Cls.run(refs, n)
        ms    = (time.perf_counter() - t0) * 1000

        self.last_steps = steps
        self.last_algo  = algo_name
        self.last_exec  = ms

        self._tab_gantt.render(algo_name, steps, n, ms, color)
        self._nb.select(0)

        faults = sum(1 for s in steps if s.is_fault)
        self._set_status(
            f"{algo_name}  |  {faults} faults  |  {len(steps)-faults} hits"
            f"  |  {ms:.3f} ms  |  frames: {n}  |  refs: {len(refs)}")

    def _run_all(self):
        try:
            refs = self._parse_ref()
            n    = self.frame_size.get()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e)); return

        self.ref_string = refs
        self._set_status("Running all algorithms...")
        all_r: dict[str, tuple[list[Step], float]] = {}
        for nm in AlgoRegistry.all_names():
            Cls = AlgoRegistry.get(nm)
            t0  = time.perf_counter()
            st  = Cls.run(refs, n)
            ms  = (time.perf_counter() - t0) * 1000
            all_r[nm] = (st, ms)

        self._all_results = all_r
        opt_st, opt_ms = all_r["OPT"]
        self.last_steps = opt_st; self.last_algo = "OPT"; self.last_exec = opt_ms

        self._tab_gantt.render("OPT (after Run ALL)", opt_st, n, opt_ms, C.ALGO["OPT"])
        results_only = {nm: st for nm,(st,_) in all_r.items()}
        times_only   = {nm: ms for nm,(_,ms) in all_r.items()}
        self._tab_compare.render(results_only, times_only, refs, n)
        self._nb.select(1)

        self._set_status(
            "All done — " + "  |  ".join(
                f"{nm}: {sum(1 for s in st if s.is_fault)}F"
                for nm,(st,_) in all_r.items()))

    # ── Export single algo (chế độ 1) ────────────────────────────────
    def _export_single(self, algo_name: str):
        """Xuất CSV của một thuật toán cụ thể.
        Ưu tiên lấy từ _all_results (Run ALL), fallback sang last_steps nếu cùng algo.
        """
        steps, exec_ms = None, 0.0

        if self._all_results and algo_name in self._all_results:
            steps, exec_ms = self._all_results[algo_name]
        elif self.last_algo == algo_name and self.last_steps:
            steps, exec_ms = self.last_steps, self.last_exec

        if not steps:
            messagebox.showwarning(
                "Export",
                f"Chưa có kết quả {algo_name}.\n"
                f"Hãy nhấn '▶ Run {algo_name}' hoặc '⚡ Run ALL' trước.")
            return

        path = filedialog.asksaveasfilename(
            title=f"Lưu kết quả {algo_name}",
            defaultextension=".csv",
            initialfile=f"{algo_name}_result.csv",
            filetypes=[("CSV files", "*.csv")])
        if not path: return

        try:
            refs = self._parse_ref()
            FileHandler.write_output(path, algo_name,
                                      self.frame_size.get(), refs,
                                      steps, exec_ms)
            messagebox.showinfo("Export", f"✓ Đã lưu {algo_name}:\n{path}")
            self._set_status(f"Exported {algo_name} → {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── _export_csv giữ lại cho tương thích (xuất algo hiện tại) ────────
    def _export_csv(self):
        if not self.last_steps:
            messagebox.showwarning("Export", "Run an algorithm first."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"output_{self.last_algo}.csv",
            filetypes=[("CSV files", "*.csv")])
        if not path: return
        try:
            refs = self._parse_ref()
            FileHandler.write_output(path, self.last_algo,
                                      self.frame_size.get(), refs,
                                      self.last_steps, self.last_exec)
            messagebox.showinfo("Export", f"Saved:\n{path}")
            self._set_status(f"Exported → {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _batch_csv(self):
        if not self._all_results:
            messagebox.showwarning("Batch Export",'Run "Run ALL & Compare" first.'); return
        folder = filedialog.askdirectory(title="Select output folder")
        if not folder: return
        try:
            refs  = self._parse_ref()
            n     = self.frame_size.get()
            paths = FileHandler.batch_export(folder, n, refs, self._all_results)
            messagebox.showinfo("Batch Export","Exported:\n"+"\n".join(paths))
            self._set_status(f"Batch exported {len(paths)} files → {folder}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ── Unit Tests tab ──────────────────────────────────────────────────
    def _build_tests_tab(self, parent):
        tk.Label(parent, text="Unit Tests",
                 font=F(13, bold=True), bg=C.BG, fg=C.WHITE
                 ).pack(pady=(16, 2))
        tk.Label(parent,
                 text="Verified against OS Concepts 10th Edition — Silberschatz et al.",
                 font=F(9), bg=C.BG, fg=C.TEXT2).pack()
        HLine(parent).pack(fill="x", padx=16, pady=8)

        run_btn = tk.Button(parent,
                             text="▶  Run All Unit Tests",
                             font=F(11, bold=True),
                             bg=C.ACCENT, fg=C.BG,
                             relief="flat", cursor="hand2", pady=9,
                             command=lambda: self._run_tests_inline(rf))
        run_btn.pack(padx=24, pady=(0, 10))

        rf = tk.Frame(parent, bg=C.BG)
        rf.pack(fill="both", expand=True, padx=20, pady=4)

    def _run_tests_inline(self, result_frame):
        for w in result_frame.winfo_children(): w.destroy()
        self._set_status("Running unit tests...")

        # Scrollable list
        outer  = tk.Canvas(result_frame, bg=C.BG, highlightthickness=0)
        vb     = tk.Scrollbar(result_frame, orient="vertical", command=outer.yview)
        outer.configure(yscrollcommand=vb.set)
        vb.pack(side="right", fill="y")
        outer.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(outer, bg=C.BG)
        cw    = outer.create_window((0,0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: (outer.configure(scrollregion=outer.bbox("all")),
                              outer.itemconfig(cw, width=outer.winfo_width())))

        tr = TestRunner()
        results, passed, failed = tr.run_all()

        for status, name in results:
            row = tk.Frame(inner, bg=C.BG); row.pack(fill="x", pady=1)
            col = C.HIT if status == "PASS" else C.FAULT
            tk.Label(row, text=f"[{status}]", width=7,
                     font=F(10, bold=True), bg=C.BG2, fg=col
                     ).pack(side="left", padx=(0,6))
            tk.Label(row, text=name, font=F(10), bg=C.BG, fg=C.TEXT
                     ).pack(side="left")

        HLine(inner).pack(fill="x", pady=5)
        sc = C.HIT if failed == 0 else C.FAULT
        tk.Label(inner,
                 text=(f"Passed: {passed}  |  Failed: {failed}  |  "
                       f"Total: {passed+failed}   "
                       + ("ALL PASSED ✓" if failed == 0 else f"{failed} FAILED ✗")),
                 font=F(11, bold=True), bg=C.BG, fg=sc).pack(pady=8)

        self._set_status(f"Tests: {passed}/{passed+failed} passed" +
                          (" ✓" if failed == 0 else f"  —  {failed} FAILED"))

    # ── Open Unit Tests ─────────────────────────────────────────────────
    def _open_tests(self):
        self._nb.select(2)


    # ── Team Info ───────────────────────────────────────────────────────
    def _show_team(self):
        win = tk.Toplevel(self)
        win.title("Team Info — OS_VME_08 Group 5")
        win.geometry("560x400")
        win.configure(bg=C.BG)

        tk.Label(win, text="OS_VME_08 — Nhóm 5",
                 font=F(14, bold=True), bg=C.BG, fg=C.ACCENT).pack(pady=(14,2))
        tk.Label(win,
                 text="Đại học Giao thông Vận tải TP.HCM  |  Mã lớp: 7480201390613",
                 font=F(9), bg=C.BG, fg=C.TEXT2).pack()
        HLine(win).pack(fill="x", padx=16, pady=10)

        members = [
            ("Phan Đình Phát",         "060206002816", "Algorithm Developer"),
            ("Nguyễn Thị Xuân Tuyền",  "054306001845", "Data & File Handler"),
            ("Nguyễn Thanh Tuấn",      "051206002660", "GUI Developer"),
            ("Dương Trọng Nghĩa",      "066206008908", "Tester & Integrator"),
            ("Kim Nhựt Hoàng",         "084206006510", "Documentation"),
        ]
        for i, (name, sid, role) in enumerate(members, 1):
            bg  = C.BG2 if i % 2 == 0 else C.BG
            row = tk.Frame(win, bg=bg); row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=f"{i}.", width=3, font=F(10, bold=True),
                     bg=bg, fg=C.ACCENT).pack(side="left", padx=(8,0))
            tk.Label(row, text=name, width=24, anchor="w",
                     font=F(10, bold=True), bg=bg, fg=C.YELLOW).pack(side="left")
            tk.Label(row, text=sid, width=14, font=F(9),
                     bg=bg, fg=C.TEXT2).pack(side="left")
            tk.Label(row, text=role, font=F(9), bg=bg, fg=C.HIT).pack(side="left", padx=8)

        HLine(win).pack(fill="x", padx=16, pady=10)
        tk.Label(win,
                 text="Ref: OS Concepts 10th Ed. — Silberschatz, Galvin, Gagne",
                 font=F(9), bg=C.BG, fg=C.TEXT2).pack()
