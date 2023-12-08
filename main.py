import tkinter as tk

from app import HostPingWindow, AppWindow

if __name__ == "__main__":
    root = tk.Tk()
    HostPingWindow(root)
    root.mainloop()