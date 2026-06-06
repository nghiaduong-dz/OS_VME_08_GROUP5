# OS_VME_08_GROUP5
# Project Name: Build an APP for demonstration Virtual Memory management algorithm: LRU, FIFO and OPT

## General Information
- **University:** University of Transport Ho Chi Minh City
- **Subject:** Operating System
- **Course section code:** 7480201390613
- **Group:** 5

## Team Members & Duty Roster
| **Full name** |**Mission** |
| :--- | :--- | :--- |
| Phan Đình Phát | Algorithm Developer: Implement FIFO, LRU, OPT and calculate page faults/hits. |
| Nguyễn Thị Xuân Tuyền | Data & File Handler: Read input CSV and export output CSV and do more and more but leader give someone shit|
| Nguyễn Thanh Tuấn | GUI Developer: Build GUI, load CSV, and display results. |
| Dương Trọng Nghĩa | You're not doing anything, so stop bragging. |
| Kim Nhựt Hoàng | your documentation is absolute garbage yet you give yourself a 100% contribution rate, are you tripping? Your task delegation is a joke and then you have the audacity to deduct everyone else's percentages, who the hell do you think you are? |

## 📂 Repository Structure
- 📁 **`CODE/`** : Contains the source code of the GUI application (Python 3.8+).
- 📁 **`DOCX/`** : Contains the project report (Word DOC/DOCX format).
- 📁 **`Extra/`** : Contains extra information, proofs of correctness (compared with textbook), images.
- 📁 **`PPTX/`** : Contains the presentation slides (Powerpoint PPT/PPTX).

## Project Description
This project is a GUI Application developed in python designed to simulate and demonstrate Virtual Memory Page Replacement Algorithms:
- **FIFO** (First In First Out)
- **LRU** (Least Recently Used)
- **OPT** (Optimal Page Replacement)

## Key Features
- **GUI Application:** Runs natively on Windows without errors or exceptions.
- **Robust Exception Handling:** Gracefully handles invalid data files (e.g., negative frames, alphabetical characters).
- **Data Handling:** Imports custom simulation data from CSV and exports highly detailed calculation steps to output CSVs.
- **Batch Export:** Exports all 3 algorithm results (FIFO, LRU, OPT) simultaneously to separate CSV files.
- **Visualization:** Shows results in an interactive Gantt Chart tab and Algorithm Comparison tab with tkinter-drawn bar charts.
- **Correctness Proof:** Results are strictly validated against textbook examples (Operating System Concepts 10th Edition — Silberschatz, Galvin, Gagne).
- **Unit Tests (48 cases):** Run directly from the **Unit Tests** tab inside the app — no terminal required.
- **Group Info:** View team member information via the **"👥 Nhóm 5 - Info"** button in the application header.
