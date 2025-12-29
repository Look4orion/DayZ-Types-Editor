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
