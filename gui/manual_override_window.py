from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QMessageBox, QWidget
)
from PySide6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter
from PySide6.QtCore import Qt, QRegularExpression
import xml.etree.ElementTree as ET


class XMLHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(QColor("blue"))
        self.attr_format = QTextCharFormat()
        self.attr_format.setForeground(QColor("green"))
        self.value_format = QTextCharFormat()
        self.value_format.setForeground(QColor("darkRed"))

    def highlightBlock(self, text):
        tag_expr = QRegularExpression(r"</?\w+")
        attr_expr = QRegularExpression(r"\b\w+=")
        val_expr = QRegularExpression(r'"[^"]*"')

        for match in tag_expr.globalMatch(text):
            self.setFormat(match.capturedStart(), match.capturedLength(), self.tag_format)

        for match in attr_expr.globalMatch(text):
            self.setFormat(match.capturedStart(), match.capturedLength(), self.attr_format)

        for match in val_expr.globalMatch(text):
            self.setFormat(match.capturedStart(), match.capturedLength(), self.value_format)


class ManualOverrideDialog(QDialog):
    def __init__(self, parent=None, current_xml=""):
        super().__init__(parent)
        self.setWindowTitle("Manual XML Override")
        self.setMinimumSize(800, 500)

        self.updated_xml = current_xml

        layout = QVBoxLayout()

        # === Side-by-side preview ===
        preview_layout = QHBoxLayout()

        self.raw_view = QTextEdit()
        self.raw_view.setPlainText(current_xml)
        self.raw_view.setReadOnly(True)
        preview_layout.addWidget(self._group("Incoming XML", self.raw_view))

        self.editor = QTextEdit()
        self.editor.setPlainText(current_xml)
        preview_layout.addWidget(self._group("Override XML", self.editor))

        layout.addLayout(preview_layout)

        # === Syntax highlighting
        XMLHighlighter(self.raw_view.document())
        XMLHighlighter(self.editor.document())

        # === Save / Cancel buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Changes")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.validate_and_close)
        self.cancel_btn.clicked.connect(self.reject)

    def _group(self, label_text, widget):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        container = QWidget()
        container.setLayout(layout)
        return container

    def validate_and_close(self):
        text = self.editor.toPlainText()
        try:
            ET.fromstring(text)  # XML validation
            self.updated_xml = text
            self.accept()
        except ET.ParseError as e:
            QMessageBox.critical(self, "Invalid XML", f"Error: {e}")

    def get_xml(self):
        return self.updated_xml
