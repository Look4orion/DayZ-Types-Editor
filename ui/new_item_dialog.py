"""
New Item Dialog
Allows creating new type entries with duplicate checking
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox,
                             QCheckBox, QGroupBox, QGridLayout, QMessageBox,
                             QWidget, QScrollArea)
from PyQt5.QtCore import Qt
from models.type_item import TypeItem
from typing import List
from ui.draggable_spinbox import EnhancedSpinBox

class NewItemDialog(QDialog):
    def __init__(self, parent, types_files, limits_parser):
        super().__init__(parent)
        self.parent = parent
        self.types_files = types_files
        self.limits_parser = limits_parser
        self.created_item = None
        self.target_file = None
        
        self.setWindowTitle("Add New Item")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        
        # Create scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
            QGroupBox {
                color: #cccccc;
                border: 1px solid #444;
                margin-top: 6px;
                padding-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
        # Required fields
        required_group = QGroupBox("Required Information")
        required_layout = QFormLayout()
        
        # Item name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter unique item name (e.g., MyCustomItem)")
        required_layout.addRow("Item Name:", self.name_input)
        
        # Target file
        self.file_combo = QComboBox()
        for tf in self.types_files:
            # Show full relative path so user can distinguish multiple types.xml files
            self.file_combo.addItem(tf.path, tf)
        required_layout.addRow("Add to File:", self.file_combo)
        
        required_group.setLayout(required_layout)
        layout.addWidget(required_group)
        
        # Numeric fields
        numeric_group = QGroupBox("Numeric Values")
        numeric_layout = QFormLayout()
        
        self.nominal_spin = EnhancedSpinBox()
        self.nominal_spin.setRange(0, 99999999)
        self.nominal_spin.setValue(0)
        numeric_layout.addRow("Nominal:", self.nominal_spin)
        
        self.lifetime_spin = EnhancedSpinBox()
        self.lifetime_spin.setRange(0, 99999999)
        self.lifetime_spin.setValue(3600)
        numeric_layout.addRow("Lifetime:", self.lifetime_spin)
        
        self.min_spin = EnhancedSpinBox()
        self.min_spin.setRange(0, 99999999)
        self.min_spin.setValue(0)
        numeric_layout.addRow("Min:", self.min_spin)
        
        self.restock_spin = EnhancedSpinBox()
        self.restock_spin.setRange(0, 99999999)
        self.restock_spin.setValue(0)
        numeric_layout.addRow("Restock:", self.restock_spin)
        
        self.quantmin_spin = EnhancedSpinBox()
        self.quantmin_spin.setRange(-1, 100)
        self.quantmin_spin.setValue(-1)
        numeric_layout.addRow("Quantmin:", self.quantmin_spin)
        
        self.quantmax_spin = EnhancedSpinBox()
        self.quantmax_spin.setRange(-1, 100)
        self.quantmax_spin.setValue(-1)
        numeric_layout.addRow("Quantmax:", self.quantmax_spin)
        
        self.cost_spin = EnhancedSpinBox()
        self.cost_spin.setRange(0, 100)
        self.cost_spin.setValue(100)
        numeric_layout.addRow("Cost:", self.cost_spin)
        
        numeric_group.setLayout(numeric_layout)
        layout.addWidget(numeric_group)
        
        # Category
        category_group = QGroupBox("Category")
        category_layout = QVBoxLayout()
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("(None)")
        if self.limits_parser:
            for category in sorted(self.limits_parser.get_categories()):
                self.category_combo.addItem(category)
        category_layout.addWidget(self.category_combo)
        
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)
        
        # Usage checkboxes
        usage_group = QGroupBox("Usage (Multiple)")
        usage_layout = QGridLayout()
        usage_layout.setSpacing(4)
        
        self.usage_checkboxes = []
        if self.limits_parser:
            usages = sorted(self.limits_parser.get_usages())
            for idx, usage in enumerate(usages):
                cb = QCheckBox(usage)
                row = idx // 2
                col = idx % 2
                usage_layout.addWidget(cb, row, col)
                self.usage_checkboxes.append(cb)
        
        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)
        
        # Value checkboxes
        value_group = QGroupBox("Value (Multiple)")
        value_layout = QGridLayout()
        value_layout.setSpacing(4)
        
        self.value_checkboxes = []
        if self.limits_parser:
            values = sorted(self.limits_parser.get_values())
            for idx, value in enumerate(values):
                cb = QCheckBox(value)
                row = idx // 2
                col = idx % 2
                value_layout.addWidget(cb, row, col)
                self.value_checkboxes.append(cb)
        
        value_group.setLayout(value_layout)
        layout.addWidget(value_group)
        
        # Tag checkboxes
        tag_group = QGroupBox("Tag (Multiple)")
        tag_layout = QGridLayout()
        tag_layout.setSpacing(4)
        
        self.tag_checkboxes = []
        if self.limits_parser:
            tags = sorted(self.limits_parser.get_tags())
            for idx, tag in enumerate(tags):
                cb = QCheckBox(tag)
                row = idx // 2
                col = idx % 2
                tag_layout.addWidget(cb, row, col)
                self.tag_checkboxes.append(cb)
        
        tag_group.setLayout(tag_layout)
        layout.addWidget(tag_group)
        
        # Flags
        flags_group = QGroupBox("Flags")
        flags_layout = QGridLayout()
        
        self.count_in_cargo_cb = QCheckBox("Count in Cargo")
        flags_layout.addWidget(self.count_in_cargo_cb, 0, 0)
        
        self.count_in_hoarder_cb = QCheckBox("Count in Hoarder")
        flags_layout.addWidget(self.count_in_hoarder_cb, 0, 1)
        
        self.count_in_map_cb = QCheckBox("Count in Map")
        self.count_in_map_cb.setChecked(True)  # Default to 1
        flags_layout.addWidget(self.count_in_map_cb, 1, 0)
        
        self.count_in_player_cb = QCheckBox("Count in Player")
        flags_layout.addWidget(self.count_in_player_cb, 1, 1)
        
        self.crafted_cb = QCheckBox("Crafted")
        flags_layout.addWidget(self.crafted_cb, 2, 0)
        
        self.deloot_cb = QCheckBox("Deloot")
        flags_layout.addWidget(self.deloot_cb, 2, 1)
        
        flags_group.setLayout(flags_layout)
        layout.addWidget(flags_group)
        
        # Set content widget
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Buttons (outside scroll area, always visible)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        create_btn = QPushButton("Create Item")
        create_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        create_btn.clicked.connect(self.create_item)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("QPushButton { background-color: #555; }")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def check_duplicate_name(self, name: str) -> List[str]:
        """Check if item name already exists, return list of files containing it"""
        duplicate_files = []
        
        for types_file in self.types_files:
            for item in types_file.items:
                if item.name.lower() == name.lower():
                    # Get display name
                    display_name = types_file.path.split('/')[-1] if '/' in types_file.path else types_file.path
                    duplicate_files.append(display_name)
                    break  # Only add file once even if multiple matches
        
        return duplicate_files
    
    def create_item(self):
        """Create new item with validation"""
        # Validate name
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Item name cannot be empty."
            )
            self.name_input.setFocus()
            return
        
        # Check for duplicates
        duplicate_files = self.check_duplicate_name(name)
        
        if duplicate_files:
            # Show duplicate warning with options
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Item Already Exists")
            
            file_list = "\n• ".join(duplicate_files)
            msg.setText(f"An item named '{name}' already exists in:\n\n• {file_list}\n\n"
                       f"You cannot create duplicate items.")
            
            edit_btn = msg.addButton("Edit Existing Item", QMessageBox.AcceptRole)
            change_btn = msg.addButton("Change Name", QMessageBox.RejectRole)
            
            msg.exec_()
            
            if msg.clickedButton() == edit_btn:
                # Close dialog and jump to existing item
                self.reject()
                self.parent.jump_to_item(name)
            else:
                # Return to name field
                self.name_input.setFocus()
                self.name_input.selectAll()
            
            return
        
        # Get target file
        self.target_file = self.file_combo.currentData()
        
        # Validate min <= nominal
        nominal_value = self.nominal_spin.value()
        min_value = self.min_spin.value()
        if min_value > nominal_value:
            min_value = nominal_value
        
        # Create item
        category_text = self.category_combo.currentText()
        category = None if category_text == "(None)" else category_text
        
        # Get selected usage, value, tag
        usage_list = [cb.text() for cb in self.usage_checkboxes if cb.isChecked()]
        value_list = [cb.text() for cb in self.value_checkboxes if cb.isChecked()]
        tag_list = [cb.text() for cb in self.tag_checkboxes if cb.isChecked()]
        
        self.created_item = TypeItem(
            name=name,
            nominal=nominal_value,
            lifetime=self.lifetime_spin.value(),
            restock=self.restock_spin.value(),
            min=min_value,
            quantmin=self.quantmin_spin.value(),
            quantmax=self.quantmax_spin.value(),
            cost=self.cost_spin.value(),
            category=category,
            usage=usage_list,
            value=value_list,
            tag=tag_list,
            count_in_cargo=1 if self.count_in_cargo_cb.isChecked() else 0,
            count_in_hoarder=1 if self.count_in_hoarder_cb.isChecked() else 0,
            count_in_map=1 if self.count_in_map_cb.isChecked() else 0,
            count_in_player=1 if self.count_in_player_cb.isChecked() else 0,
            crafted=1 if self.crafted_cb.isChecked() else 0,
            deloot=1 if self.deloot_cb.isChecked() else 0,
            source_file=self.target_file.path,
            modified=True
        )
        
        self.accept()
