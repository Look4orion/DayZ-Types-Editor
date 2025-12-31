"""
Main Application Window
"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMessageBox,
                             QWidget, QVBoxLayout, QAction, QMenuBar, QMenu,
                             QProgressDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent
from config.app_config import AppConfig
from config.sftp_manager import SFTPManager
from config.local_file_manager import LocalFileManager
from core.backup_manager import BackupManager
from core.limits_parser import LimitsParser
from core.economy_parser import EconomyParser
from core.xml_parser import TypesParser
from models.types_file import TypesFile
from models.type_item import TypeItem
from ui.types_editor import TypesEditorTab
from ui.settings_tab import SettingsTab
from ui.sftp_dialog import SFTPDialog
<<<<<<< HEAD
from version import __version__
=======
>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
from ui.startup_dialog import StartupDialog
from ui.save_dialog import SaveDialog
from typing import List, Dict
import traceback

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Core components
        self.config = AppConfig()
        self.sftp = SFTPManager()  # Keep for backward compatibility
        self.file_manager = None  # Will be set to SFTP or Local manager
        self.backup_manager = BackupManager(self.config.get_backup_location())
        self.limits_parser = LimitsParser()
        
        # Data
        self.types_files: List[TypesFile] = []
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_stack = 50
        
        self.init_ui()
        self.restore_window_state()
        
        # Show startup dialog instead of auto-connecting
        QTimer.singleShot(100, self.show_startup_dialog)
    
    def show_startup_dialog(self):
        """Show startup dialog to choose connection mode"""
        startup = StartupDialog(self, self.config)
        if startup.exec_():
            if startup.mode == 'sftp':
                self.file_manager = self.sftp
                # Show SFTP connection dialog
                sftp_dialog = SFTPDialog(self)
                if sftp_dialog.exec_():
                    self.load_server_data()
            else:  # local mode
                local_manager = LocalFileManager()
                success, message = local_manager.connect(startup.local_path)
                if success:
                    self.file_manager = local_manager
                    self.load_server_data()
                else:
                    QMessageBox.critical(
                        self,
                        "Connection Failed",
                        f"Failed to open local folder:\n{message}"
                    )
        else:
            # User cancelled - just show empty app
            pass
    
    def init_ui(self):
        """Initialize the user interface"""
<<<<<<< HEAD
        self.setWindowTitle(f"DayZ Types Editor v{__version__}")
=======
        self.setWindowTitle("DayZ Types Editor")
>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.types_editor_tab = TypesEditorTab(self)
        self.settings_tab = SettingsTab(self)
        
        self.tabs.addTab(self.types_editor_tab, "Types Editor")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Initialize undo/redo button states
        self.update_undo_redo_buttons()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        connect_action = QAction('Connect to Server...', self)
        connect_action.triggered.connect(self.show_sftp_dialog)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction('Disconnect', self)
        disconnect_action.triggered.connect(self.disconnect_sftp)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('Save Changes', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_changes)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        readme_action = QAction('View Documentation', self)
        readme_action.triggered.connect(self.show_documentation)
        help_menu.addAction(readme_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('About DayZ Types Editor', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_documentation(self):
        """Show documentation dialog"""
        from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("DayZ Types Editor - Documentation")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        
        # Load documentation
        doc_text = """
<html>
<head>
<style>
body { background-color: #1e1e1e; color: #cccccc; font-family: Arial, sans-serif; }
h1 { color: #51cf66; }
h2 { color: #0e639c; margin-top: 20px; }
h3 { color: #cccccc; margin-top: 15px; }
code { background-color: #252526; padding: 2px 6px; border-radius: 3px; }
pre { background-color: #252526; padding: 10px; border-radius: 5px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #444; padding: 8px; text-align: left; }
th { background-color: #252526; }
</style>
</head>
<body>

<h1>DayZ Types Editor - Quick Reference</h1>

<h2>Field Descriptions</h2>

<h3>Numeric Fields</h3>
<table>
<tr><th>Field</th><th>Description</th><th>Range</th></tr>
<tr><td><b>Nominal</b></td><td>Maximum number that can exist in the world</td><td>0-99,999,999</td></tr>
<tr><td><b>Lifetime</b></td><td>Seconds before item despawns (3600 = 1 hour)</td><td>0-99,999,999</td></tr>
<tr><td><b>Min</b></td><td>Minimum number that should exist (triggers respawn)</td><td>0-Nominal</td></tr>
<tr><td><b>Restock</b></td><td>Seconds before item can respawn</td><td>0-99,999,999</td></tr>
<tr><td><b>Quantmin</b></td><td>Minimum stack size percentage (-1 = disabled)</td><td>-1 or 1-100</td></tr>
<tr><td><b>Quantmax</b></td><td>Maximum stack size percentage (-1 = disabled)</td><td>-1 or 1-100</td></tr>
<tr><td><b>Cost</b></td><td>In-game value/spawn priority (higher = rarer)</td><td>0-100</td></tr>
</table>

<h3>Item Flags</h3>
<table>
<tr><th>Flag</th><th>When Enabled (1)</th></tr>
<tr><td><b>Count in Cargo</b></td><td>Items in containers count toward nominal</td></tr>
<tr><td><b>Count in Hoarder</b></td><td>Items in underground stashes count toward nominal</td></tr>
<tr><td><b>Count in Map</b></td><td>Items spawned in world count toward nominal (usually enabled)</td></tr>
<tr><td><b>Count in Player</b></td><td>Items on players count toward nominal</td></tr>
<tr><td><b>Crafted</b></td><td>Item MUST be crafted - Central Economy will NOT spawn it naturally</td></tr>
<tr><td><b>Deloot</b></td><td>Remove from all natural loot spawns (event/admin only)</td></tr>
</table>

<h3>Multi-Select Fields</h3>
<table>
<tr><th>Field</th><th>Purpose</th></tr>
<tr><td><b>Usage</b></td><td>Where item can spawn (Military, Police, Farm, etc.)</td></tr>
<tr><td><b>Value</b></td><td>Tier/rarity level (Tier1=common, Tier4=very rare)</td></tr>
<tr><td><b>Tag</b></td><td>Additional spawn restrictions (floor, shelves, etc.)</td></tr>
<tr><td><b>Category</b></td><td>Item classification (defined in cfglimitsdefinition.xml)</td></tr>
</table>

<h2>Common Workflows</h2>

<h3>Finding Items</h3>
<ol>
<li>Use search bar for item name</li>
<li>Filter by category, usage, value, tag, or flags</li>
<li>Adjust nominal range if needed</li>
<li>Toggle AND/OR logic for complex filters</li>
</ol>

<h3>Editing Single Item</h3>
<ol>
<li>Select item in table</li>
<li>Edit fields in detail panel (right side)</li>
<li>Click "Apply Changes"</li>
<li>Item marked green (modified)</li>
</ol>

<h3>Batch Editing Multiple Items</h3>
<ol>
<li>Filter to desired items OR select multiple</li>
<li>Click "Batch Operations" toolbar button</li>
<<<<<<< HEAD
<li>Configure changes in three columns:
  <ul>
  <li><b>Numeric Fields:</b> Check field, choose Multiply or Set Value, enter value</li>
  <li><b>Category & Multi-Select:</b> Set category, toggle Usage/Value/Tag (ON=add, OFF=remove)</li>
  <li><b>Item Flags:</b> Toggle switches for 6 flags</li>
  </ul>
</li>
<li>Preview changes (green = will change, gray = unchanged)</li>
<li>Click "Apply Changes"</li>
</ol>

<p><b>Example:</b> To add Military usage to multiple items, check "Usage: Military" and toggle to ON.</p>

=======
<li>Check fields to modify</li>
<li>Set values (Multiply or Set Value)</li>
<li>Preview changes (green = changing)</li>
<li>Click "Apply Changes"</li>
</ol>

>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
<h3>Creating New Items</h3>
<ol>
<li>Click "New Item" toolbar button</li>
<li>Enter unique item name</li>
<li>Choose file to add to</li>
<li>Set values and flags</li>
<li>Click "Create Item"</li>
<li>Duplicate names are blocked</li>
</ol>

<h3>Saving Changes</h3>
<ol>
<li>Click Save button or press Ctrl+S</li>
<li>Review modified files</li>
<li>Automatic backup created</li>
<li>Files uploaded (SFTP) or saved (Local)</li>
</ol>

<h2>Keyboard Shortcuts</h2>
<ul>
<li><b>Ctrl+S</b> - Save changes</li>
<li><b>Ctrl+Z</b> - Undo</li>
<li><b>Ctrl+Y</b> - Redo</li>
<li><b>Ctrl+F</b> - Focus search bar</li>
</ul>

<h2>Important Notes</h2>
<ul>
<li><b>Crafted Flag:</b> Setting this to 1 means the item can ONLY be obtained through crafting - it will NOT spawn naturally in the world</li>
<li><b>Min vs Nominal:</b> Min cannot exceed Nominal (automatically capped)</li>
<li><b>Duplicate Names:</b> Each item name must be unique across all loaded files</li>
<li><b>Undo After Save:</b> Cannot undo past save point (save is a commit)</li>
<li><b>Backups:</b> Always created before saving - check Settings tab for location</li>
</ul>

<h2>Troubleshooting</h2>
<p><b>Items not spawning?</b> Check these settings:</p>
<ul>
<li>Nominal > 0</li>
<li>Min > 0 (to trigger spawning)</li>
<li>Crafted = 0 (unless you want craft-only)</li>
<li>Deloot = 0 (unless you want event-only)</li>
<li>At least one Usage flag set</li>
<li>At least one Value flag set</li>
</ul>

</body>
</html>
        """
        
        browser.setHtml(doc_text)
        layout.addWidget(browser)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About DayZ Types Editor",
<<<<<<< HEAD
            f"<h2>DayZ Types Editor</h2>"
            f"<p>Version {__version__}</p>"
=======
            "<h2>DayZ Types Editor</h2>"
            "<p>Version 1.0</p>"
>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
            "<p>A comprehensive desktop application for editing DayZ types.xml files.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>SFTP and Local file support</li>"
            "<li>Multi-file editing</li>"
<<<<<<< HEAD
            "<li>Batch operations (Numeric, Category, Usage, Value, Tag, Flags)</li>"
            "<li>Smart filtering with AND/OR logic</li>"
            "<li>New item creation</li>"
            "<li>Undo/Redo support (50 changes)</li>"
            "<li>Automatic backups</li>"
            "<li>File caching (80-90% faster loads)</li>"
            "</ul>"
            "<p>Created for DayZ server administrators and modders.</p>"
            "<p>© 2024 - Licensed under GPL v3.0</p>"
=======
            "<li>Batch operations</li>"
            "<li>Smart filtering</li>"
            "<li>Undo/Redo support</li>"
            "<li>Automatic backups</li>"
            "<li>File caching</li>"
            "</ul>"
            "<p>Created for DayZ server administrators and modders.</p>"
            "<p>© 2024 - Use at your own risk. Always backup your files.</p>"
>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
        )
    
    def show_sftp_dialog(self):
        """Show SFTP connection dialog"""
        dialog = SFTPDialog(self)
        if dialog.exec_():
            # Connection successful
            self.load_server_data()
    
    def disconnect_sftp(self):
        """Disconnect from current file source"""
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                'You have unsaved changes. Disconnect anyway?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        if self.file_manager:
            self.file_manager.disconnect()
            self.file_manager = None
        
        self.types_files = []
        self.types_editor_tab.clear_data()
        self.update_status_bar()
    
    def load_server_data(self):
        """Load all data from the server"""
        try:
            self.status_bar.showMessage("Loading data...")
            
            # Load limits definitions
            self.load_limits_definitions()
            
            # Load economy core to find types files
            economy_xml = self.file_manager.read_file('cfgeconomycore.xml')
            types_file_paths = EconomyParser.parse(economy_xml)
            
            # Load files with progress dialog
            self.load_types_files_with_progress(types_file_paths)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Data",
                f"Failed to load server data:\n{str(e)}\n\n{traceback.format_exc()}"
            )
            self.status_bar.showMessage("Error loading data", 5000)
    
    def load_types_files_with_progress(self, types_file_paths: List[str], retry_files: List[str] = None):
        """Load types files with progress dialog and caching"""
        from ui.loading_progress_dialog import LoadingProgressDialog
        from PyQt5.QtWidgets import QApplication
        
        # Determine which files to load
        files_to_load = retry_files if retry_files else types_file_paths
        
        # Create progress dialog
        progress = LoadingProgressDialog(self, len(files_to_load))
        progress.show()
        QApplication.processEvents()
        
        # Track errors and cache statistics
        loading_errors = []
        cached_count = 0
        downloaded_count = 0
        
        # Load files (keep existing if retrying)
        if not retry_files:
            self.types_files = []
        
        for i, file_path in enumerate(files_to_load, 1):
            if progress.is_cancelled():
                break
            
            try:
                # Check if we can use cached version
                use_cache = False
                types_xml = None
                
                if not retry_files:  # Don't use cache when retrying
                    # Get remote file modification time
                    remote_mtime = self.file_manager.get_file_mtime(file_path)
                    
                    if remote_mtime:
                        # Check cache
                        cached = self.config.get_cached_file(file_path)
                        if cached and cached.get('timestamp') == remote_mtime:
                            # Cache is valid
                            types_xml = cached.get('content')
                            use_cache = True
                            cached_count += 1
                
                # Download if not using cache
                if not use_cache:
                    types_xml = self.file_manager.read_file(file_path)
                    downloaded_count += 1
                    
                    # Cache the file
                    remote_mtime = self.file_manager.get_file_mtime(file_path)
                    if remote_mtime:
                        self.config.set_cached_file(file_path, remote_mtime, types_xml)
                
                # Parse the XML
                types_file = TypesParser.parse(types_xml, file_path, self.limits_parser)
                
                # Store original content for comparison
                types_file.original_content = types_xml
                
                # If retrying, remove old version first
                if retry_files:
                    self.types_files = [tf for tf in self.types_files if tf.path != file_path]
                
                self.types_files.append(types_file)
                progress.update_progress(i, file_path, True)
                
            except Exception as e:
                error_msg = str(e)
                loading_errors.append({
                    'file': file_path,
                    'error': error_msg
                })
                progress.update_progress(i, file_path, False)
            
            QApplication.processEvents()
        
        progress.close()
        
        # Update UI
        self.types_editor_tab.load_data(self.types_files, self.limits_parser)
        
        total_items = sum(len(tf.items) for tf in self.types_files)
        cache_msg = f" ({cached_count} cached, {downloaded_count} downloaded)" if not retry_files else ""
        self.status_bar.showMessage(
            f"Loaded {len(self.types_files)} files with {total_items} items{cache_msg}", 
            5000
        )
        self.update_status_bar()
        
        # Show error dialog if there were any errors
        if loading_errors:
            from ui.file_error_dialog import FileErrorDialog
            error_dialog = FileErrorDialog(
                self,
                loading_errors,
                len(types_file_paths),
                len(self.types_files)
            )
            
            if error_dialog.exec_() and hasattr(error_dialog, 'retry_requested') and error_dialog.retry_requested:
                # User wants to retry - get list of failed files
                failed_files = [err['file'] for err in loading_errors]
                QMessageBox.information(
                    self,
                    "Retry Files",
                    f"Please fix the {len(failed_files)} file(s) on your server, then click OK to retry loading them."
                )
                self.load_types_files_with_progress(types_file_paths, failed_files)
    
    def load_limits_definitions(self):
        """Load limits definition files"""
        self.limits_parser = LimitsParser()
        
        # Load main limits file
        try:
            limits_xml = self.file_manager.read_file('cfglimitsdefinition.xml')
            self.limits_parser.parse(limits_xml)
            print(f"Loaded limits: {len(self.limits_parser.get_categories())} categories, "
                  f"{len(self.limits_parser.get_usages())} usages, "
                  f"{len(self.limits_parser.get_values())} values, "
                  f"{len(self.limits_parser.get_tags())} tags")
        except Exception as e:
            print(f"Error loading cfglimitsdefinition.xml: {e}")
            import traceback
            traceback.print_exc()
        
        # Load user limits file (contains user group definitions)
        try:
            user_limits_xml = self.file_manager.read_file('cfglimitsdefinitionuser.xml')
            self.limits_parser.parse_user_definitions(user_limits_xml)
            print(f"Loaded {len(self.limits_parser.get_user_names())} user definitions")
        except Exception as e:
            print(f"Error loading cfglimitsdefinitionuser.xml: {e}")
            import traceback
            traceback.print_exc()
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are any unsaved changes"""
        return any(tf.has_modifications() for tf in self.types_files)
    
    def update_status_bar(self):
        """Update status bar with current info"""
        if self.file_manager and self.file_manager.is_connected():
            connection_info = self.file_manager.get_connection_info()
            files_count = len(self.types_files)
            total_items = sum(len(tf.items) for tf in self.types_files)
            modified_count = sum(len(tf.get_modified_items()) for tf in self.types_files)
            
            status = f"Connected: {connection_info} | {files_count} files | {total_items} items"
            if modified_count > 0:
                status += f" | Modified: {modified_count} items ⚠"
            
            self.status_bar.showMessage(status)
        else:
            self.status_bar.showMessage("Not connected")
    
    def undo(self):
        """Undo last operation"""
        if not self.undo_stack:
            return
        
        # Pop last change from undo stack
        change = self.undo_stack.pop()
        
        # Store current state for redo
        redo_snapshots = []
        for item_name, old_snapshot in change:
            # Find the current item
            current_item = None
            for types_file in self.types_files:
                current_item = types_file.get_item_by_name(item_name)
                if current_item:
                    break
            
            if current_item:
                # Save current state for redo
                redo_snapshots.append((item_name, current_item.clone()))
                
                # Restore old state
                self._apply_snapshot(current_item, old_snapshot)
        
        # Push to redo stack
        self.redo_stack.append(redo_snapshots)
        
        # Update UI
        self.types_editor_tab.refresh_display()
        self.update_undo_redo_buttons()
        self.update_status_bar()
    
    def redo(self):
        """Redo last undone operation"""
        if not self.redo_stack:
            return
        
        # Pop last undone change from redo stack
        change = self.redo_stack.pop()
        
        # Store current state for undo
        undo_snapshots = []
        for item_name, new_snapshot in change:
            # Find the current item
            current_item = None
            for types_file in self.types_files:
                current_item = types_file.get_item_by_name(item_name)
                if current_item:
                    break
            
            if current_item:
                # Save current state for undo
                undo_snapshots.append((item_name, current_item.clone()))
                
                # Restore new state
                self._apply_snapshot(current_item, new_snapshot)
        
        # Push to undo stack
        self.undo_stack.append(undo_snapshots)
        
        # Update UI
        self.types_editor_tab.refresh_display()
        self.update_undo_redo_buttons()
        self.update_status_bar()
    
    def _apply_snapshot(self, target_item: TypeItem, snapshot: TypeItem):
        """Apply a snapshot to an item"""
        target_item.nominal = snapshot.nominal
        target_item.lifetime = snapshot.lifetime
        target_item.restock = snapshot.restock
        target_item.min = snapshot.min
        target_item.quantmin = snapshot.quantmin
        target_item.quantmax = snapshot.quantmax
        target_item.cost = snapshot.cost
        target_item.category = snapshot.category
        target_item.usage = snapshot.usage.copy()
        target_item.value = snapshot.value.copy()
        target_item.tag = snapshot.tag.copy()
        target_item.count_in_cargo = snapshot.count_in_cargo
        target_item.count_in_hoarder = snapshot.count_in_hoarder
        target_item.count_in_map = snapshot.count_in_map
        target_item.count_in_player = snapshot.count_in_player
        target_item.crafted = snapshot.crafted
        target_item.deloot = snapshot.deloot
        target_item.modified = snapshot.modified
    
    def push_undo_state(self, items: List[TypeItem]):
        """Push current state of items to undo stack before modification"""
        if not items:
            return
        
        # Create snapshots of items before modification
        snapshots = [(item.name, item.clone()) for item in items]
        
        # Add to undo stack
        self.undo_stack.append(snapshots)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_undo_stack:
            self.undo_stack.pop(0)
        
        # Clear redo stack (new changes invalidate redo history)
        self.redo_stack.clear()
        
        # Update button states
        self.update_undo_redo_buttons()
    
    def clear_undo_redo(self):
        """Clear undo/redo stacks (called after save)"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.update_undo_redo_buttons()
    
    def update_undo_redo_buttons(self):
        """Update undo/redo button enabled state"""
        if hasattr(self, 'types_editor_tab'):
            self.types_editor_tab.undo_btn.setEnabled(len(self.undo_stack) > 0)
            self.types_editor_tab.redo_btn.setEnabled(len(self.redo_stack) > 0)
    
    def save_changes(self):
        """Save modified files"""
        # Check if file manager is connected
        if not self.file_manager or not self.file_manager.is_connected():
            QMessageBox.warning(
                self,
                "Not Connected",
                "Please connect to a server or open local files first."
            )
            return
        
        # Get modified files
        modified_files = [tf for tf in self.types_files if tf.has_modifications()]
        
        if not modified_files:
            QMessageBox.information(
                self,
                "No Changes",
                "There are no modified files to save."
            )
            return
        
        # Show file selection dialog
        dialog = SaveDialog(self, modified_files)
        if not dialog.exec_():
            return
        
        selected_files = dialog.get_selected_files()
        
        if not selected_files:
            QMessageBox.information(
                self,
                "No Files Selected",
                "No files were selected to save."
            )
            return
        
        # Save files with progress
        self.save_files_with_progress(selected_files)
    
    def save_files_with_progress(self, files_to_save: List[TypesFile]):
        """Save files with progress dialog"""
        progress = QProgressDialog("Saving files...", "Cancel", 0, len(files_to_save), self)
        progress.setWindowTitle("Saving Changes")
        progress.setModal(True)
        progress.setMinimumDuration(0)
        
        errors = []
        saved_count = 0
        
        for i, types_file in enumerate(files_to_save):
            progress.setValue(i)
            progress.setLabelText(f"Saving {types_file.path}...")
            
            if progress.wasCanceled():
                break
            
            try:
                # Generate XML with user tag preservation
                xml_content = types_file.to_xml(self.limits_parser)
                
                # Create backup if we have original content
                if types_file.original_content:
                    self.backup_manager.create_backup(
                        types_file.path, 
                        types_file.original_content
                    )
                
                # Write file using file manager (works for both SFTP and Local)
                self.file_manager.write_file(types_file.path, xml_content)
                
                # Update cache with new timestamp
                new_mtime = self.file_manager.get_file_mtime(types_file.path)
                if new_mtime:
                    self.config.set_cached_file(types_file.path, new_mtime, xml_content)
                
                # Update original content and clear modified flags
                types_file.original_content = xml_content
                for item in types_file.items:
                    item.modified = False
                
                saved_count += 1
            
            except Exception as e:
                errors.append({
                    'file': types_file.path,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        progress.setValue(len(files_to_save))
        
        # Show results
        self.show_save_results(saved_count, errors)
        
        # Clear undo/redo stacks after successful save
        if saved_count > 0:
            self.clear_undo_redo()
        
        # Refresh UI
        self.update_status_bar()
    
    def show_save_results(self, success_count: int, errors: List[Dict]):
        """Show save results with error details if any"""
        if not errors:
            QMessageBox.information(
                self,
                "Save Successful",
                f"Successfully saved {success_count} file(s)."
            )
        else:
            # Build error message
            msg = f"Saved {success_count} file(s) successfully.\n\n"
            msg += f"Failed to save {len(errors)} file(s):\n\n"
            
            for error in errors:
                msg += f"• {error['file']}\n  Error: {error['error']}\n\n"
            
            # Show error dialog with option to retry
            reply = QMessageBox.critical(
                self,
                "Save Errors",
                msg,
                QMessageBox.Retry | QMessageBox.Ok,
                QMessageBox.Ok
            )
            
            # If user wants to retry, collect failed files and try again
            if reply == QMessageBox.Retry:
                failed_files = []
                for error in errors:
                    for tf in self.types_files:
                        if tf.path == error['file'] and tf.has_modifications():
                            failed_files.append(tf)
                            break
                
                if failed_files:
                    self.save_files_with_progress(failed_files)

    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                'You have unsaved changes. Exit anyway?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Save window state
        self.save_window_state()
        
        # Disconnect from file source
        if self.file_manager:
            self.file_manager.disconnect()
        
        event.accept()
    
    def save_window_state(self):
        """Save window geometry and state"""
        # Convert QByteArray to bytes, then to base64 string
        geometry = self.saveGeometry().toBase64().data().decode()
        state = self.saveState().toBase64().data().decode()
        
        self.config.set_window_geometry(geometry)
        self.config.set_window_state(state)
    
    def restore_window_state(self):
        """Restore window geometry and state"""
        geometry = self.config.get_window_geometry()
        state = self.config.get_window_state()
        
        if geometry:
            from PyQt5.QtCore import QByteArray
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        
        if state:
            from PyQt5.QtCore import QByteArray
            self.restoreState(QByteArray.fromBase64(state.encode()))
