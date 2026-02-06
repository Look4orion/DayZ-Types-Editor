"""
Spawnable Types XML Parser
Parses cfgspawnabletypes.xml files with comment preservation
"""
import xml.etree.ElementTree as ET
import re
from typing import List, Tuple
from models.spawnable_type import (
    SpawnableTypesFile, SpawnableType, CargoBlock, 
    AttachmentsBlock, SpawnableItem
)


class SpawnableTypesParser:
    """Parser for cfgspawnabletypes.xml files"""
    
    @staticmethod
    def parse(xml_content: str, source_file: str = "") -> SpawnableTypesFile:
        """
        Parse spawnable types XML content
        
        Args:
            xml_content: XML string content
            source_file: Source filename for reference
            
        Returns:
            SpawnableTypesFile object
            
        Raises:
            Exception: If XML is invalid or structure is incorrect
        """
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise Exception(f"XML parse error in {source_file}: {str(e)}")
        
        # Validate root element
        if root.tag != 'spawnabletypes':
            raise Exception(f"Root element must be <spawnabletypes>, got <{root.tag}>")
        
        # Extract comments
        header_comments, footer_comments, type_comments = SpawnableTypesParser._extract_comments(xml_content)
        
        # Create file object
        spawnable_types_file = SpawnableTypesFile(
            source_file=source_file,
            header_comments=header_comments,
            footer_comments=footer_comments,
            type_comments=type_comments
        )
        
        # Parse types
        warnings = []
        for type_elem in root.findall('type'):
            try:
                spawnable_type = SpawnableTypesParser._parse_type(type_elem)
                spawnable_types_file.add_type(spawnable_type)
                
                # Check for validation warnings
                if spawnable_type.has_validation_warnings():
                    warnings.append(f"Type '{spawnable_type.name}' has items missing chance values in multi-item blocks")
                
            except Exception as e:
                raise Exception(f"Error parsing type '{type_elem.get('name', 'unknown')}': {str(e)}")
        
        # Show warnings if any (but don't fail)
        if warnings:
            print(f"Warnings in {source_file}:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        
        return spawnable_types_file
    
    @staticmethod
    def _parse_type(type_elem: ET.Element) -> SpawnableType:
        """Parse a single type element"""
        # Get name (required)
        name = type_elem.get('name')
        if not name:
            raise Exception("Type element missing required 'name' attribute")
        
        # Initialize type
        spawnable_type = SpawnableType(name=name)
        
        # Parse child elements
        for child in type_elem:
            if child.tag == 'hoarder':
                spawnable_type.hoarder = True
            
            elif child.tag == 'damage':
                # Parse damage min/max
                min_val = child.get('min')
                max_val = child.get('max')
                
                if min_val is not None:
                    try:
                        spawnable_type.damage_min = float(min_val)
                    except ValueError:
                        raise Exception(f"Invalid damage min value: {min_val}")
                
                if max_val is not None:
                    try:
                        spawnable_type.damage_max = float(max_val)
                    except ValueError:
                        raise Exception(f"Invalid damage max value: {max_val}")
            
            elif child.tag == 'tag':
                # Preserve tag but don't expose in UI
                spawnable_type.tag = child.get('name')
            
            elif child.tag == 'cargo':
                cargo_block = SpawnableTypesParser._parse_cargo_block(child)
                spawnable_type.cargo_blocks.append(cargo_block)
            
            elif child.tag == 'attachments':
                attachments_block = SpawnableTypesParser._parse_attachments_block(child)
                spawnable_type.attachments_blocks.append(attachments_block)
        
        return spawnable_type
    
    @staticmethod
    def _parse_cargo_block(cargo_elem: ET.Element) -> CargoBlock:
        """Parse a cargo block element"""
        preset = cargo_elem.get('preset')
        chance_str = cargo_elem.get('chance')
        
        # Preset-based block
        if preset:
            return CargoBlock(preset=preset)
        
        # Chance-based block OR block with items only (no chance attribute)
        if chance_str is not None:
            try:
                chance = float(chance_str)
            except ValueError:
                raise Exception(f"Invalid cargo chance value: {chance_str}")
        else:
            # No chance attribute - check if there are items
            items = []
            for item_elem in cargo_elem.findall('item'):
                item = SpawnableTypesParser._parse_item(item_elem)
                items.append(item)
            
            if not items:
                raise Exception("Cargo block must have either 'preset' attribute or 'chance' attribute or contain items")
            
            # Items without chance attribute on block - use chance=1.0
            return CargoBlock(chance=1.0, items=items)
        
        # Has chance attribute - parse items
        items = []
        for item_elem in cargo_elem.findall('item'):
            item = SpawnableTypesParser._parse_item(item_elem)
            items.append(item)
        
        if not items:
            raise Exception("Chance-based cargo block must have at least one item")
        
        return CargoBlock(chance=chance, items=items)
    
    @staticmethod
    def _parse_attachments_block(attachments_elem: ET.Element) -> AttachmentsBlock:
        """Parse an attachments block element"""
        preset = attachments_elem.get('preset')
        chance_str = attachments_elem.get('chance')
        
        # Preset-based block
        if preset:
            return AttachmentsBlock(preset=preset)
        
        # Chance-based block OR block with items only (no chance attribute)
        if chance_str is not None:
            try:
                chance = float(chance_str)
            except ValueError:
                raise Exception(f"Invalid attachments chance value: {chance_str}")
        else:
            # No chance attribute - check if there are items
            items = []
            for item_elem in attachments_elem.findall('item'):
                item = SpawnableTypesParser._parse_item(item_elem)
                items.append(item)
            
            if not items:
                raise Exception("Attachments block must have either 'preset' attribute or 'chance' attribute or contain items")
            
            # Items without chance attribute on block - use chance=1.0
            return AttachmentsBlock(chance=1.0, items=items)
        
        # Has chance attribute - parse items
        items = []
        for item_elem in attachments_elem.findall('item'):
            item = SpawnableTypesParser._parse_item(item_elem)
            items.append(item)
        
        if not items:
            raise Exception("Chance-based attachments block must have at least one item")
        
        return AttachmentsBlock(chance=chance, items=items)
    
    @staticmethod
    def _parse_item(item_elem: ET.Element) -> SpawnableItem:
        """Parse an item element"""
        name = item_elem.get('name')
        if not name:
            raise Exception("Item element missing required 'name' attribute")
        
        chance_str = item_elem.get('chance')
        chance = None
        if chance_str is not None:
            try:
                chance = float(chance_str)
            except ValueError:
                raise Exception(f"Invalid item chance value: {chance_str}")
        
        return SpawnableItem(name=name, chance=chance)
    
    @staticmethod
    def _extract_comments(xml_content: str) -> Tuple[List[str], List[str], dict]:
        """
        Extract comments from XML content
        
        Returns:
            Tuple of (header_comments, footer_comments, type_comments)
        """
        header_comments = []
        footer_comments = []
        type_comments = {}
        
        # Find all comments
        comment_pattern = r'<!--(.*?)-->'
        comments = re.findall(comment_pattern, xml_content, re.DOTALL)
        
        # Find position of <spawnabletypes> and </spawnabletypes>
        root_start = xml_content.find('<spawnabletypes')
        root_end = xml_content.rfind('</spawnabletypes>')
        
        if root_start == -1 or root_end == -1:
            return header_comments, footer_comments, type_comments
        
        # Find header comments (before <spawnabletypes>)
        header_section = xml_content[:root_start]
        for comment in re.finditer(comment_pattern, header_section, re.DOTALL):
            header_comments.append(comment.group(1).strip())
        
        # Find footer comments (after </spawnabletypes>)
        footer_section = xml_content[root_end + len('</spawnabletypes>'):]
        for comment in re.finditer(comment_pattern, footer_section, re.DOTALL):
            footer_comments.append(comment.group(1).strip())
        
        # Find type-specific comments (comments immediately before <type> tags)
        # Only match comments that appear directly before a type (no other elements between)
        type_pattern = r'<!--([^<>]*?)-->\s*<type\s+name="([^"]+)"'
        for match in re.finditer(type_pattern, xml_content):
            comment_text = match.group(1).strip()
            type_name = match.group(2)
            
            if type_name not in type_comments:
                type_comments[type_name] = []
            type_comments[type_name].append(comment_text)
        
        return header_comments, footer_comments, type_comments
