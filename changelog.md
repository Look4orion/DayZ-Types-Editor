# Changelog

All notable changes to DayZ Types Editor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Loot map viewer with spawn location visualization
- Import/export presets for batch operations
- Search and replace functionality
- Dark/light theme toggle
- Export to CSV/Excel
- Multi-language support

---

## [2.0.0] - 2025-01-17

### Major Features Added

#### Spawnable Types Editor
- **Full cfgspawnabletypes.xml Support**: Complete editing of spawnable type configurations
- **Cargo Blocks**: Add, edit, delete cargo blocks (preset-based or chance-based)
- **Attachments Blocks**: Add, edit, delete attachments blocks (preset-based or chance-based)
- **Preset Tooltips**: Hover over preset blocks/dropdowns to see contents
- **Item Management**: Add, edit, delete, reorder items in chance-based blocks
- **Two-Step Workflow**: Guided creation of chance-based blocks with required first item
- **Properties Editing**: Set hoarder and damage flags per type
- **Filtering**: Search by name, filter by file, properties (has hoarder, damage, cargo, attachments)
- **Dark Mode UI**: Consistent styling with main Types Editor
- **Undo/Redo**: Full support for all operations

#### Random Presets Editor
- **Full cfgrandompresets.xml Support**: Create and manage cargo and attachments presets
- **Preset Management**: Add, edit, delete presets with name and chance
- **Item Management**: Add, edit, remove items from presets with individual chances
- **Dual Preset Types**: Separate cargo and attachments preset lists
- **Validation**: Item name validation against types.xml, duplicate preset name prevention
- **Filtering**: Filter by preset type (cargo/attachments) or search by name
- **Dark Mode UI**: Matching design throughout
- **Undo/Redo**: Track all preset and item changes

#### File Discovery
- **Vanilla File Support**: Automatically detect and load db/types.xml and cfgspawnabletypes.xml
- **Smart Loading**: Check for vanilla files not always referenced in cfgeconomycore.xml
- **Priority Ordering**: Load vanilla files first (matching game behavior)

#### Unified Save System
- **Multi-File Save**: Save changes across types, spawnable types, and presets in one operation
- **Save Dialog**: Review and select which modified files to save
- **Consistent Behavior**: All tabs share unified save workflow
- **Validation**: Check for errors before writing files
- **Backup Integration**: Automatic backups before every save

### Enhanced
- **Context Menus**: Right-click operations for blocks and items
- **Keyboard Shortcuts**: Undo (Ctrl+Z), Redo (Ctrl+Y), Save (Ctrl+S) work across all tabs
- **Modified Tracking**: Visual indicators for unsaved changes in all tabs
- **Error Handling**: Better validation and user feedback throughout

### Fixed
- Dialog initialization errors in add/edit dialogs
- Dark mode styling inconsistencies (white/black boxes eliminated)
- Unhashable type errors in filter operations
- Missing imports and attribute errors
- Vanilla file discovery and loading

### Technical
- **New Models**: SpawnableType, SpawnableTypesFile, RandomPreset, RandomPresetsFile
- **New Parsers**: spawnabletypes_parser.py, random_presets_parser.py
- **New Writers**: spawnabletypes_writer.py, random_presets_writer.py
- **New UI Tabs**: spawnable_types_tab.py, random_presets_tab.py
- **New Dialogs**: add_block_dialog.py, edit_block_dialog.py, add_item_dialog.py, edit_item_dialog.py, add_preset_dialog.py

---

## [1.0.1] - 2024-12-30

### Added
- **Batch Operations Expanded**: Added Category, Usage, Value, and Tag editing
  - Category field with dropdown (set or clear)
  - All Usage flags with toggle switches (add/remove)
  - All Value flags with toggle switches (add/remove)
  - All Tag flags with toggle switches (add/remove)
  - Three-column layout for better organization
  - Scrollable multi-select area (3 columns, max 400px height)
- **Enhanced Spinboxes**: Larger up/down arrows (30px wide) for easier clicking
- **Toggle Switches**: iOS-style animated toggles for all flag editing
  - Blue when ON, gray when OFF
  - Smooth animations
  - Clear visual feedback

### Changed
- Batch Operations dialog now resizable (default 1400x800, min 1200x600)
- Multi-select fields organized in compact 3-column grid
- Removed default checkboxes in batch operations (user must explicitly select fields)

### Fixed
- Middle column layout in batch operations now displays correctly
- Toggle switches now properly respond to clicks
- Import errors resolved (QWidget, QScrollArea)

---

## [1.0.0] - 2024-12-29

### Initial Release

The first stable release of DayZ Types Editor - a comprehensive desktop application for editing DayZ types.xml files.

### Added

#### Core Features
- **Dual File Source Support**: Connect via SFTP to remote servers or work with local files
- **Multi-file Editing**: Load and edit multiple types.xml files simultaneously from cfgeconomycore.xml
- **File Caching System**: Intelligent caching reduces subsequent load times by 80-90%
- **Automatic Backups**: Timestamped backups created before every save operation
- **Comment Preservation**: XML comments are preserved through edit/save cycles

#### Editing Capabilities
- **Individual Item Editing**: Edit all 13 item fields in detail panel
  - Numeric: Nominal, Lifetime, Min, Restock, Quantmin, Quantmax, Cost
  - Category: Single selection from cfglimitsdefinition.xml
  - Multi-select: Usage, Value, Tag flags
  - Item Flags: 6 binary flags (Count in Cargo/Hoarder/Map/Player, Crafted, Deloot)
- **Batch Operations**: Modify multiple items simultaneously
  - Two operation modes: Multiply or Set Value
  - Live preview showing all changes before applying
  - Smart validation (Min capped at Nominal)
  - Larger spinbox arrows for easier clicking
  - Toggle switches for flag editing (ON/OFF sliders)
- **New Item Creation**: Add new type entries
  - Full field configuration during creation
  - Duplicate name detection across all loaded files
  - Option to edit existing item or change name if duplicate found
  - Auto-selection of newly created item
- **Undo/Redo System**: Track up to 50 changes
  - Works for single and batch edits
  - Clears after save (intentional commit point)

#### Filtering System
- **Search by Name**: Partial match on item names
- **Filter by Category**: Dropdown selection
- **Filter by Usage**: Multi-select checkboxes with item counts
- **Filter by Value**: Multi-select checkboxes with item counts
- **Filter by Tag**: Multi-select checkboxes with item counts
- **Filter by Flags**: 6 item flags checkboxes
- **Filter by Nominal Range**: Min/max spawn quantity slider
- **Filter by File**: Source file dropdown
- **AND/OR Logic Toggle**: Switch between filter logic modes
- **Active Filter Counter**: Shows number of active filters
- **Clear All Filters**: Reset all filters with one click

#### User Interface
- **Dark Theme**: Consistent dark color scheme throughout application
- **Two-Tab Layout**:
  - Types Editor: Main editing interface with filters and detail panel
  - Settings: Connection settings and backup management
- **Responsive Design**: Checkbox groups adapt to window size
- **Enhanced Spinboxes**: Larger up/down arrows (30px wide) for easier clicking
- **Toggle Switches**: iOS-style slider toggles for flag editing
  - Animated transitions
  - Blue when ON, gray when OFF
  - Clear ON/OFF text labels
- **Status Bar**: Real-time display of file counts, item counts, connection status
- **Detail Panel**: Right-side panel for editing selected items
  - Field validation
  - Modified items highlighted in green
  - Auto-updates when switching items

#### Help System
- **Built-in Documentation**: Help menu with comprehensive reference guide
  - Field descriptions with value ranges
  - Common workflows and use cases
  - Keyboard shortcuts
  - Troubleshooting tips
  - Correct flag explanations (especially Crafted flag)
- **About Dialog**: Version info and feature list

#### Data Validation
- **Field-Specific Limits**:
  - Nominal, Lifetime, Min, Restock: 0 to 99,999,999
  - Quantmin, Quantmax: -1 or 1-100 (percentages)
  - Cost: 0 to 100
  - Flags: 0 or 1
- **Smart Min Validation**: Min automatically capped at Nominal value
- **Duplicate Name Prevention**: Cannot create items with existing names
- **Empty Value Handling**: Graceful handling of invalid/empty values

#### SFTP Features
- **Connection Management**:
  - Host, port, username, password configuration
  - Mission path specification
  - Optional credential saving (encrypted)
  - Connection testing
  - Disconnect functionality
- **Settings Tab**: View and edit SFTP configuration
- **Status Display**: Connection info shown in status bar

#### Local Files Features
- **Folder Browser**: Select local mission folder
- **Direct File Access**: Read and write without network overhead
- **Settings Display**: Shows current mission folder path

#### Backup System
- **Automatic Creation**: Backup before every save
- **Timestamped Files**: Format YYYYMMDD_HHMMSS
- **Configurable Location**: User-specified backup directory
- **Backup Statistics**: View count and total size
- **Quick Access**: Open backup folder button
- **Cleanup Tools**: Remove old backups

#### File Support
- **types.xml**: Full read/write with all fields
- **cfgeconomycore.xml**: Parse file references for auto-loading
- **cfglimitsdefinition.xml**: Parse categories, usage, value, tags
- **cfglimitsdefinitionuser.xml**: Support for user-defined limit groups
- **Multiple Files**: Load all types files referenced in economy core

### Technical Details
- **Language**: Python 3.8+
- **GUI Framework**: PyQt5
- **SFTP Library**: Paramiko
- **Encryption**: Cryptography library for credential storage
- **Packaging**: PyInstaller for standalone executable
- **Platform**: Windows 10+

### Keyboard Shortcuts
- `Ctrl+S`: Save changes
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+F`: Focus search bar

### Known Limitations
- **Comment Precision**: Comments inside `<type>` elements (between fields) not preserved
- **Undo After Save**: Cannot undo past save point (intentional for data safety)
- **File Types**: Only edits types.xml files (not events, spawnable_types, etc.)
- **XML Declaration**: Always regenerated on save

### Files Included in Release
- `DayZTypesEditor.exe`: Main application executable
- All required DLLs and dependencies
- No installation required

### Configuration
- **Settings Location**: `C:\Users\[Username]\.dayz_types_editor\config.json`
- **Cache Location**: Same directory as config
- **Default Backup Location**: Same directory as config

---

## Version History

### Semantic Versioning
This project uses semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes or major redesigns
- **MINOR**: New features added in a backwards compatible manner
- **PATCH**: Backwards compatible bug fixes

### Version Tags
- `v1.0.0` - Initial stable release

---

## Contributing

If you'd like to contribute to this project:
1. Report bugs via GitHub Issues
2. Suggest features via GitHub Issues
3. Submit pull requests with improvements

---

## Credits

Created for DayZ server administrators and modders who need efficient bulk editing of types.xml files.

---

## Links
- [GitHub Repository](https://github.com/YOUR-USERNAME/DayZ-Types-Editor)
- [Latest Release](https://github.com/YOUR-USERNAME/DayZ-Types-Editor/releases/latest)
- [Report Issues](https://github.com/YOUR-USERNAME/DayZ-Types-Editor/issues)

---

[Unreleased]: https://github.com/Look4orion/DayZ-Types-Editor/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/Look4orion/DayZ-Types-Editor/releases/tag/v2.0.0
[1.0.1]: https://github.com/Look4orion/DayZ-Types-Editor/releases/tag/v1.0.1
[1.0.0]: https://github.com/Look4orion/DayZ-Types-Editor/releases/tag/v1.0.0
