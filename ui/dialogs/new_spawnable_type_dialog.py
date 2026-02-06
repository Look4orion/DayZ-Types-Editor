"""
New Spawnable Type Dialog
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QComboBox, QDialogButtonBox, QMessageBox)
from typing import List
from models.spawnable_type import SpawnableTypesFile

class NewSpawnableTypeDialog(QDialog):
    def __init__(self, parent, spawnabletypes_files: List[SpawnableTypesFile]):
        super().__init__(parent)
        self.spawnabletypes_files = spawnabletypes_files
        
        self.setWindowTitle("New Spawnable Type")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Type name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., ZmbM_SoldierNormal")
        form_layout.addRow("Type Name:", self.name_edit)
        
        # File selection
        self.file_combo = QComboBox()
        for f in self.spawnabletypes_files:
            self.file_combo.addItem(f.source_file, f)
        form_layout.addRow("File:", self.file_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Type name cannot be empty.")
            return
        
        # Check if name already exists in selected file
        selected_file = self.get_selected_file()
        if selected_file.get_type_by_name(name):
            QMessageBox.warning(self, "Duplicate Name", 
                              f"Type '{name}' already exists in {selected_file.source_file}.")
            return
        
        self.accept()
    
    def get_type_name(self) -> str:
        return self.name_edit.text().strip()
    
    def get_selected_file(self) -> SpawnableTypesFile:
        return self.file_combo.currentData()
