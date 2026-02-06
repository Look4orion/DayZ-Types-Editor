"""
Save Dialog - Select which modified files to save
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QScrollArea, QWidget,
                             QFrame)
from PyQt5.QtCore import Qt
from typing import List, Optional
from models.types_file import TypesFile
from models.spawnable_type import SpawnableTypesFile

class SaveDialog(QDialog):
    """Dialog to select which modified files to save"""
    
    def __init__(self, parent, types_files: List[TypesFile], 
                 spawnabletypes_files: List[SpawnableTypesFile] = None,
                 has_random_preset_changes: bool = False):
        super().__init__(parent)
        self.types_files = types_files
        self.spawnabletypes_files = spawnabletypes_files or []
        self.has_random_preset_changes = has_random_preset_changes
        self.file_checkboxes = {}
        self.spawnabletypes_checkboxes = {}
        self.random_presets_checkbox = None
        
        self.setWindowTitle("Save Changes")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout()
        
        # Count total changes
        total_files = len(self.types_files) + len(self.spawnabletypes_files)
        if self.has_random_preset_changes:
            total_files += 1
        
        # Header
        header = QLabel(f"Select files to save ({total_files} file(s) modified):")
        header.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        layout.addWidget(header)
        
        # Scrollable file list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setSpacing(5)
        
        # Create checkbox for each types file
        for types_file in self.types_files:
            modified_count = len(types_file.get_modified_items())
            
            cb = QCheckBox(f"{types_file.path} ({modified_count} item(s) modified)")
            cb.setChecked(True)  # All checked by default
            cb.setProperty('types_file', types_file)
            
            self.file_checkboxes[types_file.path] = cb
            container_layout.addWidget(cb)
        
        # Create checkbox for each spawnable types file
        for spawnable_types_file in self.spawnabletypes_files:
            type_count = len(spawnable_types_file.types)
            
            cb = QCheckBox(f"{spawnable_types_file.source_file} ({type_count} type(s))")
            cb.setChecked(True)  # All checked by default
            cb.setProperty('spawnable_types_file', spawnable_types_file)
            
            self.spawnabletypes_checkboxes[spawnable_types_file.source_file] = cb
            container_layout.addWidget(cb)
        
        # Add random presets checkbox if modified
        if self.has_random_preset_changes:
            cb = QCheckBox("cfgrandompresets.xml (modified)")
            cb.setChecked(True)
            self.random_presets_checkbox = cb
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
        for cb in self.spawnabletypes_checkboxes.values():
            cb.setChecked(True)
        if self.random_presets_checkbox:
            self.random_presets_checkbox.setChecked(True)
    
    def select_none(self):
        """Uncheck all file checkboxes"""
        for cb in self.file_checkboxes.values():
            cb.setChecked(False)
        for cb in self.spawnabletypes_checkboxes.values():
            cb.setChecked(False)
        if self.random_presets_checkbox:
            self.random_presets_checkbox.setChecked(False)
    
    def get_selected_files(self) -> List[TypesFile]:
        """Get list of selected types files to save"""
        selected = []
        for cb in self.file_checkboxes.values():
            if cb.isChecked():
                types_file = cb.property('types_file')
                selected.append(types_file)
        return selected
    
    def get_selected_spawnabletypes_files(self) -> List[SpawnableTypesFile]:
        """Get list of selected spawnable types files to save"""
        selected = []
        for cb in self.spawnabletypes_checkboxes.values():
            if cb.isChecked():
                spawnable_types_file = cb.property('spawnable_types_file')
                selected.append(spawnable_types_file)
        return selected
    
    def should_save_random_presets(self) -> bool:
        """Check if random presets should be saved"""
        if self.random_presets_checkbox:
            return self.random_presets_checkbox.isChecked()
        return False
    
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
