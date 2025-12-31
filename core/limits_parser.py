"""
Limits Definition Parser
Parses cfglimitsdefinition.xml and cfglimitsdefinitionuser.xml
to extract valid categories, usages, values, tags, and user definitions
"""
import xml.etree.ElementTree as ET
from typing import List, Set, Dict

class LimitsParser:
    """Parser for limits definition files"""
    
    def __init__(self):
        self.categories: Set[str] = set()
        self.usages: Set[str] = set()
        self.values: Set[str] = set()
        self.tags: Set[str] = set()
        # User definitions can contain any combination of usage/category/value/tag
        self.user_definitions: Dict[str, Dict[str, List[str]]] = {}
    
    def parse(self, xml_content: str):
        """
        Parse a limits definition file and extract lists
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Root should be 'lists'
            if root.tag != 'lists':
                print(f"WARNING: Expected root tag 'lists', got '{root.tag}'")
                return
            
            # Parse categories from <categories> element
            categories_elem = root.find('categories')
            if categories_elem is not None:
                for cat in categories_elem.findall('category'):
                    name = cat.get('name')
                    if name:
                        self.categories.add(name)
            
            # Parse usages from <usageflags> element
            usageflags_elem = root.find('usageflags')
            if usageflags_elem is not None:
                for usage in usageflags_elem.findall('usage'):
                    name = usage.get('name')
                    if name:
                        self.usages.add(name)
            
            # Parse values from <valueflags> element
            valueflags_elem = root.find('valueflags')
            if valueflags_elem is not None:
                for value in valueflags_elem.findall('value'):
                    name = value.get('name')
                    if name:
                        self.values.add(name)
            
            # Parse tags from <tags> element
            tags_elem = root.find('tags')
            if tags_elem is not None:
                for tag in tags_elem.findall('tag'):
                    name = tag.get('name')
                    if name:
                        self.tags.add(name)
                        
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse limits definition: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing limits: {str(e)}")
    
    def parse_user_definitions(self, xml_content: str):
        """
        Parse cfglimitsdefinitionuser.xml to extract user group definitions
        Each user can contain multiple usages, categories, values, or tags
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Find all user elements
            for user_elem in root.findall('.//user'):
                user_name = user_elem.get('name')
                if not user_name:
                    continue
                
                user_def = {
                    'usage': [],
                    'category': [],
                    'value': [],
                    'tag': []
                }
                
                # Parse all child elements
                for child in user_elem:
                    tag_type = child.tag
                    tag_name = child.get('name')
                    
                    if tag_type in user_def and tag_name:
                        user_def[tag_type].append(tag_name)
                
                self.user_definitions[user_name] = user_def
                        
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse user definitions: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing user definitions: {str(e)}")
    
    def expand_user(self, user_name: str) -> Dict[str, List[str]]:
        """
        Expand a user definition into its component parts
        Returns dict with keys: usage, category, value, tag (lists)
        """
        return self.user_definitions.get(user_name, {
            'usage': [],
            'category': [],
            'value': [],
            'tag': []
        })
    
    def get_categories(self) -> List[str]:
        """Get sorted list of categories"""
        return sorted(self.categories)
    
    def get_usages(self) -> List[str]:
        """Get sorted list of usages"""
        return sorted(self.usages)
    
    def get_values(self) -> List[str]:
        """Get sorted list of values"""
        return sorted(self.values)
    
    def get_tags(self) -> List[str]:
        """Get sorted list of tags"""
        return sorted(self.tags)
    
    def get_user_names(self) -> List[str]:
        """Get sorted list of user definition names"""
        return sorted(self.user_definitions.keys())
    
    def merge(self, other: 'LimitsParser'):
        """Merge another LimitsParser's data into this one"""
        self.categories.update(other.categories)
        self.usages.update(other.usages)
        self.values.update(other.values)
        self.tags.update(other.tags)
        self.user_definitions.update(other.user_definitions)
    
    @staticmethod
    def validate_xml(xml_content: str) -> tuple[bool, str]:
        """
        Validate limits definition XML structure
        Returns: (is_valid, error_message)
        """
        try:
            root = ET.fromstring(xml_content)
            
            if root.tag != 'lists':
                return False, "Root element must be <lists>"
            
            return True, "Valid"
            
        except ET.ParseError as e:
            return False, f"XML parse error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
