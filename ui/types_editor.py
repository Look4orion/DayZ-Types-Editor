"""
Types Editor Tab
Main editing interface for types.xml files
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QTableWidget,
                             QTableWidgetItem, QScrollArea, QFrame, QGroupBox,
                             QFormLayout, QComboBox, QCheckBox, QSplitter,
                             QHeaderView, QAbstractItemView, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from models.type_item import TypeItem
from models.types_file import TypesFile
from core.limits_parser import LimitsParser
from typing import List, Optional
from ui.draggable_spinbox import EnhancedSpinBox

class TypesEditorTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.types_files: List[TypesFile] = []
        self.limits_parser: Optional[LimitsParser] = None
        self.filtered_items: List[TypeItem] = []
        self.selected_items: List[TypeItem] = []
        
        # Debounce timer for search
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
        
        # Splitter for filter sidebar and main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Filter sidebar
        self.filter_sidebar = self.create_filter_sidebar()
        splitter.addWidget(self.filter_sidebar)
        
        # Item table
        self.item_table = self.create_item_table()
        splitter.addWidget(self.item_table)
        
        # Detail panel
        self.detail_panel = self.create_detail_panel()
        splitter.addWidget(self.detail_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([250, 400, 550])
        
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
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator)
        
        # New Item button
        new_item_btn = QPushButton("New Item")
        new_item_btn.setStyleSheet("QPushButton { background-color: #0e639c; }")
        new_item_btn.clicked.connect(self.show_new_item_dialog)
        layout.addWidget(new_item_btn)
        
        # Separator
        separator_new = QFrame()
        separator_new.setFrameShape(QFrame.VLine)
        separator_new.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator_new)
        
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.parent.undo)
        self.undo_btn = undo_btn  # Store reference for enabling/disabling
        layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.parent.redo)
        self.redo_btn = redo_btn  # Store reference for enabling/disabling
        layout.addWidget(redo_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator2)
        
        batch_btn = QPushButton("Batch Operations")
        batch_btn.clicked.connect(self.show_batch_operations)
        layout.addWidget(batch_btn)
        
        layout.addStretch()
        
        # Active filters label
        self.active_filters_label = QLabel("0 Active Filters")
        self.active_filters_label.setStyleSheet(
            "QLabel { background-color: #0e639c; color: white; padding: 4px 8px; border-radius: 12px; }"
        )
        layout.addWidget(self.active_filters_label)
        
        toolbar.setLayout(layout)
        return toolbar
    
    def create_filter_sidebar(self):
        """Create collapsible filter sidebar"""
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar.setStyleSheet("QFrame { background-color: #252526; border-right: 1px solid #444; }")
        sidebar.setMinimumWidth(350)
        sidebar.setMaximumWidth(450)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Collapse button
        collapse_layout = QHBoxLayout()
        collapse_layout.addStretch()
        collapse_btn = QPushButton("Collapse ◀")
        collapse_btn.setStyleSheet("QPushButton { background-color: #555; font-size: 10px; padding: 4px 8px; }")
        collapse_btn.clicked.connect(self.toggle_sidebar)
        collapse_layout.addWidget(collapse_btn)
        layout.addLayout(collapse_layout)
        
        # Scroll area for filters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        filter_widget = QWidget()
        filter_layout = QVBoxLayout()
        
        # Search
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        search_group.setLayout(search_layout)
        filter_layout.addWidget(search_group)
        
        # Logic selector
        logic_group = QGroupBox("Filter Logic")
        logic_layout = QHBoxLayout()
        self.and_radio = QCheckBox("AND")
        self.and_radio.setChecked(True)
        self.and_radio.toggled.connect(self.apply_filters)
        logic_layout.addWidget(self.and_radio)
        self.or_radio = QCheckBox("OR")
        self.or_radio.toggled.connect(self.on_logic_changed)
        logic_layout.addWidget(self.or_radio)
        logic_group.setLayout(logic_layout)
        filter_layout.addWidget(logic_group)
        
        # Category filter
        category_group = QGroupBox("Category")
        category_layout = QVBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self.apply_filters)
        category_layout.addWidget(self.category_combo)
        category_group.setLayout(category_layout)
        filter_layout.addWidget(category_group)
        
        # Tag filter
        tag_group = QGroupBox("Tags")
        tag_layout = QVBoxLayout()
        self.tag_checkboxes = []
        self.tag_scroll = QScrollArea()
        self.tag_scroll.setFrameShape(QScrollArea.StyledPanel)
        self.tag_scroll.setMaximumHeight(150)
        self.tag_scroll.setWidgetResizable(True)
        self.tag_widget = QWidget()
        self.tag_widget_layout = QGridLayout()  # Changed to grid
        self.tag_widget_layout.setSpacing(2)
        self.tag_widget.setLayout(self.tag_widget_layout)
        self.tag_scroll.setWidget(self.tag_widget)
        tag_layout.addWidget(self.tag_scroll)
        tag_group.setLayout(tag_layout)
        filter_layout.addWidget(tag_group)
        
        # Usage filter
        usage_group = QGroupBox("Usage")
        usage_layout = QVBoxLayout()
        self.usage_checkboxes = []
        self.usage_scroll = QScrollArea()
        self.usage_scroll.setFrameShape(QScrollArea.StyledPanel)
        self.usage_scroll.setMaximumHeight(150)
        self.usage_scroll.setWidgetResizable(True)
        self.usage_widget = QWidget()
        self.usage_widget_layout = QGridLayout()  # Changed to grid
        self.usage_widget_layout.setSpacing(2)
        self.usage_widget.setLayout(self.usage_widget_layout)
        self.usage_scroll.setWidget(self.usage_widget)
        usage_layout.addWidget(self.usage_scroll)
        usage_group.setLayout(usage_layout)
        filter_layout.addWidget(usage_group)
        
        # Value filter
        value_group = QGroupBox("Value")
        value_layout = QVBoxLayout()
        self.value_checkboxes = []
        self.value_scroll = QScrollArea()
        self.value_scroll.setFrameShape(QScrollArea.StyledPanel)
        self.value_scroll.setMaximumHeight(150)
        self.value_scroll.setWidgetResizable(True)
        self.value_widget = QWidget()
        self.value_widget_layout = QGridLayout()  # Changed to grid
        self.value_widget_layout.setSpacing(2)
        self.value_widget.setLayout(self.value_widget_layout)
        self.value_scroll.setWidget(self.value_widget)
        value_layout.addWidget(self.value_scroll)
        value_group.setLayout(value_layout)
        filter_layout.addWidget(value_group)
        
        # Nominal range filter
        nominal_group = QGroupBox("Nominal Range")
        nominal_layout = QVBoxLayout()
        range_layout = QHBoxLayout()
        self.nominal_min_input = QSpinBox()
        self.nominal_min_input.setRange(-1, 999999)
        self.nominal_min_input.setValue(-1)
        self.nominal_min_input.setPrefix("Min: ")
        self.nominal_min_input.valueChanged.connect(self.apply_filters)
        range_layout.addWidget(self.nominal_min_input)
        
        self.nominal_max_input = QSpinBox()
        self.nominal_max_input.setRange(-1, 999999)
        self.nominal_max_input.setValue(-1)
        self.nominal_max_input.setPrefix("Max: ")
        self.nominal_max_input.valueChanged.connect(self.apply_filters)
        range_layout.addWidget(self.nominal_max_input)
        nominal_layout.addLayout(range_layout)
        nominal_group.setLayout(nominal_layout)
        filter_layout.addWidget(nominal_group)
        
        # Flags filter
        flags_group = QGroupBox("Flags")
        flags_layout = QGridLayout()
        flags_layout.setSpacing(4)
        
        self.filter_cargo_cb = QCheckBox("Cargo")
        self.filter_cargo_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_cargo_cb, 0, 0)
        
        self.filter_hoarder_cb = QCheckBox("Hoarder")
        self.filter_hoarder_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_hoarder_cb, 0, 1)
        
        self.filter_map_cb = QCheckBox("Map")
        self.filter_map_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_map_cb, 1, 0)
        
        self.filter_player_cb = QCheckBox("Player")
        self.filter_player_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_player_cb, 1, 1)
        
        self.filter_crafted_cb = QCheckBox("Crafted")
        self.filter_crafted_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_crafted_cb, 2, 0)
        
        self.filter_deloot_cb = QCheckBox("Deloot")
        self.filter_deloot_cb.stateChanged.connect(self.apply_filters)
        flags_layout.addWidget(self.filter_deloot_cb, 2, 1)
        
        flags_group.setLayout(flags_layout)
        filter_layout.addWidget(flags_group)
        
        # File/Mod path filter
        path_group = QGroupBox("File/Mod Path")
        path_layout = QVBoxLayout()
        self.path_combo = QComboBox()
        self.path_combo.addItem("All Files")
        self.path_combo.currentTextChanged.connect(self.apply_filters)
        path_layout.addWidget(self.path_combo)
        path_group.setLayout(path_layout)
        filter_layout.addWidget(path_group)
        
        # Clear filters button
        clear_btn = QPushButton("Clear All Filters")
        clear_btn.setStyleSheet("QPushButton { background-color: #555; }")
        clear_btn.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_btn)
        
        filter_layout.addStretch()
        filter_widget.setLayout(filter_layout)
        scroll.setWidget(filter_widget)
        
        layout.addWidget(scroll)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_item_table(self):
        """Create item table widget"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Name", "Path"])
        
        # Configure table
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        # Style for better readability
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252526;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #264f78;
            }
        """)
        
        # Header settings
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Connect selection changed
        table.itemSelectionChanged.connect(self.on_selection_changed)
        
        return table
    
    def create_detail_panel(self):
        """Create detail editing panel"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("QFrame { background-color: #1e1e1e; }")
        
        layout = QVBoxLayout()
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        
        # Title
        self.detail_title = QLabel("Select an item to edit")
        self.detail_title.setStyleSheet("QLabel { font-size: 16px; color: #4a9eff; margin-bottom: 10px; }")
        form_layout.addWidget(self.detail_title)
        
        # Form fields
        field_layout = QFormLayout()
        
        # Numeric fields - DRAGGABLE
        self.nominal_spin = EnhancedSpinBox()
        self.nominal_spin.setRange(0, 99999999)  # Up to 99 million
        self.nominal_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Nominal:", self.nominal_spin)
        
        self.lifetime_spin = EnhancedSpinBox()
        self.lifetime_spin.setRange(0, 99999999)  # Up to 99 million seconds (~3 years)
        self.lifetime_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Lifetime:", self.lifetime_spin)
        
        self.restock_spin = EnhancedSpinBox()
        self.restock_spin.setRange(0, 99999999)  # Up to 99 million seconds (~3 years)
        self.restock_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Restock:", self.restock_spin)
        
        self.min_spin = EnhancedSpinBox()
        self.min_spin.setRange(0, 99999999)  # Up to 99 million
        self.min_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Min:", self.min_spin)
        
        self.quantmin_spin = EnhancedSpinBox()
        self.quantmin_spin.setRange(-1, 100)  # -1 (disabled) or 1-100 (percentage)
        self.quantmin_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Quantmin:", self.quantmin_spin)
        
        self.quantmax_spin = EnhancedSpinBox()
        self.quantmax_spin.setRange(-1, 100)  # -1 (disabled) or 1-100 (percentage)
        self.quantmax_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Quantmax:", self.quantmax_spin)
        
        self.cost_spin = EnhancedSpinBox()
        self.cost_spin.setRange(0, 100)  # 0-100 only
        self.cost_spin.valueChanged.connect(self.on_field_changed)
        field_layout.addRow("Cost:", self.cost_spin)
        
        # Category
        self.category_detail_combo = QComboBox()
        self.category_detail_combo.currentTextChanged.connect(self.on_field_changed)
        field_layout.addRow("Category:", self.category_detail_combo)
        
        form_layout.addLayout(field_layout)
        
        # Flags section
        flags_group = QGroupBox("Flags")
        flags_layout = QGridLayout()
        flags_layout.setSpacing(4)
        
        self.count_in_cargo_cb = QCheckBox("Count in Cargo")
        self.count_in_cargo_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.count_in_cargo_cb, 0, 0)
        
        self.count_in_hoarder_cb = QCheckBox("Count in Hoarder")
        self.count_in_hoarder_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.count_in_hoarder_cb, 0, 1)
        
        self.count_in_map_cb = QCheckBox("Count in Map")
        self.count_in_map_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.count_in_map_cb, 1, 0)
        
        self.count_in_player_cb = QCheckBox("Count in Player")
        self.count_in_player_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.count_in_player_cb, 1, 1)
        
        self.crafted_cb = QCheckBox("Crafted")
        self.crafted_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.crafted_cb, 2, 0)
        
        self.deloot_cb = QCheckBox("Deloot")
        self.deloot_cb.stateChanged.connect(self.on_field_changed)
        flags_layout.addWidget(self.deloot_cb, 2, 1)
        
        flags_group.setLayout(flags_layout)
        form_layout.addWidget(flags_group)
        
        # Usage checkboxes - responsive grid
        usage_detail_group = QGroupBox("Usage (Multiple)")
        self.usage_detail_layout = QGridLayout()
        self.usage_detail_layout.setSpacing(4)
        self.usage_detail_checkboxes = []
        usage_detail_group.setLayout(self.usage_detail_layout)
        form_layout.addWidget(usage_detail_group)
        
        # Tag checkboxes - responsive grid
        tag_detail_group = QGroupBox("Tag (Multiple)")
        self.tag_detail_layout = QGridLayout()
        self.tag_detail_layout.setSpacing(4)
        self.tag_detail_checkboxes = []
        tag_detail_group.setLayout(self.tag_detail_layout)
        form_layout.addWidget(tag_detail_group)
        
        # Value checkboxes - responsive grid
        value_detail_group = QGroupBox("Value (Multiple)")
        self.value_detail_layout = QGridLayout()
        self.value_detail_layout.setSpacing(4)
        self.value_detail_checkboxes = []
        value_detail_group.setLayout(self.value_detail_layout)
        form_layout.addWidget(value_detail_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self.apply_item_changes)
        button_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("QPushButton { background-color: #555; }")
        reset_btn.clicked.connect(self.reset_detail_panel)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        form_layout.addLayout(button_layout)
        form_layout.addStretch()
        
        form_widget.setLayout(form_layout)
        scroll.setWidget(form_widget)
        
        layout.addWidget(scroll)
        panel.setLayout(layout)
        
        # Initially disable panel
        self.set_detail_panel_enabled(False)
        
        return panel
    
    def toggle_sidebar(self):
        """Toggle filter sidebar visibility"""
        if self.filter_sidebar.width() > 50:
            self.filter_sidebar.setMaximumWidth(30)
            self.filter_sidebar.setMinimumWidth(30)
        else:
            self.filter_sidebar.setMaximumWidth(450)
            self.filter_sidebar.setMinimumWidth(350)
    
    def on_search_changed(self):
        """Handle search text changed with debounce"""
        self.search_timer.stop()
        self.search_timer.start(250)  # 250ms debounce
    
    def on_logic_changed(self):
        """Handle logic radio button changes"""
        if self.sender() == self.or_radio and self.or_radio.isChecked():
            self.and_radio.setChecked(False)
        elif self.sender() == self.and_radio and self.and_radio.isChecked():
            self.or_radio.setChecked(False)
        self.apply_filters()
    
    def load_data(self, types_files: List[TypesFile], limits_parser: LimitsParser):
        """Load types files and limits data"""
        self.types_files = types_files
        self.limits_parser = limits_parser
        
        # Populate filter options
        self.populate_filter_options()
        
        # Apply initial filters (show all)
        self.apply_filters()
    
    def refresh_display(self):
        """Refresh the display after undo/redo"""
        # Re-apply current filters to refresh table
        self.apply_filters()
        
        # If an item is currently selected in detail panel, refresh its display
        if hasattr(self, 'current_item') and self.current_item:
            # Find the item again (it may have been modified)
            for types_file in self.types_files:
                found = types_file.get_item_by_name(self.current_item.name)
                if found:
                    self.load_item_details(found)
                    break
    
    def populate_filter_options(self):
        """Populate filter dropdowns and checkboxes"""
        if not self.limits_parser:
            print("WARNING: No limits_parser available!")
            return
        
        print(f"Populating filters from limits_parser with {len(self.limits_parser.get_categories())} categories")
        
        # Count items by tag, usage, value for display
        tag_counts = {}
        usage_counts = {}
        value_counts = {}
        
        for tf in self.types_files:
            for item in tf.items:
                for tag in item.tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                for usage in item.usage:
                    usage_counts[usage] = usage_counts.get(usage, 0) + 1
                for value in item.value:
                    value_counts[value] = value_counts.get(value, 0) + 1
        
        # Categories
        self.category_combo.clear()
        self.category_combo.addItem("All")
        for cat in self.limits_parser.get_categories():
            self.category_combo.addItem(cat)
        
        # Category for detail panel
        self.category_detail_combo.clear()
        self.category_detail_combo.addItem("(None)")  # Option for no category
        for cat in self.limits_parser.get_categories():
            self.category_detail_combo.addItem(cat)
        
        # Tags with counts - 2 columns
        self.clear_checkbox_layout(self.tag_widget_layout, self.tag_checkboxes)
        for idx, tag in enumerate(sorted(self.limits_parser.get_tags())):
            count = tag_counts.get(tag, 0)
            label = f"{tag} ({count})" if count > 0 else tag
            cb = QCheckBox(label)
            cb.setProperty('tag_name', tag)  # Store actual tag name
            cb.stateChanged.connect(self.apply_filters)
            self.tag_checkboxes.append(cb)
            row = idx // 2
            col = idx % 2
            self.tag_widget_layout.addWidget(cb, row, col)
        
        # Usage with counts - 2 columns
        self.clear_checkbox_layout(self.usage_widget_layout, self.usage_checkboxes)
        for idx, usage in enumerate(sorted(self.limits_parser.get_usages())):
            count = usage_counts.get(usage, 0)
            label = f"{usage} ({count})" if count > 0 else usage
            cb = QCheckBox(label)
            cb.setProperty('usage_name', usage)  # Store actual usage name
            cb.stateChanged.connect(self.apply_filters)
            self.usage_checkboxes.append(cb)
            row = idx // 2
            col = idx % 2
            self.usage_widget_layout.addWidget(cb, row, col)
        
        # Value with counts - 2 columns
        self.clear_checkbox_layout(self.value_widget_layout, self.value_checkboxes)
        for idx, value in enumerate(sorted(self.limits_parser.get_values())):
            count = value_counts.get(value, 0)
            label = f"{value} ({count})" if count > 0 else value
            cb = QCheckBox(label)
            cb.setProperty('value_name', value)  # Store actual value name
            cb.stateChanged.connect(self.apply_filters)
            self.value_checkboxes.append(cb)
            row = idx // 2
            col = idx % 2
            self.value_widget_layout.addWidget(cb, row, col)
        
        # File paths
        self.path_combo.clear()
        self.path_combo.addItem("All Files")
        unique_paths = set()
        for tf in self.types_files:
            unique_paths.add(tf.path)
        for path in sorted(unique_paths):
            self.path_combo.addItem(path)
        
        # Detail panel checkboxes
        self.populate_detail_checkboxes()
    
    def populate_detail_checkboxes(self):
        """Populate detail panel checkboxes with 2-column grid layout"""
        if not self.limits_parser:
            return
        
        # Use 2 columns for detail panel (could be made responsive later)
        num_cols = 2
        
        # Usage - 2-column grid
        self.clear_checkbox_layout(self.usage_detail_layout, self.usage_detail_checkboxes)
        for idx, usage in enumerate(sorted(self.limits_parser.get_usages())):
            cb = QCheckBox(usage)
            cb.stateChanged.connect(self.on_field_changed)
            self.usage_detail_checkboxes.append(cb)
            row = idx // num_cols
            col = idx % num_cols
            self.usage_detail_layout.addWidget(cb, row, col)
        
        # Tag - 2-column grid
        self.clear_checkbox_layout(self.tag_detail_layout, self.tag_detail_checkboxes)
        for idx, tag in enumerate(sorted(self.limits_parser.get_tags())):
            cb = QCheckBox(tag)
            cb.stateChanged.connect(self.on_field_changed)
            self.tag_detail_checkboxes.append(cb)
            row = idx // num_cols
            col = idx % num_cols
            self.tag_detail_layout.addWidget(cb, row, col)
        
        # Value - 2-column grid
        self.clear_checkbox_layout(self.value_detail_layout, self.value_detail_checkboxes)
        for idx, value in enumerate(sorted(self.limits_parser.get_values())):
            cb = QCheckBox(value)
            cb.stateChanged.connect(self.on_field_changed)
            self.value_detail_checkboxes.append(cb)
            row = idx // num_cols
            col = idx % num_cols
            self.value_detail_layout.addWidget(cb, row, col)
    
    def clear_checkbox_layout(self, layout, checkbox_list):
        """Clear a layout of checkboxes"""
        checkbox_list.clear()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def apply_filters(self):
        """Apply current filters to items"""
        self.filtered_items = []
        
        # Gather filter values
        search_text = self.search_input.text().strip()
        category = self.category_combo.currentText()
        if category == "All":
            category = ""
        
        selected_tags = [cb.property('tag_name') or cb.text().split(' (')[0] for cb in self.tag_checkboxes if cb.isChecked()]
        selected_usage = [cb.property('usage_name') or cb.text().split(' (')[0] for cb in self.usage_checkboxes if cb.isChecked()]
        selected_value = [cb.property('value_name') or cb.text().split(' (')[0] for cb in self.value_checkboxes if cb.isChecked()]
        
        nominal_min = self.nominal_min_input.value() if self.nominal_min_input.value() >= 0 else None
        nominal_max = self.nominal_max_input.value() if self.nominal_max_input.value() >= 0 else None
        
        source_file = self.path_combo.currentText()
        if source_file == "All Files":
            source_file = ""
        
        # Gather flag filters (only if checked)
        filter_flags = {}
        if self.filter_cargo_cb.isChecked():
            filter_flags['count_in_cargo'] = 1
        if self.filter_hoarder_cb.isChecked():
            filter_flags['count_in_hoarder'] = 1
        if self.filter_map_cb.isChecked():
            filter_flags['count_in_map'] = 1
        if self.filter_player_cb.isChecked():
            filter_flags['count_in_player'] = 1
        if self.filter_crafted_cb.isChecked():
            filter_flags['crafted'] = 1
        if self.filter_deloot_cb.isChecked():
            filter_flags['deloot'] = 1
        
        use_or_logic = self.or_radio.isChecked()
        
        # Filter items
        for types_file in self.types_files:
            for item in types_file.items:
                # Check flag filters first (simple equality check)
                flags_match = True
                for flag_name, flag_value in filter_flags.items():
                    if getattr(item, flag_name) != flag_value:
                        flags_match = False
                        break
                
                if not flags_match:
                    continue
                
                if item.matches_filter(
                    search_text=search_text,
                    category=category,
                    tags=selected_tags,
                    usage=selected_usage,
                    value=selected_value,
                    source_file=source_file,
                    nominal_min=nominal_min,
                    nominal_max=nominal_max,
                    use_or_logic=use_or_logic
                ):
                    self.filtered_items.append(item)
        
        # Update table
        self.populate_table()
        
        # Update active filters count
        filter_count = 0
        if search_text:
            filter_count += 1
        if category:
            filter_count += 1
        if selected_tags:
            filter_count += 1
        if selected_usage:
            filter_count += 1
        if selected_value:
            filter_count += 1
        if source_file:
            filter_count += 1
        if nominal_min is not None or nominal_max is not None:
            filter_count += 1
        if filter_flags:
            filter_count += len(filter_flags)
        
        self.active_filters_label.setText(f"{filter_count} Active Filter{'s' if filter_count != 1 else ''}")
    
    def populate_table(self):
        """Populate table with filtered items"""
        self.item_table.setRowCount(len(self.filtered_items))
        
        for row, item in enumerate(self.filtered_items):
            # Name
            name_item = QTableWidgetItem(item.name)
            if item.modified:
                name_item.setForeground(QColor("#51cf66"))
            self.item_table.setItem(row, 0, name_item)
            
            # Path
            path_item = QTableWidgetItem(item.source_file)
            if item.modified:
                path_item.setForeground(QColor("#51cf66"))
            self.item_table.setItem(row, 1, path_item)
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.path_combo.setCurrentIndex(0)
        self.nominal_min_input.setValue(-1)
        self.nominal_max_input.setValue(-1)
        
        for cb in self.tag_checkboxes:
            cb.setChecked(False)
        for cb in self.usage_checkboxes:
            cb.setChecked(False)
        for cb in self.value_checkboxes:
            cb.setChecked(False)
        
        # Clear flag filters
        self.filter_cargo_cb.setChecked(False)
        self.filter_hoarder_cb.setChecked(False)
        self.filter_map_cb.setChecked(False)
        self.filter_player_cb.setChecked(False)
        self.filter_crafted_cb.setChecked(False)
        self.filter_deloot_cb.setChecked(False)
        
        self.apply_filters()
    
    def on_selection_changed(self):
        """Handle item selection changed"""
        selected_rows = set(item.row() for item in self.item_table.selectedItems())
        self.selected_items = [self.filtered_items[row] for row in selected_rows if row < len(self.filtered_items)]
        
        if len(self.selected_items) == 1:
            # Single selection - show detail panel
            self.load_item_to_detail(self.selected_items[0])
            self.set_detail_panel_enabled(True)
        elif len(self.selected_items) > 1:
            # Multi-selection - disable detail panel (use batch ops instead)
            self.detail_title.setText(f"{len(self.selected_items)} items selected - Use Batch Operations")
            self.set_detail_panel_enabled(False)
        else:
            # No selection
            self.detail_title.setText("Select an item to edit")
            self.set_detail_panel_enabled(False)
    
    def load_item_to_detail(self, item: TypeItem):
        """Load an item into the detail panel"""
        self.detail_title.setText(f"Editing: {item.name}")
        
        # Block signals while loading
        self.nominal_spin.blockSignals(True)
        self.lifetime_spin.blockSignals(True)
        self.restock_spin.blockSignals(True)
        self.min_spin.blockSignals(True)
        self.quantmin_spin.blockSignals(True)
        self.quantmax_spin.blockSignals(True)
        self.cost_spin.blockSignals(True)
        self.category_detail_combo.blockSignals(True)
        
        # Load values
        self.nominal_spin.setValue(item.nominal)
        self.lifetime_spin.setValue(item.lifetime)
        self.restock_spin.setValue(item.restock)
        self.min_spin.setValue(item.min)
        self.quantmin_spin.setValue(item.quantmin)
        self.quantmax_spin.setValue(item.quantmax)
        self.cost_spin.setValue(item.cost)
        
        # Category
        if item.category:
            index = self.category_detail_combo.findText(item.category)
            if index >= 0:
                self.category_detail_combo.setCurrentIndex(index)
            else:
                # Category not found, default to None
                self.category_detail_combo.setCurrentIndex(0)
        else:
            # No category set
            self.category_detail_combo.setCurrentIndex(0)  # Select "(None)"
        
        # Flags
        self.count_in_cargo_cb.blockSignals(True)
        self.count_in_hoarder_cb.blockSignals(True)
        self.count_in_map_cb.blockSignals(True)
        self.count_in_player_cb.blockSignals(True)
        self.crafted_cb.blockSignals(True)
        self.deloot_cb.blockSignals(True)
        
        self.count_in_cargo_cb.setChecked(item.count_in_cargo == 1)
        self.count_in_hoarder_cb.setChecked(item.count_in_hoarder == 1)
        self.count_in_map_cb.setChecked(item.count_in_map == 1)
        self.count_in_player_cb.setChecked(item.count_in_player == 1)
        self.crafted_cb.setChecked(item.crafted == 1)
        self.deloot_cb.setChecked(item.deloot == 1)
        
        self.count_in_cargo_cb.blockSignals(False)
        self.count_in_hoarder_cb.blockSignals(False)
        self.count_in_map_cb.blockSignals(False)
        self.count_in_player_cb.blockSignals(False)
        self.crafted_cb.blockSignals(False)
        self.deloot_cb.blockSignals(False)
        
        # Usage checkboxes
        for cb in self.usage_detail_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(cb.text() in item.usage)
            cb.blockSignals(False)
        
        # Tag checkboxes
        for cb in self.tag_detail_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(cb.text() in item.tag)
            cb.blockSignals(False)
        
        # Value checkboxes
        for cb in self.value_detail_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(cb.text() in item.value)
            cb.blockSignals(False)
        
        # Unblock signals
        self.nominal_spin.blockSignals(False)
        self.lifetime_spin.blockSignals(False)
        self.restock_spin.blockSignals(False)
        self.min_spin.blockSignals(False)
        self.quantmin_spin.blockSignals(False)
        self.quantmax_spin.blockSignals(False)
        self.cost_spin.blockSignals(False)
        self.category_detail_combo.blockSignals(False)
    
    def set_detail_panel_enabled(self, enabled: bool):
        """Enable or disable detail panel"""
        self.nominal_spin.setEnabled(enabled)
        self.lifetime_spin.setEnabled(enabled)
        self.restock_spin.setEnabled(enabled)
        self.min_spin.setEnabled(enabled)
        self.quantmin_spin.setEnabled(enabled)
        self.quantmax_spin.setEnabled(enabled)
        self.cost_spin.setEnabled(enabled)
        self.category_detail_combo.setEnabled(enabled)
        
        # Flags
        self.count_in_cargo_cb.setEnabled(enabled)
        self.count_in_hoarder_cb.setEnabled(enabled)
        self.count_in_map_cb.setEnabled(enabled)
        self.count_in_player_cb.setEnabled(enabled)
        self.crafted_cb.setEnabled(enabled)
        self.deloot_cb.setEnabled(enabled)
        
        for cb in self.usage_detail_checkboxes:
            cb.setEnabled(enabled)
        for cb in self.tag_detail_checkboxes:
            cb.setEnabled(enabled)
        for cb in self.value_detail_checkboxes:
            cb.setEnabled(enabled)
    
    def on_field_changed(self):
        """Handle field value changed (for auto-apply if needed)"""
        # Currently fields don't auto-apply - user must click Apply
        pass
    
    def apply_item_changes(self):
        """Apply changes from detail panel to selected item"""
        if len(self.selected_items) != 1:
            return
        
        item = self.selected_items[0]
        
        # Push to undo stack before modification
        self.parent.push_undo_state([item])
        
        # Update values with validation
        nominal_value = self.nominal_spin.value()
        min_value = self.min_spin.value()
        
        # Ensure min doesn't exceed nominal
        if min_value > nominal_value:
            min_value = nominal_value
            self.min_spin.setValue(min_value)  # Update UI to show capped value
        
        item.nominal = nominal_value
        item.lifetime = self.lifetime_spin.value()
        item.restock = self.restock_spin.value()
        item.min = min_value
        item.quantmin = self.quantmin_spin.value()
        item.quantmax = self.quantmax_spin.value()
        item.cost = self.cost_spin.value()
        
        # Handle category - convert "(None)" to None
        category_text = self.category_detail_combo.currentText()
        item.category = None if category_text == "(None)" else category_text
        
        # Update usage
        item.usage = [cb.text() for cb in self.usage_detail_checkboxes if cb.isChecked()]
        
        # Update tags
        item.tag = [cb.text() for cb in self.tag_detail_checkboxes if cb.isChecked()]
        
        # Update values
        item.value = [cb.text() for cb in self.value_detail_checkboxes if cb.isChecked()]
        
        # Update flags (convert checkbox state to 0/1)
        item.count_in_cargo = 1 if self.count_in_cargo_cb.isChecked() else 0
        item.count_in_hoarder = 1 if self.count_in_hoarder_cb.isChecked() else 0
        item.count_in_map = 1 if self.count_in_map_cb.isChecked() else 0
        item.count_in_player = 1 if self.count_in_player_cb.isChecked() else 0
        item.crafted = 1 if self.crafted_cb.isChecked() else 0
        item.deloot = 1 if self.deloot_cb.isChecked() else 0
        
        # Mark as modified
        item.modified = True
        
        # Mark parent file as modified
        for tf in self.types_files:
            if item in tf.items:
                tf.modified = True
                break
        
        # Refresh table to show modified state
        self.populate_table()
        
        # Update parent status bar
        self.parent.update_status_bar()
    
    def reset_detail_panel(self):
        """Reset detail panel to current item values"""
        if len(self.selected_items) == 1:
            self.load_item_to_detail(self.selected_items[0])
    
    def save_changes(self):
        """Save changes - delegate to main window"""
        self.parent.save_changes()
    
    
    def show_new_item_dialog(self):
        """Show new item creation dialog"""
        if not self.types_files:
            QMessageBox.warning(
                self,
                "No Files Loaded",
                "Please load types.xml files before creating new items."
            )
            return
        
        from ui.new_item_dialog import NewItemDialog
        dialog = NewItemDialog(self, self.types_files, self.limits_parser)
        
        if dialog.exec_() == QDialog.Accepted and dialog.created_item and dialog.target_file:
            # Add item to target file
            dialog.target_file.items.append(dialog.created_item)
            dialog.target_file.modified = True
            
            # Push to undo stack
            self.parent.push_undo_state([dialog.created_item])
            
            # Refresh display
            self.apply_filters()
            
            # Select the new item
            self.jump_to_item(dialog.created_item.name)
            
            # Update status bar
            self.parent.update_status_bar()
            
            QMessageBox.information(
                self,
                "Item Created",
                f"Successfully created '{dialog.created_item.name}' in {dialog.target_file.path}"
            )
    
    def jump_to_item(self, item_name: str):
        """Jump to and select an item by name"""
        # Clear filters to show all items
        self.clear_filters()
        
        # Search for the item
        for row, item in enumerate(self.filtered_items):
            if item.name.lower() == item_name.lower():
                # Select the row
                self.item_table.selectRow(row)
                # Scroll to it
                self.item_table.scrollToItem(
                    self.item_table.item(row, 0),
                    QTableWidget.PositionAtCenter
                )
                # Load into detail panel
                self.selected_items = [item]
                self.load_item_to_detail(item)
                self.set_detail_panel_enabled(True)
                break
    
    def show_batch_operations(self):
        """Show batch operations dialog"""
        # Use filtered items if no specific selection, otherwise use selected items
        if len(self.selected_items) > 1:
            items = self.selected_items
            description = f"{len(items)} selected items"
        elif len(self.filtered_items) > 0:
            items = self.filtered_items
            # Build filter description
            filter_parts = []
            
            search = self.search_input.text().strip()
            if search:
                filter_parts.append(f"Search: '{search}'")
            
            category = self.category_combo.currentText()
            if category != "All":
                filter_parts.append(f"Category: {category}")
            
            selected_tags = [cb.property('tag_name') or cb.text().split(' (')[0] for cb in self.tag_checkboxes if cb.isChecked()]
            if selected_tags:
                filter_parts.append(f"Tags: {', '.join(selected_tags)}")
            
            selected_usage = [cb.property('usage_name') or cb.text().split(' (')[0] for cb in self.usage_checkboxes if cb.isChecked()]
            if selected_usage:
                filter_parts.append(f"Usage: {', '.join(selected_usage)}")
            
            selected_value = [cb.property('value_name') or cb.text().split(' (')[0] for cb in self.value_checkboxes if cb.isChecked()]
            if selected_value:
                filter_parts.append(f"Value: {', '.join(selected_value)}")
            
            path = self.path_combo.currentText()
            if path != "All Files":
                filter_parts.append(f"File: {path}")
            
            nominal_min = self.nominal_min_input.value()
            nominal_max = self.nominal_max_input.value()
            if nominal_min >= 0 or nominal_max >= 0:
                if nominal_min >= 0 and nominal_max >= 0:
                    filter_parts.append(f"Nominal: {nominal_min}-{nominal_max}")
                elif nominal_min >= 0:
                    filter_parts.append(f"Nominal: ≥{nominal_min}")
                else:
                    filter_parts.append(f"Nominal: ≤{nominal_max}")
            
            description = " • ".join(filter_parts) if filter_parts else "All items"
        else:
            QMessageBox.warning(
                self,
                "No Items",
                "No items available for batch operations. Apply filters or select items first."
            )
            return
        
        from ui.batch_ops import BatchOperationsDialog
        dialog = BatchOperationsDialog(self, items, description)
        dialog.exec_()
    
    def clear_data(self):
        """Clear all loaded data"""
        self.types_files = []
        self.filtered_items = []
        self.selected_items = []
        self.item_table.setRowCount(0)
        self.detail_title.setText("Select an item to edit")
        self.set_detail_panel_enabled(False)
