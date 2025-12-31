"""
File Loading Progress Dialog
Shows progress while loading types files
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar,
                             QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class LoadingProgressDialog(QDialog):
    def __init__(self, parent, total_files: int):
        super().__init__(parent)
        self.total_files = total_files
        self.current_file = 0
        self.cancelled = False
        
        self.setWindowTitle("Loading Files")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Loading types files...")
        self.status_label.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Current file label
        self.file_label = QLabel("")
        self.file_label.setStyleSheet("font-size: 11px; color: #999; padding: 5px;")
        layout.addWidget(self.file_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_files)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Stats label
        self.stats_label = QLabel("0 of {} files loaded".format(self.total_files))
        self.stats_label.setStyleSheet("font-size: 10px; color: #999; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_progress(self, current: int, file_path: str, success: bool):
        """Update progress display"""
        self.current_file = current
        self.progress_bar.setValue(current)
        
        # Show current file being loaded
        filename = file_path.split('/')[-1] if '/' in file_path else file_path
        status = "✓" if success else "✗"
        self.file_label.setText(f"{status} {filename}")
        
        # Update stats
        self.stats_label.setText(f"{current} of {self.total_files} files processed")
    
    def cancel(self):
        """Cancel loading"""
        self.cancelled = True
        self.reject()
    
    def is_cancelled(self) -> bool:
        """Check if loading was cancelled"""
        return self.cancelled
