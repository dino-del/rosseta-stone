
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox, QLineEdit, QListWidget, QListWidgetItem, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer
from backend import transform, database

class MessageSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find Message")
        self.setMinimumSize(800, 500)
        self.selected_message = None

        layout = QHBoxLayout(self)

        self.message_list = QListWidget()
        self.preview_box = QTextEdit()
        self.preview_box.setReadOnly(True)
        self.preview_box.setFont(QFont("Courier", 10))

        self.message_list.currentItemChanged.connect(self.update_preview)

        layout.addWidget(self.message_list, 2)
        layout.addWidget(self.preview_box, 3)

        self.load_messages()

        select_btn = QPushButton("Load Selected Message")
        select_btn.clicked.connect(self.apply_selection)
        layout.addWidget(select_btn)

    def load_messages(self):
    
            if current:
                self.preview_box.setPlainText(current.data(1000))

    def load_messages(self):
        self.messages = database.get_recent_messages() or [("Now", "<event uid=\"Test01\" time=\"...\"><point lat=\"0\" lon=\"0\" /></event>")]
        for ts, msg in self.messages:
            item = QListWidgetItem(f"{ts} | {msg[:40].replace('\n', ' ')}...")
            item.setData(1000, msg)
            self.message_list.addItem(item)

    def update_preview(self, current, previous):
        if current:
            self.preview_box.setPlainText(current.data(1000))

    def apply_selection(self):
        selected = self.message_list.currentItem()
        if selected:
            self.selected_message = selected.data(1000)
            self.accept()


class CustomTemplateEditor(QDialog):
    def __init__(self, parent=None, incoming_xml="", message_list=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Template Builder")
        self.setMinimumSize(800, 800)
        self._parent = parent
        self._incoming_xml = incoming_xml

        layout = QVBoxLayout(self)

        find_btn = QPushButton("Find Message")
        find_btn.setMaximumWidth(120)
        find_btn.clicked.connect(self.open_message_selector)
        layout.addWidget(find_btn)

        layout.addWidget(QLabel("1. Incoming XML (readonly):"))
        self.raw_view = QTextEdit()
        self.raw_view.setFont(QFont("Courier", 10))
        self.raw_view.setReadOnly(True)
        self.raw_view.setText(incoming_xml)
        layout.addWidget(self.raw_view)

        layout.addWidget(QLabel("2. Editable Template (modifying this affects output):"))
        self.template_editor = QTextEdit()
        self.template_editor.setFont(QFont("Courier", 10))
        self.template_editor.setText(incoming_xml)
        layout.addWidget(self.template_editor)

        var_layout = QHBoxLayout()
        self.variable_dropdown = QComboBox()
        self.variable_dropdown.addItems(["uid", "lat", "lon", "alt", "timestamp"])
        self.custom_var_input = QLineEdit()
        self.custom_var_input.setPlaceholderText("Or enter a custom variable")
        self.replace_btn = QPushButton("Replace Selection with Variable")
        self.replace_btn.clicked.connect(self.replace_selected_text)
        var_layout.addWidget(QLabel("Variable:"))
        var_layout.addWidget(self.variable_dropdown)
        var_layout.addWidget(self.custom_var_input)
        var_layout.addWidget(self.replace_btn)
        layout.addLayout(var_layout)

        layout.addWidget(QLabel("3. Live Transformation Preview (based on template):"))
        self.preview_display = QTextEdit()
        self.preview_display.setFont(QFont("Courier", 10))
        self.preview_display.setReadOnly(True)
        layout.addWidget(self.preview_display)

        preview_btn = QPushButton("Preview Now")
        preview_btn.clicked.connect(self.generate_preview)
        layout.addWidget(preview_btn)

        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Set as Active Template")
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn.clicked.connect(self.set_active_template)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self._live_preview_timer = QTimer(self)
        self._live_preview_timer.timeout.connect(self.generate_preview)
        self._live_preview_timer.start(1000)

    def open_message_selector(self):
        dlg = MessageSelectorDialog(self)
        if dlg.exec() and dlg.selected_message:
            self._incoming_xml = dlg.selected_message
            self.raw_view.setPlainText(dlg.selected_message)
            self.template_editor.setPlainText(dlg.selected_message)

    def replace_selected_text(self):
        cursor = self.template_editor.textCursor()
        selected = cursor.selectedText()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Highlight text in the template editor to replace.")
            return
        variable = self.custom_var_input.text().strip() or self.variable_dropdown.currentText()
        if not variable:
            QMessageBox.warning(self, "Missing Variable", "Select or enter a variable.")
            return
        replacement = "{{" + variable + "}}"
        cursor.insertText(replacement)

    def generate_preview(self):
        overrides = {
            "uid": "Alpha01",
            "lat": "47.6",
            "lon": "-122.3",
            "alt": "1000",
            "timestamp": "2025-04-08T12:00:00Z"
        }
        template = self.template_editor.toPlainText()
        try:
            output = transform.transform(
                self._incoming_xml,
                fmt="Simdis XML",
                overrides=overrides,
                use_custom_template=True,
                custom_template=template
            )
            self.preview_display.setPlainText(output)
        except Exception as e:
            self.preview_display.setPlainText(f"[Transform Error] {e}")

    def set_active_template(self):
        if self._parent:
            self._parent.template_status.setText("Template: Custom (Active)")
            self._parent.custom_template = self.template_editor.toPlainText()
            self._parent.use_custom_template = True
            self._parent.message_log.addItem(QListWidgetItem("[INFO] Using custom template for next transmission."))
        self.accept()