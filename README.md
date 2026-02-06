# DayZ Types Editor

A comprehensive desktop application for editing and managing DayZ server economy files with SFTP support, including types.xml, cfgspawnabletypes.xml, and cfgrandompresets.xml.

## Features

### Core Capabilities
- ✅ **Types Editor** - Full control over item spawn economy (types.xml)
- ✅ **Spawnable Types Editor** - Manage item attachments and cargo presets (cfgspawnabletypes.xml)
- ✅ **Random Presets Editor** - Create and edit cargo/attachment preset definitions (cfgrandompresets.xml)
- ✅ **SFTP & Local File Support** - Work with remote servers or local files
- ✅ **Automatic File Discovery** - Loads all economy files including vanilla db/types.xml and cfgspawnabletypes.xml
- ✅ **Unified Save System** - Save multiple modified files together with validation
- ✅ **Dark Theme UI** - Comfortable editing experience
- ✅ **Undo/Redo System** - Track changes across all tabs

### Types Editor
- ✅ Multi-file editing (all types.xml files from cfgeconomycore.xml)
- ✅ Advanced filtering (name, category, tags, usage, value, flags, nominal range, file)
- ✅ AND/OR filter logic
- ✅ Batch operations (multiply/set values for multiple items)
- ✅ Individual item editing with live validation
- ✅ New item creation with duplicate detection
- ✅ Item flags: Count in Cargo/Hoarder/Map/Player, Crafted, Deloot

### Spawnable Types Editor
- ✅ Edit cargo and attachments blocks for any spawnable type
- ✅ Preset-based blocks (reference cfgrandompresets.xml)
- ✅ Chance-based blocks (inline item definitions with probabilities)
- ✅ Preset tooltips showing contents on hover
- ✅ Full CRUD operations (create, edit, delete blocks and items)
- ✅ Item reordering (spawn priority control)
- ✅ Two-step guided workflow for chance-based blocks
- ✅ Hoarder and Damage properties per type
- ✅ Filter by file, properties, or search
- ✅ Undo/redo support for all operations

### Random Presets Editor
- ✅ Create and manage cargo presets
- ✅ Create and manage attachments presets
- ✅ Set preset-level and item-level chance values
- ✅ Add/edit/remove items from presets
- ✅ Item name validation against types.xml
- ✅ Filter presets by name or type
- ✅ Undo/redo support
- ✅ Validation prevents duplicate names

### File Management
- ✅ Automatic discovery of vanilla files (db/types.xml, cfgspawnabletypes.xml)
- ✅ Parse all files referenced in cfgeconomycore.xml
- ✅ Comment preservation in XML files
- ✅ File caching system (80-90% faster subsequent loads)
- ✅ Automatic timestamped backups before saves
- ✅ Modified file tracking across all tabs

## Installation

### Requirements
- Python 3.8 or higher
- PyQt5
- paramiko (SFTP)
- cryptography (for credential encryption)

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
   - Go to File → Connect to Server (or Open Local Folder)
   - **For SFTP:**
     - Host: Your server IP
     - Port: SSH port (default 22)
     - Username: Your SSH username
     - Password: Your SSH password
     - Mission Path: Path to your mission folder (e.g., `/dayzserver/mpmissions/dayzOffline.deerisle/`)
   - **For Local Files:**
     - Browse to your local mission folder
   - Optionally check "Save credentials" to auto-connect next time

2. **Configure Backup Location** (Settings Tab)
   - Default: `~/.dayz_types_editor/backups`
   - Click "Browse..." to change location
   - Backups are created automatically before saves

### Working with Files

The editor automatically loads:
- All `types.xml` files referenced in `cfgeconomycore.xml`
- Vanilla `db/types.xml` (if it exists)
- All `cfgspawnabletypes.xml` files referenced in `cfgeconomycore.xml`
- Vanilla `cfgspawnabletypes.xml` (if it exists)
- `cfgrandompresets.xml` (if it exists)

### Editing Types (Types Editor Tab)

1. **Find Items:**
   - Use search bar for names
   - Apply filters (category, usage, value, tag, flags, nominal range)
   - Toggle AND/OR logic for complex filters

2. **Edit Single Item:**
   - Select item in table
   - Edit fields in detail panel
   - Changes tracked automatically

3. **Batch Edit:**
   - Filter or multi-select items
   - Click "Batch Operations"
   - Choose operation (Multiply/Set Value)
   - Preview changes before applying

4. **Create New Item:**
   - Click "New Item"
   - Fill in all fields
   - Duplicate names are detected

### Editing Spawnable Types (Spawnable Types Tab)

1. **Find Types:**
   - Search by name
   - Filter by file or properties (hoarder, damage, cargo, attachments)

2. **Edit Cargo/Attachments:**
   - Select type in list
   - Add/Edit/Delete blocks (preset-based or chance-based)
   - Add/Edit/Delete items in chance-based blocks
   - Reorder items (controls spawn priority)
   - Hover over presets to see contents

3. **Block Types:**
   - **Preset blocks:** Reference a preset from cfgrandompresets.xml
   - **Chance blocks:** Define items inline with individual chances

### Editing Presets (Random Presets Tab)

1. **Create Preset:**
   - Choose Cargo or Attachments
   - Click "Add Preset"
   - Set name and preset chance
   - Add items with individual chances

2. **Edit Preset:**
   - Select preset in list
   - Edit name or chance
   - Add/Edit/Remove items

### Saving Changes

- File → Save Changes (Ctrl+S)
- Review modified files
- Select files to save
- Backup created automatically
- Changes uploaded (SFTP) or saved (Local)

## Configuration Files

The application stores configuration in:
- `~/.dayz_types_editor/config.json` - Settings
- `~/.dayz_types_editor/.key` - Encryption key for credentials

## Project Structure

```
DayZTypesEditor/
├── main.py                          # Entry point
├── config/
│   ├── app_config.py               # Configuration management
│   ├── sftp_manager.py             # SFTP operations
│   └── local_file_manager.py       # Local file operations
├── core/
│   ├── backup_manager.py           # Backup handling
│   ├── economy_parser.py           # cfgEconomyCore.xml parser
│   ├── limits_parser.py            # Limits definition parser
│   ├── xml_parser.py               # types.xml parser
│   ├── spawnabletypes_parser.py    # cfgspawnabletypes.xml parser
│   ├── spawnabletypes_writer.py    # cfgspawnabletypes.xml writer
│   ├── random_presets_parser.py    # cfgrandompresets.xml parser
│   └── random_presets_writer.py    # cfgrandompresets.xml writer
├── models/
│   ├── type_item.py                # Type item data model
│   ├── types_file.py               # Types file container
│   ├── spawnable_type.py           # Spawnable type data model
│   ├── spawnabletypes_file.py      # Spawnable types file container
│   └── random_preset.py            # Random preset data model
└── ui/
    ├── main_window.py              # Main application window
    ├── types_editor_tab.py         # Types editing tab
    ├── spawnable_types_tab.py      # Spawnable types tab
    ├── random_presets_tab.py       # Random presets tab
    ├── settings_tab.py             # Settings tab
    ├── sftp_dialog.py              # SFTP connection dialog
    └── dialogs/
        ├── add_block_dialog.py     # Add cargo/attachments block
        ├── edit_block_dialog.py    # Edit existing block
        ├── add_item_dialog.py      # Add item to block/preset
        ├── edit_item_dialog.py     # Edit existing item
        └── add_preset_dialog.py    # Add new preset
```

## Current Version

**v2.0.0** - Major Feature Release ✅

Complete economy file editing suite with:
- Types Editor (types.xml)
- Spawnable Types Editor (cfgspawnabletypes.xml)
- Random Presets Editor (cfgrandompresets.xml)
- Unified save system
- Automatic vanilla file discovery

## Notes

- The app requires network access for SFTP connections
- All economy files are loaded into memory on connect
- Changes are tracked but not saved until explicitly committed
- Backups are created automatically before any save
- Window position and size are remembered between sessions
- Undo/redo works across all tabs (up to 50 changes)
- Vanilla files (db/types.xml, cfgspawnabletypes.xml) are auto-detected

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
