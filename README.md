<<<<<<< HEAD
# DayZ Types Editor

A desktop application for editing and managing DayZ server types.xml files with SFTP support, map-based spawn visualization, and batch operations.

## Features

### Phase 1 & 2 (Completed)
- ✅ SFTP connection management with encrypted credential storage
- ✅ Automatic discovery of types.xml files via cfgEconomyCore.xml
- ✅ Settings management (SFTP, Map Profiles, Backups)
- ✅ Local backup system with cleanup
- ✅ Dark theme UI

### Phase 3 (Completed)
- ✅ Collapsible filter sidebar with multiple filter options
- ✅ Real-time debounced search
- ✅ Filter by: name, category, tags, usage, value, file path, nominal range
- ✅ AND/OR filter logic
- ✅ Item table with sorting and multi-select
- ✅ Detail editing panel for single items
- ✅ Edit all type attributes (nominal, lifetime, restock, min, quantmin, quantmax, cost, category, usage, tags, values)
- ✅ Modified items tracking and visual indication
- ✅ Active filter count display

### Phase 4 (Completed)
- ✅ Batch operations dialog
- ✅ Multiply values across filtered or selected items
- ✅ Field selection (nominal, min, max, restock, quantmin, quantmax)
- ✅ Live preview with side-by-side old→new values
- ✅ Shows first 100 changes with summary
- ✅ Confirmation before applying
- ✅ Applies to filtered items or multi-selected items
- ✅ Smart handling (skips -1 values, ensures min ≤ nominal)

### Coming Soon
- Phase 5: Save/Upload system with validation
- Phase 6: Loot map viewer with spawn locations

## Installation

### Requirements
- Python 3.8 or higher
- PyQt5
- paramiko (SFTP)
- cryptography (for credential encryption)
- Pillow (for map images)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### First Time Setup

1. **Connect to Server**
   - Go to File → Connect to Server
   - Enter your SFTP credentials:
     - Host: Your server IP
     - Port: SSH port (default 22)
     - Username: Your SSH username
     - Password: Your SSH password
     - Mission Path: Path to your mission folder (e.g., `/dayzserver/mpmissions/dayzOffline.deerisle/`)
   - Optionally check "Save credentials" to auto-connect next time

2. **Configure Map Profile** (Settings Tab)
   - Click "New" to create a map profile
   - Set Profile Name (e.g., "Deer Isle Winter")
   - Browse for map image (PNG/JPG)
   - Set world bounds (e.g., Deer Isle: 0-16384 for both X and Z)
   - Select coordinate origin (usually Bottom-Left for DayZ maps)
   - Click "Save Map Profile"

3. **Configure Backup Location** (Settings Tab)
   - Default: `~/DayZEditor/Backups`
   - Click "Browse..." to change location
   - Backups are created automatically before uploads

## Configuration Files

The application stores configuration in:
- `~/.dayz_types_editor/config.json` - Settings
- `~/.dayz_types_editor/.key` - Encryption key for credentials

## Project Structure

```
DayZTypesEditor/
├── main.py                 # Entry point
├── config/
│   ├── app_config.py      # Configuration management
│   └── sftp_manager.py    # SFTP operations
├── core/
│   ├── backup_manager.py  # Backup handling
│   ├── economy_parser.py  # cfgEconomyCore.xml parser
│   ├── limits_parser.py   # Limits definition parser
│   └── xml_parser.py      # types.xml parser
├── models/
│   ├── type_item.py       # Type item data model
│   └── types_file.py      # Types file container
└── ui/
    ├── main_window.py     # Main application window
    ├── types_editor.py    # Types editing tab
    ├── map_viewer.py      # Map visualization tab
    ├── settings_tab.py    # Settings tab
    └── sftp_dialog.py     # SFTP connection dialog
```

## Development Status

**Current Phase: Phase 4 Complete** ✅

Next up: Phase 5 - Save/Upload System with:
- XML validation before save
- Upload file selection dialog
- Automatic backup creation
- SFTP upload with progress
- Success/error reporting

## Notes

- The app requires network access to connect to your SFTP server
- All types.xml files are loaded into memory on connect
- Changes are tracked but not saved until explicitly uploaded
- Backups are created locally before any upload
- Window position and size are remembered between sessions

## Troubleshooting

### Cannot connect to SFTP server
- Verify your server IP and port
- Check firewall settings
- Ensure SSH/SFTP is enabled on your server
- Verify mission path exists on server

### Map not displaying correctly
- Check that image file exists and is valid PNG/JPG
- Verify world bounds match your map's coordinate system
- Try different coordinate origin settings

### Backups filling up disk
- Use Settings → Backup Management → Clean Up Old Backups
- This keeps only the last 10 backups per file
=======
[![Release](https://img.shields.io/github/v/release/Look4orion/DayZ-Types-Editor)](https://github.com/Look4orion/DayZ-Types-Editor/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/YOUR-Look4orion/DayZ-Types-Editor/releases)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A comprehensive desktop application for editing DayZ `types.xml` files with support for both SFTP (remote server) and local file access.

![DayZ Types Editor Screenshot](docs/screenshot.png)

## Features

### Core Functionality
- **Dual File Source Support** - Connect via SFTP or work with local files
- **Multi-file Editing** - Load and edit multiple types.xml files simultaneously
- **Smart Filtering** - Filter by name, category, usage, value, tags, flags, and nominal range
- **Batch Operations** - Modify multiple items at once with live preview
- **New Item Creation** - Add type entries with duplicate name detection
- **Undo/Redo** - Track up to 50 changes
- **Auto Backup** - Automatic timestamped backups before saving
- **File Caching** - 80-90% faster load times on subsequent opens
- **Built-in Help** - Quick reference guide in Help menu

### User Interface
- Dark theme throughout
- Enhanced spinboxes with larger arrows
- Toggle switches for flag editing
- Real-time validation
- Responsive design

## Download

**[Download Latest Release](https://github.com/YOUR-USERNAME/DayZ-Types-Editor/releases/latest)**

### Windows
1. Download `DayZTypesEditor-v1.0-Windows.zip`
2. Extract to any folder
3. Run `DayZTypesEditor.exe`
4. No installation required

## Quick Start

### SFTP Connection
1. Launch the application
2. Select "Connect to SFTP Server"
3. Enter server details:
   - Host (IP or domain)
   - Port (default: 22)
   - Username & Password
   - Mission folder path
4. Click "Connect"

### Local Files
1. Launch the application
2. Select "Use Local Files"
3. Browse to your mission folder
4. Click "Connect"

### Editing Items
1. Use filters to find items
2. Select item to edit in detail panel
3. Modify values
4. Click "Apply Changes"
5. Save when ready (Ctrl+S)

### Batch Editing
1. Filter to desired items
2. Click "Batch Operations"
3. Check fields to modify
4. Set operation mode (Multiply or Set Value)
5. Preview changes
6. Click "Apply Changes"

### Creating New Items
1. Click "New Item" in toolbar
2. Enter unique item name
3. Select target file
4. Configure all fields
5. Click "Create Item"

## Field Reference

### Numeric Fields
- **Nominal** - Maximum number in world (0-99,999,999)
- **Lifetime** - Seconds before despawn (0-99,999,999)
- **Min** - Minimum to trigger respawn (0-Nominal)
- **Restock** - Seconds before respawn (0-99,999,999)
- **Quantmin** - Min stack percentage (-1 or 1-100)
- **Quantmax** - Max stack percentage (-1 or 1-100)
- **Cost** - Spawn priority/rarity (0-100)

### Item Flags
- **Count in Cargo** - Count items in containers toward nominal
- **Count in Hoarder** - Count items in stashes toward nominal
- **Count in Map** - Count spawned items toward nominal
- **Count in Player** - Count items on players toward nominal
- **Crafted** - Item can ONLY be crafted (will NOT spawn naturally)
- **Deloot** - Remove from all natural spawns

### Multi-Select
- **Usage** - Spawn locations (Military, Police, Farm, etc.)
- **Value** - Tier/rarity (Tier1=common, Tier4=rare)
- **Tag** - Spawn restrictions (floor, shelves, etc.)
- **Category** - Item classification

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save changes |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+F` | Focus search |

## Requirements

- Windows 10 or later
- No additional software needed (standalone executable)

## Building from Source

### Prerequisites
- Python 3.8 or later
- pip package manager

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/DayZ-Types-Editor.git
cd DayZ-Types-Editor

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build
build.bat

# Executable in dist/DayZTypesEditor/
```

## Configuration

Settings are stored in:
```
C:\Users\[Username]\.dayz_types_editor\
├── config.json          # Application settings
├── cache/               # File cache
└── backups/             # Automatic backups
```

## Troubleshooting

### Items Not Spawning?
Check:
- Nominal > 0
- Min > 0
- Crafted = 0 (unless craft-only)
- Deloot = 0 (unless event-only)
- At least one Usage flag set
- At least one Value flag set

### Connection Issues (SFTP)
- Verify credentials
- Check firewall settings
- Test connection in Settings tab
- Ensure mission path is correct

### File Loading Errors
- Check XML syntax
- View error dialog for details
- Verify file names match cfgeconomycore.xml

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- [Report Issues](https://github.com/Look4orion/DayZ-Types-Editor/issues)
- [View Documentation](https://github.com/Look4orion/DayZ-Types-Editor/wiki)
- [Latest Release](https://github.com/Look4orion/DayZ-Types-Editor/releases/latest)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Created for DayZ server administrators and modders who need efficient bulk editing of types.xml files.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

[![Release](https://img.shields.io/github/v/release/Look4orion/DayZ-Types-Editor)](https://github.com/Look4orion/DayZ-Types-Editor/releases)
>>>>>>> ae17e1d3df9de3bae6cafb0adce4246ccdab1f99
