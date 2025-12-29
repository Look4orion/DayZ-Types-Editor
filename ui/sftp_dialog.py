"""
SFTP Connection Dialog
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QSpinBox, QPushButton, QCheckBox,
                             QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class SFTPDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Connect to SFTP Server")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.load_saved_config()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Form layout for connection details
        form = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.100")
        form.addRow("Host:", self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        form.addRow("Port:", self.port_input)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("admin")
        form.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.password_input)
        
        self.mission_path_input = QLineEdit()
        self.mission_path_input.setPlaceholderText("/dayzserver/mpmissions/dayzOffline.deerisle/")
        form.addRow("Mission Path:", self.mission_path_input)
        
        self.save_credentials_cb = QCheckBox("Save credentials (encrypted)")
        form.addRow("", self.save_credentials_cb)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect)
        connect_btn.setDefault(True)
        button_layout.addWidget(connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_saved_config(self):
        """Load saved SFTP configuration"""
        config = self.parent.config.get_sftp_config()
        
        if config.get('host'):
            self.host_input.setText(config['host'])
        if config.get('port'):
            self.port_input.setValue(config['port'])
        if config.get('username'):
            self.username_input.setText(config['username'])
        if config.get('password'):
            self.password_input.setText(config['password'])
        if config.get('mission_path'):
            self.mission_path_input.setText(config['mission_path'])
        if config.get('save_credentials'):
            self.save_credentials_cb.setChecked(True)
    
    def test_connection(self):
        """Test SFTP connection without saving"""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        mission_path = self.mission_path_input.text().strip()
        
        if not all([host, username, password, mission_path]):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in all fields"
            )
            return
        
        # Test connection
        success, message = self.parent.sftp.connect(
            host, port, username, password, mission_path
        )
        
        if success:
            QMessageBox.information(
                self,
                "Connection Successful",
                f"Successfully connected to {host}:{port}"
            )
            self.parent.sftp.disconnect()  # Disconnect after test
        else:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Failed to connect:\n{message}"
            )
    
    def connect(self):
        """Connect and save configuration"""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        mission_path = self.mission_path_input.text().strip()
        save_credentials = self.save_credentials_cb.isChecked()
        
        if not all([host, username, password, mission_path]):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in all fields"
            )
            return
        
        # Attempt connection
        success, message = self.parent.sftp.connect(
            host, port, username, password, mission_path
        )
        
        if success:
            # Save configuration
            self.parent.config.set_sftp_config(
                host, port, username, password, mission_path, save_credentials
            )
            self.parent.config.update_last_connected()
            self.parent.update_status_bar()
            
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Failed to connect:\n{message}"
            )
