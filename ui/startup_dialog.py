"""
Startup Dialog
Choose between SFTP or Local file mode
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QCheckBox, QFileDialog,
                             QLineEdit, QGroupBox, QButtonGroup)
from PyQt5.QtCore import Qt

class StartupDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.mode = None  # 'sftp' or 'local'
        self.local_path = None
        
        self.setWindowTitle("DayZ Types Editor - Startup")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.load_saved_preferences()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("How would you like to work?")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Mode selection group
        mode_group = QGroupBox()
        mode_layout = QVBoxLayout()
        
        self.button_group = QButtonGroup()
        
        # SFTP option
        self.sftp_radio = QRadioButton("Connect to SFTP Server")
        self.sftp_radio.setStyleSheet("font-size: 12px; padding: 8px;")
        sftp_desc = QLabel("    Edit files directly on your remote server")
        sftp_desc.setStyleSheet("font-size: 11px; color: #999; margin-left: 20px;")
        self.button_group.addButton(self.sftp_radio)
        mode_layout.addWidget(self.sftp_radio)
        mode_layout.addWidget(sftp_desc)
        
        mode_layout.addSpacing(10)
        
        # Local option
        self.local_radio = QRadioButton("Work with Local Files")
        self.local_radio.setStyleSheet("font-size: 12px; padding: 8px;")
        local_desc = QLabel("    Edit a local mirror of your mission files")
        local_desc.setStyleSheet("font-size: 11px; color: #999; margin-left: 20px;")
        self.button_group.addButton(self.local_radio)
        mode_layout.addWidget(self.local_radio)
        mode_layout.addWidget(local_desc)
        
        # Local path selection
        local_path_layout = QHBoxLayout()
        local_path_layout.addSpacing(20)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("Mission folder path...")
        self.local_path_input.setEnabled(False)
        local_path_layout.addWidget(self.local_path_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(self.browse_local_path)
        local_path_layout.addWidget(self.browse_btn)
        
        mode_layout.addLayout(local_path_layout)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Remember choice checkbox
        self.remember_cb = QCheckBox("Remember my choice")
        self.remember_cb.setStyleSheet("margin-top: 10px;")
        layout.addWidget(self.remember_cb)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        connect_btn = QPushButton("Continue")
        connect_btn.setDefault(True)
        connect_btn.clicked.connect(self.accept_selection)
        button_layout.addWidget(connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("QPushButton { background-color: #555; }")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect radio button signals
        self.sftp_radio.toggled.connect(self.on_mode_changed)
        self.local_radio.toggled.connect(self.on_mode_changed)
        
        # Set default
        self.sftp_radio.setChecked(True)
    
    def on_mode_changed(self):
        """Handle mode selection change"""
        is_local = self.local_radio.isChecked()
        self.local_path_input.setEnabled(is_local)
        self.browse_btn.setEnabled(is_local)
    
    def browse_local_path(self):
        """Browse for local mission folder"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Mission Folder",
            self.local_path_input.text() or ""
        )
        
        if directory:
            self.local_path_input.setText(directory)
    
    def load_saved_preferences(self):
        """Load saved preferences"""
        startup_mode = self.config.config.get('startup_mode')
        if startup_mode == 'sftp':
            self.sftp_radio.setChecked(True)
        elif startup_mode == 'local':
            self.local_radio.setChecked(True)
            local_path = self.config.config.get('local_mission_path', '')
            if local_path:
                self.local_path_input.setText(local_path)
    
    def accept_selection(self):
        """Accept the selection"""
        if self.sftp_radio.isChecked():
            self.mode = 'sftp'
        elif self.local_radio.isChecked():
            self.mode = 'local'
            self.local_path = self.local_path_input.text().strip()
            
            if not self.local_path:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "No Path Selected",
                    "Please select a mission folder path."
                )
                return
        
        # Save preferences if requested
        if self.remember_cb.isChecked():
            self.config.config['startup_mode'] = self.mode
            if self.mode == 'local':
                self.config.config['local_mission_path'] = self.local_path
            self.config.save()
        
        self.accept()
