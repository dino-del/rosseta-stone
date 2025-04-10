# gui/about_window.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Rosetta Stone")
        self.setMinimumSize(300, 200)

        layout = QVBoxLayout()

        # Optional: add logo
        try:
            pixmap = QPixmap("assets/icon.png")
            logo = QLabel()
            logo.setPixmap(pixmap.scaledToHeight(64, Qt.SmoothTransformation))
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)
        except Exception:
            pass

        title = QLabel("Rosetta Stone")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Built for telemetry transformation and forwarding of Data from a UDP source to other systems"))
        layout.addWidget(QLabel("v1.5 — Developed by James Di Natale GitHub @dino-del"))
        layout.addWidget(QLabel("This version includes the custome template option"))
        layout.addWidget(QLabel("Software is 'as is' and no warranty is provided"))
        layout.addWidget(QLabel("Copyright (c) 2025 James Di Natale"))
        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
