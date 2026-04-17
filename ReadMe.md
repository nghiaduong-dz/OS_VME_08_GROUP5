# OS_VME_08_GROUP5
# Project Name: Build an APP for demonstration Virtual Memory management algorithm: LRU, FIFO and OPT

## General Information
- **University:** University of Transport Ho Chi Minh City
- **Subject:** Operating System
- **Course section code:** 7480201390613
- **Group:** 5

## Team Members & Duty Roster
| **Full name** | **Student ID** | **Mission** |
| :--- | :--- | :--- |
| Phan Đình Phát | 060206002816 | Algorithm Developer: Implement FIFO, LRU, OPT and calculate page faults/hits. |
| Nguyễn Thị Xuân Tuyền | 054306001845 | Data & File Handler: Read input CSV and export output CSV. |
| Nguyễn Thanh Tuấn | 051206002660 | GUI Developer: Build GUI, load CSV, and display results. |
| Dương Trọng Nghĩa | 066206008908 | Tester & Integrator: Test, debug, integrate modules, and record demo video. |
| Kim Nhựt Hoàng | 084206006510 | Documentation & Presentation: Write report and create slides. |

## 🚀 How to Run
```
python CODE/main.py
```
Requires **Python 3.8+** — no external dependencies (uses native `tkinter` only).

## 📂 Repository Structure
This repository strictly follows the requirements for the OS project:
- 📁 **`CODE/`** : Contains the source code of the GUI application (Python 3.8+).
  - `main.py` : Main execution entry-point.
  - `/algorithms/` : Core logic modules (`fifo.py`, `lru.py`, `opt.py`, `registry.py`).
  - `/GUI/` : Application interface (`display.py`, `gantt.py`, `compare.py`, `widgets.py`).
  - `/models/` : Data representation structures tracing memory steps (`step.py`).
  - `/utils/` : Helper utilities implementing the data architecture (`file_handler.py`, `html_exporter.py`).
  - `/unit_tests/` : Automated test suites — run via the **Unit Tests** tab inside the app (`test_algorithms.py`).
  - `/input/` : Data tables (CSV files) used as input for the algorithms.
  - `/Output/` : Detailed step-by-step result exports (CSV files).
- 📁 **`DOCX/`** : Contains the project report (Word DOC/DOCX format).
- 📁 **`Extra/`** : Contains extra information, proofs of correctness (compared with textbook), images.
- 📁 **`PPTX/`** : Contains the presentation slides (Powerpoint PPT/PPTX).

## Project Description
This project is a GUI Application developed in python designed to simulate and demonstrate Virtual Memory Page Replacement Algorithms:
- **FIFO** (First In First Out)
- **LRU** (Least Recently Used)
- **OPT** (Optimal Page Replacement)

## Data Structure & File Handling Architecture
This project employs highly optimized and structured CSV formats for data mapping between the Core Algorithm backend and the Application GUI.

### 1. Input CSV Format
Designed for straightforward modifications and edge-case testing, input files structure is built mathematically:
- **Row 1:** Frame Size Allocation (e.g., `3` or `4`).
- **Row 2:** The Target Reference String, separated by commas (e.g., `7, 0, 1, 2, 0, 3, 0, 4, 2, 3...`).

> **Strict Input Policies:**
> The `FileHandler` enforces rigorous exception protections. It instantly blocks negative frame sizes (e.g., `-3`), filters unparseable characters instead of crashing, and securely processes file missing issues.

#### Included Test Suites (`CODE/input/`):
To thoroughly evaluate the algorithms and exception handling, the following test files are provided natively:
- **Basic & Textbook Proofs (`basic_testcase_1.csv`, `basic_testcase_2.csv`, `input.csv`):** Standard OS Concepts textbook examples with 3 and 4 frames designed for manual verification and presentation slides.
- **Belady's Anomaly (`belady_test.csv`):** Specific reference strings proving that FIFO can generate more page faults when allocated more frames.
- **Edge Cases & Exception Testing (`testcase_extreme_page_fault.csv`, `testcase_no_page_fault.csv`, `testcase_invalid_negative_frame.csv`, `testcase_invalid_characters.csv`, `testcase_large_frames.csv`):** Tests the system's stability against thrashing, best-case scenarios, negative inputs, unparseable alphabetic characters, and over-allocation.
- **Stress & Benchmark Testing (`stress_test_1.csv`, `stress_test_2.csv`, `stress_test_3.csv`):** Massive structural data files to benchmark algorithm execution times.

### 2. Output CSV Design
The application exports detailed CSVs intended for mapping to Gantt and memory allocation charts.
- **Detailed Steps:** Tracks memory blocks per step (`Step | Page | Frame_1 | Frame_2 | Page_Fault_Flag | Total_Faults`).
- **Batch Export:** Run all 3 algorithms simultaneously, then use **"Batch Export 3 CSV"** to save FIFO, LRU, and OPT results to separate files in one click.

## Key Features
- **GUI Application:** Runs natively on Windows without errors or exceptions.
- **Robust Exception Handling:** Gracefully handles invalid data files (e.g., negative frames, alphabetical characters).
- **Data Handling:** Imports custom simulation data from CSV and exports highly detailed calculation steps to output CSVs.
- **Batch Export:** Exports all 3 algorithm results (FIFO, LRU, OPT) simultaneously to separate CSV files.
- **Visualization:** Shows results in an interactive Gantt Chart tab and Algorithm Comparison tab with tkinter-drawn bar charts.
- **Correctness Proof:** Results are strictly validated against textbook examples (Operating System Concepts 10th Edition — Silberschatz, Galvin, Gagne).
- **Unit Tests (48 cases):** Run directly from the **Unit Tests** tab inside the app — no terminal required.
- **Group Info:** View team member information via the **"👥 Nhóm 5 - Info"** button in the application header.
