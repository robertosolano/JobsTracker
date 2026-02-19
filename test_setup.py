# test_setup.py
try:
    import tkinter as tk
    import sqlite3
    import customtkinter as ctk
    print("✅ All packages available!")
    print(f"Python tkinter version: {tk.TkVersion}")
    print(f"SQLite version: {sqlite3.sqlite_version}")
except ImportError as e:
    print(f"❌ Missing package: {e}")
