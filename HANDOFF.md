# DayZ Types Editor - Development Handoff Document

## Project Overview

**Application:** DayZ Types Editor - Desktop application for editing DayZ server types.xml files  
**Technology:** Python + PyQt5  
**Current Status:** Phases 1-4 Complete, Ready for Phase 5 (Save/Upload System)  
**Latest Build:** DayZTypesEditor_BatchColors.zip  
**Token Usage (Previous Session):** 121k/190k (64%)

---

## Quick Start for New Developer

**What Works:**
- ✅ SFTP and Local file modes
- ✅ File loading with progress dialog
- ✅ Error handling with retry functionality
- ✅ Filter system (search, category, tags, usage, value, nominal range)
- ✅ Item editing (single and batch operations)
- ✅ User tag expansion from cfglimitsdefinitionuser.xml
- ✅ 2-column grid layout for filters
- ✅ Dark theme UI throughout

**What's Needed:**
- ⏳ Save/Upload system (Phase 5)
- ⏳ User tag reconstruction on save
- ⏳ File selection dialog
- ⏳ Upload progress with error handling
- ⏳ Map viewer (Phase 6 - future)

---

## Critical Design Decisions

### 1. User Tag System (MOST IMPORTANT!)

User tags are groups defined in `cfglimitsdefinitionuser.xml`:

```xml
<lists>
  <user name="TownVillage">
    <usage name="Town"/>
    <usage name="Village"/>
  </user>
  <user name="MilitaryPolice">
    <usage name="Military"/>
    <usage name="Police"/>
  </user>
</lists>
```

#### On Load (Already Implemented):
1. Parse `<user>` tags from types.xml
2. Look up definition in limits_parser.user_definitions
3. Expand to individual usage/value/tag items
4. Store original user tag name in `TypeItem.original_users`
5. Display expanded items in UI

#### On Save (NEEDS IMPLEMENTATION):
**Smart Reconstruction Rules:**

```python
# Example: Original had <user name="TownVillage"/> which expands to Town, Village

# Case 1: No changes
Current usages: [Town, Village]
Export: <user name="TownVillage"/>

# Case 2: User added Industrial
Current usages: [Town, Village, Industrial]
Export: <user name="TownVillage"/>
        <usage name="Industrial"/>

# Case 3: User removed Village
Current usages: [Town]
Export: <usage name="Town"/>  # Can't use user tag anymore

# Case 4: User removed Village, added Industrial  
Current usages: [Town, Industrial]
Export: <usage name="Town"/>
        <usage name="Industrial"/>
```

**Implementation Location:** `TypeItem.to_xml_element(limits_parser)` in `/models/type_item.py`

**Current Implementation:** Partially done but needs verification of logic

---

### 2. Data Model - TypeItem Fields

```python
@dataclass
class TypeItem:
    # CRITICAL: There is NO "max" field!
    name: str
    nominal: int = 0
    lifetime: int = 3600
    restock: int = 0
    min: int = 0              # NOT "max"!
    quantmin: int = -1
    quantmax: int = -1
    cost: int = 100
    category: Optional[str] = None
    usage: List[str] = field(default_factory=list)
    value: List[str] = field(default_factory=list)
    tag: List[str] = field(default_factory=list)
    original_users: List[str] = field(default_factory=list)  # Track user tags
    source_file: str = ""
    modified: bool = False
```

**Common Mistake:** Batch operations had a "max" checkbox - this is wrong! Field is called "min".

---

### 3. XML File Structures

#### cfglimitsdefinition.xml (Actual Structure)
```xml
<lists>
  <categories>
    <category name="tools"/>
    <category name="weapons"/>
  </categories>
  <usageflags>
    <usage name="Military"/>
    <usage name="Town"/>
  </usageflags>
  <valueflags>
    <value name="Tier1"/>
    <value name="Tier2"/>
  </valueflags>
  <tags>
    <tag name="floor"/>
    <tag name="shelves"/>
  </tags>
</lists>
```

**IMPORTANT:** Structure is direct children, NOT `<list name="category">` wrapper!

#### cfglimitsdefinitionuser.xml
```xml
<lists>
  <user name="GroupName">
    <usage name="..."/>
    <value name="..."/>
    <tag name="..."/>
    <category name="..."/>  <!-- Rare but possible -->
  </user>
</lists>
```

#### types.xml (What we're editing)
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<types>
  <type name="ItemName">
    <nominal>10</nominal>
    <min>5</min>
    <lifetime>3600</lifetime>
    <restock>1800</restock>
    <quantmin>-1</quantmin>
    <quantmax>-1</quantmax>
    <cost>100</cost>
    <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
    <category name="weapons"/>
    <user name="TownVillage"/>  <!-- This should be preserved if unchanged -->
    <usage name="Industrial"/>   <!-- Extra usage beyond user group -->
    <value name="Tier3"/>
    <tag name="floor"/>
  </type>
</types>
```

---

### 4. File Manager Abstraction

Both `SFTPManager` and `LocalFileManager` implement same interface:

```python
# In main_window.py:
self.file_manager  # Set to either SFTP or Local in startup dialog

# Common methods:
file_manager.connect(...)       # SFTP: host/port/etc, Local: path
file_manager.is_connected()     # bool
file_manager.read_file(path)    # str
file_manager.write_file(path, content)  # None
file_manager.disconnect()
file_manager.get_connection_info()  # str for status bar
```

**Phase 5 Note:** Use `file_manager.write_file()` for both modes!

---

### 5. XML Parsing Rules

**Robustness Requirements:**
```python
# Handle comments before XML declaration
xml_content = "<!-- Comment -->\n<?xml version='1.0'?>\n<types>..."
# Strip comments before parsing

# Empty integer fields
<nominal></nominal>  # Use safe_int() → defaults to 0

# Malformed individual elements
# Skip bad <type>, continue with rest - don't crash entire file

# Case-insensitive paths
"custom/Lootchests/file.xml" should match "custom/LootChests/file.xml"
# Check EACH directory component, not just filename
```

**Current Implementation:** All handled in `/core/xml_parser.py`

---

### 6. UI Styling Rules

#### Table Colors (CRITICAL - Common Bug!)
```python
# ALWAYS use this stylesheet for tables:
table.setStyleSheet("""
    QTableWidget {
        background-color: #1e1e1e;
        alternate-background-color: #252526;
        gridline-color: #333;
    }
    QTableWidget::item {
        padding: 4px;
    }
    QTableWidget::item:selected {
        background-color: #264f78;
    }
""")
```

**DO NOT** use default alternating colors - they're black/white and unreadable!

#### Filter Sidebar
- Width: 350-450px (not 250px!)
- Checkboxes: QGridLayout with 2 columns
- Item counts: `Military (892)` format
- Store actual names in properties: `cb.setProperty('usage_name', usage)`

#### Debounced Search
```python
# 250ms delay after last keystroke
self.search_timer = QTimer()
self.search_timer.setSingleShot(True)
self.search_timer.timeout.connect(self.apply_filters)
self.search_timer.setInterval(250)
```

---

## File Structure

```
DayZTypesEditor/
├── main.py                      # Entry point
├── core/
│   ├── xml_parser.py           # TypesParser.parse(xml, path, limits_parser)
│   ├── limits_parser.py        # parse(), parse_user_definitions(), expand_user()
│   ├── economy_parser.py       # Parse cfgeconomycore.xml for file list
│   └── backup_manager.py       # create_backup(filename, content)
├── models/
│   ├── type_item.py            # TypeItem dataclass + to_xml_element()
│   └── types_file.py           # TypesFile with get_modified_items()
├── config/
│   ├── app_config.py           # JSON config storage
│   ├── sftp_manager.py         # SFTP operations
│   └── local_file_manager.py  # Local file operations
└── ui/
    ├── main_window.py          # Main window with tabs
    ├── types_editor.py         # Main editing interface
    ├── batch_ops.py            # Batch operations dialog
    ├── startup_dialog.py       # SFTP vs Local choice
    ├── loading_progress_dialog.py
    ├── file_error_dialog.py
    ├── sftp_dialog.py
    ├── settings_tab.py
    └── map_viewer.py           # Placeholder for Phase 6
```

---

## Important Code Locations

### Loading Flow
```python
# main_window.py
def load_server_data():
    load_limits_definitions()         # Parse cfglimitsdefinition.xml + user
    economy_xml = read cfgeconomycore.xml
    types_file_paths = EconomyParser.parse(economy_xml)
    load_types_files_with_progress(types_file_paths)

def load_types_files_with_progress():
    # Shows progress dialog
    # Calls TypesParser.parse(xml, path, limits_parser) for each file
    # Tracks errors
    # Shows error dialog with retry option
```

### Limits Parser Usage
```python
# limits_parser.py
limits_parser = LimitsParser()
limits_parser.parse(xml_content)                    # Main definitions
limits_parser.parse_user_definitions(xml_content)   # User groups
expanded = limits_parser.expand_user('TownVillage') # Returns dict
# expanded = {'usage': ['Town', 'Village'], 'value': [], 'tag': [], 'category': []}
```

### Type Parsing with User Expansion
```python
# xml_parser.py - _parse_type_element()
for user_elem in elem.findall('user'):
    user_name = user_elem.get('name')
    original_users.append(user_name)  # Track for save
    
    if limits_parser:
        expanded = limits_parser.expand_user(user_name)
        usage_list.extend(expanded.get('usage', []))
        value_list.extend(expanded.get('value', []))
        # etc...
```

---

## Phase 5 Implementation Guide

### Step 1: TypesFile XML Export
**File:** `/models/types_file.py`

```python
def to_xml(self, limits_parser=None) -> str:
    """Generate XML content from items"""
    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    lines.append('<types>')
    
    for item in self.items:
        lines.append(item.to_xml_element(limits_parser))
    
    lines.append('</types>')
    return '\n'.join(lines)
```

**Note:** `item.to_xml_element(limits_parser)` already implemented - verify user tag logic!

### Step 2: File Selection Dialog
**New File:** `/ui/save_dialog.py`

```python
class SaveDialog(QDialog):
    """Select which modified files to save"""
    
    def __init__(self, parent, types_files: List[TypesFile]):
        # Show checkboxes for each file with modifications
        # Display: filename + (X items modified)
        # Buttons: Select All, Select None, Save, Cancel
```

### Step 3: Save Handler in Main Window
**File:** `/ui/main_window.py`

```python
def save_changes(self):
    """Save modified files"""
    # Get modified files
    modified_files = [tf for tf in self.types_files if tf.get_modified_items()]
    
    if not modified_files:
        QMessageBox.information("No changes to save")
        return
    
    # Show file selection dialog
    dialog = SaveDialog(self, modified_files)
    if not dialog.exec_():
        return
    
    selected_files = dialog.get_selected_files()
    
    # Save each file
    self.save_files_with_progress(selected_files)
```

### Step 4: Save with Progress
**File:** `/ui/main_window.py`

```python
def save_files_with_progress(self, files_to_save):
    """Save files with progress dialog"""
    progress = QProgressDialog("Saving files...", "Cancel", 0, len(files_to_save))
    progress.setModal(True)
    
    errors = []
    
    for i, types_file in enumerate(files_to_save):
        progress.setValue(i)
        if progress.wasCanceled():
            break
        
        try:
            # Generate XML
            xml_content = types_file.to_xml(self.limits_parser)
            
            # Create backup
            self.backup_manager.create_backup(types_file.path, types_file.original_content)
            
            # Write file
            self.file_manager.write_file(types_file.path, xml_content)
            
            # Clear modified flags
            for item in types_file.items:
                item.modified = False
        
        except Exception as e:
            errors.append({'file': types_file.path, 'error': str(e)})
    
    progress.close()
    
    # Show results
    self.show_save_results(len(files_to_save) - len(errors), errors)
```

### Step 5: Results Dialog
**File:** `/ui/main_window.py` or new dialog

```python
def show_save_results(self, success_count, errors):
    """Show save results with error details"""
    if errors:
        # Show dialog similar to file_error_dialog
        # Allow retry option
    else:
        QMessageBox.information(f"Successfully saved {success_count} file(s)")
    
    # Refresh UI
    self.update_status_bar()
```

---

## Testing Checklist for Phase 5

### User Tag Preservation
- [ ] Load file with `<user name="TownVillage"/>`
- [ ] Verify it shows as Town + Village in UI
- [ ] Save without changes → Should keep `<user>` tag
- [ ] Add Industrial, save → Should have `<user>` + `<usage name="Industrial"/>`
- [ ] Remove Village, save → Should expand to `<usage name="Town"/>` only
- [ ] Verify XML output is valid and parseable

### Save Functionality
- [ ] Modify multiple files
- [ ] File selection dialog shows all modified files
- [ ] Can select/deselect files
- [ ] Progress dialog appears
- [ ] Can cancel save operation
- [ ] Backups created before saves
- [ ] SFTP mode uploads correctly
- [ ] Local mode writes to disk correctly
- [ ] Error handling for write failures
- [ ] Success message shows correct count
- [ ] Modified flags cleared after successful save

### Edge Cases
- [ ] Save with no modifications → Show message
- [ ] Save fails mid-way → Show partial success + errors
- [ ] Cancel during save → Don't mark items as unmodified
- [ ] Network error in SFTP mode → Proper error message
- [ ] Disk full in Local mode → Proper error message
- [ ] Invalid XML generated → Catch before write

---

## Known Bugs (Fixed - Watch for Regression)

1. ✅ Import QGridLayout for filter layouts
2. ✅ No "max" field in TypeItem (use "min")
3. ✅ Limits parser uses direct children not `<list name="...">`
4. ✅ Table colors - must set stylesheet
5. ✅ Case-insensitive paths - check each directory
6. ✅ Batch operations field names
7. ✅ XML comments before declaration
8. ✅ Empty integer values in XML

---

## Development Workflow Preferences

From previous developer conversations:

1. **Ask before coding** - Request clarification when uncertain
2. **Guide, don't guess** - If info is missing, ask for it
3. **Brief explanations** - Unless detail is requested
4. **No folder structures** - Just describe structure, don't create
5. **Test systematically** - One feature at a time

---

## Token Budget Strategy

**Previous Session:** 121k / 190k used (64%)  
**Fresh Chat Starts With:** 190k tokens  

**Estimated Requirements:**
- Phase 5 (Save/Upload): ~15-20k tokens
- Phase 6 (Map Viewer): ~25-30k tokens  
- Bug fixes & polish: ~10-15k tokens

**Recommendation:** Complete Phase 5 in new chat, assess remaining budget for Phase 6

---

## Quick Reference - Common Tasks

### Add New Field to TypeItem
1. Update `@dataclass` in `/models/type_item.py`
2. Update `clone()` method
3. Update `to_xml_element()` method
4. Update XML parser in `/core/xml_parser.py`
5. Update UI in `/ui/types_editor.py` detail panel
6. Update batch operations if numeric field

### Add New Filter
1. Update `/ui/types_editor.py` create_filter_sidebar()
2. Add to populate_filter_options()
3. Add logic to apply_filters()
4. Update clear_filters()

### Fix Table Colors
1. Find table creation
2. Add stylesheet with #1e1e1e / #252526
3. Test alternating colors

---

## Contact Points for User

**User's Environment:**
- Windows machine
- Testing with local DayZ server files
- ~61 types files, 7000+ items
- Has custom XML structures with comments
- Case-sensitive path issues (Lootchests vs LootChests)

**User's Files to Test With:**
- cfglimitsdefinition.xml (attached in previous session)
- cfglimitsdefinitionuser.xml (attached in previous session)
- Various types files with edge cases

---

## First Message for New Chat

```
I'm continuing development of a DayZ Types Editor desktop app. Phases 1-4 are complete:
- ✅ SFTP and Local file modes with startup dialog
- ✅ Robust file loading (handles comments, empty values, case issues)
- ✅ Filter system with 2-column grid layout
- ✅ Single and batch item editing
- ✅ User tag expansion from cfglimitsdefinitionuser.xml

I need to implement Phase 5: Save/Upload System with intelligent user tag reconstruction.

CRITICAL: TypeItem has fields: nominal, min (NOT max!), restock, quantmin, quantmax

Key requirement: When saving, we must intelligently preserve <user> tags:
- If all values from user group still present → keep <user> tag
- If user added extras → keep <user> + add individual tags
- If user removed any from group → fully expand to individual tags

I have:
- DayZTypesEditor_BatchColors.zip (latest build)
- HANDOFF.md (comprehensive documentation)
- User definitions already parsed and stored in limits_parser

Please confirm you understand the user tag preservation rules before we start implementing the save system.
```

**Attach:**
1. This HANDOFF.md document
2. DayZTypesEditor_BatchColors.zip

---

## End of Handoff Document

Good luck with Phase 5! The foundation is solid - just needs the save system implemented carefully with proper user tag reconstruction.
