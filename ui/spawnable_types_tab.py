"""
Spawnable Types Editor Tab
Main editing interface for cfgspawnabletypes.xml
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QFrame, QGroupBox,
                             QSplitter, QHeaderView, QAbstractItemView, 
                             QMessageBox, QTreeWidget, QTreeWidgetItem,
                             QTreeWidgetItemIterator, QMenu,
                             QDialog, QFormLayout, QDoubleSpinBox, QComboBox,
                             QDialogButtonBox, QCheckBox, QSpinBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from models.spawnable_type import (SpawnableTypesFile, SpawnableType, 
                                   CargoBlock, AttachmentsBlock, SpawnableItem)
from typing import Optional, List
import copy

class SpawnableTypesTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.spawnabletypes_files: List[SpawnableTypesFile] = []
        self.selected_type: Optional[SpawnableType] = None
        self.selected_file: Optional[SpawnableTypesFile] = None
        self.filtered_types: List[SpawnableType] = []
        
        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.apply_filters)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter for filter sidebar, type list, and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Filter sidebar
        filter_sidebar = self.create_filter_sidebar()
        splitter.addWidget(filter_sidebar)
        
        # Middle: Type list
        type_list_panel = self.create_type_list_panel()
        splitter.addWidget(type_list_panel)
        
        # Right: Type details
        detail_panel = self.create_detail_panel()
        splitter.addWidget(detail_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([250, 350, 600])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
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
        
        # New Type button
        new_type_btn = QPushButton("New Type")
        new_type_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        new_type_btn.clicked.connect(self.add_new_type)
        layout.addWidget(new_type_btn)
        
        # Delete Type button
        self.delete_type_btn = QPushButton("Delete Type")
        self.delete_type_btn.clicked.connect(self.delete_type)
        self.delete_type_btn.setEnabled(False)
        layout.addWidget(self.delete_type_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator2)
        
        # Undo button
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        layout.addWidget(self.undo_btn)
        
        # Redo button
        self.redo_btn = QPushButton("Redo")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        layout.addWidget(self.redo_btn)
        
        layout.addStretch()
        
        # Stats label
        self.stats_label = QLabel("No data loaded")
        self.stats_label.setStyleSheet("color: #cccccc; padding: 0 8px;")
        layout.addWidget(self.stats_label)
        
        toolbar.setLayout(layout)
        return toolbar
    
    def create_filter_sidebar(self):
        """Create filter sidebar"""
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar.setStyleSheet("QFrame { background-color: #252526; border-right: 1px solid #444; }")
        sidebar.setMinimumWidth(250)
        sidebar.setMaximumWidth(350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search group
        search_group = QGroupBox("Search")
        search_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        search_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # File filter group
        file_group = QGroupBox("File")
        file_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        file_layout = QVBoxLayout()
        self.file_combo = QComboBox()
        self.file_combo.addItem("All Files")
        self.file_combo.currentTextChanged.connect(self.apply_filters)
        file_layout.addWidget(self.file_combo)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Properties filter group
        props_group = QGroupBox("Properties")
        props_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        props_layout = QVBoxLayout()
        
        self.hoarder_check = QCheckBox("Has Hoarder")
        self.hoarder_check.stateChanged.connect(self.apply_filters)
        props_layout.addWidget(self.hoarder_check)
        
        self.damage_check = QCheckBox("Has Damage")
        self.damage_check.stateChanged.connect(self.apply_filters)
        props_layout.addWidget(self.damage_check)
        
        self.cargo_check = QCheckBox("Has Cargo")
        self.cargo_check.stateChanged.connect(self.apply_filters)
        props_layout.addWidget(self.cargo_check)
        
        self.attachments_check = QCheckBox("Has Attachments")
        self.attachments_check.stateChanged.connect(self.apply_filters)
        props_layout.addWidget(self.attachments_check)
        
        props_group.setLayout(props_layout)
        layout.addWidget(props_group)
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_type_list_panel(self):
        """Create type list panel"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("QFrame { background-color: #1e1e1e; }")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Types tree
        self.types_tree = QTreeWidget()
        self.types_tree.setHeaderLabel("Spawnable Types")
        self.types_tree.setAlternatingRowColors(False)  # Disable to avoid white rows
        self.types_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                border: none;
                color: #cccccc;
            }
            QTreeWidget::item {
                padding: 4px;
                background-color: #1e1e1e;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.types_tree.itemSelectionChanged.connect(self.on_type_selected)
        self.types_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.types_tree.customContextMenuRequested.connect(self.show_type_context_menu)
        layout.addWidget(self.types_tree)
        
        panel.setLayout(layout)
        return panel
    
    def create_detail_panel(self):
        """Create right panel with type details"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                color: #cccccc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QDoubleSpinBox, QSpinBox {
                background-color: #252526;
                border: 1px solid #444;
                color: #cccccc;
                padding: 4px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #0e639c;
            }
            QCheckBox {
                color: #cccccc;
            }
            QLabel {
                color: #cccccc;
            }
        """)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #1e1e1e; border: none; }")
        
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Type information group
        info_group = QGroupBox("Type Information")
        info_layout = QFormLayout()
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_name_changed)
        info_layout.addRow("Name:", self.name_edit)
        
        # Hoarder checkbox
        self.hoarder_checkbox = QCheckBox()
        self.hoarder_checkbox.stateChanged.connect(self.on_hoarder_changed)
        info_layout.addRow("Hoarder:", self.hoarder_checkbox)
        
        # Damage min/max
        damage_layout = QHBoxLayout()
        self.damage_min_spin = QDoubleSpinBox()
        self.damage_min_spin.setRange(0.0, 1.0)
        self.damage_min_spin.setSingleStep(0.1)
        self.damage_min_spin.setDecimals(1)
        self.damage_min_spin.valueChanged.connect(self.on_damage_changed)
        self.damage_max_spin = QDoubleSpinBox()
        self.damage_max_spin.setRange(0.0, 1.0)
        self.damage_max_spin.setSingleStep(0.1)
        self.damage_max_spin.setDecimals(1)
        self.damage_max_spin.valueChanged.connect(self.on_damage_changed)
        damage_layout.addWidget(QLabel("Min:"))
        damage_layout.addWidget(self.damage_min_spin)
        damage_layout.addWidget(QLabel("Max:"))
        damage_layout.addWidget(self.damage_max_spin)
        damage_layout.addStretch()
        info_layout.addRow("Damage:", damage_layout)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Cargo blocks group
        cargo_group = self.create_cargo_blocks_group()
        layout.addWidget(cargo_group)
        
        # Attachments blocks group
        attachments_group = self.create_attachments_blocks_group()
        layout.addWidget(attachments_group)
        
        layout.addStretch()
        
        container.setLayout(layout)
        scroll.setWidget(container)
        
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
        panel.setLayout(panel_layout)
        
        return panel
    
    def create_cargo_blocks_group(self):
        """Create cargo blocks section"""
        group = QGroupBox("Cargo Blocks")
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        add_cargo_btn = QPushButton("Add Cargo Block")
        add_cargo_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        add_cargo_btn.clicked.connect(self.add_cargo_block)
        toolbar_layout.addWidget(add_cargo_btn)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Cargo blocks tree
        self.cargo_tree = QTreeWidget()
        self.cargo_tree.setHeaderLabels(["Type", "Details"])
        self.cargo_tree.setAlternatingRowColors(False)  # Disable to avoid white rows
        self.cargo_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                border: 1px solid #444;
                color: #cccccc;
            }
            QTreeWidget::item {
                padding: 4px;
                background-color: #252526;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.cargo_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cargo_tree.customContextMenuRequested.connect(self.show_cargo_context_menu)
        layout.addWidget(self.cargo_tree)
        
        group.setLayout(layout)
        return group
    
    def create_attachments_blocks_group(self):
        """Create attachments blocks section"""
        group = QGroupBox("Attachments Blocks")
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        add_attachments_btn = QPushButton("Add Attachments Block")
        add_attachments_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        add_attachments_btn.clicked.connect(self.add_attachments_block)
        toolbar_layout.addWidget(add_attachments_btn)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Attachments blocks tree
        self.attachments_tree = QTreeWidget()
        self.attachments_tree.setHeaderLabels(["Type", "Details"])
        self.attachments_tree.setAlternatingRowColors(False)  # Disable to avoid white rows
        self.attachments_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                border: 1px solid #444;
                color: #cccccc;
            }
            QTreeWidget::item {
                padding: 4px;
                background-color: #252526;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.attachments_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.attachments_tree.customContextMenuRequested.connect(self.show_attachments_context_menu)
        layout.addWidget(self.attachments_tree)
        
        group.setLayout(layout)
        return group
    
    # --- Data Loading and Display ---
    
    def load_data(self, spawnabletypes_files: List[SpawnableTypesFile]):
        """Load spawnable types data"""
        self.spawnabletypes_files = spawnabletypes_files
        self.populate_file_filter()
        self.refresh_types_list()
        self.update_stats()
    
    def populate_file_filter(self):
        """Populate file filter dropdown"""
        self.file_combo.blockSignals(True)
        self.file_combo.clear()
        self.file_combo.addItem("All Files")
        
        for f in self.spawnabletypes_files:
            self.file_combo.addItem(f.source_file)
        
        self.file_combo.blockSignals(False)
    
    def refresh_types_list(self):
        """Refresh the types tree with current filters"""
        self.types_tree.clear()
        
        if not self.spawnabletypes_files:
            return
        
        # Apply filters
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters and update type list"""
        self.types_tree.clear()
        self.filtered_types = []
        
        if not self.spawnabletypes_files:
            return
        
        search_text = self.search_input.text().lower()
        selected_file = self.file_combo.currentText()
        
        # Collect types matching filters
        for types_file in self.spawnabletypes_files:
            # File filter
            if selected_file != "All Files" and types_file.source_file != selected_file:
                continue
            
            for spawnable_type in types_file.types:
                # Search filter
                if search_text and search_text not in spawnable_type.name.lower():
                    continue
                
                # Property filters
                if self.hoarder_check.isChecked() and not spawnable_type.hoarder:
                    continue
                
                if self.damage_check.isChecked() and not spawnable_type.has_damage():
                    continue
                
                if self.cargo_check.isChecked() and len(spawnable_type.cargo_blocks) == 0:
                    continue
                
                if self.attachments_check.isChecked() and len(spawnable_type.attachments_blocks) == 0:
                    continue
                
                # Type matches all filters
                self.filtered_types.append((types_file, spawnable_type))
        
        # Group by file using file path as key
        files_dict = {}
        for types_file, spawnable_type in self.filtered_types:
            file_path = types_file.source_file
            if file_path not in files_dict:
                files_dict[file_path] = {'file': types_file, 'types': []}
            files_dict[file_path]['types'].append(spawnable_type)
        
        # Add to tree
        for file_path, data in files_dict.items():
            types_file = data['file']
            types_list = data['types']
            
            file_item = QTreeWidgetItem([f"{types_file.source_file} ({len(types_list)} types)"])
            file_item.setData(0, Qt.UserRole, types_file)
            self.types_tree.addTopLevelItem(file_item)
            
            # Add types (sorted)
            for spawnable_type in sorted(types_list, key=lambda t: t.name):
                type_item = QTreeWidgetItem([spawnable_type.name])
                type_item.setData(0, Qt.UserRole, spawnable_type)
                type_item.setData(0, Qt.UserRole + 1, types_file)
                file_item.addChild(type_item)
            
            file_item.setExpanded(True)
        
        # Update stats
        self.update_stats()
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.file_combo.setCurrentIndex(0)
        self.hoarder_check.setChecked(False)
        self.damage_check.setChecked(False)
        self.cargo_check.setChecked(False)
        self.attachments_check.setChecked(False)
        self.apply_filters()
    
    def on_search_changed(self):
        """Handle search text changed"""
        # Debounce search
        self.search_timer.stop()
        self.search_timer.start(300)
    
    def on_type_selected(self):
        """Handle type selection"""
        selected_items = self.types_tree.selectedItems()
        if not selected_items:
            self.selected_type = None
            self.selected_file = None
            self.clear_details()
            self.delete_type_btn.setEnabled(False)
            return
        
        item = selected_items[0]
        
        # Check if this is a type item
        if item.parent():
            self.selected_type = item.data(0, Qt.UserRole)
            self.selected_file = item.data(0, Qt.UserRole + 1)
            self.display_type_details()
            self.delete_type_btn.setEnabled(True)
        else:
            # File item selected
            self.selected_type = None
            self.selected_file = item.data(0, Qt.UserRole)
            self.clear_details()
            self.delete_type_btn.setEnabled(False)
    
    def display_type_details(self):
        """Display selected type details"""
        if not self.selected_type:
            return
        
        # Block signals
        self.name_edit.blockSignals(True)
        self.hoarder_checkbox.blockSignals(True)
        self.damage_min_spin.blockSignals(True)
        self.damage_max_spin.blockSignals(True)
        
        # Update fields
        self.name_edit.setText(self.selected_type.name)
        self.hoarder_checkbox.setChecked(self.selected_type.hoarder)
        
        if self.selected_type.damage_min is not None:
            self.damage_min_spin.setValue(self.selected_type.damage_min)
        else:
            self.damage_min_spin.setValue(0.0)
        
        if self.selected_type.damage_max is not None:
            self.damage_max_spin.setValue(self.selected_type.damage_max)
        else:
            self.damage_max_spin.setValue(0.0)
        
        # Unblock signals
        self.name_edit.blockSignals(False)
        self.hoarder_checkbox.blockSignals(False)
        self.damage_min_spin.blockSignals(False)
        self.damage_max_spin.blockSignals(False)
        
        # Display blocks
        self.display_cargo_blocks()
        self.display_attachments_blocks()
    
    def display_cargo_blocks(self):
        """Display cargo blocks for selected type"""
        self.cargo_tree.clear()
        
        if not self.selected_type:
            return
        
        for i, cargo_block in enumerate(self.selected_type.cargo_blocks):
            if cargo_block.is_preset_based():
                block_item = QTreeWidgetItem(["Preset", cargo_block.preset])
                block_item.setData(0, Qt.UserRole, cargo_block)
                block_item.setData(0, Qt.UserRole + 1, i)
                
                # Add tooltip showing preset contents
                tooltip = self.get_preset_tooltip(cargo_block.preset, "cargo")
                if tooltip:
                    block_item.setToolTip(0, tooltip)
                    block_item.setToolTip(1, tooltip)
                
                self.cargo_tree.addTopLevelItem(block_item)
            else:
                block_item = QTreeWidgetItem(["Chance", f"{cargo_block.chance} ({len(cargo_block.items)} items)"])
                block_item.setData(0, Qt.UserRole, cargo_block)
                block_item.setData(0, Qt.UserRole + 1, i)
                self.cargo_tree.addTopLevelItem(block_item)
                
                # Add items
                for item in cargo_block.items:
                    chance_str = f"{item.chance}" if item.chance is not None else "implicit 1.0"
                    item_node = QTreeWidgetItem([item.name, f"chance: {chance_str}"])
                    item_node.setData(0, Qt.UserRole, item)
                    block_item.addChild(item_node)
                
                block_item.setExpanded(True)
        
        self.cargo_tree.expandAll()
    
    def display_attachments_blocks(self):
        """Display attachments blocks for selected type"""
        self.attachments_tree.clear()
        
        if not self.selected_type:
            return
        
        for i, attachments_block in enumerate(self.selected_type.attachments_blocks):
            if attachments_block.is_preset_based():
                block_item = QTreeWidgetItem(["Preset", attachments_block.preset])
                block_item.setData(0, Qt.UserRole, attachments_block)
                block_item.setData(0, Qt.UserRole + 1, i)
                
                # Add tooltip showing preset contents
                tooltip = self.get_preset_tooltip(attachments_block.preset, "attachments")
                if tooltip:
                    block_item.setToolTip(0, tooltip)
                    block_item.setToolTip(1, tooltip)
                
                self.attachments_tree.addTopLevelItem(block_item)
            else:
                block_item = QTreeWidgetItem(["Chance", f"{attachments_block.chance} ({len(attachments_block.items)} items)"])
                block_item.setData(0, Qt.UserRole, attachments_block)
                block_item.setData(0, Qt.UserRole + 1, i)
                self.attachments_tree.addTopLevelItem(block_item)
                
                # Add items
                for item in attachments_block.items:
                    chance_str = f"{item.chance}" if item.chance is not None else "implicit 1.0"
                    item_node = QTreeWidgetItem([item.name, f"chance: {chance_str}"])
                    item_node.setData(0, Qt.UserRole, item)
                    block_item.addChild(item_node)
                
                block_item.setExpanded(True)
        
        self.attachments_tree.expandAll()
    
    def clear_details(self):
        """Clear detail panel"""
        self.name_edit.clear()
        self.hoarder_checkbox.setChecked(False)
        self.damage_min_spin.setValue(0.0)
        self.damage_max_spin.setValue(0.0)
        self.cargo_tree.clear()
        self.attachments_tree.clear()
    
    def update_stats(self):
        """Update statistics label"""
        if not self.spawnabletypes_files:
            self.stats_label.setText("No data loaded")
            return
        
        total_files = len(self.spawnabletypes_files)
        total_types = sum(len(f.types) for f in self.spawnabletypes_files)
        filtered_count = len(self.filtered_types)
        
        if filtered_count < total_types:
            self.stats_label.setText(f"{total_files} file(s), {filtered_count}/{total_types} type(s)")
        else:
            self.stats_label.setText(f"{total_files} file(s), {total_types} type(s)")
    
    def get_preset_tooltip(self, preset_name: str, preset_kind: str) -> str:
        """Generate tooltip showing preset contents"""
        if not self.parent.random_presets_file:
            return ""
        
        from models.random_preset import PresetType
        preset_type = PresetType.CARGO if preset_kind == "cargo" else PresetType.ATTACHMENTS
        
        preset = self.parent.random_presets_file.get_preset_by_name(preset_name, preset_type)
        if not preset:
            return f"Preset '{preset_name}' not found"
        
        # Build tooltip
        lines = [f"Preset: {preset.name}"]
        lines.append(f"Chance: {preset.chance}")
        lines.append(f"Items ({len(preset.items)}):")
        
        for item in preset.items:
            lines.append(f"  • {item.name} (chance: {item.chance})")
        
        return "\n".join(lines)
    
    # --- Change Handlers ---
    
    def on_name_changed(self):
        """Handle name field changed"""
        if not self.selected_type:
            return
        
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.selected_type.name:
            self.save_undo_state()
            self.selected_type.name = new_name
            self.mark_modified()
            self.refresh_types_list()
    
    def on_hoarder_changed(self):
        """Handle hoarder checkbox changed"""
        if not self.selected_type:
            return
        
        new_value = self.hoarder_checkbox.isChecked()
        if new_value != self.selected_type.hoarder:
            self.save_undo_state()
            self.selected_type.hoarder = new_value
            self.mark_modified()
    
    def on_damage_changed(self):
        """Handle damage values changed"""
        if not self.selected_type:
            return
        
        min_val = self.damage_min_spin.value()
        max_val = self.damage_max_spin.value()
        
        # Only set if non-zero
        new_min = min_val if min_val > 0 else None
        new_max = max_val if max_val > 0 else None
        
        if new_min != self.selected_type.damage_min or new_max != self.selected_type.damage_max:
            self.save_undo_state()
            self.selected_type.damage_min = new_min
            self.selected_type.damage_max = new_max
            self.mark_modified()
    
    # --- Type Operations ---
    
    def add_new_type(self):
        """Add a new type"""
        if not self.spawnabletypes_files:
            QMessageBox.warning(self, "No Files", "No spawnable types files loaded.")
            return
        
        from ui.dialogs.new_spawnable_type_dialog import NewSpawnableTypeDialog
        dialog = NewSpawnableTypeDialog(self, self.spawnabletypes_files)
        
        if dialog.exec_():
            type_name = dialog.get_type_name()
            target_file = dialog.get_selected_file()
            
            self.save_undo_state()
            new_type = SpawnableType(name=type_name)
            target_file.add_type(new_type)
            
            self.mark_modified()
            self.refresh_types_list()
            self.update_stats()
    
    def delete_type(self):
        """Delete selected type"""
        if not self.selected_type or not self.selected_file:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Type",
            f"Are you sure you want to delete type '{self.selected_type.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_undo_state()
            self.selected_file.remove_type(self.selected_type)
            self.selected_type = None
            
            self.mark_modified()
            self.refresh_types_list()
            self.clear_details()
            self.update_stats()
    
    # --- Cargo Block Operations ---
    
    def add_cargo_block(self):
        """Add a cargo block to selected type"""
        if not self.selected_type:
            QMessageBox.warning(self, "No Type Selected", "Please select a type first.")
            return
        
        from ui.dialogs.add_block_dialog import AddBlockDialog
        dialog = AddBlockDialog(self, "cargo", self.parent.random_presets_file)
        
        if dialog.exec_():
            block_type = dialog.get_block_type()
            
            if block_type == "preset":
                # Preset-based - create immediately
                self.save_undo_state()
                preset_name = dialog.get_preset_name()
                cargo_block = CargoBlock(preset=preset_name)
                self.selected_type.cargo_blocks.append(cargo_block)
                self.mark_modified()
                self.display_cargo_blocks()
            else:
                # Chance-based - need at least one item
                chance = dialog.get_chance()
                
                # Prompt for first item
                from ui.dialogs.add_item_dialog import AddItemDialog
                item_dialog = AddItemDialog(self, self.parent.types_files, False)
                
                if item_dialog.exec_():
                    # User added item - create block
                    self.save_undo_state()
                    
                    item_name = item_dialog.get_item_name()
                    item_chance = item_dialog.get_item_chance()
                    first_item = SpawnableItem(name=item_name, chance=item_chance)
                    
                    cargo_block = CargoBlock(chance=chance, items=[first_item])
                    self.selected_type.cargo_blocks.append(cargo_block)
                    self.mark_modified()
                    self.display_cargo_blocks()
                else:
                    # User cancelled item dialog - don't create block
                    QMessageBox.information(
                        self, 
                        "Block Not Created", 
                        "Chance-based blocks require at least one item. Block creation cancelled."
                    )
    
    def show_cargo_context_menu(self, position):
        """Show context menu for cargo blocks"""
        item = self.cargo_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        if item.parent() is None:
            # Block item
            edit_action = menu.addAction("Edit Block")
            delete_action = menu.addAction("Delete Block")
            
            # Add items option if chance-based
            cargo_block = item.data(0, Qt.UserRole)
            if cargo_block.is_chance_based():
                menu.addSeparator()
                add_item_action = menu.addAction("Add Item to Block")
            
            action = menu.exec_(self.cargo_tree.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_cargo_block(item)
            elif action == delete_action:
                self.delete_cargo_block(item)
            elif cargo_block.is_chance_based() and action == add_item_action:
                self.add_item_to_cargo_block(item)
        else:
            # Item within block
            edit_action = menu.addAction("Edit Item")
            delete_action = menu.addAction("Delete Item")
            menu.addSeparator()
            add_action = menu.addAction("Add Item to Block")
            menu.addSeparator()
            move_up_action = menu.addAction("Move Up")
            move_down_action = menu.addAction("Move Down")
            
            action = menu.exec_(self.cargo_tree.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_cargo_item(item)
            elif action == delete_action:
                self.delete_cargo_item(item)
            elif action == add_action:
                self.add_item_to_cargo_block(item.parent())
            elif action == move_up_action:
                self.move_cargo_item_up(item)
            elif action == move_down_action:
                self.move_cargo_item_down(item)
    
    def edit_cargo_block(self, block_item):
        """Edit a cargo block"""
        cargo_block = block_item.data(0, Qt.UserRole)
        block_index = block_item.data(0, Qt.UserRole + 1)
        
        from ui.dialogs.edit_block_dialog import EditBlockDialog
        dialog = EditBlockDialog(self, cargo_block, "cargo", self.parent.random_presets_file)
        
        if dialog.exec_():
            block_type = dialog.get_block_type()
            
            self.save_undo_state()
            
            if block_type == "preset":
                preset_name = dialog.get_preset_name()
                new_block = CargoBlock(preset=preset_name)
            else:
                chance = dialog.get_chance()
                # Preserve items if staying chance-based
                if cargo_block.is_chance_based():
                    new_block = CargoBlock(chance=chance, items=cargo_block.items[:])
                else:
                    new_block = CargoBlock(chance=chance, items=[])
            
            # Replace block
            self.selected_type.cargo_blocks[block_index] = new_block
            self.mark_modified()
            self.display_cargo_blocks()
    
    def delete_cargo_block(self, block_item):
        """Delete a cargo block"""
        block_index = block_item.data(0, Qt.UserRole + 1)
        
        reply = QMessageBox.question(
            self,
            "Delete Block",
            "Are you sure you want to delete this cargo block?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_undo_state()
            del self.selected_type.cargo_blocks[block_index]
            self.mark_modified()
            self.display_cargo_blocks()
    
    def add_item_to_cargo_block(self, block_item):
        """Add an item to a cargo block"""
        cargo_block = block_item.data(0, Qt.UserRole)
        
        if cargo_block.is_preset_based():
            QMessageBox.warning(self, "Preset Block", "Cannot add items to preset-based blocks.")
            return
        
        from ui.dialogs.add_item_dialog import AddItemDialog
        dialog = AddItemDialog(self, self.parent.types_files, len(cargo_block.items) > 0)
        
        if dialog.exec_():
            item_name = dialog.get_item_name()
            item_chance = dialog.get_item_chance()
            
            self.save_undo_state()
            new_item = SpawnableItem(name=item_name, chance=item_chance)
            cargo_block.items.append(new_item)
            self.mark_modified()
            self.display_cargo_blocks()
    
    def edit_cargo_item(self, item_node):
        """Edit an item in a cargo block"""
        block_item = item_node.parent()
        cargo_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        # Find item index
        item_index = cargo_block.items.index(item)
        
        from ui.dialogs.edit_item_dialog import EditItemDialog
        dialog = EditItemDialog(self, item, self.parent.types_files, len(cargo_block.items) > 1)
        
        if dialog.exec_():
            self.save_undo_state()
            item.name = dialog.get_item_name()
            item.chance = dialog.get_item_chance()
            self.mark_modified()
            self.display_cargo_blocks()
    
    def move_cargo_item_up(self, item_node):
        """Move item up in cargo block"""
        block_item = item_node.parent()
        cargo_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        item_index = cargo_block.items.index(item)
        if item_index > 0:
            self.save_undo_state()
            cargo_block.items[item_index], cargo_block.items[item_index - 1] = \
                cargo_block.items[item_index - 1], cargo_block.items[item_index]
            self.mark_modified()
            self.display_cargo_blocks()
    
    def move_cargo_item_down(self, item_node):
        """Move item down in cargo block"""
        block_item = item_node.parent()
        cargo_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        item_index = cargo_block.items.index(item)
        if item_index < len(cargo_block.items) - 1:
            self.save_undo_state()
            cargo_block.items[item_index], cargo_block.items[item_index + 1] = \
                cargo_block.items[item_index + 1], cargo_block.items[item_index]
            self.mark_modified()
            self.display_cargo_blocks()
    
    def delete_cargo_item(self, item_node):
        """Delete an item from a cargo block"""
        block_item = item_node.parent()
        cargo_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        if item in cargo_block.items:
            self.save_undo_state()
            cargo_block.items.remove(item)
            self.mark_modified()
            self.display_cargo_blocks()
    
    # --- Attachments Block Operations ---
    
    def add_attachments_block(self):
        """Add an attachments block to selected type"""
        if not self.selected_type:
            QMessageBox.warning(self, "No Type Selected", "Please select a type first.")
            return
        
        from ui.dialogs.add_block_dialog import AddBlockDialog
        dialog = AddBlockDialog(self, "attachments", self.parent.random_presets_file)
        
        if dialog.exec_():
            block_type = dialog.get_block_type()
            
            if block_type == "preset":
                # Preset-based - create immediately
                self.save_undo_state()
                preset_name = dialog.get_preset_name()
                attachments_block = AttachmentsBlock(preset=preset_name)
                self.selected_type.attachments_blocks.append(attachments_block)
                self.mark_modified()
                self.display_attachments_blocks()
            else:
                # Chance-based - need at least one item
                chance = dialog.get_chance()
                
                # Prompt for first item
                from ui.dialogs.add_item_dialog import AddItemDialog
                item_dialog = AddItemDialog(self, self.parent.types_files, False)
                
                if item_dialog.exec_():
                    # User added item - create block
                    self.save_undo_state()
                    
                    item_name = item_dialog.get_item_name()
                    item_chance = item_dialog.get_item_chance()
                    first_item = SpawnableItem(name=item_name, chance=item_chance)
                    
                    attachments_block = AttachmentsBlock(chance=chance, items=[first_item])
                    self.selected_type.attachments_blocks.append(attachments_block)
                    self.mark_modified()
                    self.display_attachments_blocks()
                else:
                    # User cancelled item dialog - don't create block
                    QMessageBox.information(
                        self, 
                        "Block Not Created", 
                        "Chance-based blocks require at least one item. Block creation cancelled."
                    )
    
    def show_attachments_context_menu(self, position):
        """Show context menu for attachments blocks"""
        item = self.attachments_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        if item.parent() is None:
            # Block item
            edit_action = menu.addAction("Edit Block")
            delete_action = menu.addAction("Delete Block")
            
            # Add items option if chance-based
            attachments_block = item.data(0, Qt.UserRole)
            if attachments_block.is_chance_based():
                menu.addSeparator()
                add_item_action = menu.addAction("Add Item to Block")
            
            action = menu.exec_(self.attachments_tree.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_attachments_block(item)
            elif action == delete_action:
                self.delete_attachments_block(item)
            elif attachments_block.is_chance_based() and action == add_item_action:
                self.add_item_to_attachments_block(item)
        else:
            # Item within block
            edit_action = menu.addAction("Edit Item")
            delete_action = menu.addAction("Delete Item")
            menu.addSeparator()
            add_action = menu.addAction("Add Item to Block")
            menu.addSeparator()
            move_up_action = menu.addAction("Move Up")
            move_down_action = menu.addAction("Move Down")
            
            action = menu.exec_(self.attachments_tree.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_attachments_item(item)
            elif action == delete_action:
                self.delete_attachments_item(item)
            elif action == add_action:
                self.add_item_to_attachments_block(item.parent())
            elif action == move_up_action:
                self.move_attachments_item_up(item)
            elif action == move_down_action:
                self.move_attachments_item_down(item)
    
    def edit_attachments_block(self, block_item):
        """Edit an attachments block"""
        attachments_block = block_item.data(0, Qt.UserRole)
        block_index = block_item.data(0, Qt.UserRole + 1)
        
        from ui.dialogs.edit_block_dialog import EditBlockDialog
        dialog = EditBlockDialog(self, attachments_block, "attachments", self.parent.random_presets_file)
        
        if dialog.exec_():
            block_type = dialog.get_block_type()
            
            self.save_undo_state()
            
            if block_type == "preset":
                preset_name = dialog.get_preset_name()
                new_block = AttachmentsBlock(preset=preset_name)
            else:
                chance = dialog.get_chance()
                # Preserve items if staying chance-based
                if attachments_block.is_chance_based():
                    new_block = AttachmentsBlock(chance=chance, items=attachments_block.items[:])
                else:
                    new_block = AttachmentsBlock(chance=chance, items=[])
            
            # Replace block
            self.selected_type.attachments_blocks[block_index] = new_block
            self.mark_modified()
            self.display_attachments_blocks()
    
    def delete_attachments_block(self, block_item):
        """Delete an attachments block"""
        block_index = block_item.data(0, Qt.UserRole + 1)
        
        reply = QMessageBox.question(
            self,
            "Delete Block",
            "Are you sure you want to delete this attachments block?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.save_undo_state()
            del self.selected_type.attachments_blocks[block_index]
            self.mark_modified()
            self.display_attachments_blocks()
    
    def add_item_to_attachments_block(self, block_item):
        """Add an item to an attachments block"""
        attachments_block = block_item.data(0, Qt.UserRole)
        
        if attachments_block.is_preset_based():
            QMessageBox.warning(self, "Preset Block", "Cannot add items to preset-based blocks.")
            return
        
        from ui.dialogs.add_item_dialog import AddItemDialog
        dialog = AddItemDialog(self, self.parent.types_files, len(attachments_block.items) > 0)
        
        if dialog.exec_():
            item_name = dialog.get_item_name()
            item_chance = dialog.get_item_chance()
            
            self.save_undo_state()
            new_item = SpawnableItem(name=item_name, chance=item_chance)
            attachments_block.items.append(new_item)
            self.mark_modified()
            self.display_attachments_blocks()
    
    def edit_attachments_item(self, item_node):
        """Edit an item in an attachments block"""
        block_item = item_node.parent()
        attachments_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        # Find item index
        item_index = attachments_block.items.index(item)
        
        from ui.dialogs.edit_item_dialog import EditItemDialog
        dialog = EditItemDialog(self, item, self.parent.types_files, len(attachments_block.items) > 1)
        
        if dialog.exec_():
            self.save_undo_state()
            item.name = dialog.get_item_name()
            item.chance = dialog.get_item_chance()
            self.mark_modified()
            self.display_attachments_blocks()
    
    def move_attachments_item_up(self, item_node):
        """Move item up in attachments block"""
        block_item = item_node.parent()
        attachments_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        item_index = attachments_block.items.index(item)
        if item_index > 0:
            self.save_undo_state()
            attachments_block.items[item_index], attachments_block.items[item_index - 1] = \
                attachments_block.items[item_index - 1], attachments_block.items[item_index]
            self.mark_modified()
            self.display_attachments_blocks()
    
    def move_attachments_item_down(self, item_node):
        """Move item down in attachments block"""
        block_item = item_node.parent()
        attachments_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        item_index = attachments_block.items.index(item)
        if item_index < len(attachments_block.items) - 1:
            self.save_undo_state()
            attachments_block.items[item_index], attachments_block.items[item_index + 1] = \
                attachments_block.items[item_index + 1], attachments_block.items[item_index]
            self.mark_modified()
            self.display_attachments_blocks()
    
    def delete_attachments_item(self, item_node):
        """Delete an item from an attachments block"""
        block_item = item_node.parent()
        attachments_block = block_item.data(0, Qt.UserRole)
        item = item_node.data(0, Qt.UserRole)
        
        if item in attachments_block.items:
            self.save_undo_state()
            attachments_block.items.remove(item)
            self.mark_modified()
            self.display_attachments_blocks()
    
    # --- Context Menu for Types ---
    
    def show_type_context_menu(self, position):
        """Show context menu for types tree"""
        item = self.types_tree.itemAt(position)
        if not item or not item.parent():
            return
        
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Type")
        
        action = menu.exec_(self.types_tree.viewport().mapToGlobal(position))
        
        if action == delete_action:
            self.delete_type()
    
    # --- Save/Undo/Redo ---
    
    def save_changes(self):
        """Save changes via main window"""
        self.parent.save_changes()
    
    def mark_modified(self):
        """Mark spawnable types as modified"""
        self.parent.has_spawnabletypes_changes = True
        self.parent.update_status_bar()
        self.update_button_states()
    
    def save_undo_state(self):
        """Save current state to undo stack"""
        state = []
        for f in self.spawnabletypes_files:
            state.append(copy.deepcopy(f))
        
        self.parent.undo_stack.append(('spawnable_types', state))
        
        if len(self.parent.undo_stack) > self.parent.max_undo_stack:
            self.parent.undo_stack.pop(0)
        
        self.parent.redo_stack.clear()
        self.update_button_states()
    
    def undo(self):
        """Undo last change"""
        if not self.parent.undo_stack:
            return
        
        if self.parent.undo_stack[-1][0] != 'spawnable_types':
            return
        
        current_state = []
        for f in self.spawnabletypes_files:
            current_state.append(copy.deepcopy(f))
        self.parent.redo_stack.append(('spawnable_types', current_state))
        
        _, previous_state = self.parent.undo_stack.pop()
        self.spawnabletypes_files = previous_state
        self.parent.spawnabletypes_files = self.spawnabletypes_files
        
        self.refresh_types_list()
        self.clear_details()
        self.update_stats()
        self.update_button_states()
    
    def redo(self):
        """Redo last undone change"""
        if not self.parent.redo_stack:
            return
        
        if self.parent.redo_stack[-1][0] != 'spawnable_types':
            return
        
        current_state = []
        for f in self.spawnabletypes_files:
            current_state.append(copy.deepcopy(f))
        self.parent.undo_stack.append(('spawnable_types', current_state))
        
        _, redo_state = self.parent.redo_stack.pop()
        self.spawnabletypes_files = redo_state
        self.parent.spawnabletypes_files = self.spawnabletypes_files
        
        self.refresh_types_list()
        self.clear_details()
        self.update_stats()
        self.update_button_states()
    
    def update_button_states(self):
        """Update undo/redo button states"""
        has_undo = bool(self.parent.undo_stack and 
                       self.parent.undo_stack[-1][0] == 'spawnable_types')
        has_redo = bool(self.parent.redo_stack and 
                       self.parent.redo_stack[-1][0] == 'spawnable_types')
        
        self.undo_btn.setEnabled(has_undo)
        self.redo_btn.setEnabled(has_redo)
