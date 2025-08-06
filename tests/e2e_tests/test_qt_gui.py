"""
Test GUI using PyQt5 and matplotlib.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QFrame
from PyQt5.QtCore import Qt
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Euler Test GUI (Qt)")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)

        # Add status labels
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)

        score_label = QLabel("Market Risk Score: 78.49")
        score_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        status_layout.addWidget(score_label)

        regime_label = QLabel("Current Regime: 🟥 HIGH STRESS")
        regime_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        status_layout.addWidget(regime_label)

        overview_layout.addWidget(status_frame)

        # Add matplotlib figure
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        ax.set_title("Test Plot")
        canvas = FigureCanvasQTAgg(fig)
        overview_layout.addWidget(canvas)

        tabs.addTab(overview_tab, "Overview")

        # Details tab
        details_tab = QWidget()
        tabs.addTab(details_tab, "Details")

        # Health tab
        health_tab = QWidget()
        tabs.addTab(health_tab, "Health")


def main():
    # Create Qt application
    app = QApplication(sys.argv)

    # Print versions
    print(f"Qt version: {app.applicationVersion()}")
    print(f"Matplotlib backend: {matplotlib.get_backend()}")

    # Create and show window
    window = TestWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
