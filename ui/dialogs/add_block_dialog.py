"""
Add Block Dialog - For adding cargo/attachments blocks
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QRadioButton,
                             QComboBox, QDoubleSpinBox, QDialogButtonBox, 
                             QMessageBox, QGroupBox, QButtonGroup, QLabel)
from PyQt5.QtCore import Qt
from models.random_preset import RandomPresetsFile, PresetType
from typing import Optional

class AddBlockDialog(QDialog):
    def __init__(self, parent, block_kind: str, random_presets_file: Optional[RandomPresetsFile]):
        super().__init__(parent)
        self.block_kind = block_kind  # "cargo" or "attachments"
        self.random_presets_file = random_presets_file
        
        self.setWindowTitle(f"Add {block_kind.title()} Block")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Block type selection
        type_group = QGroupBox("Block Type")
        type_layout = QVBoxLayout()
        
        self.button_group = QButtonGroup()
        
        self.preset_radio = QRadioButton("Preset-based")
        self.button_group.addButton(self.preset_radio)
        type_layout.addWidget(self.preset_radio)
        
        self.chance_radio = QRadioButton("Chance-based (with items)")
        self.button_group.addButton(self.chance_radio)
        type_layout.addWidget(self.chance_radio)
        
        self.preset_radio.setChecked(True)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Options
        self.form_layout = QFormLayout()
        
        # Info label for chance-based
        self.info_label = QLabel("ℹ You'll be prompted to add the first item after clicking OK")
        self.info_label.setStyleSheet("color: #6c9bcf; font-size: 10px; padding: 4px;")
        self.info_label.setWordWrap(True)
        self.info_label.setVisible(False)
        layout.addWidget(self.info_label)
        
        # Preset selection
        self.preset_combo = QComboBox()
        self.populate_presets()
        self.form_layout.addRow("Preset:", self.preset_combo)
        
        # Chance spinner
        self.chance_spin = QDoubleSpinBox()
        self.chance_spin.setRange(0.0, 1.0)
        self.chance_spin.setSingleStep(0.1)
        self.chance_spin.setValue(1.0)
        self.chance_spin.setDecimals(2)
        self.form_layout.addRow("Chance:", self.chance_spin)
        
        layout.addLayout(self.form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Connect signals AFTER all widgets are created
        self.preset_radio.toggled.connect(self.on_type_changed)
        self.chance_radio.toggled.connect(self.on_type_changed)
        
        # Initial state
        self.on_type_changed()
    
    def populate_presets(self):
        """Populate preset dropdown"""
        self.preset_combo.clear()
        
        if not self.random_presets_file:
            self.preset_combo.addItem("(No presets file loaded)")
            self.preset_combo.setEnabled(False)
            return
        
        # Filter by type
        preset_type = PresetType.CARGO if self.block_kind == "cargo" else PresetType.ATTACHMENTS
        
        # Get presets of matching type
        if preset_type == PresetType.CARGO:
            matching_presets = self.random_presets_file.cargo_presets
        else:
            matching_presets = self.random_presets_file.attachments_presets
        
        if not matching_presets:
            self.preset_combo.addItem(f"(No {self.block_kind} presets found)")
            self.preset_combo.setEnabled(False)
        else:
            for preset in sorted(matching_presets, key=lambda p: p.name):
                # Build tooltip
                tooltip_lines = [f"Chance: {preset.chance}"]
                tooltip_lines.append(f"Items ({len(preset.items)}):")
                for item in preset.items:
                    tooltip_lines.append(f"  • {item.name} (chance: {item.chance})")
                tooltip = "\n".join(tooltip_lines)
                
                self.preset_combo.addItem(preset.name)
                self.preset_combo.setItemData(self.preset_combo.count() - 1, tooltip, Qt.ToolTipRole)
    
    def on_type_changed(self):
        """Handle block type radio button change"""
        is_preset = self.preset_radio.isChecked()
        
        # Show/hide appropriate fields
        self.preset_combo.setEnabled(is_preset and self.random_presets_file is not None)
        self.chance_spin.setEnabled(not is_preset)
        
        # Show info for chance-based
        self.info_label.setVisible(not is_preset)
    
    def validate_and_accept(self):
        if self.preset_radio.isChecked():
            if not self.random_presets_file:
                QMessageBox.warning(self, "No Presets", 
                                  "Random presets file is not loaded. Cannot create preset-based block.")
                return
            
            if self.preset_combo.count() == 0 or self.preset_combo.currentText().startswith("("):
                QMessageBox.warning(self, "No Preset", 
                                  f"No {self.block_kind} presets available. Please create one first or choose chance-based.")
                return
        
        self.accept()
    
    def get_block_type(self) -> str:
        """Returns 'preset' or 'chance'"""
        return "preset" if self.preset_radio.isChecked() else "chance"
    
    def get_preset_name(self) -> str:
        """Get selected preset name"""
        return self.preset_combo.currentText()
    
    def get_chance(self) -> float:
        """Get chance value"""
        return self.chance_spin.value()
