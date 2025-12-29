# Building Standalone Executable

## Prerequisites
- Python 3.8+ installed
- All requirements installed: `pip install -r requirements.txt`

## Quick Build (Windows)

### Option 1: Automatic Build (Recommended)
1. Double-click `build.bat`
2. Wait for build to complete (may take 3-5 minutes)
3. Executable will be in `dist/DayZTypesEditor.exe`

### Option 2: Manual Build
```cmd
pip install pyinstaller
pyinstaller DayZTypesEditor.spec
```

## Build Outputs

**Single Folder (Default):**
- Output: `dist/DayZTypesEditor/` folder
- Contains: `DayZTypesEditor.exe` + dependencies
- Distribution: Share entire folder (~100-150 MB)
- Startup: Fast

**Single File (Alternative):**
Edit `DayZTypesEditor.spec`, change `exe = EXE(` section to add:
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DayZTypesEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # <-- ADD THIS LINE
    icon=None,
)
```

Then rebuild. This creates a single ~80 MB .exe file but is slower to start.

## Testing the Executable

1. Navigate to `dist/DayZTypesEditor/`
2. Double-click `DayZTypesEditor.exe`
3. Test all features:
   - SFTP connection
   - File loading
   - Item editing
   - Batch operations
   - Save functionality
   - Undo/Redo

## Common Issues

### "Missing DLL" Error
**Solution:** Use the folder distribution (default), not single-file mode

### Antivirus False Positive
**Solution:** Add exception for the .exe file. PyInstaller executables sometimes trigger antivirus.

### Slow Startup
**Solution:** 
- First launch is always slower (Windows security scan)
- Use folder distribution instead of single-file
- Exclude from Windows Defender real-time scanning

### "Failed to execute script" Error
**Solution:** 
- Run build.bat again
- Check console output for errors
- Ensure all dependencies are installed

## Distribution

### For Single User:
1. Zip the `dist/DayZTypesEditor/` folder
2. Send the zip file
3. User extracts and runs `DayZTypesEditor.exe`

### For Multiple Users:
1. Create installer (optional, see below)
2. Or distribute as zip with README

## Optional: Create Installer (Advanced)

Use Inno Setup or NSIS to create a proper installer:

**Inno Setup (Recommended):**
1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create script pointing to `dist/DayZTypesEditor/` folder
3. Compile installer

**Benefits:**
- Professional installation experience
- Start menu shortcuts
- Uninstaller
- File associations (optional)

## File Size Expectations

**Folder Distribution:**
- Total: ~100-150 MB
- Main exe: ~30-40 MB
- DLLs and dependencies: ~60-110 MB

**Single File:**
- Single exe: ~80-100 MB
- Slower startup (extracts to temp on each run)

## Configuration Storage

The executable will store configuration in:
```
C:\Users\[Username]\.dayz_types_editor\config.json
```

This persists between runs and includes:
- SFTP credentials (encrypted)
- File cache
- Window position/size
- Recent connections

## Security Notes

**Credentials:**
- Stored encrypted using Fernet (cryptography library)
- Key stored in `.dayz_types_editor/.key`
- Safe to distribute executable (no credentials included)

**File Cache:**
- Cached files stored in config.json
- Can grow to several MB with many files
- Clear via Settings (future feature) or delete config.json

## Performance

**Startup Time:**
- Folder distribution: 2-4 seconds
- Single file: 5-10 seconds (first run slower)

**Memory Usage:**
- Idle: ~100-150 MB
- With 61 files loaded: ~200-300 MB
- Batch operations: +50-100 MB temporary

## Troubleshooting Build Issues

**Import Errors:**
```
Add missing imports to hiddenimports in .spec file
```

**Missing Modules:**
```
pip install --upgrade -r requirements.txt
pyinstaller --clean DayZTypesEditor.spec
```

**Build Fails:**
```
1. Delete build/ and dist/ folders
2. Run: pip install --upgrade pyinstaller
3. Try again
```

## Alternative: Use Python

If building executable is problematic, users can run directly with Python:

```cmd
pip install -r requirements.txt
python main.py
```

Requires Python 3.8+ installed on user's machine.
