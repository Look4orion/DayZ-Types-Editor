"""
Type Item Data Model
Represents a single type entry from types.xml
"""
from typing import List, Optional, Dict
from dataclasses import dataclass, field

@dataclass
class TypeItem:
    """Represents a single type entry"""
    name: str
    nominal: int = 0
    lifetime: int = 3600
    restock: int = 0
    min: int = 0
    quantmin: int = -1
    quantmax: int = -1
    cost: int = 100
    category: Optional[str] = None
    usage: List[str] = field(default_factory=list)
    value: List[str] = field(default_factory=list)
    tag: List[str] = field(default_factory=list)
    
    # Flags (0 or 1)
    count_in_cargo: int = 0
    count_in_hoarder: int = 0
    count_in_map: int = 1
    count_in_player: int = 0
    crafted: int = 0
    deloot: int = 0
    
    # Track original user tags for reconstruction on save
    original_users: List[str] = field(default_factory=list)
    
    # Metadata
    source_file: str = ""  # Path to the types.xml file this item came from
    modified: bool = False  # Whether this item has been modified
    
    def __post_init__(self):
        """Ensure lists are properly initialized"""
        if not isinstance(self.usage, list):
            self.usage = []
        if not isinstance(self.value, list):
            self.value = []
        if not isinstance(self.tag, list):
            self.tag = []
    
    def clone(self) -> 'TypeItem':
        """Create a deep copy of this item"""
        return TypeItem(
            name=self.name,
            nominal=self.nominal,
            lifetime=self.lifetime,
            restock=self.restock,
            min=self.min,
            quantmin=self.quantmin,
            quantmax=self.quantmax,
            cost=self.cost,
            category=self.category,
            usage=self.usage.copy(),
            value=self.value.copy(),
            tag=self.tag.copy(),
            count_in_cargo=self.count_in_cargo,
            count_in_hoarder=self.count_in_hoarder,
            count_in_map=self.count_in_map,
            count_in_player=self.count_in_player,
            crafted=self.crafted,
            deloot=self.deloot,
            original_users=self.original_users.copy(),
            source_file=self.source_file,
            modified=self.modified
        )
    
    def to_xml_element(self, limits_parser=None) -> str:
        """Convert to XML string, preserving user tags where possible"""
        lines = [f'    <type name="{self.name}">']
        lines.append(f'        <nominal>{self.nominal}</nominal>')
        lines.append(f'        <lifetime>{self.lifetime}</lifetime>')
        lines.append(f'        <restock>{self.restock}</restock>')
        lines.append(f'        <min>{self.min}</min>')
        lines.append(f'        <quantmin>{self.quantmin}</quantmin>')
        lines.append(f'        <quantmax>{self.quantmax}</quantmax>')
        lines.append(f'        <cost>{self.cost}</cost>')
        
        # Flags - export actual values
        lines.append(
            f'        <flags count_in_cargo="{self.count_in_cargo}" '
            f'count_in_hoarder="{self.count_in_hoarder}" '
            f'count_in_map="{self.count_in_map}" '
            f'count_in_player="{self.count_in_player}" '
            f'crafted="{self.crafted}" '
            f'deloot="{self.deloot}"/>'
        )
        
        if self.category:
            lines.append(f'        <category name="{self.category}"/>')
        
        # Initialize remaining lists
        remaining_usage = self.usage.copy()
        remaining_value = self.value.copy()
        remaining_tag = self.tag.copy()
        
        # Handle user tags intelligently
        if limits_parser and self.original_users:
            # Try to preserve user tags
            preserved_users = []
            
            for user_name in self.original_users:
                user_def = limits_parser.expand_user(user_name)
                
                # Check if all components of this user are still present
                all_present = True
                if user_def['usage']:
                    all_present = all_present and all(u in remaining_usage for u in user_def['usage'])
                if user_def['value']:
                    all_present = all_present and all(v in remaining_value for v in user_def['value'])
                if user_def['tag']:
                    all_present = all_present and all(t in remaining_tag for t in user_def['tag'])
                # Note: category in user tags is rare, skipping for now
                
                if all_present:
                    # Keep this user tag
                    preserved_users.append(user_name)
                    # Remove these items from remaining lists
                    for u in user_def['usage']:
                        if u in remaining_usage:
                            remaining_usage.remove(u)
                    for v in user_def['value']:
                        if v in remaining_value:
                            remaining_value.remove(v)
                    for t in user_def['tag']:
                        if t in remaining_tag:
                            remaining_tag.remove(t)
            
            # Export preserved user tags
            for user in preserved_users:
                lines.append(f'        <user name="{user}"/>')
        
        # Export remaining individual tags as direct children (no wrapper)
        for u in remaining_usage:
            lines.append(f'        <usage name="{u}"/>')
        
        for v in remaining_value:
            lines.append(f'        <value name="{v}"/>')
        
        for t in remaining_tag:
            lines.append(f'        <tag name="{t}"/>')
        
        lines.append('    </type>')
        return '\n'.join(lines)
    
    def matches_filter(self, search_text: str = "", category: str = "", 
                      tags: List[str] = None, usage: List[str] = None,
                      value: List[str] = None, source_file: str = "",
                      nominal_min: Optional[int] = None, nominal_max: Optional[int] = None,
                      use_or_logic: bool = False) -> bool:
        """
        Check if this item matches the given filters
        """
        if tags is None:
            tags = []
        if usage is None:
            usage = []
        if value is None:
            value = []
        
        matches = []
        
        # Search text (in name)
        if search_text:
            matches.append(search_text.lower() in self.name.lower())
        
        # Category filter
        if category:
            matches.append(self.category == category)
        
        # Tag filter
        if tags:
            tag_match = any(t in self.tag for t in tags)
            matches.append(tag_match)
        
        # Usage filter
        if usage:
            usage_match = any(u in self.usage for u in usage)
            matches.append(usage_match)
        
        # Value filter
        if value:
            value_match = any(v in self.value for v in value)
            matches.append(value_match)
        
        # Source file filter
        if source_file:
            matches.append(self.source_file == source_file)
        
        # Nominal range filter
        if nominal_min is not None:
            matches.append(self.nominal >= nominal_min)
        if nominal_max is not None:
            matches.append(self.nominal <= nominal_max)
        
        # Apply logic (AND or OR)
        if not matches:
            return True  # No filters applied
        
        if use_or_logic:
            return any(matches)
        else:
            return all(matches)
