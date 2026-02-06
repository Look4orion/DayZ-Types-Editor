"""
Random Presets Parser
Parses cfgrandompresets.xml files and creates RandomPreset objects
"""
import xml.etree.ElementTree as ET
from typing import Tuple
from models.random_preset import RandomPresetsFile, RandomPreset, PresetItem, PresetType

class RandomPresetsParser:
    """Parser for cfgrandompresets.xml files"""
    
    @staticmethod
    def parse(xml_content: str, source_file: str) -> RandomPresetsFile:
        """
        Parse a cfgrandompresets.xml file
        
        Args:
            xml_content: XML content as string
            source_file: Path to the source file
            
        Returns:
            RandomPresetsFile object containing all parsed presets
            
        Raises:
            ValueError: If XML is malformed or validation fails
        """
        presets_file = RandomPresetsFile(source_file=source_file)
        presets_file.original_content = xml_content
        
        try:
            # Extract comments before parsing
            RandomPresetsParser._extract_comments(xml_content, presets_file)
            # Parse XML
            root = ET.fromstring(xml_content.strip())
            
            # Validate root element
            if root.tag != 'randompresets':
                raise ValueError(f"Root element must be <randompresets>, found <{root.tag}>")
            
            # Parse cargo presets
            for cargo_elem in root.findall('cargo'):
                try:
                    preset = RandomPresetsParser._parse_preset_element(
                        cargo_elem, 
                        PresetType.CARGO
                    )
                    presets_file.add_preset(preset)
                except Exception as e:
                    preset_name = cargo_elem.get('name', 'unknown')
                    raise ValueError(f"Error parsing cargo preset '{preset_name}': {str(e)}")
            
            # Parse attachments presets
            for attach_elem in root.findall('attachments'):
                try:
                    preset = RandomPresetsParser._parse_preset_element(
                        attach_elem, 
                        PresetType.ATTACHMENTS
                    )
                    presets_file.add_preset(preset)
                except Exception as e:
                    preset_name = attach_elem.get('name', 'unknown')
                    raise ValueError(f"Error parsing attachments preset '{preset_name}': {str(e)}")
            
            # Validate we found at least one preset
            if presets_file.get_total_preset_count() == 0:
                raise ValueError("No cargo or attachments presets found in file")
            
            return presets_file
            
        except ET.ParseError as e:
            raise ValueError(f"XML parse error in {source_file}: {str(e)}")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error parsing random presets file {source_file}: {str(e)}")
    
    @staticmethod
    def _extract_comments(xml_content: str, presets_file):
        """Extract and store comments from XML content"""
        import re
        
        # Find all comments
        comment_pattern = r'<!--(.*?)-->'
        
        # Find header comments (before <randompresets>)
        presets_start = xml_content.find('<randompresets')
        if presets_start > 0:
            header_section = xml_content[:presets_start]
            header_comments = re.findall(comment_pattern, header_section, re.DOTALL)
            presets_file.header_comments = [f'<!--{c.strip()}-->' for c in header_comments]
        
        # Find footer comments (after </randompresets>)
        presets_end = xml_content.find('</randompresets>')
        if presets_end > 0:
            footer_section = xml_content[presets_end + 16:]  # 16 = len('</randompresets>')
            footer_comments = re.findall(comment_pattern, footer_section, re.DOTALL)
            presets_file.footer_comments = [f'<!--{c.strip()}-->' for c in footer_comments]
        
        # Find comments associated with specific presets
        # Look for comments immediately before <cargo or <attachments tags
        preset_pattern = r'((?:<!--.*?-->\s*)*)<(cargo|attachments)\s+[^>]*name="([^"]+)"'
        matches = re.findall(preset_pattern, xml_content, re.DOTALL)
        
        for comment_block, preset_type, preset_name in matches:
            if comment_block.strip():
                # Extract individual comments from the block
                preset_comments = re.findall(comment_pattern, comment_block, re.DOTALL)
                if preset_comments:
                    presets_file.preset_comments[preset_name] = [f'<!--{c.strip()}-->' for c in preset_comments]
    
    @staticmethod
    def _parse_preset_element(elem: ET.Element, preset_type: PresetType) -> RandomPreset:
        """
        Parse a single <cargo> or <attachments> element
        
        Args:
            elem: XML element to parse
            preset_type: Type of preset (CARGO or ATTACHMENTS)
            
        Returns:
            RandomPreset object
            
        Raises:
            ValueError: If required attributes are missing or invalid
        """
        # Get required attributes
        name = elem.get('name')
        if not name:
            raise ValueError(f"Missing required 'name' attribute in {preset_type.value} preset")
        
        chance_str = elem.get('chance')
        if not chance_str:
            raise ValueError(f"Missing required 'chance' attribute in preset '{name}'")
        
        # Parse and validate chance
        try:
            chance = float(chance_str)
        except ValueError:
            raise ValueError(f"Invalid chance value '{chance_str}' in preset '{name}' - must be a number")
        
        if not 0.0 <= chance <= 1.0:
            raise ValueError(f"Chance value {chance} in preset '{name}' must be between 0.0 and 1.0")
        
        # Create preset
        preset = RandomPreset(
            preset_type=preset_type,
            name=name,
            chance=chance
        )
        
        # Parse items
        for item_elem in elem.findall('item'):
            try:
                item = RandomPresetsParser._parse_item_element(item_elem)
                preset.add_item(item)
            except Exception as e:
                item_name = item_elem.get('name', 'unknown')
                raise ValueError(f"Error parsing item '{item_name}' in preset '{name}': {str(e)}")
        
        # Validate preset has at least one item
        if preset.get_item_count() == 0:
            raise ValueError(f"Preset '{name}' has no items - at least one item is required")
        
        return preset
    
    @staticmethod
    def _parse_item_element(elem: ET.Element) -> PresetItem:
        """
        Parse a single <item> element
        
        Args:
            elem: XML element to parse
            
        Returns:
            PresetItem object
            
        Raises:
            ValueError: If required attributes are missing or invalid
        """
        # Get required attributes
        name = elem.get('name')
        if not name:
            raise ValueError("Missing required 'name' attribute in item")
        
        chance_str = elem.get('chance')
        if not chance_str:
            raise ValueError(f"Missing required 'chance' attribute in item '{name}'")
        
        # Parse and validate chance
        try:
            chance = float(chance_str)
        except ValueError:
            raise ValueError(f"Invalid chance value '{chance_str}' in item '{name}' - must be a number")
        
        if not 0.0 <= chance <= 1.0:
            raise ValueError(f"Chance value {chance} in item '{name}' must be between 0.0 and 1.0")
        
        return PresetItem(name=name, chance=chance)
    
    @staticmethod
    def validate_xml(xml_content: str) -> Tuple[bool, str]:
        """
        Validate cfgrandompresets.xml structure without full parsing
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = ET.fromstring(xml_content.strip())
            
            if root.tag != 'randompresets':
                return False, "Root element must be <randompresets>"
            
            # Check for at least one preset
            cargo_count = len(root.findall('cargo'))
            attach_count = len(root.findall('attachments'))
            
            if cargo_count == 0 and attach_count == 0:
                return False, "No <cargo> or <attachments> elements found"
            
            return True, "Valid"
            
        except ET.ParseError as e:
            return False, f"XML parse error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
