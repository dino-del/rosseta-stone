def _init_ui(self):
        layout = QVBoxLayout()

        # Network Inputs
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

        # Protocol + Format
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

        # Overrides
        overrides_layout = QHBoxLayout()
        self.uid_input = QLineEdit()
        self.lat_input = QLineEdit()
        self.lon_input = QLineEdit()
        self.alt_input = QLineEdit()

        overrides_layout.addWidget(QLabel("UID:"))
        overrides_layout.addWidget(self.uid_input)
        overrides_layout.addWidget(QLabel("Lat:"))
        overrides_layout.addWidget(self.lat_input)
        overrides_layout.addWidget(QLabel("Lon:"))
        overrides_layout.addWidget(self.lon_input)
        overrides_layout.addWidget(QLabel("Alt:"))
        overrides_layout.addWidget(self.alt_input)
        layout.addLayout(overrides_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Listening")
        self.stop_btn = QPushButton("Stop")
        self.send_btn = QPushButton("Send Message")
        self.auto_forward_btn = QPushButton("Start Auto-Forwarding")
        self.override_btn = QPushButton("Manual Override")
        self.template_btn = QPushButton("Custom Template Builder")  # NEW

        self.stop_btn.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.start_btn.clicked.connect(self.start_listener)
        self.stop_btn.clicked.connect(self.stop_listener)
        self.send_btn.clicked.connect(self.send_last_transformed)
        self.auto_forward_btn.clicked.connect(self.toggle_auto_forward)
        self.override_btn.clicked.connect(self.open_manual_override)
        self.template_btn.clicked.connect(self.open_template_editor)  # NEW

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.auto_forward_btn)
        button_layout.addWidget(self.override_btn)
        button_layout.addWidget(self.template_btn)  # NEW
        layout.addLayout(button_layout)

        # Displays
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

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        # About Button
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

        self.listener = UDPListener(
            port,
            lambda data, addr, ts: self.packet_received.emit(data, addr, ts)
        )
        self.listener.start()

        self.status_label.setText(f"Status: Listening on UDP {port}")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.message_log.clear()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.manual_override_xml = None
        self.use_override = False
        self.status_label.setText("Status: Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def toggle_auto_forward(self):
        self.auto_forward_enabled = not self.auto_forward_enabled
        if self.auto_forward_enabled:
            self.auto_forward_btn.setText("Pause Auto-Forwarding")
            self.message_log.addItem(QListWidgetItem("[Auto-Forwarding ENABLED]"))
        else:
            self.auto_forward_btn.setText("Start Auto-Forwarding")
            self.message_log.addItem(QListWidgetItem("[Auto-Forwarding PAUSED]"))

    def open_manual_override(self):
        dialog = ManualOverrideDialog(self, current_xml=self.packet_display.toPlainText())
        if dialog.exec():
            self.manual_override_xml = dialog.get_xml()
            self.use_override = True
            self.message_log.addItem(QListWidgetItem("[Manual Override] Override loaded and active."))
            self.status_label.setText("Status: Manual XML override ENABLED")
        else:
            self.status_label.setText("Status: Manual override canceled")

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    @Slot(str, tuple, str)
    def handle_packet_safe(self, data, addr, timestamp):
        pkt = Packet(timestamp, addr[0], addr[1], data)
        database.log_packet_obj(pkt)

        self.packet_display.setPlainText(data)

        ovr = Overrides(
            uid=self.uid_input.text() or None,
            lat=self.lat_input.text() or None,
            lon=self.lon_input.text() or None,
            alt=self.alt_input.text() or None
        )

        fmt = self.format_combo.currentText()

        try:
            if self.use_override and self.manual_override_xml:
                input_data = self.manual_override_xml
                self.message_log.addItem(QListWidgetItem("[Override Mode] Using manual override for transform."))
            else:
                input_data = data

            transformed = transform.transform(input_data, fmt=fmt, overrides=ovr.to_dict())
            self.transformed_display.setPlainText(transformed)
            self.last_transformed = transformed
            self.send_btn.setEnabled(True)
            self.message_log.addItem(QListWidgetItem(f"[Received] {addr[0]}:{addr[1]} @ {timestamp}"))

            if self.auto_forward_enabled:
                self.auto_forward(transformed)

        except Exception as e:
            error_msg = f"[Transform Error] {e}"
            self.transformed_display.setPlainText(error_msg)
            self.message_log.addItem(QListWidgetItem(error_msg))
            log_error(error_msg)
            self.send_btn.setEnabled(False)

        self.status_label.setText(f"Status: Packet received from {addr[0]}:{addr[1]} at {timestamp}")

    def auto_forward(self, message: str):
        protocol = "TCP" if self.tcp_radio.isChecked() else "UDP"
        ip = self.dest_ip_input.text()
        try:
            port = int(self.dest_port_input.text())
        except ValueError:
            self.message_log.addItem(QListWidgetItem("[AutoForward Error] Invalid destination port"))
            log_error("Invalid destination port in auto-forward")
            return

        self.forwarder = Forwarder(protocol=protocol, ip=ip, port=port)
        success = self.forwarder.send(message)

        if success:
            msg = f"[AutoSent] {protocol} → {ip}:{port}"
            self.message_log.addItem(QListWidgetItem(msg))
            self.status_label.setText(f"Status: {msg}")
        else:
            err = f"[AutoSend Error] {protocol} failed to {ip}:{port}"
            self.message_log.addItem(QListWidgetItem(err))
            self.status_label.setText(f"Status: {err}")
            log_error(err)

    def send_last_transformed(self):
        if not self.last_transformed:
            QMessageBox.warning(self, "No Data", "No message to send.")
            return

        protocol = "TCP" if self.tcp_radio.isChecked() else "UDP"
        ip = self.dest_ip_input.text()
        try:
            port = int(self.dest_port_input.text())
        except ValueError:
            QMessageBox.critical(self, "Invalid Port", "Please enter a valid destination port.")
            return

        self.forwarder = Forwarder(protocol=protocol, ip=ip, port=port)
        success = self.forwarder.send(self.last_transformed)

        if success:
            msg = f"Sent via {protocol} to {ip}:{port}"
            self.status_label.setText(f"Status: {msg}")
            self.message_log.addItem(QListWidgetItem(f"[Sent] {msg}"))
        else:
            err = f"Failed to send via {protocol}"
            self.status_label.setText(f"[ERROR] {err}")
            self.message_log.addItem(QListWidgetItem(f"[Error] {err}"))
            log_error(err)

    def open_template_editor(self):
        from gui.custom_template_editor import CustomTemplateEditor
        dialog = CustomTemplateEditor(self, incoming_xml=self.packet_display.toPlainText())
        dialog.exec()
        
        self.custom_template = None
self.use_custom_template = False

