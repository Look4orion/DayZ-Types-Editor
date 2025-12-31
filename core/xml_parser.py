"""
Types XML Parser
Parses types.xml files and creates TypeItem objects
"""
import xml.etree.ElementTree as ET
import re
from typing import List, Dict
from models.type_item import TypeItem
from models.types_file import TypesFile

class TypesParser:
    """Parser for types.xml files"""
    
    @staticmethod
    def parse(xml_content: str, source_file: str, limits_parser=None) -> TypesFile:
        """
        Parse a types.xml file
        Args:
            xml_content: XML content as string
            source_file: Relative path to the source file
            limits_parser: LimitsParser instance for expanding user tags
        Returns:
            TypesFile object containing all parsed items
        """
        types_file = TypesFile(source_file)
        types_file.original_content = xml_content
        
        try:
            # Extract comments before parsing
            TypesParser._extract_comments(xml_content, types_file)
            
            # Clean XML content - remove leading whitespace and comments before <?xml
            cleaned_content = xml_content.strip()
            
            # If content starts with comment, find the <?xml tag
            if cleaned_content.startswith('<!--'):
                xml_start = cleaned_content.find('<?xml')
                if xml_start > 0:
                    cleaned_content = cleaned_content[xml_start:]
            
            root = ET.fromstring(cleaned_content)
            
            # Parse all type elements
            for type_elem in root.findall('type'):
                try:
                    item = TypesParser._parse_type_element(type_elem, limits_parser)
                    types_file.add_item(item)
                except Exception as e:
                    # Skip this individual type element but continue parsing others
                    item_name = type_elem.get('name', 'unknown')
                    print(f"Warning: Skipping malformed type '{item_name}' in {source_file}: {e}")
                    continue
            
            return types_file
            
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse {source_file}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing types file {source_file}: {str(e)}")
    
    @staticmethod
    def _extract_comments(xml_content: str, types_file: TypesFile):
        """Extract and store comments from XML content"""
        # Find all comments
        comment_pattern = r'<!--(.*?)-->'
        
        # Find header comments (before <types>)
        types_start = xml_content.find('<types')
        if types_start > 0:
            header_section = xml_content[:types_start]
            header_comments = re.findall(comment_pattern, header_section, re.DOTALL)
            # Strip any trailing/leading whitespace including line endings
            types_file.header_comments = [f'<!--{c.strip()}-->' for c in header_comments]
        
        # Find footer comments (after </types>)
        types_end = xml_content.find('</types>')
        if types_end > 0:
            footer_section = xml_content[types_end + 8:]  # 8 = len('</types>')
            footer_comments = re.findall(comment_pattern, footer_section, re.DOTALL)
            # Strip any trailing/leading whitespace including line endings
            types_file.footer_comments = [f'<!--{c.strip()}-->' for c in footer_comments]
        
        # Find comments associated with specific items
        # Look for comments immediately before <type name="...">
        type_pattern = r'((?:<!--.*?-->\s*)*)<type\s+name="([^"]+)"'
        matches = re.findall(type_pattern, xml_content, re.DOTALL)
        
        for comment_block, item_name in matches:
            if comment_block.strip():
                # Extract individual comments from the block
                item_comments = re.findall(comment_pattern, comment_block, re.DOTALL)
                if item_comments:
                    # Strip any trailing/leading whitespace including line endings
                    types_file.item_comments[item_name] = [f'<!--{c.strip()}-->' for c in item_comments]
    
    @staticmethod
    def _parse_type_element(elem: ET.Element, limits_parser=None) -> TypeItem:
        """Parse a single <type> element"""
        name = elem.get('name', '')
        
        # Helper to safely parse integers with default fallback
        def safe_int(text, default=0):
            if text is None or text.strip() == '':
                return default
            try:
                return int(text)
            except (ValueError, AttributeError):
                return default
        
        # Parse simple numeric fields
        nominal = safe_int(elem.findtext('nominal'), 0)
        lifetime = safe_int(elem.findtext('lifetime'), 3600)
        restock = safe_int(elem.findtext('restock'), 0)
        min_val = safe_int(elem.findtext('min'), 0)
        quantmin = safe_int(elem.findtext('quantmin'), -1)
        quantmax = safe_int(elem.findtext('quantmax'), -1)
        cost = safe_int(elem.findtext('cost'), 100)
        
        # Parse category (single value)
        category = None
        category_elem = elem.find('category')
        if category_elem is not None:
            category = category_elem.get('name')
        
        # Parse usage (multiple values) - handle both <usage> and <user> tags
        usage_list = []
        value_list = []
        tag_list = []
        original_users = []
        
        # Look for direct <usage> children
        for usage_elem in elem.findall('usage'):
            usage_name = usage_elem.get('name')
            if usage_name:
                usage_list.append(usage_name)
        
        # Parse value (multiple values)
        for value_elem in elem.findall('value'):
            value_name = value_elem.get('name')
            if value_name:
                value_list.append(value_name)
        
        # Parse tag (multiple values)
        for tag_elem in elem.findall('tag'):
            tag_name = tag_elem.get('name')
            if tag_name:
                tag_list.append(tag_name)
        
        # Look for direct <user> children and expand them
        for user_elem in elem.findall('user'):
            user_name = user_elem.get('name')
            if user_name:
                original_users.append(user_name)
                if limits_parser:
                    # Expand user group
                    expanded = limits_parser.expand_user(user_name)
                    usage_list.extend(expanded.get('usage', []))
                    value_list.extend(expanded.get('value', []))
                    tag_list.extend(expanded.get('tag', []))
        
        # Parse flags element
        count_in_cargo = 0
        count_in_hoarder = 0
        count_in_map = 1  # Default to 1
        count_in_player = 0
        crafted = 0
        deloot = 0
        
        flags_elem = elem.find('flags')
        if flags_elem is not None:
            count_in_cargo = safe_int(flags_elem.get('count_in_cargo'), 0)
            count_in_hoarder = safe_int(flags_elem.get('count_in_hoarder'), 0)
            count_in_map = safe_int(flags_elem.get('count_in_map'), 1)
            count_in_player = safe_int(flags_elem.get('count_in_player'), 0)
            crafted = safe_int(flags_elem.get('crafted'), 0)
            deloot = safe_int(flags_elem.get('deloot'), 0)
        
        return TypeItem(
            name=name,
            nominal=nominal,
            lifetime=lifetime,
            restock=restock,
            min=min_val,
            quantmin=quantmin,
            quantmax=quantmax,
            cost=cost,
            category=category,
            usage=usage_list,
            value=value_list,
            tag=tag_list,
            count_in_cargo=count_in_cargo,
            count_in_hoarder=count_in_hoarder,
            count_in_map=count_in_map,
            count_in_player=count_in_player,
            crafted=crafted,
            deloot=deloot,
            original_users=original_users
        )
    
    @staticmethod
    def validate_xml(xml_content: str) -> tuple[bool, str]:
        """
        Validate types.xml structure
        Returns: (is_valid, error_message)
        """
        try:
            root = ET.fromstring(xml_content)
            
            if root.tag != 'types':
                return False, "Root element must be <types>"
            
            # Check that there's at least one type element
            types = root.findall('type')
            if not types:
                return False, "No <type> elements found"
            
            # Validate each type has a name
            for idx, type_elem in enumerate(types):
                if not type_elem.get('name'):
                    return False, f"Type element at index {idx} missing 'name' attribute"
            
            return True, "Valid"
            
        except ET.ParseError as e:
            return False, f"XML parse error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_item_structure(item: TypeItem, valid_categories: List[str],
                               valid_usages: List[str], valid_values: List[str],
                               valid_tags: List[str]) -> tuple[bool, List[str]]:
        """
        Validate a TypeItem against DayZ rules
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate numeric ranges
        if item.nominal < 0:
            errors.append(f"{item.name}: nominal must be >= 0")
        if item.min < 0:
            errors.append(f"{item.name}: min must be >= 0")
        if item.min > item.nominal:
            errors.append(f"{item.name}: min cannot be greater than nominal")
        if item.lifetime < 0:
            errors.append(f"{item.name}: lifetime must be >= 0")
        if item.restock < 0:
            errors.append(f"{item.name}: restock must be >= 0")
        if item.cost < 0:
            errors.append(f"{item.name}: cost must be >= 0")
        
        # Validate category
        if item.category and item.category not in valid_categories:
            errors.append(f"{item.name}: invalid category '{item.category}'")
        
        # Validate usages
        for usage in item.usage:
            if usage not in valid_usages:
                errors.append(f"{item.name}: invalid usage '{usage}'")
        
        # Validate values
        for value in item.value:
            if value not in valid_values:
                errors.append(f"{item.name}: invalid value '{value}'")
        
        # Validate tags
        for tag in item.tag:
            if tag not in valid_tags:
                errors.append(f"{item.name}: invalid tag '{tag}'")
        
        return len(errors) == 0, errors
