from gui.about_window import AboutDialog
self.send_btn = QPushButton("Send Message")
self.manual_override_xml = None
self.use_override = False

# Inside _init_ui()
about_btn = QPushButton("About")
about_btn.clicked.connect(self.show_about)
layout.addWidget(about_btn, alignment=Qt.AlignmentFlag.AlignRight)
