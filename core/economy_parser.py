"""
Economy Core XML Parser
Parses cfgEconomyCore.xml to find all types.xml and spawnabletypes.xml file paths
"""
import xml.etree.ElementTree as ET
from typing import List, Tuple

class EconomyParser:
    """Parser for cfgEconomyCore.xml"""
    
    @staticmethod
    def parse(xml_content: str) -> List[str]:
        """
        Parse cfgEconomyCore.xml and return list of types.xml file paths
        Returns: List of relative file paths (backward compatibility)
        """
        types_files, _ = EconomyParser.parse_all(xml_content)
        return types_files
    
    @staticmethod
    def parse_all(xml_content: str) -> Tuple[List[str], List[str]]:
        """
        Parse cfgEconomyCore.xml and return lists of types and spawnabletypes file paths
        Returns: (types_files, spawnabletypes_files)
        """
        try:
            root = ET.fromstring(xml_content)
            types_files = []
            spawnabletypes_files = []
            
            # Find all <ce> elements that contain file elements
            for ce_elem in root.findall('.//ce'):
                folder = ce_elem.get('folder', '')
                
                # Find all <file> elements within this ce element
                for file_elem in ce_elem.findall('file'):
                    file_type = file_elem.get('type')
                    file_name = file_elem.get('name')
                    
                    if not file_name:
                        continue
                    
                    # Combine folder and filename
                    if folder:
                        full_path = f"{folder}/{file_name}"
                    else:
                        full_path = file_name
                    
                    # Categorize by type
                    if file_type == 'types':
                        types_files.append(full_path)
                    elif file_type == 'spawnabletypes':
                        spawnabletypes_files.append(full_path)
            
            return types_files, spawnabletypes_files
            
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse cfgEconomyCore.xml: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing economy core: {str(e)}")
    
    @staticmethod
    def validate_xml(xml_content: str) -> tuple[bool, str]:
        """
        Validate cfgEconomyCore.xml structure
        Returns: (is_valid, error_message)
        """
        try:
            root = ET.fromstring(xml_content)
            
            if root.tag != 'economycore':
                return False, "Root element must be <economycore>"
            
            # Check for required ce element
            ce = root.find('ce')
            if ce is None:
                return False, "Missing <ce> element"
            
            return True, "Valid"
            
        except ET.ParseError as e:
            return False, f"XML parse error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
