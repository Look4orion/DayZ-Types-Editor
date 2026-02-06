"""
Add Item Dialog - For adding items to cargo/attachments blocks
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QDoubleSpinBox, QDialogButtonBox, QMessageBox, QLabel)
from typing import List, Optional
from models.types_file import TypesFile

class AddItemDialog(QDialog):
    def __init__(self, parent, types_files: List[TypesFile], has_existing_items: bool):
        super().__init__(parent)
        self.types_files = types_files
        self.has_existing_items = has_existing_items
        
        self.setWindowTitle("Add Item")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Item name with autocomplete
        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        self.item_combo.setPlaceholderText("Type or select item name")
        self.populate_item_names()
        form_layout.addRow("Item Name:", self.item_combo)
        
        # Chance (required if block has multiple items)
        self.chance_spin = QDoubleSpinBox()
        self.chance_spin.setRange(0.0, 1.0)
        self.chance_spin.setSingleStep(0.1)
        self.chance_spin.setValue(1.0)
        self.chance_spin.setDecimals(2)
        
        if self.has_existing_items:
            # Chance is required
            form_layout.addRow("Chance (required)*:", self.chance_spin)
            info_label = QLabel("* Chance is required when block has multiple items")
            info_label.setStyleSheet("color: #888; font-size: 10px;")
            layout.addWidget(info_label)
        else:
            # Chance is optional
            form_layout.addRow("Chance (optional):", self.chance_spin)
            info_label = QLabel("Leave as 1.0 for implicit chance (can be omitted for single item)")
            info_label.setStyleSheet("color: #888; font-size: 10px;")
            layout.addWidget(info_label)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def populate_item_names(self):
        """Populate item name dropdown from types files"""
        if not self.types_files:
            return
        
        # Collect all item names
        item_names = set()
        for types_file in self.types_files:
            for item in types_file.items:
                item_names.add(item.name)
        
        # Add to combo
        for name in sorted(item_names):
            self.item_combo.addItem(name)
        
        # Set completer
        self.item_combo.setInsertPolicy(QComboBox.NoInsert)
        self.item_combo.completer().setCompletionMode(self.item_combo.completer().PopupCompletion)
        self.item_combo.completer().setCaseSensitivity(0)  # Case insensitive
    
    def validate_and_accept(self):
        item_name = self.item_combo.currentText().strip()
        
        if not item_name:
            QMessageBox.warning(self, "Invalid Input", "Item name cannot be empty.")
            return
        
        self.accept()
    
    def get_item_name(self) -> str:
        return self.item_combo.currentText().strip()
    
    def get_item_chance(self) -> Optional[float]:
        """Get item chance - returns None if 1.0 and block has single item"""
        chance = self.chance_spin.value()
        
        # If this is the first item and chance is 1.0, return None (implicit)
        if not self.has_existing_items and chance == 1.0:
            return None
        
        return chance
