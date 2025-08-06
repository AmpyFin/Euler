"""
Minimal GUI test to verify Tkinter functionality.
"""

import tkinter as tk
from tkinter import ttk

import matplotlib

matplotlib.use("TkAgg")
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def main():
    # Create root window
    root = tk.Tk()
    root.title("Euler Test GUI")
    root.geometry("800x600")

    # Print versions
    print(f"Tk version: {tk.TkVersion}")
    print(f"Tcl version: {tk.TclVersion}")
    print(f"Matplotlib backend: {matplotlib.get_backend()}")

    # Create a simple frame
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Add a label
    label = ttk.Label(frame, text="Test Label", font=("TkDefaultFont", 24))
    label.grid(row=0, column=0, pady=10)

    # Create a matplotlib figure
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x))
    ax.set_title("Test Plot")

    # Add the figure to the window
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=0, pady=10)

    # Configure grid weights
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    # Start the event loop
    root.mainloop()


if __name__ == "__main__":
    main()
