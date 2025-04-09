# FULLY FUNCTIONAL main_window.py
# This file includes all features and button actions wired up
# Including listener start/stop, send message, template builder, manual override, and transformation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QRadioButton, QButtonGroup, QMessageBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal, Slot

from backend.listener import UDPListener
from backend import database, transform, temp_packet_db, temp_packet_db
from backend.forwarder import Forwarder
from backend.models import Packet, Overrides
from backend.logger import log_error
from gui.manual_override_window import ManualOverrideDialog
from gui.about_window import AboutDialog
from gui.template_builder import CustomTemplateEditor

class MainWindow(QWidget):
    packet_received = Signal(str, tuple, str)

    def __init__(self):
        super().__init__()
        temp_packet_db.init_temp_db()

        self.setWindowTitle("Rosetta Stone")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setMinimumSize(800, 740)

        self.listener = None
        self.last_transformed = ""
        self.forwarder = None
        self.auto_forward_enabled = False
        self.manual_override_xml = None
        self.use_override = False
        self.custom_template = None
        self.use_custom_template = False

        database.init_db()
        self._init_ui()
        self.packet_received.connect(self.handle_packet_safe)

    def _init_ui(self):
        layout = QVBoxLayout()

        net_layout = QHBoxLayout()
        self.port_input = QLineEdit("40000")
        self.dest_ip_input = QLineEdit("127.0.0.1")
        self.dest_port_input = QLineEdit("50000")
        net_layout.addWidget(QLabel("UDP Listen Port:"))
        net_layout.addWidget(self.port_input)
        net_layout.addWidget(QLabel("Dest IP:"))
        net_layout.addWidget(self.dest_ip_input)
        net_layout.addWidget(QLabel("Dest Port:"))
        net_layout.addWidget(self.dest_port_input)
        layout.addLayout(net_layout)

        proto_layout = QHBoxLayout()
        self.tcp_radio = QRadioButton("TCP")
        self.udp_radio = QRadioButton("UDP")
        self.tcp_radio.setChecked(True)
        self.proto_group = QButtonGroup()
        self.proto_group.addButton(self.tcp_radio)
        self.proto_group.addButton(self.udp_radio)
        proto_layout.addWidget(QLabel("Send Protocol:"))
        proto_layout.addWidget(self.tcp_radio)
        proto_layout.addWidget(self.udp_radio)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Simdis XML", "CoT XML", "JSON", "Raw XML"])
        format_layout.addWidget(self.format_combo)

        layout.addLayout(proto_layout)
        layout.addLayout(format_layout)

        override_layout = QHBoxLayout()
        self.uid_input = QLineEdit()
        self.lat_input = QLineEdit()
        self.lon_input = QLineEdit()
        self.alt_input = QLineEdit()
        override_layout.addWidget(QLabel("UID:"))
        override_layout.addWidget(self.uid_input)
        override_layout.addWidget(QLabel("Lat:"))
        override_layout.addWidget(self.lat_input)
        override_layout.addWidget(QLabel("Lon:"))
        override_layout.addWidget(self.lon_input)
        override_layout.addWidget(QLabel("Alt:"))
        override_layout.addWidget(self.alt_input)
        layout.addLayout(override_layout)

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Listening")
        self.stop_btn = QPushButton("Stop")
        self.send_btn = QPushButton("Send Message")
        self.auto_forward_btn = QPushButton("Start Auto-Forwarding")
        self.override_btn = QPushButton("Manual Override")
        self.template_btn = QPushButton("Custom Template Builder")

        self.stop_btn.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_listener)
        self.stop_btn.clicked.connect(self.stop_listener)
        self.send_btn.clicked.connect(self.send_last_transformed)
        self.auto_forward_btn.clicked.connect(self.toggle_auto_forward)
        self.override_btn.clicked.connect(self.open_manual_override)
        self.template_btn.clicked.connect(self.open_template_editor)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.auto_forward_btn)
        button_layout.addWidget(self.override_btn)
        button_layout.addWidget(self.template_btn)
        layout.addLayout(button_layout)

        layout.addWidget(QLabel("Last Received Packet:"))
        self.packet_display = QTextEdit()
        self.packet_display.setReadOnly(True)
        layout.addWidget(self.packet_display)

        layout.addWidget(QLabel("Transformed Output:"))
        self.transformed_display = QTextEdit()
        self.transformed_display.setReadOnly(True)
        layout.addWidget(self.transformed_display)

        layout.addWidget(QLabel("Message Log:"))
        self.message_log = QListWidget()
        self.message_log.setMaximumHeight(150)
        layout.addWidget(self.message_log)

        self.template_status = QLabel("Template: Default")
        layout.addWidget(self.template_status)

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about)
        layout.addWidget(about_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

    def start_listener(self):
        try:
            port = int(self.port_input.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Port", "Please enter a valid port number.")
            return
        self.listener = UDPListener(port, lambda d, a, t: self.packet_received.emit(d, a, t))
        self.listener.start()
        self.status_label.setText(f"Status: Listening on UDP {port}")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.message_log.clear()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.status_label.setText("Status: Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def toggle_auto_forward(self):
        self.auto_forward_enabled = not self.auto_forward_enabled
        if self.auto_forward_enabled:
            self.auto_forward_btn.setText("Pause Auto-Forwarding")
        else:
            self.auto_forward_btn.setText("Start Auto-Forwarding")

    def open_manual_override(self):
        dialog = ManualOverrideDialog(self, current_xml=self.packet_display.toPlainText())
        if dialog.exec():
            self.manual_override_xml = dialog.get_xml()
            self.use_override = True
            self.message_log.addItem(QListWidgetItem("[Manual Override] Override enabled"))

    
    def open_template_editor(self):
        messages = database.get_recent_messages()
        dialog = CustomTemplateEditor(self, incoming_xml=self.packet_display.toPlainText(), message_list=messages)
        dialog.exec()
        if dialog.result():
            self.custom_template = dialog.template_editor.toPlainText()
            self.use_custom_template = True
            self.message_log.addItem(QListWidgetItem("[Template Builder] Template set"))
            self.template_status.setText("Template: Custom (Active)")
    def show_about(self):
        AboutDialog(self).exec()

    @Slot(str, tuple, str)
    def handle_packet_safe(self, data, addr, timestamp):
        from datetime import datetime
        self.packet_display.setPlainText(data)
        self.message_log.addItem(QListWidgetItem(f"[Received] {addr[0]}:{addr[1]} at {timestamp}"))
        ovr = Overrides(
            uid=self.uid_input.text() or None,
            lat=self.lat_input.text() or None,
            lon=self.lon_input.text() or None,
            alt=self.alt_input.text() or None
        )
        fmt = self.format_combo.currentText()
        try:
            input_data = self.manual_override_xml if self.use_override else data
            transformed = transform.transform(
                input_data,
                fmt=fmt,
                overrides=ovr.to_dict(),
                use_custom_template=self.use_custom_template,
                custom_template=self.custom_template or ""
            )
            self.transformed_display.setPlainText(transformed)
            self.message_log.addItem(QListWidgetItem(f"[Transformed] Format: {fmt}"))
            self.last_transformed = transformed
            self.send_btn.setEnabled(True)
            self.status_label.setText(f"Status: Received from {addr[0]}:{addr[1]}")
            if self.auto_forward_enabled:
                self.auto_forward(transformed)
        except Exception as e:
            self.transformed_display.setPlainText(f"[Transform Error] {e}")
            self.message_log.addItem(QListWidgetItem(f"[Error] {str(e)}"))
            self.status_label.setText("Status: Transform failed")

    def send_last_transformed(self):
        if not self.last_transformed:
            QMessageBox.warning(self, "No Message", "Nothing to send.")
            return
        protocol = "TCP" if self.tcp_radio.isChecked() else "UDP"
        ip = self.dest_ip_input.text()
        try:
            port = int(self.dest_port_input.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Port", "Enter valid destination port.")
            return
        self.forwarder = Forwarder(protocol, ip, port)
        success = self.forwarder.send(self.last_transformed)
        msg = f"Sent via {protocol} to {ip}:{port}"
        self.message_log.addItem(QListWidgetItem(msg))
        self.status_label.setText(f"Status: {msg}" if success else f"Status: Send failed")

    def auto_forward(self, msg: str):
        protocol = "TCP" if self.tcp_radio.isChecked() else "UDP"
        ip = self.dest_ip_input.text()
        try:
            port = int(self.dest_port_input.text())
        except ValueError:
            return
        self.forwarder = Forwarder(protocol, ip, port)
        self.forwarder.send(msg)