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
from core.random_presets_parser import RandomPresetsParser
from core.spawnabletypes_parser import SpawnableTypesParser
from models.types_file import TypesFile
from models.type_item import TypeItem
from models.spawnable_type import SpawnableTypesFile
from ui.types_editor import TypesEditorTab
from ui.settings_tab import SettingsTab
from ui.random_presets_tab import RandomPresetsTab
from ui.spawnable_types_tab import SpawnableTypesTab
from ui.sftp_dialog import SFTPDialog
from version import __version__
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
        self.spawnabletypes_files: List[SpawnableTypesFile] = []
        self.random_presets_file = None  # RandomPresetsFile or None
        self.has_random_preset_changes = False  # Track if random presets modified
        self.has_spawnabletypes_changes = False  # Track if spawnable types modified
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
        self.setWindowTitle(f"DayZ Types Editor v{__version__}")
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.types_editor_tab = TypesEditorTab(self)
        self.random_presets_tab = RandomPresetsTab(self)
        self.spawnable_types_tab = SpawnableTypesTab(self)
        self.settings_tab = SettingsTab(self)
        
        self.tabs.addTab(self.types_editor_tab, "Types Editor")
        self.tabs.addTab(self.random_presets_tab, "Random Presets")
        self.tabs.addTab(self.spawnable_types_tab, "Spawnable Types")
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

<h2>Spawnable Types Editor</h2>

<h3>Overview</h3>
<p>Edit <code>cfgspawnabletypes.xml</code> files to control what items spawn attached to or inside other items.</p>

<h3>Block Types</h3>
<table>
<tr><th>Type</th><th>Description</th></tr>
<tr><td><b>Preset Block</b></td><td>References a preset from cfgrandompresets.xml</td></tr>
<tr><td><b>Chance Block</b></td><td>Defines items inline with individual spawn chances</td></tr>
</table>

<h3>Cargo vs Attachments</h3>
<table>
<tr><th>Type</th><th>Purpose</th><th>Example</th></tr>
<tr><td><b>Cargo</b></td><td>Items inside container</td><td>Food in backpack</td></tr>
<tr><td><b>Attachments</b></td><td>Items attached to item</td><td>Magazine in gun</td></tr>
</table>

<h3>Working with Blocks</h3>
<ol>
<li>Select type in list (filter by file or properties)</li>
<li>Right-click cargo/attachments tree for context menu</li>
<li>Add Block → Choose preset or chance-based</li>
<li>Edit Block → Change preset or adjust chance</li>
<li>Delete Block → Remove entirely</li>
<li>Hover over preset blocks to see contents</li>
</ol>

<h3>Chance-Based Blocks</h3>
<ul>
<li><b>Block Chance:</b> Probability this block attempts to spawn (0.0-1.0)</li>
<li><b>Item Chance:</b> Probability each item spawns if block triggers</li>
<li><b>First Item Wins:</b> Only first successful item spawns per block</li>
<li><b>Reordering:</b> Use Move Up/Down to control spawn priority</li>
</ul>

<h3>Properties</h3>
<table>
<tr><th>Property</th><th>Effect</th></tr>
<tr><td><b>Hoarder</b></td><td>Can spawn in underground stashes</td></tr>
<tr><td><b>Damage</b></td><td>Spawns with random damage (0.0-1.0 range)</td></tr>
</table>

<h2>Random Presets Editor</h2>

<h3>Overview</h3>
<p>Create and manage presets in <code>cfgrandompresets.xml</code> for reuse across multiple spawnable types.</p>

<h3>Preset Structure</h3>
<ul>
<li><b>Preset Name:</b> Unique identifier (e.g., "foodMilitary")</li>
<li><b>Preset Chance:</b> Probability preset attempts to spawn (0.0-1.0)</li>
<li><b>Items:</b> List of items with individual spawn chances</li>
</ul>

<h3>Creating Presets</h3>
<ol>
<li>Choose Cargo or Attachments preset type</li>
<li>Click "Add Preset"</li>
<li>Enter name and preset chance</li>
<li>Add items with individual chances</li>
<li>Item names validated against types.xml</li>
</ol>

<h3>Using Presets</h3>
<ol>
<li>Create preset in Random Presets tab</li>
<li>Go to Spawnable Types tab</li>
<li>Select type → Add Block → Preset-based</li>
<li>Choose your preset from dropdown</li>
<li>Hover to see preset contents</li>
</ol>

<h3>Best Practices</h3>
<ul>
<li>Name presets descriptively (e.g., "policeWeapons", "medicalSupplies")</li>
<li>Group similar items together</li>
<li>Reuse presets across multiple types for consistency</li>
<li>Higher chance = more likely to spawn</li>
<li>Total item chances can exceed 1.0 (each rolls independently)</li>
</ul>

<h2>Keyboard Shortcuts</h2>
<ul>
<li><b>Ctrl+S</b> - Save changes</li>
<li><b>Ctrl+Z</b> - Undo</li>
<li><b>Ctrl+Y</b> - Redo</li>
<li><b>Ctrl+F</b> - Focus search bar</li>
</ul>

<h2>Important Notes</h2>
<ul>
<li><b>Unified Save:</b> Save dialog shows ALL modified files (types, spawnable types, presets) - select which to save</li>
<li><b>Vanilla Files:</b> Editor automatically loads db/types.xml and cfgspawnabletypes.xml if they exist</li>
<li><b>Crafted Flag:</b> Setting this to 1 means the item can ONLY be obtained through crafting - it will NOT spawn naturally in the world</li>
<li><b>Min vs Nominal:</b> Min cannot exceed Nominal (automatically capped)</li>
<li><b>Duplicate Names:</b> Each item name must be unique across all loaded files</li>
<li><b>Undo Across Tabs:</b> Undo/Redo works across all tabs (Types, Spawnable Types, Random Presets)</li>
<li><b>Undo After Save:</b> Cannot undo past save point (save is a commit)</li>
<li><b>Backups:</b> Always created before saving - check Settings tab for location</li>
<li><b>Preset Tooltips:</b> Hover over preset blocks or dropdown items to see contents</li>
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
            f"<h2>DayZ Types Editor</h2>"
            f"<p>Version {__version__}</p>"
            "<p>A comprehensive economy file editor for DayZ servers.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Types Editor - Full types.xml editing</li>"
            "<li>Spawnable Types Editor - cfgspawnabletypes.xml support</li>"
            "<li>Random Presets Editor - cfgrandompresets.xml management</li>"
            "<li>SFTP and Local file support</li>"
            "<li>Batch operations with live preview</li>"
            "<li>Smart filtering with AND/OR logic</li>"
            "<li>Preset tooltips and validation</li>"
            "<li>Unified save system</li>"
            "<li>Undo/Redo across all tabs (50 changes)</li>"
            "<li>Automatic backups and file caching</li>"
            "<li>Auto-discovery of vanilla files</li>"
            "</ul>"
            "<p>Created for DayZ server administrators and modders.</p>"
            "<p>© 2024-2025 - Licensed under GPL v3.0</p>"
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
            
            # Load economy core to find types and spawnabletypes files
            economy_xml = self.file_manager.read_file('cfgeconomycore.xml')
            types_file_paths, spawnabletypes_file_paths = EconomyParser.parse_all(economy_xml)
            
            # Add vanilla db/types.xml if it exists (not always in cfgeconomycore but loaded by game)
            vanilla_types = 'db/types.xml'
            if self.file_manager.file_exists(vanilla_types):
                # Add at the beginning so it's loaded first (like vanilla does)
                if vanilla_types not in types_file_paths:
                    types_file_paths.insert(0, vanilla_types)
            
            # Add vanilla cfgspawnabletypes.xml if it exists (not in cfgeconomycore but loaded by game)
            vanilla_spawnabletypes = 'cfgspawnabletypes.xml'
            if self.file_manager.file_exists(vanilla_spawnabletypes):
                # Add at the beginning so it's loaded first (like vanilla does)
                if vanilla_spawnabletypes not in spawnabletypes_file_paths:
                    spawnabletypes_file_paths.insert(0, vanilla_spawnabletypes)
            
            # Load types files with progress dialog
            self.load_types_files_with_progress(types_file_paths)
            
            # Load spawnable types files with progress dialog
            self.load_spawnabletypes_files_with_progress(spawnabletypes_file_paths)
            
            # Load random presets (optional file)
            self.load_random_presets()
            
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
    
    def load_spawnabletypes_files_with_progress(self, spawnabletypes_file_paths: List[str], retry_files: List[str] = None):
        """Load spawnable types files with progress dialog"""
        from ui.loading_progress_dialog import LoadingProgressDialog
        from PyQt5.QtWidgets import QApplication
        
        if not spawnabletypes_file_paths:
            print("No spawnable types files found in cfgeconomycore.xml")
            return
        
        # Determine which files to load
        files_to_load = retry_files if retry_files else spawnabletypes_file_paths
        
        # Create progress dialog
        progress = LoadingProgressDialog(self, len(files_to_load))
        progress.setWindowTitle("Loading Spawnable Types")
        progress.show()
        QApplication.processEvents()
        
        # Track errors
        loading_errors = []
        
        # Load files (keep existing if retrying)
        if not retry_files:
            self.spawnabletypes_files = []
        
        for i, file_path in enumerate(files_to_load, 1):
            if progress.is_cancelled():
                break
            
            try:
                # Read file
                xml_content = self.file_manager.read_file(file_path)
                
                # Parse the XML
                spawnable_types_file = SpawnableTypesParser.parse(xml_content, file_path)
                
                # If retrying, remove old version first
                if retry_files:
                    self.spawnabletypes_files = [stf for stf in self.spawnabletypes_files if stf.source_file != file_path]
                
                self.spawnabletypes_files.append(spawnable_types_file)
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
        
        # Load data into tab
        self.spawnable_types_tab.load_data(self.spawnabletypes_files)
        
        # Update status
        total_types = sum(len(stf.types) for stf in self.spawnabletypes_files)
        print(f"Loaded {len(self.spawnabletypes_files)} spawnable types files with {total_types} types")
        
        # Show error dialog if there were any errors
        if loading_errors:
            from ui.file_error_dialog import FileErrorDialog
            error_dialog = FileErrorDialog(
                self,
                loading_errors,
                len(spawnabletypes_file_paths),
                len(self.spawnabletypes_files)
            )
            
            if error_dialog.exec_() and hasattr(error_dialog, 'retry_requested') and error_dialog.retry_requested:
                # User wants to retry - get list of failed files
                failed_files = [err['file'] for err in loading_errors]
                QMessageBox.information(
                    self,
                    "Retry Files",
                    f"Please fix the {len(failed_files)} file(s) on your server, then click OK to retry loading them."
                )
                self.load_spawnabletypes_files_with_progress(spawnabletypes_file_paths, failed_files)
    
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
    
    def load_random_presets(self):
        """Load random presets file (optional)"""
        try:
            presets_xml = self.file_manager.read_file('cfgrandompresets.xml')
            self.random_presets_file = RandomPresetsParser.parse(presets_xml, 'cfgrandompresets.xml')
            
            # Load into tab
            self.random_presets_tab.load_data(self.random_presets_file)
            
            total_presets = self.random_presets_file.get_total_preset_count()
            print(f"Loaded cfgrandompresets.xml: {total_presets} presets "
                  f"({len(self.random_presets_file.cargo_presets)} cargo, "
                  f"{len(self.random_presets_file.attachments_presets)} attachments)")
            
        except FileNotFoundError:
            # File doesn't exist - this is okay, user can create it later
            self.random_presets_file = None
            self.random_presets_tab.load_data(None)
            print("cfgrandompresets.xml not found - file is optional and can be created later")
            
            # Show info message to user
            QMessageBox.information(
                self,
                "Random Presets Not Found",
                "The file 'cfgrandompresets.xml' was not found in your mission folder.\n\n"
                "This file is optional. You can create it later by adding your first preset "
                "in the Random Presets tab."
            )
            
        except Exception as e:
            # Parse error or other issue
            self.random_presets_file = None
            self.random_presets_tab.load_data(None)
            print(f"Error loading cfgrandompresets.xml: {e}")
            
            # Show warning with option to continue
            reply = QMessageBox.warning(
                self,
                "Random Presets Load Error",
                f"Failed to load cfgrandompresets.xml:\n\n{str(e)}\n\n"
                "The editor will continue without random presets support.\n"
                "You can fix the file and reconnect to try again.",
                QMessageBox.Ok
            )
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are any unsaved changes"""
        types_modified = any(tf.has_modifications() for tf in self.types_files)
        return types_modified or self.has_random_preset_changes or self.has_spawnabletypes_changes
    
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
            
            # Add random preset changes indicator
            if self.has_random_preset_changes:
                status += f" | Random Presets Modified ⚠"
            
            # Add spawnable types changes indicator
            if self.has_spawnabletypes_changes:
                status += f" | Spawnable Types Modified ⚠"
            
            self.status_bar.showMessage(status)
        else:
            self.status_bar.showMessage("Not connected")
    
    def undo(self):
        """Undo last operation"""
        if not self.undo_stack:
            return
        
        # Pop last change from undo stack
        change = self.undo_stack.pop()
        
        # Check if this is a random_presets change or types change
        if isinstance(change, tuple) and change[0] == 'random_presets':
            # Random presets undo
            _, old_state = change
            
            # Save current state for redo
            if self.random_presets_file:
                import copy
                self.redo_stack.append(('random_presets', copy.deepcopy(self.random_presets_file)))
            else:
                self.redo_stack.append(('random_presets', None))
            
            # Restore old state
            self.random_presets_file = old_state
            self.random_presets_tab.load_data(old_state)
            
        else:
            # Types items undo (existing behavior)
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
            
            # Update types editor UI
            self.types_editor_tab.refresh_display()
        
        # Update UI
        self.update_undo_redo_buttons()
        self.update_status_bar()
    
    def redo(self):
        """Redo last undone operation"""
        if not self.redo_stack:
            return
        
        # Pop last undone change from redo stack
        change = self.redo_stack.pop()
        
        # Check if this is a random_presets change or types change
        if isinstance(change, tuple) and change[0] == 'random_presets':
            # Random presets redo
            _, new_state = change
            
            # Save current state for undo
            if self.random_presets_file:
                import copy
                self.undo_stack.append(('random_presets', copy.deepcopy(self.random_presets_file)))
            else:
                self.undo_stack.append(('random_presets', None))
            
            # Restore new state
            self.random_presets_file = new_state
            self.random_presets_tab.load_data(new_state)
            
        else:
            # Types items redo (existing behavior)
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
            
            # Update types editor UI
            self.types_editor_tab.refresh_display()
        
        # Update UI
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
        modified_spawnabletypes = self.spawnabletypes_files if self.has_spawnabletypes_changes else []
        
        if not modified_files and not modified_spawnabletypes and not self.has_random_preset_changes:
            QMessageBox.information(
                self,
                "No Changes",
                "There are no modified files to save."
            )
            return
        
        # Show file selection dialog with all modified files
        dialog = SaveDialog(self, modified_files, modified_spawnabletypes, self.has_random_preset_changes)
        if not dialog.exec_():
            return
        
        selected_files = dialog.get_selected_files()
        selected_spawnabletypes = dialog.get_selected_spawnabletypes_files()
        save_random_presets = dialog.should_save_random_presets()
        
        if not selected_files and not selected_spawnabletypes and not save_random_presets:
            QMessageBox.information(
                self,
                "No Files Selected",
                "No files were selected to save."
            )
            return
        
        # Save types files with progress
        if selected_files:
            self.save_files_with_progress(selected_files)
        
        # Save spawnable types files
        if selected_spawnabletypes:
            self.save_spawnabletypes_files(selected_spawnabletypes)
        
        # Save random presets if selected
        if save_random_presets and self.random_presets_file:
            self.save_random_presets_from_main()
    
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
    
    def save_random_presets_from_main(self):
        """Save random presets from main window"""
        try:
            from core.random_presets_writer import RandomPresetsWriter
            
            # Write to XML
            xml_content = RandomPresetsWriter.write(self.random_presets_file)
            
            # Save via file manager
            self.file_manager.write_file('cfgrandompresets.xml', xml_content)
            
            # Clear undo/redo stacks on save
            self.undo_stack.clear()
            self.redo_stack.clear()
            
            # Clear modified flag
            self.has_random_preset_changes = False
            
            # Update UI
            self.random_presets_tab.update_button_states()
            self.update_status_bar()
            
            print(f"Saved cfgrandompresets.xml ({self.random_presets_file.get_total_preset_count()} presets)")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save cfgrandompresets.xml:\n{str(e)}"
            )
    
    def save_spawnabletypes_files(self, files_to_save: List[SpawnableTypesFile]):
        """Save spawnable types files"""
        from core.spawnabletypes_writer import SpawnableTypesWriter
        
        errors = []
        saved_count = 0
        
        for spawnable_types_file in files_to_save:
            try:
                # Write to XML
                xml_content = SpawnableTypesWriter.write(spawnable_types_file)
                
                # Save via file manager
                self.file_manager.write_file(spawnable_types_file.source_file, xml_content)
                
                saved_count += 1
                print(f"Saved {spawnable_types_file.source_file} ({len(spawnable_types_file.types)} types)")
                
            except Exception as e:
                errors.append({
                    'file': spawnable_types_file.source_file,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        # Clear modified flag if all saved successfully
        if saved_count > 0 and not errors:
            self.has_spawnabletypes_changes = False
            
            # Clear undo/redo stacks
            self.undo_stack.clear()
            self.redo_stack.clear()
        
        # Update UI
        self.update_status_bar()
        
        # Show results
        if errors:
            error_msg = f"Saved {saved_count} file(s), but {len(errors)} file(s) failed:\n\n"
            for err in errors:
                error_msg += f"• {err['file']}: {err['error']}\n"
            QMessageBox.warning(self, "Save Completed with Errors", error_msg)
        elif saved_count > 0:
            QMessageBox.information(
                self,
                "Save Successful",
                f"Successfully saved {saved_count} spawnable types file(s)."
            )
    
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
