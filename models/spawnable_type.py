"""
Spawnable Types Data Models
Represents cfgspawnabletypes.xml structure
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class BlockType(Enum):
    """Type of spawnable block"""
    CARGO = "cargo"
    ATTACHMENTS = "attachments"


@dataclass
class SpawnableItem:
    """Item within a cargo or attachments block"""
    name: str
    chance: Optional[float] = None  # Optional, treated as 1.0 if not specified
    
    def __post_init__(self):
        """Validate item data"""
        if not self.name or not self.name.strip():
            raise ValueError("Item name cannot be empty")
        
        if self.chance is not None:
            if not (0.0 <= self.chance <= 1.0):
                raise ValueError(f"Item chance must be between 0.0 and 1.0, got {self.chance}")
    
    def get_effective_chance(self) -> float:
        """Get effective chance (1.0 if not specified)"""
        return self.chance if self.chance is not None else 1.0


@dataclass
class CargoBlock:
    """Cargo block - either preset-based or chance-based with items"""
    preset: Optional[str] = None
    chance: Optional[float] = None
    items: List[SpawnableItem] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate cargo block data"""
        # Must be either preset-based OR chance-based, not both
        has_preset = self.preset is not None and self.preset.strip()
        has_chance = self.chance is not None
        
        if has_preset and has_chance:
            raise ValueError("Cargo block cannot have both preset and chance")
        
        if not has_preset and not has_chance:
            raise ValueError("Cargo block must have either preset or chance")
        
        # If chance-based, must have items
        if has_chance and not self.items:
            raise ValueError("Chance-based cargo block must have at least one item")
        
        # If preset-based, should not have items
        if has_preset and self.items:
            raise ValueError("Preset-based cargo block should not have items")
        
        # Validate chance range
        if self.chance is not None:
            if not (0.0 <= self.chance <= 1.0):
                raise ValueError(f"Cargo chance must be between 0.0 and 1.0, got {self.chance}")
    
    def is_preset_based(self) -> bool:
        """Check if this is a preset-based block"""
        return self.preset is not None and self.preset.strip()
    
    def is_chance_based(self) -> bool:
        """Check if this is a chance-based block"""
        return self.chance is not None
    
    def has_items_missing_chance(self) -> bool:
        """Check if multiple items exist and any are missing chance"""
        if len(self.items) <= 1:
            return False
        return any(item.chance is None for item in self.items)


@dataclass
class AttachmentsBlock:
    """Attachments block - either preset-based or chance-based with items"""
    preset: Optional[str] = None
    chance: Optional[float] = None
    items: List[SpawnableItem] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate attachments block data"""
        # Must be either preset-based OR chance-based, not both
        has_preset = self.preset is not None and self.preset.strip()
        has_chance = self.chance is not None
        
        if has_preset and has_chance:
            raise ValueError("Attachments block cannot have both preset and chance")
        
        if not has_preset and not has_chance:
            raise ValueError("Attachments block must have either preset or chance")
        
        # If chance-based, must have items
        if has_chance and not self.items:
            raise ValueError("Chance-based attachments block must have at least one item")
        
        # If preset-based, should not have items
        if has_preset and self.items:
            raise ValueError("Preset-based attachments block should not have items")
        
        # Validate chance range
        if self.chance is not None:
            if not (0.0 <= self.chance <= 1.0):
                raise ValueError(f"Attachments chance must be between 0.0 and 1.0, got {self.chance}")
    
    def is_preset_based(self) -> bool:
        """Check if this is a preset-based block"""
        return self.preset is not None and self.preset.strip()
    
    def is_chance_based(self) -> bool:
        """Check if this is a chance-based block"""
        return self.chance is not None
    
    def has_items_missing_chance(self) -> bool:
        """Check if multiple items exist and any are missing chance"""
        if len(self.items) <= 1:
            return False
        return any(item.chance is None for item in self.items)


@dataclass
class SpawnableType:
    """Spawnable type configuration"""
    name: str
    hoarder: bool = False
    damage_min: Optional[float] = None
    damage_max: Optional[float] = None
    tag: Optional[str] = None  # Preserved but not editable in UI
    cargo_blocks: List[CargoBlock] = field(default_factory=list)
    attachments_blocks: List[AttachmentsBlock] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate spawnable type data"""
        if not self.name or not self.name.strip():
            raise ValueError("Type name cannot be empty")
        
        # Validate damage range
        if self.damage_min is not None:
            if not (0.0 <= self.damage_min <= 1.0):
                raise ValueError(f"Damage min must be between 0.0 and 1.0, got {self.damage_min}")
        
        if self.damage_max is not None:
            if not (0.0 <= self.damage_max <= 1.0):
                raise ValueError(f"Damage max must be between 0.0 and 1.0, got {self.damage_max}")
        
        if self.damage_min is not None and self.damage_max is not None:
            if self.damage_min > self.damage_max:
                raise ValueError(f"Damage min ({self.damage_min}) cannot be greater than damage max ({self.damage_max})")
    
    def has_damage(self) -> bool:
        """Check if type has damage configuration"""
        return self.damage_min is not None or self.damage_max is not None
    
    def get_cargo_count(self) -> int:
        """Get number of cargo blocks"""
        return len(self.cargo_blocks)
    
    def get_attachments_count(self) -> int:
        """Get number of attachments blocks"""
        return len(self.attachments_blocks)
    
    def has_validation_warnings(self) -> bool:
        """Check if type has any validation warnings"""
        # Check for blocks with multiple items missing chances
        for block in self.cargo_blocks:
            if block.has_items_missing_chance():
                return True
        
        for block in self.attachments_blocks:
            if block.has_items_missing_chance():
                return True
        
        return False


@dataclass
class SpawnableTypesFile:
    """Container for spawnable types file"""
    types: List[SpawnableType] = field(default_factory=list)
    source_file: str = ""
    header_comments: List[str] = field(default_factory=list)
    footer_comments: List[str] = field(default_factory=list)
    type_comments: dict = field(default_factory=dict)  # type_name -> comments
    
    def get_type_by_name(self, name: str) -> Optional[SpawnableType]:
        """Find type by name"""
        for spawnable_type in self.types:
            if spawnable_type.name == name:
                return spawnable_type
        return None
    
    def add_type(self, spawnable_type: SpawnableType):
        """Add a new type (allows duplicates with warning)"""
        existing = self.get_type_by_name(spawnable_type.name)
        if existing:
            print(f"⚠ Warning: Duplicate type '{spawnable_type.name}' - keeping last occurrence")
            self.types.remove(existing)
        self.types.append(spawnable_type)
    
    def remove_type(self, spawnable_type: SpawnableType):
        """Remove a type"""
        if spawnable_type in self.types:
            self.types.remove(spawnable_type)
            # Remove associated comments
            if spawnable_type.name in self.type_comments:
                del self.type_comments[spawnable_type.name]
    
    def get_total_type_count(self) -> int:
        """Get total number of types"""
        return len(self.types)
    
    def get_types_with_warnings(self) -> List[SpawnableType]:
        """Get list of types with validation warnings"""
        return [t for t in self.types if t.has_validation_warnings()]
