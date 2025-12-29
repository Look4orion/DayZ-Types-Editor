[![Release](https://img.shields.io/github/v/release/Look4orion/DayZ-Types-Editor)](https://github.com/Look4orion/DayZ-Types-Editor/releases)

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

[![Release](https://img.shields.io/github/v/release/Look4orion/DayZ-Types-Editor)](https://github.com/Look4orion/DayZ-Types-Editor/releases)
