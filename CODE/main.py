"""
================================================================
  VIRTUAL MEMORY PAGE REPLACEMENT SIMULATOR
  OS_VME_08 — GROUP 5
  Trường Đại học Giao thông Vận tải TP.HCM (HCMUTRANS)
  Môn học: Hệ Điều Hành | Mã lớp: 7480201390613
================================================================
  Chạy: python main.py
  Yêu cầu: Python 3.8+ 
================================================================
"""

import sys
import os
import io

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python or environments where reconfigure isn't available
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Đảm bảo import đúng từ thư mục gốc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GUI.display import App


if __name__ == "__main__":
    app = App()
    app.mainloop()
