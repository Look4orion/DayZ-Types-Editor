"""
Save Dialog - Select which modified files to save
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QScrollArea, QWidget,
                             QFrame)
from PyQt5.QtCore import Qt
from typing import List
from models.types_file import TypesFile

class SaveDialog(QDialog):
    """Dialog to select which modified files to save"""
    
    def __init__(self, parent, types_files: List[TypesFile]):
        super().__init__(parent)
        self.types_files = types_files
        self.file_checkboxes = {}
        
        self.setWindowTitle("Save Changes")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Select files to save ({len(self.types_files)} file(s) modified):")
        header.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        layout.addWidget(header)
        
        # Scrollable file list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(5)
        
        # Create checkbox for each file
        for types_file in self.types_files:
            modified_count = len(types_file.get_modified_items())
            
            cb = QCheckBox(f"{types_file.path} ({modified_count} item(s) modified)")
            cb.setChecked(True)  # All checked by default
            cb.setProperty('types_file', types_file)
            
            self.file_checkboxes[types_file.path] = cb
            container_layout.addWidget(cb)
        
        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Select All / None buttons
        select_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_none)
        select_layout.addWidget(select_none_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Save / Cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Selected")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def select_all(self):
        """Check all file checkboxes"""
        for cb in self.file_checkboxes.values():
            cb.setChecked(True)
    
    def select_none(self):
        """Uncheck all file checkboxes"""
        for cb in self.file_checkboxes.values():
            cb.setChecked(False)
    
    def get_selected_files(self) -> List[TypesFile]:
        """Get list of selected files to save"""
        selected = []
        for cb in self.file_checkboxes.values():
            if cb.isChecked():
                types_file = cb.property('types_file')
                selected.append(types_file)
        return selected
    
    def apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #d4d4d4;
            }
            QCheckBox {
                color: #d4d4d4;
                spacing: 8px;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555;
                background-color: #2d2d2d;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            QCheckBox::indicator:hover {
                border-color: #777;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 6px 16px;
                border-radius: 2px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QPushButton:default {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            QPushButton:default:hover {
                background-color: #1177bb;
            }
            QScrollArea {
                border: 1px solid #555;
                background-color: #252526;
            }
        """)
