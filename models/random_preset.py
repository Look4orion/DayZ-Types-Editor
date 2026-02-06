"""
Random Preset Data Model
Represents cargo and attachment presets from cfgrandompresets.xml
"""
from typing import List, Dict
from dataclasses import dataclass, field
from enum import Enum

class PresetType(Enum):
    """Type of preset"""
    CARGO = "cargo"
    ATTACHMENTS = "attachments"

@dataclass
class PresetItem:
    """Represents a single item in a preset"""
    name: str
    chance: float
    
    def __post_init__(self):
        """Validate item data"""
        if not self.name:
            raise ValueError("Item name cannot be empty")
        if not 0.0 <= self.chance <= 1.0:
            raise ValueError(f"Item chance must be between 0.0 and 1.0, got {self.chance}")

@dataclass
class RandomPreset:
    """Base class for a random preset group"""
    preset_type: PresetType
    name: str
    chance: float
    items: List[PresetItem] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate preset data"""
        if not self.name:
            raise ValueError("Preset name cannot be empty")
        if not 0.0 <= self.chance <= 1.0:
            raise ValueError(f"Preset chance must be between 0.0 and 1.0, got {self.chance}")
        if not isinstance(self.items, list):
            self.items = []
    
    def add_item(self, item: PresetItem):
        """Add an item to this preset"""
        self.items.append(item)
    
    def remove_item(self, index: int):
        """Remove an item by index"""
        if 0 <= index < len(self.items):
            del self.items[index]
    
    def get_item_count(self) -> int:
        """Get total number of items in this preset"""
        return len(self.items)
    
    def clone(self) -> 'RandomPreset':
        """Create a deep copy of this preset"""
        return RandomPreset(
            preset_type=self.preset_type,
            name=self.name,
            chance=self.chance,
            items=[PresetItem(name=item.name, chance=item.chance) for item in self.items]
        )

@dataclass
class RandomPresetsFile:
    """Container for all random presets from a file"""
    source_file: str
    cargo_presets: List[RandomPreset] = field(default_factory=list)
    attachments_presets: List[RandomPreset] = field(default_factory=list)
    original_content: str = ""  # Store original XML for comparison
    
    # Comment preservation
    header_comments: List[str] = field(default_factory=list)  # Comments before <randompresets>
    footer_comments: List[str] = field(default_factory=list)  # Comments after </randompresets>
    preset_comments: Dict[str, List[str]] = field(default_factory=dict)  # Comments before presets {preset_name: [comments]}
    
    def add_preset(self, preset: RandomPreset):
        """Add a preset to the appropriate list"""
        if preset.preset_type == PresetType.CARGO:
            self.cargo_presets.append(preset)
        elif preset.preset_type == PresetType.ATTACHMENTS:
            self.attachments_presets.append(preset)
    
    def get_all_presets(self) -> List[RandomPreset]:
        """Get all presets combined"""
        return self.cargo_presets + self.attachments_presets
    
    def get_preset_by_name(self, name: str, preset_type: PresetType = None) -> RandomPreset:
        """Find a preset by name, optionally filtered by type"""
        if preset_type == PresetType.CARGO or preset_type is None:
            for preset in self.cargo_presets:
                if preset.name == name:
                    return preset
        
        if preset_type == PresetType.ATTACHMENTS or preset_type is None:
            for preset in self.attachments_presets:
                if preset.name == name:
                    return preset
        
        return None
    
    def remove_preset(self, preset: RandomPreset):
        """Remove a preset from the file"""
        if preset.preset_type == PresetType.CARGO:
            if preset in self.cargo_presets:
                self.cargo_presets.remove(preset)
        elif preset.preset_type == PresetType.ATTACHMENTS:
            if preset in self.attachments_presets:
                self.attachments_presets.remove(preset)
    
    def get_total_preset_count(self) -> int:
        """Get total number of presets in file"""
        return len(self.cargo_presets) + len(self.attachments_presets)
