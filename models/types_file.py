"""
Types File Data Model
Container for a types.xml file and its items
"""
from typing import List, Dict, Optional
from models.type_item import TypeItem

class TypesFile:
    """Container for a types.xml file"""
    
    def __init__(self, path: str):
        self.path = path  # Relative path from mission folder
        self.items: List[TypeItem] = []
        self.modified = False
        self.original_content: Optional[str] = None
        self.header_comments: List[str] = []  # Comments before <types>
        self.footer_comments: List[str] = []  # Comments after </types>
        self.item_comments: Dict[str, List[str]] = {}  # Comments before each item
    
    def add_item(self, item: TypeItem):
        """Add an item to this file"""
        item.source_file = self.path
        self.items.append(item)
    
    def get_item_by_name(self, name: str) -> Optional[TypeItem]:
        """Get an item by its name"""
        for item in self.items:
            if item.name == name:
                return item
        return None
    
    def get_modified_items(self) -> List[TypeItem]:
        """Get all modified items"""
        return [item for item in self.items if item.modified]
    
    def has_modifications(self) -> bool:
        """Check if any items have been modified"""
        return any(item.modified for item in self.items)
    
    def to_xml(self, limits_parser=None) -> str:
        """Convert all items to XML string, preserving comments"""
        lines = []
        
        # Add header comments
        for comment in self.header_comments:
            lines.append(comment)
        
        lines.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        lines.append('<types>')
        
        for item in self.items:
            # Add any comments associated with this item
            if item.name in self.item_comments:
                for comment in self.item_comments[item.name]:
                    lines.append(comment)
            
            lines.append(item.to_xml_element(limits_parser))
        
        lines.append('</types>')
        
        # Add footer comments
        for comment in self.footer_comments:
            lines.append(comment)
        
        return '\n'.join(lines)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about this file"""
        return {
            'total_items': len(self.items),
            'modified_items': len(self.get_modified_items()),
            'categories': len(set(item.category for item in self.items if item.category))
        }
    
    def __repr__(self) -> str:
        return f"TypesFile(path='{self.path}', items={len(self.items)}, modified={self.modified})"
