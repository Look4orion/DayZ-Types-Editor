"""
Settings Tab
Application settings management
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QFormLayout,
                             QGroupBox, QFileDialog, QMessageBox, QScrollArea,
                             QComboBox, QCheckBox)
from PyQt5.QtCore import Qt
from core.backup_manager import BackupManager

class SettingsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        # Main layout with scroll area
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # File Source Settings - show SFTP or Local based on current file_manager type
        from config.local_file_manager import LocalFileManager
        if isinstance(self.parent.file_manager, LocalFileManager):
            source_group = self.create_local_group()
        else:  # SFTP or not connected yet
            source_group = self.create_sftp_group()
        layout.addWidget(source_group)
        
        # Backup Settings
        backup_group = self.create_backup_group()
        layout.addWidget(backup_group)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.setLayout(main_layout)
        self.load_settings()
    
    def create_sftp_group(self):
        """Create SFTP settings group"""
        group = QGroupBox("SFTP Connection")
        layout = QFormLayout()
        
        config = self.parent.config.get_sftp_config()
        
        self.host_input = QLineEdit(config.get('host', ''))
        layout.addRow("Host:", self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(config.get('port', 22))
        layout.addRow("Port:", self.port_input)
        
        self.username_input = QLineEdit(config.get('username', ''))
        layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if config.get('save_credentials'):
            self.password_input.setText(config.get('password', ''))
        layout.addRow("Password:", self.password_input)
        
        self.mission_path_input = QLineEdit(config.get('mission_path', ''))
        layout.addRow("Mission Path:", self.mission_path_input)
        
        self.save_creds_cb = QCheckBox("Save credentials (encrypted)")
        self.save_creds_cb.setChecked(config.get('save_credentials', False))
        layout.addRow("", self.save_creds_cb)
        
        button_layout = QHBoxLayout()
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_sftp_settings)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        
        layout.addRow("", button_layout)
        
        group.setLayout(layout)
        return group
    
    def create_local_group(self):
        """Create Local Files settings group"""
        group = QGroupBox("Local Files")
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("You are using Local Files mode. File source is selected at startup.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Show current local path
        mission_path = "Not connected"
        if hasattr(self.parent, 'file_manager') and self.parent.file_manager:
            if hasattr(self.parent.file_manager, 'mission_path'):
                mission_path = self.parent.file_manager.mission_path or "Not set"
        
        path_layout = QVBoxLayout()
        path_layout.addWidget(QLabel("<b>Mission Folder:</b>"))
        path_value = QLabel(str(mission_path))
        path_value.setWordWrap(True)
        path_value.setStyleSheet("color: #51cf66; padding-left: 10px;")
        path_layout.addWidget(path_value)
        layout.addLayout(path_layout)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    # Map profile group removed - map viewer not implemented
    # def create_map_profile_group(self):
    #     \"\"\"Create map profile settings group\"\"\"
    #     ... (commented out)
    
    def create_backup_group(self):
        """Create backup settings group"""
        group = QGroupBox("Backup Management")
        layout = QVBoxLayout()
        
        # Backup location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Backup Location:"))
        
        self.backup_path_input = QLineEdit(self.parent.config.get_backup_location())
        self.backup_path_input.setReadOnly(True)
        location_layout.addWidget(self.backup_path_input, 1)
        
        browse_backup_btn = QPushButton("Browse...")
        browse_backup_btn.clicked.connect(self.browse_backup_location)
        location_layout.addWidget(browse_backup_btn)
        
        layout.addLayout(location_layout)
        
        # Backup statistics
        self.backup_stats_label = QLabel()
        self.update_backup_stats()
        layout.addWidget(self.backup_stats_label)
        
        # Backup actions
        button_layout = QHBoxLayout()
        
        open_folder_btn = QPushButton("Open Backup Folder")
        open_folder_btn.clicked.connect(self.open_backup_folder)
        button_layout.addWidget(open_folder_btn)
        
        cleanup_btn = QPushButton("Clean Up Old Backups")
        cleanup_btn.clicked.connect(self.cleanup_backups)
        cleanup_btn.setStyleSheet("QPushButton { background-color: #c72e2e; }")
        button_layout.addWidget(cleanup_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        return group
    
    def load_settings(self):
        """Load and display settings"""
        # Map profiles removed - nothing to load currently
        pass
    
    
    # Map profile methods removed - map viewer not implemented
    
    def test_connection(self):
        """Test SFTP connection"""
        from ui.sftp_dialog import SFTPDialog
        dialog = SFTPDialog(self.parent)
        dialog.exec_()
    
    def save_sftp_settings(self):
        """Save SFTP settings"""
        self.parent.config.set_sftp_config(
            self.host_input.text().strip(),
            self.port_input.value(),
            self.username_input.text().strip(),
            self.password_input.text(),
            self.mission_path_input.text().strip(),
            self.save_creds_cb.isChecked()
        )
        
        QMessageBox.information(self, "Settings Saved", "SFTP settings have been saved.")
    
    def browse_backup_location(self):
        """Browse for backup location"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Directory",
            self.parent.config.get_backup_location()
        )
        
        if dir_path:
            self.parent.config.set_backup_location(dir_path)
            self.backup_path_input.setText(dir_path)
            self.parent.backup_manager = BackupManager(dir_path)
            self.update_backup_stats()
    
    def open_backup_folder(self):
        """Open backup folder in file manager"""
        import os
        import subprocess
        import platform
        
        path = self.parent.config.get_backup_location()
        
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux
            subprocess.Popen(['xdg-open', path])
    
    def cleanup_backups(self):
        """Clean up old backups"""
        stats = self.parent.backup_manager.get_backup_statistics()
        
        reply = QMessageBox.question(
            self,
            "Clean Up Backups",
            f"Keep only the last 10 backups for each file?\n\n"
            f"Current: {stats['total_backups']} backups ({stats['total_size_mb']:.1f} MB)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted = self.parent.backup_manager.cleanup_old_backups(keep_last_n=10)
            self.update_backup_stats()
            QMessageBox.information(
                self,
                "Cleanup Complete",
                f"Deleted {deleted} old backup(s)."
            )
    
    def update_backup_stats(self):
        """Update backup statistics display"""
        stats = self.parent.backup_manager.get_backup_statistics()
        self.backup_stats_label.setText(
            f"Current Backups: {stats['total_backups']} files ({stats['total_size_mb']:.1f} MB)"
        )
