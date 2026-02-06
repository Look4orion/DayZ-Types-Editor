"""
Batch Operations Dialog
Allows batch modification of multiple items with preview
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDoubleSpinBox, QSpinBox, QTableWidget,
                             QTableWidgetItem, QCheckBox, QGroupBox, QComboBox,
                             QScrollArea, QHeaderView, QFrame, QMessageBox, QGridLayout,
                             QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from models.type_item import TypeItem
from typing import List, Dict
from ui.draggable_spinbox import EnhancedSpinBox, EnhancedDoubleSpinBox
from ui.toggle_switch import ToggleSwitch

class BatchOperationsDialog(QDialog):
    def __init__(self, parent, items: List[TypeItem], filter_description: str):
        super().__init__(parent)
        self.parent = parent
        self.items = items
        self.filter_description = filter_description
        self.preview_data: List[Dict] = []
        
        self.setWindowTitle("Batch Operations - Edit Multiple Items")
        self.setModal(True)
        self.resize(1400, 800)  # Default size
        self.setMinimumSize(1200, 600)  # Minimum but allow resize
        
        self.init_ui()
        self.calculate_preview()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Info section
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("QFrame { background-color: #252526; padding: 10px; }")
        info_layout = QVBoxLayout()
        
        filter_label = QLabel(f"<b>Current Filters:</b> {self.filter_description}")
        filter_label.setWordWrap(True)
        info_layout.addWidget(filter_label)
        
        self.items_label = QLabel(f"<b>Items Affected:</b> {len(self.items)}")
        info_layout.addWidget(self.items_label)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Field controls section - Two column layout
        fields_group = QGroupBox("Apply To Fields")
        fields_main_layout = QHBoxLayout()
        
        # Left side: Numeric fields
        left_group = QGroupBox("Numeric Fields")
        left_layout = QGridLayout()
        left_layout.setSpacing(8)
        
        # Headers for left side
        left_layout.addWidget(QLabel("<b>Field</b>"), 0, 0)
        left_layout.addWidget(QLabel("<b>Mode</b>"), 0, 1)
        left_layout.addWidget(QLabel("<b>Value</b>"), 0, 2)
        
        # Middle: Category and Multi-Select
        middle_group = QGroupBox("Category & Multi-Select")
        middle_outer_layout = QVBoxLayout()  # Outer layout for the group
        middle_layout = QGridLayout()
        middle_layout.setSpacing(8)
        
        # Headers for middle
        middle_layout.addWidget(QLabel("<b>Field</b>"), 0, 0)
        middle_layout.addWidget(QLabel("<b>Set To</b>"), 0, 1)
        
        # Right side: Flags
        right_group = QGroupBox("Flags")
        right_layout = QGridLayout()
        right_layout.setSpacing(8)
        
        # Headers for right side
        right_layout.addWidget(QLabel("<b>Flag</b>"), 0, 0)
        right_layout.addWidget(QLabel("<b>Set To</b>"), 0, 1)
        
        # Create controls for each field
        self.field_controls = {}
        
        # Numeric fields (left side)
        numeric_fields = [
            ('nominal', 'Nominal', 'multiply', 1.5),
            ('lifetime', 'Lifetime', 'multiply', 1.5),
            ('min', 'Min', 'multiply', 1.5),
            ('restock', 'Restock', 'multiply', 1.5),
            ('quantmin', 'Quantmin', 'set', -1),
            ('quantmax', 'Quantmax', 'set', -1),
            ('cost', 'Cost', 'set', 100)
        ]
        
        # Flag fields (right side)
        flag_fields = [
            ('count_in_cargo', 'Count in Cargo', 'flag', 0),
            ('count_in_hoarder', 'Count in Hoarder', 'flag', 0),
            ('count_in_map', 'Count in Map', 'flag', 1),
            ('count_in_player', 'Count in Player', 'flag', 0),
            ('crafted', 'Crafted', 'flag', 0),
            ('deloot', 'Deloot', 'flag', 0)
        ]
        
        # Build numeric fields
        for row, (field_name, display_name, default_mode, default_value) in enumerate(numeric_fields, start=1):
            # Checkbox - NO DEFAULT CHECKS
            cb = QCheckBox(display_name)
            cb.setChecked(False)  # All unchecked by default
            cb.stateChanged.connect(self.calculate_preview)
            left_layout.addWidget(cb, row, 0)
            
            # Mode dropdown
            mode_combo = QComboBox()
            mode_combo.addItems(['Multiply', 'Set Value'])
            mode_combo.setCurrentText('Multiply' if default_mode == 'multiply' else 'Set Value')
            mode_combo.setProperty('field_name', field_name)
            mode_combo.currentTextChanged.connect(self.on_mode_changed)
            left_layout.addWidget(mode_combo, row, 1)
            
            # Value input with field-specific limits - DRAGGABLE
            if default_mode == 'multiply':
                # Multiplier - use draggable double spin box
                value_input = EnhancedDoubleSpinBox()
                value_input.setRange(0.01, 100.0)
                value_input.setValue(default_value)
                value_input.setSingleStep(0.1)
                value_input.setDecimals(2)
            else:
                # Set value - use draggable integer spin box with field-specific limits
                value_input = EnhancedSpinBox()
                
                # Set ranges based on field type
                if field_name in ['quantmin', 'quantmax']:
                    value_input.setRange(-1, 100)
                elif field_name == 'cost':
                    value_input.setRange(0, 100)
                else:
                    value_input.setRange(0, 99999999)
                
                value_input.setValue(int(default_value))
            
            value_input.valueChanged.connect(self.calculate_preview)
            left_layout.addWidget(value_input, row, 2)
            
            # Store references
            self.field_controls[field_name] = {
                'checkbox': cb,
                'mode': mode_combo,
                'value': value_input
            }
        
        # Build middle fields - Category and Multi-select in scrollable area
        middle_row = 1
        
        # Category field (always at top)
        category_cb = QCheckBox("Category")
        category_cb.setChecked(False)
        category_cb.stateChanged.connect(self.calculate_preview)
        middle_layout.addWidget(category_cb, middle_row, 0)
        
        category_combo = QComboBox()
        category_combo.addItem("(Clear)")
        if self.parent.limits_parser:
            for cat in sorted(self.parent.limits_parser.get_categories()):
                category_combo.addItem(cat)
        category_combo.currentTextChanged.connect(self.calculate_preview)
        middle_layout.addWidget(category_combo, middle_row, 1)
        
        self.field_controls['category'] = {
            'checkbox': category_cb,
            'mode': None,
            'value': category_combo
        }
        middle_row += 1
        
        # Scrollable area for Usage, Value, Tag with 3 columns
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.StyledPanel)
        scroll.setMaximumHeight(400)  # Limit height
        
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(4)
        
        # Multi-select fields in 3 columns
        multi_select_fields = []
        
        if self.parent.limits_parser:
            # Usage
            usages = sorted(self.parent.limits_parser.get_usages())
            for usage in usages:
                multi_select_fields.append(('usage', usage, 0))
            
            # Value
            values = sorted(self.parent.limits_parser.get_values())
            for value in values:
                multi_select_fields.append(('value', value, 0))
            
            # Tag
            tags = sorted(self.parent.limits_parser.get_tags())
            for tag in tags:
                multi_select_fields.append(('tag', tag, 0))
        
        # Build multi-select fields in 3 columns
        col = 0
        row = 0
        for field_type, field_value, default in multi_select_fields:
            # Create container for checkbox + toggle
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(4)
            
            cb = QCheckBox(f"{field_type.capitalize()}: {field_value}")
            cb.setChecked(False)
            cb.stateChanged.connect(self.calculate_preview)
            container_layout.addWidget(cb)
            
            toggle = ToggleSwitch()
            toggle.setChecked(default == 1)
            toggle.stateChanged.connect(self.calculate_preview)
            container_layout.addWidget(toggle)
            
            # Add to grid in columns
            scroll_layout.addWidget(container, row, col)
            
            # Store with unique key
            key = f"{field_type}_{field_value}"
            self.field_controls[key] = {
                'checkbox': cb,
                'mode': None,
                'value': toggle,
                'field_type': field_type,
                'field_value': field_value
            }
            
            # Move to next column/row
            col += 1
            if col >= 3:  # 3 columns
                col = 0
                row += 1
        
        scroll.setWidget(scroll_widget)
        middle_layout.addWidget(scroll, middle_row, 0, 1, 2)  # Span both columns
        
        # Set the layout for middle group
        middle_group.setLayout(middle_layout)
        
        # Build flag fields
        for row, (field_name, display_name, default_mode, default_value) in enumerate(flag_fields, start=1):
            # Checkbox
            cb = QCheckBox(display_name)
            cb.setChecked(False)  # Flags unchecked by default
            cb.stateChanged.connect(self.calculate_preview)
            right_layout.addWidget(cb, row, 0)
            
            # Toggle switch (replaces 0/1 spinbox)
            toggle = ToggleSwitch()
            toggle.setChecked(default_value == 1)  # Set initial state
            toggle.stateChanged.connect(self.calculate_preview)
            right_layout.addWidget(toggle, row, 1)
            
            # Store references (mode is None for flags)
            self.field_controls[field_name] = {
                'checkbox': cb,
                'mode': None,
                'value': toggle  # Store toggle switch as value control
            }
        
        # Assemble three-column layout
        left_group.setLayout(left_layout)
        right_group.setLayout(right_layout)
        fields_main_layout.addWidget(left_group)
        fields_main_layout.addWidget(middle_group)
        fields_main_layout.addWidget(right_group)
        fields_group.setLayout(fields_main_layout)
        layout.addWidget(fields_group)
        
        # Preview section
        preview_label = QLabel("<b>Preview Changes</b> (showing first 100)")
        layout.addWidget(preview_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(14)
        self.preview_table.setHorizontalHeaderLabels([
            "Item", "Nominal", "Lifetime", "Min", "Restock", "Quantmin", "Quantmax", "Cost",
            "Cargo", "Hoarder", "Map", "Player", "Crafted", "Deloot"
        ])
        
        # Configure table
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.setSelectionMode(QTableWidget.NoSelection)
        self.preview_table.setAlternatingRowColors(True)
        
        # Style for better readability
        self.preview_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        
        # Header settings
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item name stretches
        for i in range(1, 14):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.preview_table)
        
        # Summary label
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("QLabel { font-size: 11px; color: #999; }")
        layout.addWidget(self.summary_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("QPushButton { background-color: #555; }")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_mode_changed(self, mode_text):
        """Handle mode change - update value spin box limits"""
        sender = self.sender()
        field_name = sender.property('field_name')
        
        if field_name not in self.field_controls:
            return
        
        value_input = self.field_controls[field_name]['value']
        current_value = value_input.value()
        
        # Update limits based on mode
        if mode_text == 'Multiply':
            # Switch to multiplier mode
            if not isinstance(value_input, QDoubleSpinBox):
                # Need to replace with QDoubleSpinBox, but for simplicity just adjust range
                value_input.setRange(0, 100)
                value_input.setValue(min(current_value, 100) if current_value > 0 else 1.5)
        else:  # Set Value
            # Set field-specific limits
            if field_name in ['quantmin', 'quantmax']:
                value_input.setRange(-1, 100)
                if current_value > 100:
                    value_input.setValue(-1)
            elif field_name == 'cost':
                value_input.setRange(0, 100)
                if current_value > 100:
                    value_input.setValue(100)
            else:
                value_input.setRange(0, 99999999)
        
        # Recalculate preview
        self.calculate_preview()
    
    def calculate_preview(self):
        """Calculate and display preview of changes - one row per item"""
        self.preview_data = []
        
        # Calculate changes for each item
        for item in self.items:
            item_data = {
                'item': item,
                'name': item.name,
                'changes': {}
            }
            
            # Check each field
            for field_name, controls in self.field_controls.items():
                if controls['checkbox'].isChecked():
                    
                    # Handle category
                    if field_name == 'category':
                        old_value = item.category
                        combo_text = controls['value'].currentText()
                        new_value = None if combo_text == "(Clear)" else combo_text
                        item_data['changes'][field_name] = {
                            'old': old_value,
                            'new': new_value
                        }
                    
                    # Handle multi-select fields (usage, value, tag)
                    elif 'field_type' in controls:
                        field_type = controls['field_type']  # 'usage', 'value', or 'tag'
                        field_value = controls['field_value']  # e.g., 'Military'
                        is_enabled = controls['value'].isChecked()  # ON or OFF
                        
                        # Get current list
                        old_list = getattr(item, field_type)
                        new_list = list(old_list)  # Copy
                        
                        # Add or remove based on toggle
                        if is_enabled and field_value not in new_list:
                            new_list.append(field_value)
                        elif not is_enabled and field_value in new_list:
                            new_list.remove(field_value)
                        
                        # Store if changed
                        if sorted(old_list) != sorted(new_list):
                            # Store in changes per field type (aggregate all usage/value/tag changes)
                            if field_type not in item_data['changes']:
                                item_data['changes'][field_type] = {
                                    'old': old_list,
                                    'new': []
                                }
                            item_data['changes'][field_type]['new'] = new_list
                    
                    # Handle regular numeric fields and flags
                    else:
                        old_value = getattr(item, field_name)
                        
                        # Flags don't have mode dropdown (use toggle switch)
                        if controls['mode'] is None:
                            # Flag field - get value from toggle switch (1 if checked, 0 if not)
                            new_value = 1 if controls['value'].isChecked() else 0
                        else:
                            mode = controls['mode'].currentText()
                            input_value = controls['value'].value()
                            
                            if mode == 'Multiply':
                                new_value = int(old_value * input_value)
                            else:  # Set Value
                                new_value = int(input_value)
                            
                            # Validation: min shouldn't exceed nominal
                            if field_name == 'min' and 'nominal' in self.field_controls:
                                nominal_value = getattr(item, 'nominal')
                                # If nominal is also being changed, use new nominal
                                if self.field_controls['nominal']['checkbox'].isChecked():
                                    nominal_controls = self.field_controls['nominal']
                                    if nominal_controls['mode'].currentText() == 'Multiply':
                                        nominal_value = int(nominal_value * nominal_controls['value'].value())
                                    else:
                                        nominal_value = int(nominal_controls['value'].value())
                                new_value = min(new_value, nominal_value)
                        
                        item_data['changes'][field_name] = {
                            'old': old_value,
                            'new': new_value
                        }
            
            # Only add if there are changes
            if item_data['changes']:
                self.preview_data.append(item_data)
        
        self.populate_preview_table()
    
    def populate_preview_table(self):
        """Populate preview table - one row per item, all fields as columns"""
        # Show first 100 items
        display_items = self.preview_data[:100]
        
        self.preview_table.setRowCount(len(display_items))
        
        field_order = [
            'nominal', 'lifetime', 'min', 'restock', 'quantmin', 'quantmax', 'cost',
            'count_in_cargo', 'count_in_hoarder', 'count_in_map', 
            'count_in_player', 'crafted', 'deloot'
        ]
        
        for row, item_data in enumerate(display_items):
            # Item name
            name_item = QTableWidgetItem(item_data['name'])
            self.preview_table.setItem(row, 0, name_item)
            
            # Each field column
            for col_idx, field_name in enumerate(field_order, start=1):
                if field_name in item_data['changes']:
                    # Field is being changed - show old → new
                    change = item_data['changes'][field_name]
                    text = f"{change['old']} → {change['new']}"
                    cell_item = QTableWidgetItem(text)
                    # Highlight changed fields
                    cell_item.setForeground(QColor("#51cf66"))  # Green
                else:
                    # Field not being changed - show current value
                    current_value = getattr(item_data['item'], field_name)
                    cell_item = QTableWidgetItem(str(current_value))
                    cell_item.setForeground(QColor("#999"))  # Gray
                
                self.preview_table.setItem(row, col_idx, cell_item)
        
        # Update summary
        total_items = len(self.preview_data)
        total_changes = sum(len(item['changes']) for item in self.preview_data)
        
        if total_items > 100:
            self.summary_label.setText(
                f"Showing first 100 of {total_items} items with {total_changes} total changes"
            )
        else:
            self.summary_label.setText(
                f"Total: {total_items} items with {total_changes} changes"
            )
    
    def apply_changes(self):
        """Apply all changes to items"""
        if not self.preview_data:
            QMessageBox.warning(
                self,
                "No Changes",
                "No fields selected or no changes to apply."
            )
            return
        
        total_items = len(self.preview_data)
        total_changes = sum(len(item['changes']) for item in self.preview_data)
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Changes",
            f"Apply {total_changes} changes to {total_items} items?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Push to undo stack before modification
        items_to_modify = [item_data['item'] for item_data in self.preview_data]
        self.parent.parent.push_undo_state(items_to_modify)
        
        # Apply changes
        modified_files = set()
        
        for item_data in self.preview_data:
            item = item_data['item']
            
            # Apply each field change
            for field_name, change in item_data['changes'].items():
                setattr(item, field_name, change['new'])
            
            item.modified = True
            
            # Mark parent file as modified
            for types_file in self.parent.parent.types_files:
                if item in types_file.items:
                    types_file.modified = True
                    modified_files.add(types_file.path)
                    break
        
        # Success message
        QMessageBox.information(
            self,
            "Changes Applied",
            f"Successfully applied {total_changes} changes to {total_items} items across {len(modified_files)} file(s)."
        )
        
        # Refresh parent table
        self.parent.populate_table()
        self.parent.parent.update_status_bar()
        
        self.accept()
