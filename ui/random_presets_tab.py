"""
Random Presets Editor Tab
Main editing interface for cfgrandompresets.xml
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QFrame, QGroupBox,
                             QSplitter, QHeaderView, QAbstractItemView, 
                             QMessageBox, QTreeWidget, QTreeWidgetItem,
                             QTreeWidgetItemIterator, QMenu,
                             QDialog, QFormLayout, QDoubleSpinBox, QComboBox,
                             QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from models.random_preset import RandomPresetsFile, RandomPreset, PresetItem, PresetType
from typing import Optional
import copy

class RandomPresetsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.presets_file: Optional[RandomPresetsFile] = None
        self.selected_preset: Optional[RandomPreset] = None
        
        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_search)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter for preset list and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Preset list with search
        left_panel = self.create_preset_list_panel()
        splitter.addWidget(left_panel)
        
        # Right: Preset details and items
        right_panel = self.create_detail_panel()
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([350, 650])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Install event filter for keyboard shortcuts
        self.items_table.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts for items table"""
        if obj == self.items_table and event.type() == event.KeyPress:
            # Delete key
            if event.key() == Qt.Key_Delete:
                if self.selected_preset and self.items_table.currentRow() >= 0:
                    self.delete_item()
                    return True
            # Ctrl+N for new item
            elif event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
                if self.selected_preset:
                    self.add_item_to_preset()
                    return True
        
        return super().eventFilter(obj, event)
    
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = QFrame()
        toolbar.setFrameShape(QFrame.StyledPanel)
        toolbar.setStyleSheet("QFrame { background-color: #252526; border-bottom: 1px solid #444; padding: 4px; }")
        toolbar.setMaximumHeight(45)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator)
        
        # New Preset button
        new_preset_btn = QPushButton("New Preset")
        new_preset_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        new_preset_btn.clicked.connect(self.show_new_preset_dialog)
        layout.addWidget(new_preset_btn)
        
        # Delete Preset button
        delete_preset_btn = QPushButton("Delete Preset")
        delete_preset_btn.setStyleSheet("QPushButton { background-color: #8B0000; }")
        delete_preset_btn.clicked.connect(self.delete_preset)
        self.delete_preset_btn = delete_preset_btn
        layout.addWidget(delete_preset_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator2)
        
        # Undo/Redo buttons
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.parent.undo)
        self.undo_btn = undo_btn
        layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.parent.redo)
        self.redo_btn = redo_btn
        layout.addWidget(redo_btn)
        
        layout.addStretch()
        
        # Stats label
        self.stats_label = QLabel("No presets loaded")
        self.stats_label.setStyleSheet("color: #888;")
        layout.addWidget(self.stats_label)
        
        toolbar.setLayout(layout)
        return toolbar
    
    def create_preset_list_panel(self):
        """Create left panel with preset list and search"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search presets...")
        self.search_box.textChanged.connect(lambda: self.search_timer.start(300))
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Preset tree
        self.preset_tree = QTreeWidget()
        self.preset_tree.setHeaderLabels(["Preset Name", "Chance", "Items"])
        self.preset_tree.setColumnWidth(0, 200)
        self.preset_tree.setColumnWidth(1, 60)
        self.preset_tree.setColumnWidth(2, 50)
        self.preset_tree.itemSelectionChanged.connect(self.on_preset_selected)
        self.preset_tree.itemDoubleClicked.connect(self.edit_preset)
        layout.addWidget(self.preset_tree)
        
        panel.setLayout(layout)
        return panel
    
    def create_detail_panel(self):
        """Create right panel with preset details"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Preset info group
        info_group = QGroupBox("Preset Information")
        info_layout = QFormLayout()
        
        # Editable name
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("Preset name...")
        self.preset_name_edit.setEnabled(False)
        self.preset_name_edit.editingFinished.connect(self.on_preset_name_changed)
        info_layout.addRow("Name:", self.preset_name_edit)
        
        # Type (read-only label)
        self.preset_type_label = QLabel("—")
        info_layout.addRow("Type:", self.preset_type_label)
        
        # Editable chance
        self.preset_chance_spin = QDoubleSpinBox()
        self.preset_chance_spin.setRange(0.0, 1.0)
        self.preset_chance_spin.setSingleStep(0.01)
        self.preset_chance_spin.setDecimals(2)
        self.preset_chance_spin.setEnabled(False)
        self.preset_chance_spin.valueChanged.connect(self.on_preset_chance_changed)
        info_layout.addRow("Chance:", self.preset_chance_spin)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Items group
        items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        # Item buttons
        item_btn_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_item_to_preset)
        self.add_item_btn = add_item_btn
        item_btn_layout.addWidget(add_item_btn)
        
        edit_item_btn = QPushButton("Edit Item")
        edit_item_btn.clicked.connect(self.edit_item)
        self.edit_item_btn = edit_item_btn
        item_btn_layout.addWidget(edit_item_btn)
        
        delete_item_btn = QPushButton("Delete Item")
        delete_item_btn.clicked.connect(self.delete_item)
        self.delete_item_btn = delete_item_btn
        item_btn_layout.addWidget(delete_item_btn)
        
        item_btn_layout.addStretch()
        items_layout.addLayout(item_btn_layout)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Chance"])
        self.items_table.horizontalHeader().setStretchLastSection(False)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.items_table.setColumnWidth(1, 80)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Enable multi-select
        self.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.items_table.itemDoubleClicked.connect(self.edit_item)
        self.items_table.itemSelectionChanged.connect(self.update_button_states)
        self.items_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.items_table.customContextMenuRequested.connect(self.show_item_context_menu)
        
        # Add keyboard shortcuts
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Delete key to delete item
        delete_shortcut = QShortcut(QKeySequence.Delete, self.items_table)
        delete_shortcut.activated.connect(self.delete_item)
        
        # Ctrl+N to add new item
        new_item_shortcut = QShortcut(QKeySequence("Ctrl+N"), self.items_table)
        new_item_shortcut.activated.connect(self.add_item_to_preset)
        
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        panel.setLayout(layout)
        return panel
    
    def load_data(self, presets_file: Optional[RandomPresetsFile]):
        """Load presets data"""
        self.presets_file = presets_file
        self.refresh_preset_list()
        self.update_stats()
        self.update_button_states()
        
        # Clear modified flag on load
        if hasattr(self.parent, 'has_random_preset_changes'):
            self.parent.has_random_preset_changes = False
    
    def refresh_preset_list(self):
        """Refresh the preset tree"""
        self.preset_tree.clear()
        
        if not self.presets_file:
            return
        
        search_text = self.search_box.text().lower()
        
        # Add cargo presets
        cargo_root = QTreeWidgetItem(self.preset_tree, ["Cargo Presets", "", ""])
        cargo_root.setExpanded(True)
        for preset in self.presets_file.cargo_presets:
            if search_text and search_text not in preset.name.lower():
                continue
            item = QTreeWidgetItem(cargo_root, [
                preset.name,
                f"{preset.chance:.2f}",
                str(preset.get_item_count())
            ])
            item.setData(0, Qt.UserRole, preset)
        
        # Add attachments presets
        attach_root = QTreeWidgetItem(self.preset_tree, ["Attachments Presets", "", ""])
        attach_root.setExpanded(True)
        for preset in self.presets_file.attachments_presets:
            if search_text and search_text not in preset.name.lower():
                continue
            item = QTreeWidgetItem(attach_root, [
                preset.name,
                f"{preset.chance:.2f}",
                str(preset.get_item_count())
            ])
            item.setData(0, Qt.UserRole, preset)
    
    def apply_search(self):
        """Apply search filter"""
        self.refresh_preset_list()
    
    def show_item_context_menu(self, position):
        """Show context menu for items table"""
        if not self.selected_preset:
            return
        
        selected_rows = self.items_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        from PyQt5.QtWidgets import QMenu
        menu = QMenu()
        
        if len(selected_rows) == 1:
            # Single item selected - show edit and delete
            edit_action = menu.addAction("Edit Item")
            edit_action.triggered.connect(self.edit_item)
            
            delete_action = menu.addAction("Delete Item")
            delete_action.triggered.connect(self.delete_item)
        else:
            # Multiple items selected - show batch operations
            batch_chance_action = menu.addAction(f"Change Chance for {len(selected_rows)} Items...")
            batch_chance_action.triggered.connect(self.batch_change_chance)
            
            menu.addSeparator()
            
            batch_delete_action = menu.addAction(f"Delete {len(selected_rows)} Items")
            batch_delete_action.triggered.connect(self.delete_item)  # Use unified delete
        
        menu.exec_(self.items_table.viewport().mapToGlobal(position))
    
    def on_preset_name_changed(self):
        """Handle preset name change"""
        if not self.selected_preset:
            return
        
        new_name = self.preset_name_edit.text().strip()
        if not new_name:
            # Revert to original
            self.preset_name_edit.setText(self.selected_preset.name)
            return
        
        if new_name != self.selected_preset.name:
            self.save_state_for_undo()
            old_name = self.selected_preset.name
            self.selected_preset.name = new_name
            self.refresh_preset_list()
            self.select_preset_by_name(new_name)
            self.parent.update_status_bar()
    
    def on_preset_chance_changed(self, value):
        """Handle preset chance change"""
        if not self.selected_preset:
            return
        
        if value != self.selected_preset.chance:
            self.save_state_for_undo()
            preset_name = self.selected_preset.name
            self.selected_preset.chance = value
            self.refresh_preset_list()
            self.select_preset_by_name(preset_name)
            self.parent.update_status_bar()
    
    def select_preset_by_name(self, preset_name: str):
        """Select a preset by name in the tree"""
        # Iterate through all items in the tree
        iterator = QTreeWidgetItemIterator(self.preset_tree)
        while iterator.value():
            item = iterator.value()
            preset = item.data(0, Qt.UserRole)
            if preset and preset.name == preset_name:
                self.preset_tree.setCurrentItem(item)
                # This will trigger on_preset_selected which updates selected_preset and display
                return
            iterator += 1
    
    def on_preset_selected(self):
        """Handle preset selection"""
        selected = self.preset_tree.selectedItems()
        if not selected:
            self.selected_preset = None
            self.clear_detail_panel()
            self.update_button_states()
            return
        
        item = selected[0]
        preset = item.data(0, Qt.UserRole)
        
        if preset:
            self.selected_preset = preset
            self.display_preset_details(preset)
        else:
            self.selected_preset = None
            self.clear_detail_panel()
        
        self.update_button_states()
    
    def display_preset_details(self, preset: RandomPreset):
        """Display preset details in right panel"""
        # Block signals while updating to avoid triggering change handlers
        self.preset_name_edit.blockSignals(True)
        self.preset_chance_spin.blockSignals(True)
        
        self.preset_name_edit.setText(preset.name)
        self.preset_name_edit.setEnabled(True)
        self.preset_type_label.setText(preset.preset_type.value.capitalize())
        self.preset_chance_spin.setValue(preset.chance)
        self.preset_chance_spin.setEnabled(True)
        
        # Unblock signals
        self.preset_name_edit.blockSignals(False)
        self.preset_chance_spin.blockSignals(False)
        
        # Populate items table
        self.items_table.setRowCount(len(preset.items))
        for row, item in enumerate(preset.items):
            name_item = QTableWidgetItem(item.name)
            chance_item = QTableWidgetItem(f"{item.chance:.2f}")
            
            self.items_table.setItem(row, 0, name_item)
            self.items_table.setItem(row, 1, chance_item)
    
    def clear_detail_panel(self):
        """Clear preset details"""
        self.preset_name_edit.setText("")
        self.preset_name_edit.setEnabled(False)
        self.preset_type_label.setText("—")
        self.preset_chance_spin.setValue(0.0)
        self.preset_chance_spin.setEnabled(False)
        self.items_table.setRowCount(0)
    
    def update_stats(self):
        """Update statistics label"""
        if not self.presets_file:
            self.stats_label.setText("No presets loaded")
            return
        
        total = self.presets_file.get_total_preset_count()
        cargo = len(self.presets_file.cargo_presets)
        attach = len(self.presets_file.attachments_presets)
        
        self.stats_label.setText(f"{total} presets ({cargo} cargo, {attach} attachments)")
    
    def update_button_states(self):
        """Update button enabled/disabled states"""
        has_preset = self.selected_preset is not None
        has_file = self.presets_file is not None
        
        self.delete_preset_btn.setEnabled(has_preset)
        self.add_item_btn.setEnabled(has_preset)
        
        # Item buttons - check selection count
        selected_count = len(self.items_table.selectionModel().selectedRows())
        has_item_selected = has_preset and selected_count > 0
        
        # Update Edit button based on selection count
        if selected_count > 1:
            # Multiple items selected - change to batch chance
            self.edit_item_btn.setText(f"Change Chance ({selected_count})")
            self.edit_item_btn.setEnabled(True)
            # Disconnect old connection and connect to batch function
            try:
                self.edit_item_btn.clicked.disconnect()
            except:
                pass
            self.edit_item_btn.clicked.connect(self.batch_change_chance)
        else:
            # Single or no item selected - normal edit
            self.edit_item_btn.setText("Edit Item")
            self.edit_item_btn.setEnabled(has_item_selected)
            # Disconnect old connection and connect to edit function
            try:
                self.edit_item_btn.clicked.disconnect()
            except:
                pass
            self.edit_item_btn.clicked.connect(self.edit_item)
        
        # Delete button - update text based on selection
        if selected_count > 1:
            self.delete_item_btn.setText(f"Delete ({selected_count})")
        else:
            self.delete_item_btn.setText("Delete Item")
        self.delete_item_btn.setEnabled(has_item_selected)
        
        # Undo/Redo
        self.undo_btn.setEnabled(len(self.parent.undo_stack) > 0)
        self.redo_btn.setEnabled(len(self.parent.redo_stack) > 0)
    
    def save_state_for_undo(self):
        """Save current state to undo stack"""
        if self.presets_file:
            # Deep copy the presets file
            state = copy.deepcopy(self.presets_file)
            self.parent.undo_stack.append(('random_presets', state))
            
            # Limit stack size
            if len(self.parent.undo_stack) > self.parent.max_undo_stack:
                self.parent.undo_stack.pop(0)
            
            # Clear redo stack on new action
            self.parent.redo_stack.clear()
            
            # Mark as modified
            self.parent.has_random_preset_changes = True
            
            self.update_button_states()
    
    def show_new_preset_dialog(self):
        """Show dialog to create new preset"""
        if not self.presets_file:
            # Create new file if it doesn't exist
            self.presets_file = RandomPresetsFile(source_file="cfgrandompresets.xml")
            self.parent.random_presets_file = self.presets_file
        
        dialog = PresetDialog(self, None)
        if dialog.exec_():
            self.save_state_for_undo()
            
            preset = dialog.get_preset()
            self.presets_file.add_preset(preset)
            
            self.refresh_preset_list()
            self.update_stats()
            self.parent.update_status_bar()
    
    def edit_preset(self, item=None, column=None):
        """Edit selected preset - now just ensures it's selected since details are inline editable"""
        # When double-clicking tree item, just make sure it's selected
        # The inline editing in the detail panel handles actual editing
        if not self.selected_preset:
            return
        
        # Focus the name field for editing
        self.preset_name_edit.setFocus()
        self.preset_name_edit.selectAll()
    
    def delete_preset(self):
        """Delete selected preset"""
        if not self.selected_preset:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f"Are you sure you want to delete preset '{self.selected_preset.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_state_for_undo()
            
            self.presets_file.remove_preset(self.selected_preset)
            self.selected_preset = None
            
            self.refresh_preset_list()
            self.clear_detail_panel()
            self.update_stats()
            self.update_button_states()
            self.parent.update_status_bar()
    
    def add_item_to_preset(self):
        """Add item to selected preset"""
        if not self.selected_preset:
            return
        
        dialog = ItemDialog(self, None)
        if dialog.exec_():
            self.save_state_for_undo()
            
            item = dialog.get_item()
            preset_name = self.selected_preset.name  # Save for reselection
            self.selected_preset.add_item(item)
            
            self.refresh_preset_list()  # Update item count
            
            # Reselect the preset to maintain selection
            self.select_preset_by_name(preset_name)
            
            # Update button states after reselection
            self.update_button_states()
            
            self.parent.update_status_bar()
    
    def edit_item(self):
        """Edit selected item"""
        if not self.selected_preset:
            return
        
        row = self.items_table.currentRow()
        if row < 0 or row >= len(self.selected_preset.items):
            return
        
        item = self.selected_preset.items[row]
        dialog = ItemDialog(self, item)
        if dialog.exec_():
            self.save_state_for_undo()
            
            # Update item with new values
            updated = dialog.get_item()
            item.name = updated.name
            item.chance = updated.chance
            
            # Refresh the display
            self.display_preset_details(self.selected_preset)
            
            # Reselect the same row in items table
            self.items_table.selectRow(row)
            
            self.parent.update_status_bar()
    
    def delete_item(self):
        """Delete selected item(s)"""
        if not self.selected_preset:
            return
        
        selected_rows = sorted([idx.row() for idx in self.items_table.selectionModel().selectedRows()], reverse=True)
        if not selected_rows:
            return
        
        # Handle single vs multiple deletion
        if len(selected_rows) == 1:
            row = selected_rows[0]
            if row < 0 or row >= len(self.selected_preset.items):
                return
            
            item = self.selected_preset.items[row]
            reply = QMessageBox.question(
                self,
                "Delete Item",
                f"Are you sure you want to delete item '{item.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self,
                "Delete Items",
                f"Are you sure you want to delete {len(selected_rows)} item(s)?",
                QMessageBox.Yes | QMessageBox.No
            )
        
        if reply == QMessageBox.Yes:
            self.save_state_for_undo()
            
            preset_name = self.selected_preset.name
            
            # Delete items in reverse order to maintain indices
            for row in selected_rows:
                if row < len(self.selected_preset.items):
                    self.selected_preset.remove_item(row)
            
            self.refresh_preset_list()  # Update item count
            
            # Reselect the preset
            self.select_preset_by_name(preset_name)
            
            self.parent.update_status_bar()
    
    def batch_change_chance(self):
        """Change chance for multiple selected items"""
        if not self.selected_preset:
            return
        
        selected_rows = sorted([idx.row() for idx in self.items_table.selectionModel().selectedRows()])
        if not selected_rows:
            return
        
        # Show dialog to get new chance value
        from PyQt5.QtWidgets import QInputDialog
        new_chance, ok = QInputDialog.getDouble(
            self,
            "Batch Change Chance",
            f"Enter new chance value for {len(selected_rows)} item(s):",
            value=0.5,
            min=0.0,
            max=1.0,
            decimals=2
        )
        
        if ok:
            self.save_state_for_undo()
            
            # Update chance for all selected items
            for row in selected_rows:
                if row < len(self.selected_preset.items):
                    self.selected_preset.items[row].chance = new_chance
            
            # Refresh the display
            self.display_preset_details(self.selected_preset)
            
            # Reselect the same rows
            for row in selected_rows:
                self.items_table.selectRow(row)
            
            self.parent.update_status_bar()
    
    def save_changes(self):
        """Save changes via main window"""
        self.parent.save_changes()


class PresetDialog(QDialog):
    """Dialog for creating/editing presets"""
    
    def __init__(self, parent, preset: Optional[RandomPreset] = None):
        super().__init__(parent)
        self.preset = preset
        self.is_edit = preset is not None
        
        self.setWindowTitle("Edit Preset" if self.is_edit else "New Preset")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
        
        if self.is_edit:
            self.load_preset_data()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., foodCity, optics, etc.")
        form.addRow("Name:", self.name_input)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Cargo", "Attachments"])
        self.type_combo.setEnabled(not self.is_edit)  # Can't change type when editing
        form.addRow("Type:", self.type_combo)
        
        # Chance
        self.chance_spin = QDoubleSpinBox()
        self.chance_spin.setRange(0.0, 1.0)
        self.chance_spin.setSingleStep(0.01)
        self.chance_spin.setDecimals(2)
        self.chance_spin.setValue(0.5)
        form.addRow("Chance:", self.chance_spin)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_preset_data(self):
        """Load existing preset data"""
        self.name_input.setText(self.preset.name)
        self.type_combo.setCurrentText(self.preset.preset_type.value.capitalize())
        self.chance_spin.setValue(self.preset.chance)
    
    def accept(self):
        """Validate and accept"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Preset name cannot be empty.")
            return
        
        super().accept()
    
    def get_preset(self) -> RandomPreset:
        """Get preset from dialog inputs"""
        preset_type = PresetType.CARGO if self.type_combo.currentText() == "Cargo" else PresetType.ATTACHMENTS
        
        if self.is_edit:
            # Return a preset with updated values (caller will copy them)
            return RandomPreset(
                preset_type=self.preset.preset_type,  # Keep original type
                name=self.name_input.text().strip(),
                chance=self.chance_spin.value(),
                items=self.preset.items  # Keep original items
            )
        else:
            # Return new preset
            return RandomPreset(
                preset_type=preset_type,
                name=self.name_input.text().strip(),
                chance=self.chance_spin.value()
            )


class ItemDialog(QDialog):
    """Dialog for creating/editing items"""
    
    def __init__(self, parent, item: Optional[PresetItem] = None):
        super().__init__(parent)
        self.parent_tab = parent
        self.item = item
        self.is_edit = item is not None
        
        self.setWindowTitle("Edit Item" if self.is_edit else "New Item")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
        
        if self.is_edit:
            self.load_item_data()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        form = QFormLayout()
        
        # Name - ComboBox with autocomplete
        self.name_input = QComboBox()
        self.name_input.setEditable(True)
        self.name_input.setInsertPolicy(QComboBox.NoInsert)
        self.name_input.lineEdit().setPlaceholderText("e.g., Apple, M4_T3NRDSOptic, etc.")
        
        # Enable autocomplete
        self.name_input.setCompleter(None)  # Remove default completer
        from PyQt5.QtWidgets import QCompleter
        from PyQt5.QtCore import Qt
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.name_input.setCompleter(completer)
        
        # Populate with items from types files
        self.populate_item_names()
        
        form.addRow("Item Name:", self.name_input)
        
        # Chance
        self.chance_spin = QDoubleSpinBox()
        self.chance_spin.setRange(0.0, 1.0)
        self.chance_spin.setSingleStep(0.01)
        self.chance_spin.setDecimals(2)
        self.chance_spin.setValue(0.5)
        form.addRow("Chance:", self.chance_spin)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def populate_item_names(self):
        """Populate combobox with item names from types files"""
        # Get all item names from parent's types files
        if hasattr(self.parent_tab, 'parent') and hasattr(self.parent_tab.parent, 'types_files'):
            item_names = set()
            for types_file in self.parent_tab.parent.types_files:
                for item in types_file.items:
                    item_names.add(item.name)
            
            # Sort alphabetically and add to combobox
            sorted_names = sorted(item_names)
            self.name_input.addItems(sorted_names)
            
            # Update completer model
            if self.name_input.completer():
                from PyQt5.QtCore import QStringListModel
                model = QStringListModel(sorted_names)
                self.name_input.completer().setModel(model)
    
    def load_item_data(self):
        """Load existing item data"""
        self.name_input.setCurrentText(self.item.name)
        self.chance_spin.setValue(self.item.chance)
    
    def accept(self):
        """Validate and accept"""
        name = self.name_input.currentText().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Item name cannot be empty.")
            return
        
        super().accept()
    
    def get_item(self) -> PresetItem:
        """Get item from dialog inputs"""
        return PresetItem(
            name=self.name_input.currentText().strip(),
            chance=self.chance_spin.value()
        )
