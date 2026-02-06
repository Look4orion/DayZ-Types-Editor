"""
Unit Tests for Random Presets Parser, Model, and Writer
Tests parsing, validation, and writing of cfgrandompresets.xml files
"""
import unittest
import xml.etree.ElementTree as ET
from models.random_preset import (
    PresetType, PresetItem, RandomPreset, RandomPresetsFile
)
from core.random_presets_parser import RandomPresetsParser
from core.random_presets_writer import RandomPresetsWriter

class TestPresetItem(unittest.TestCase):
    """Test PresetItem model"""
    
    def test_valid_item_creation(self):
        """Test creating a valid PresetItem"""
        item = PresetItem(name="TestItem", chance=0.5)
        self.assertEqual(item.name, "TestItem")
        self.assertEqual(item.chance, 0.5)
    
    def test_item_chance_validation(self):
        """Test that invalid chance values raise errors"""
        with self.assertRaises(ValueError):
            PresetItem(name="Test", chance=-0.1)
        
        with self.assertRaises(ValueError):
            PresetItem(name="Test", chance=1.5)
    
    def test_item_empty_name(self):
        """Test that empty name raises error"""
        with self.assertRaises(ValueError):
            PresetItem(name="", chance=0.5)

class TestRandomPreset(unittest.TestCase):
    """Test RandomPreset model"""
    
    def test_valid_preset_creation(self):
        """Test creating a valid RandomPreset"""
        preset = RandomPreset(
            preset_type=PresetType.CARGO,
            name="TestPreset",
            chance=0.75
        )
        self.assertEqual(preset.name, "TestPreset")
        self.assertEqual(preset.chance, 0.75)
        self.assertEqual(preset.preset_type, PresetType.CARGO)
        self.assertEqual(preset.get_item_count(), 0)
    
    def test_preset_chance_validation(self):
        """Test that invalid chance values raise errors"""
        with self.assertRaises(ValueError):
            RandomPreset(
                preset_type=PresetType.CARGO,
                name="Test",
                chance=-0.1
            )
        
        with self.assertRaises(ValueError):
            RandomPreset(
                preset_type=PresetType.CARGO,
                name="Test",
                chance=1.5
            )
    
    def test_add_remove_items(self):
        """Test adding and removing items"""
        preset = RandomPreset(
            preset_type=PresetType.CARGO,
            name="Test",
            chance=0.5
        )
        
        item1 = PresetItem(name="Item1", chance=0.3)
        item2 = PresetItem(name="Item2", chance=0.7)
        
        preset.add_item(item1)
        preset.add_item(item2)
        self.assertEqual(preset.get_item_count(), 2)
        
        preset.remove_item(0)
        self.assertEqual(preset.get_item_count(), 1)
        self.assertEqual(preset.items[0].name, "Item2")
    
    def test_preset_clone(self):
        """Test cloning a preset"""
        preset = RandomPreset(
            preset_type=PresetType.ATTACHMENTS,
            name="Original",
            chance=0.5
        )
        preset.add_item(PresetItem(name="Item1", chance=0.3))
        
        clone = preset.clone()
        self.assertEqual(clone.name, preset.name)
        self.assertEqual(clone.chance, preset.chance)
        self.assertEqual(clone.get_item_count(), preset.get_item_count())
        
        # Verify it's a deep copy
        clone.name = "Modified"
        self.assertEqual(preset.name, "Original")

class TestRandomPresetsFile(unittest.TestCase):
    """Test RandomPresetsFile model"""
    
    def test_add_presets(self):
        """Test adding presets to file"""
        file = RandomPresetsFile(source_file="test.xml")
        
        cargo = RandomPreset(PresetType.CARGO, "Cargo1", 0.5)
        attach = RandomPreset(PresetType.ATTACHMENTS, "Attach1", 0.3)
        
        file.add_preset(cargo)
        file.add_preset(attach)
        
        self.assertEqual(len(file.cargo_presets), 1)
        self.assertEqual(len(file.attachments_presets), 1)
        self.assertEqual(file.get_total_preset_count(), 2)
    
    def test_get_preset_by_name(self):
        """Test finding preset by name"""
        file = RandomPresetsFile(source_file="test.xml")
        
        cargo = RandomPreset(PresetType.CARGO, "Cargo1", 0.5)
        file.add_preset(cargo)
        
        found = file.get_preset_by_name("Cargo1")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Cargo1")
        
        not_found = file.get_preset_by_name("DoesNotExist")
        self.assertIsNone(not_found)
    
    def test_remove_preset(self):
        """Test removing preset from file"""
        file = RandomPresetsFile(source_file="test.xml")
        
        cargo = RandomPreset(PresetType.CARGO, "Cargo1", 0.5)
        file.add_preset(cargo)
        self.assertEqual(file.get_total_preset_count(), 1)
        
        file.remove_preset(cargo)
        self.assertEqual(file.get_total_preset_count(), 0)

class TestRandomPresetsParser(unittest.TestCase):
    """Test RandomPresetsParser"""
    
    def test_parse_valid_xml(self):
        """Test parsing valid XML"""
        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<randompresets>
    <cargo name="FoodBoxPreset" chance="0.40">
        <item name="Apple" chance="0.30" />
        <item name="Pear" chance="0.25" />
    </cargo>
    <attachments name="MilitaryPreset" chance="0.60">
        <item name="Bayonet" chance="0.15" />
    </attachments>
</randompresets>'''
        
        result = RandomPresetsParser.parse(xml, "test.xml")
        
        self.assertEqual(result.source_file, "test.xml")
        self.assertEqual(len(result.cargo_presets), 1)
        self.assertEqual(len(result.attachments_presets), 1)
        
        # Check cargo preset
        cargo = result.cargo_presets[0]
        self.assertEqual(cargo.name, "FoodBoxPreset")
        self.assertEqual(cargo.chance, 0.40)
        self.assertEqual(cargo.get_item_count(), 2)
        self.assertEqual(cargo.items[0].name, "Apple")
        self.assertEqual(cargo.items[0].chance, 0.30)
        
        # Check attachments preset
        attach = result.attachments_presets[0]
        self.assertEqual(attach.name, "MilitaryPreset")
        self.assertEqual(attach.chance, 0.60)
        self.assertEqual(attach.get_item_count(), 1)
    
    def test_parse_missing_root(self):
        """Test parsing XML with wrong root element"""
        xml = '''<?xml version="1.0"?>
<wrongroot>
    <cargo name="Test" chance="0.5">
        <item name="Item1" chance="0.3" />
    </cargo>
</wrongroot>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("randompresets", str(context.exception))
    
    def test_parse_missing_preset_name(self):
        """Test parsing preset without name attribute"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo chance="0.5">
        <item name="Item1" chance="0.3" />
    </cargo>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("name", str(context.exception).lower())
    
    def test_parse_missing_preset_chance(self):
        """Test parsing preset without chance attribute"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo name="Test">
        <item name="Item1" chance="0.3" />
    </cargo>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("chance", str(context.exception).lower())
    
    def test_parse_invalid_chance_value(self):
        """Test parsing with invalid chance values"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo name="Test" chance="1.5">
        <item name="Item1" chance="0.3" />
    </cargo>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("0.0", str(context.exception))
        self.assertIn("1.0", str(context.exception))
    
    def test_parse_missing_item_name(self):
        """Test parsing item without name attribute"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo name="Test" chance="0.5">
        <item chance="0.3" />
    </cargo>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("name", str(context.exception).lower())
    
    def test_parse_preset_without_items(self):
        """Test parsing preset with no items"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo name="EmptyPreset" chance="0.5">
    </cargo>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("no items", str(context.exception).lower())
    
    def test_parse_no_presets(self):
        """Test parsing file with no presets"""
        xml = '''<?xml version="1.0"?>
<randompresets>
</randompresets>'''
        
        with self.assertRaises(ValueError) as context:
            RandomPresetsParser.parse(xml, "test.xml")
        self.assertIn("no cargo", str(context.exception).lower())
    
    def test_validate_xml_valid(self):
        """Test XML validation with valid content"""
        xml = '''<?xml version="1.0"?>
<randompresets>
    <cargo name="Test" chance="0.5">
        <item name="Item1" chance="0.3" />
    </cargo>
</randompresets>'''
        
        is_valid, message = RandomPresetsParser.validate_xml(xml)
        self.assertTrue(is_valid)
    
    def test_validate_xml_invalid(self):
        """Test XML validation with invalid content"""
        xml = '''<?xml version="1.0"?>
<wrongroot>
</wrongroot>'''
        
        is_valid, message = RandomPresetsParser.validate_xml(xml)
        self.assertFalse(is_valid)
        self.assertIn("randompresets", message.lower())

class TestRandomPresetsWriter(unittest.TestCase):
    """Test RandomPresetsWriter"""
    
    def test_write_simple_file(self):
        """Test writing a simple preset file"""
        file = RandomPresetsFile(source_file="test.xml")
        
        cargo = RandomPreset(PresetType.CARGO, "TestCargo", 0.50)
        cargo.add_item(PresetItem("Apple", 0.30))
        cargo.add_item(PresetItem("Pear", 0.25))
        
        file.add_preset(cargo)
        
        xml_str = RandomPresetsWriter.write(file, pretty_print=False)
        
        # Parse result to verify structure
        root = ET.fromstring(xml_str)
        self.assertEqual(root.tag, "randompresets")
        
        cargo_elem = root.find("cargo")
        self.assertIsNotNone(cargo_elem)
        self.assertEqual(cargo_elem.get("name"), "TestCargo")
        self.assertEqual(cargo_elem.get("chance"), "0.50")
        
        items = cargo_elem.findall("item")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].get("name"), "Apple")
        self.assertEqual(items[0].get("chance"), "0.30")
    
    def test_write_with_comments(self):
        """Test that comments are preserved in output"""
        file = RandomPresetsFile(source_file="test.xml")
        
        # Add header and footer comments
        file.header_comments = ["<!--This is a header comment-->"]
        file.footer_comments = ["<!--This is a footer comment-->"]
        
        # Add preset with comment
        cargo = RandomPreset(PresetType.CARGO, "TestPreset", 0.50)
        cargo.add_item(PresetItem("Item1", 0.30))
        file.add_preset(cargo)
        
        file.preset_comments["TestPreset"] = ["<!--This preset does something-->"]
        
        xml_str = RandomPresetsWriter.write(file)
        
        # Verify comments are in output
        self.assertIn("<!--This is a header comment-->", xml_str)
        self.assertIn("<!--This is a footer comment-->", xml_str)
        self.assertIn("<!--This preset does something-->", xml_str)
        
        # Verify comment positions
        self.assertTrue(xml_str.find("<!--This is a header comment-->") < xml_str.find("<randompresets>"))
        self.assertTrue(xml_str.find("<!--This preset does something-->") < xml_str.find('name="TestPreset"'))
        self.assertTrue(xml_str.find("<!--This is a footer comment-->") > xml_str.find("</randompresets>"))
    
    def test_write_both_types(self):
        """Test writing both cargo and attachments"""
        file = RandomPresetsFile(source_file="test.xml")
        
        cargo = RandomPreset(PresetType.CARGO, "Cargo1", 0.40)
        cargo.add_item(PresetItem("Item1", 0.20))
        
        attach = RandomPreset(PresetType.ATTACHMENTS, "Attach1", 0.60)
        attach.add_item(PresetItem("Item2", 0.15))
        
        file.add_preset(cargo)
        file.add_preset(attach)
        
        xml_str = RandomPresetsWriter.write(file, pretty_print=False)
        
        root = ET.fromstring(xml_str)
        self.assertEqual(len(root.findall("cargo")), 1)
        self.assertEqual(len(root.findall("attachments")), 1)
    
    def test_roundtrip_parse_write(self):
        """Test parsing and writing produces equivalent structure"""
        original_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<randompresets>
    <cargo name="TestPreset" chance="0.40">
        <item name="Apple" chance="0.30" />
        <item name="Pear" chance="0.25" />
    </cargo>
</randompresets>'''
        
        # Parse
        parsed = RandomPresetsParser.parse(original_xml, "test.xml")
        
        # Write
        written_xml = RandomPresetsWriter.write(parsed, pretty_print=False)
        
        # Parse again
        reparsed = RandomPresetsParser.parse(written_xml, "test.xml")
        
        # Verify structure matches
        self.assertEqual(len(reparsed.cargo_presets), 1)
        cargo = reparsed.cargo_presets[0]
        self.assertEqual(cargo.name, "TestPreset")
        self.assertEqual(cargo.chance, 0.40)
        self.assertEqual(cargo.get_item_count(), 2)

if __name__ == '__main__':
    unittest.main()
