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

## 📂 Repository Structure
This repository strictly follows the requirements for the OS project:
- 📁 **`Code/`** : Contains the source code of the GUI application (C++).
  - `/input/` : Data tables (CSV files) used as input for the algorithms (includes textbook proofs, Belady's anomaly test cases, and stress test data).
  - `/output/` : Detailed step-by-step result exports (CSV files).
- 📁 **`DOCX/`** : Contains the project report (Word DOC/DOCX format).
- 📁 **`Extra/`** : Contains extra information, proofs of correctness (compared with textbook), images, and Performance/Stress Test datasets.
- 📁 **`PPTX/`** : Contains the presentation slides (Powerpoint PPT/PPTX).

## Project Description
This project is a GUI Application developed in C++ designed to simulate and demonstrate Virtual Memory Page Replacement Algorithms:
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

### 2. Output CSV Design
The application exports detailed CSVs intended for mapping to Gantt and memory allocation charts.
- **Detailed Steps:** Tracks memory blocks per step (`Step | Page | Frame_1 | Frame_2 | Page_Fault_Flag | Total_Faults`).
- **Stress Test Defense Protocol:** To fulfill academic bottlenecking theories, testcases exceeding a threshold of `1,000` sequential requests trigger a defense mode - Omit generating Step reports and strictly isolate purely runtime analytics (Execution times, Error Rates, Hit Rates) to protect local RAM overheads.

## Key Features
- GUI Application: Runs natively on Windows without errors or exceptions.
- Robust Exception Handling: Gracefully handles invalid data files (e.g., negative frames, alphabetical characters).
- Data Handling: Imports custom simulation data from CSV and exports highly detailed calculation steps to output CSVs.
- Visualization: Shows results on the screen including Gantt charts and main/virtual memory allocation.
- Correctness Proof: Results are strictly compared and validated against textbook examples (Operating System Concepts 10th Edition).
- Stress & Performance Testing: Capable of handling massive reference strings (e.g., 1,000,000 records) using optimized file I/O to benchmark the algorithms.
