# Changelog

All notable changes to DayZ Types Editor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Import/export presets for batch operations
- Search and replace functionality
- Dark/light theme toggle
- Export to CSV/Excel
- Multi-language support

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

[Unreleased]: https://github.com/YOUR-USERNAME/DayZ-Types-Editor/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR-USERNAME/DayZ-Types-Editor/releases/tag/v1.0.0
