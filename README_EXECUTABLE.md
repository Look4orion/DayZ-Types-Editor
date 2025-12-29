# DayZ Types Editor - Standalone Executable

## Quick Start

1. **Extract** the entire folder to your preferred location
2. **Run** `DayZTypesEditor.exe`
3. **Connect** to your server (SFTP) or open local mission folder

## First Launch

On first launch, you'll see a connection dialog:

**SFTP Mode (Remote Server):**
- Host: Your server IP
- Port: Usually 22 or custom SFTP port
- Username: Your SFTP username
- Password: Your SFTP password
- Mission Path: e.g., `/mpmissions/yourmap.map`

**Local Mode:**
- Browse to your local mission folder
- Must contain `cfgeconomycore.xml`

## Features

### Edit Items
- View all 7000+ items from your types.xml files
- Edit nominal, lifetime, restock, min, quantities, cost
- Modify usage flags, value flags, and tags
- Real-time filtering and search

### Batch Operations
- Select multiple items via filters
- Multiply values (e.g., increase all nominal by 1.5x)
- Apply changes to hundreds of items at once
- Preview changes before applying

### Save Changes
- **Save Button** or **Ctrl+S** or **File > Save Changes**
- Select which files to save
- Automatic backups created
- User tags intelligently preserved

### Undo/Redo
- **Undo Button** or **Ctrl+Z** - Undo last change
- **Redo Button** or **Ctrl+Y** - Redo last undone change
- Works with single edits and batch operations
- History clears after save (intentional safety)

### File Caching
- Loads much faster after first launch
- Only downloads changed files from server
- Automatically managed

## System Requirements

- **OS:** Windows 10 or later
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk:** 500 MB free space
- **Network:** For SFTP mode only

## Configuration

Settings stored in:
```
C:\Users\[YourUsername]\.dayz_types_editor\
```

Contains:
- Saved SFTP credentials (encrypted)
- File cache
- Window size/position

## Antivirus Notice

Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. The application is safe to use.

**If blocked:**
1. Add exception in your antivirus
2. Or run the Python version directly (see BUILD_INSTRUCTIONS.md)

## Support

For issues or questions:
1. Check BUILD_INSTRUCTIONS.md for troubleshooting
2. Verify SFTP credentials are correct
3. Ensure mission folder contains cfgeconomycore.xml
4. Check that you have write permissions to save files

## Backups

Before each save, the editor creates automatic backups in:
- SFTP mode: On your local machine
- Local mode: In the same directory

**Backup location:** Configured in Settings (default: `Documents\DayZEditor\Backups`)

## Tips

1. **Use Filters** - Filter before batch operations to target specific items
2. **Test Small** - Try changes on a few items before applying to hundreds
3. **Save Often** - Undo history clears after save, so commit your changes
4. **Check Cache Stats** - Status bar shows how many files were cached vs downloaded

## Known Limitations

1. **Case Sensitivity** - File paths automatically handle case mismatches
2. **User Tags** - Automatically preserved when unchanged, expanded when modified
3. **Undo Past Save** - Cannot undo past last save (by design for safety)

## Version Info

This build includes:
- Full save/upload system
- File caching for faster loads
- Undo/Redo functionality
- Batch operations
- User tag preservation
- Case-insensitive path handling

## Updates

To get updates:
1. Download new version
2. Extract to new folder (or overwrite old one)
3. Your settings/cache are preserved (stored separately)

---

**Note:** This is a standalone executable and doesn't require Python to be installed on your system.
