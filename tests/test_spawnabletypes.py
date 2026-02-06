"""
Tests for Spawnable Types Parser, Model, and Writer
"""
import unittest
from models.spawnable_type import (
    SpawnableType, CargoBlock, AttachmentsBlock, SpawnableItem, SpawnableTypesFile
)
from core.spawnabletypes_parser import SpawnableTypesParser
from core.spawnabletypes_writer import SpawnableTypesWriter


class TestSpawnableItem(unittest.TestCase):
    """Test SpawnableItem model"""
    
    def test_valid_item_with_chance(self):
        item = SpawnableItem(name="Apple", chance=0.5)
        self.assertEqual(item.name, "Apple")
        self.assertEqual(item.chance, 0.5)
        self.assertEqual(item.get_effective_chance(), 0.5)
    
    def test_valid_item_without_chance(self):
        item = SpawnableItem(name="Apple")
        self.assertEqual(item.name, "Apple")
        self.assertIsNone(item.chance)
        self.assertEqual(item.get_effective_chance(), 1.0)
    
    def test_invalid_empty_name(self):
        with self.assertRaises(ValueError):
            SpawnableItem(name="")
    
    def test_invalid_chance_too_low(self):
        with self.assertRaises(ValueError):
            SpawnableItem(name="Apple", chance=-0.1)
    
    def test_invalid_chance_too_high(self):
        with self.assertRaises(ValueError):
            SpawnableItem(name="Apple", chance=1.5)


class TestCargoBlock(unittest.TestCase):
    """Test CargoBlock model"""
    
    def test_valid_preset_based(self):
        block = CargoBlock(preset="foodArmy")
        self.assertTrue(block.is_preset_based())
        self.assertFalse(block.is_chance_based())
    
    def test_valid_chance_based(self):
        item = SpawnableItem(name="Apple", chance=0.5)
        block = CargoBlock(chance=0.8, items=[item])
        self.assertFalse(block.is_preset_based())
        self.assertTrue(block.is_chance_based())
    
    def test_invalid_both_preset_and_chance(self):
        with self.assertRaises(ValueError):
            CargoBlock(preset="foodArmy", chance=0.5)
    
    def test_invalid_neither_preset_nor_chance(self):
        with self.assertRaises(ValueError):
            CargoBlock()
    
    def test_invalid_chance_without_items(self):
        with self.assertRaises(ValueError):
            CargoBlock(chance=0.5, items=[])
    
    def test_invalid_preset_with_items(self):
        item = SpawnableItem(name="Apple")
        with self.assertRaises(ValueError):
            CargoBlock(preset="foodArmy", items=[item])
    
    def test_has_items_missing_chance_single_item(self):
        item = SpawnableItem(name="Apple")
        block = CargoBlock(chance=0.5, items=[item])
        self.assertFalse(block.has_items_missing_chance())
    
    def test_has_items_missing_chance_multiple_with_missing(self):
        item1 = SpawnableItem(name="Apple", chance=0.5)
        item2 = SpawnableItem(name="Pear")  # Missing chance
        block = CargoBlock(chance=0.8, items=[item1, item2])
        self.assertTrue(block.has_items_missing_chance())
    
    def test_has_items_missing_chance_multiple_all_present(self):
        item1 = SpawnableItem(name="Apple", chance=0.5)
        item2 = SpawnableItem(name="Pear", chance=0.3)
        block = CargoBlock(chance=0.8, items=[item1, item2])
        self.assertFalse(block.has_items_missing_chance())


class TestSpawnableType(unittest.TestCase):
    """Test SpawnableType model"""
    
    def test_valid_minimal_type(self):
        spawnable_type = SpawnableType(name="TestZombie")
        self.assertEqual(spawnable_type.name, "TestZombie")
        self.assertFalse(spawnable_type.hoarder)
        self.assertEqual(spawnable_type.get_cargo_count(), 0)
        self.assertEqual(spawnable_type.get_attachments_count(), 0)
    
    def test_valid_type_with_damage(self):
        spawnable_type = SpawnableType(name="TestZombie", damage_min=0.0, damage_max=0.5)
        self.assertTrue(spawnable_type.has_damage())
        self.assertEqual(spawnable_type.damage_min, 0.0)
        self.assertEqual(spawnable_type.damage_max, 0.5)
    
    def test_invalid_empty_name(self):
        with self.assertRaises(ValueError):
            SpawnableType(name="")
    
    def test_invalid_damage_min_too_low(self):
        with self.assertRaises(ValueError):
            SpawnableType(name="Test", damage_min=-0.1)
    
    def test_invalid_damage_max_too_high(self):
        with self.assertRaises(ValueError):
            SpawnableType(name="Test", damage_max=1.5)
    
    def test_invalid_damage_min_greater_than_max(self):
        with self.assertRaises(ValueError):
            SpawnableType(name="Test", damage_min=0.8, damage_max=0.2)
    
    def test_has_validation_warnings(self):
        item1 = SpawnableItem(name="Apple", chance=0.5)
        item2 = SpawnableItem(name="Pear")  # Missing chance
        block = CargoBlock(chance=0.8, items=[item1, item2])
        spawnable_type = SpawnableType(name="Test", cargo_blocks=[block])
        self.assertTrue(spawnable_type.has_validation_warnings())


class TestSpawnableTypesParser(unittest.TestCase):
    """Test SpawnableTypesParser"""
    
    def test_parse_minimal_type(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(len(result.types), 1)
        self.assertEqual(result.types[0].name, "TestType")
    
    def test_parse_type_with_hoarder(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="Barrel_Blue">
        <hoarder />
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertTrue(result.types[0].hoarder)
    
    def test_parse_type_with_damage(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
        <damage min="0.0" max="0.5" />
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(result.types[0].damage_min, 0.0)
        self.assertEqual(result.types[0].damage_max, 0.5)
    
    def test_parse_preset_based_cargo(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
        <cargo preset="foodArmy" />
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(len(result.types[0].cargo_blocks), 1)
        self.assertEqual(result.types[0].cargo_blocks[0].preset, "foodArmy")
    
    def test_parse_chance_based_cargo_single_item(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
        <cargo chance="0.5">
            <item name="Apple" />
        </cargo>
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        cargo = result.types[0].cargo_blocks[0]
        self.assertEqual(cargo.chance, 0.5)
        self.assertEqual(len(cargo.items), 1)
        self.assertEqual(cargo.items[0].name, "Apple")
        self.assertIsNone(cargo.items[0].chance)
    
    def test_parse_chance_based_cargo_multiple_items(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
        <cargo chance="0.5">
            <item name="Apple" chance="0.8" />
            <item name="Pear" chance="0.5" />
        </cargo>
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        cargo = result.types[0].cargo_blocks[0]
        self.assertEqual(len(cargo.items), 2)
        self.assertEqual(cargo.items[0].name, "Apple")
        self.assertEqual(cargo.items[0].chance, 0.8)
        self.assertEqual(cargo.items[1].name, "Pear")
        self.assertEqual(cargo.items[1].chance, 0.5)
    
    def test_parse_preset_based_attachments(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="TestType">
        <attachments preset="hatsArmy" />
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(len(result.types[0].attachments_blocks), 1)
        self.assertEqual(result.types[0].attachments_blocks[0].preset, "hatsArmy")
    
    def test_parse_multiple_types(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type name="Type1">
        <hoarder />
    </type>
    <type name="Type2">
        <damage min="0.0" max="1.0" />
    </type>
</spawnabletypes>'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(len(result.types), 2)
        self.assertEqual(result.types[0].name, "Type1")
        self.assertEqual(result.types[1].name, "Type2")
    
    def test_parse_comment_preservation(self):
        xml = '''<?xml version="1.0"?>
<!-- Header comment -->
<spawnabletypes>
    <!-- Type comment -->
    <type name="TestType">
    </type>
</spawnabletypes>
<!-- Footer comment -->'''
        
        result = SpawnableTypesParser.parse(xml, "test.xml")
        self.assertEqual(len(result.header_comments), 1)
        self.assertIn("Header comment", result.header_comments[0])
        self.assertEqual(len(result.footer_comments), 1)
        self.assertIn("Footer comment", result.footer_comments[0])
        self.assertIn("TestType", result.type_comments)
    
    def test_parse_error_invalid_root(self):
        xml = '''<?xml version="1.0"?>
<wrongroot>
</wrongroot>'''
        
        with self.assertRaises(Exception) as ctx:
            SpawnableTypesParser.parse(xml, "test.xml")
        self.assertIn("Root element must be", str(ctx.exception))
    
    def test_parse_error_missing_type_name(self):
        xml = '''<?xml version="1.0"?>
<spawnabletypes>
    <type>
    </type>
</spawnabletypes>'''
        
        with self.assertRaises(Exception) as ctx:
            SpawnableTypesParser.parse(xml, "test.xml")
        self.assertIn("missing required 'name'", str(ctx.exception))


class TestSpawnableTypesWriter(unittest.TestCase):
    """Test SpawnableTypesWriter"""
    
    def test_write_minimal_type(self):
        spawnable_type = SpawnableType(name="TestType")
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<type name="TestType">', xml)
        self.assertIn('</type>', xml)
    
    def test_write_type_with_hoarder(self):
        spawnable_type = SpawnableType(name="TestType", hoarder=True)
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<hoarder />', xml)
    
    def test_write_type_with_damage(self):
        spawnable_type = SpawnableType(name="TestType", damage_min=0.0, damage_max=0.5)
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<damage min="0.0" max="0.5" />', xml)
    
    def test_write_preset_based_cargo(self):
        cargo = CargoBlock(preset="foodArmy")
        spawnable_type = SpawnableType(name="TestType", cargo_blocks=[cargo])
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<cargo preset="foodArmy" />', xml)
    
    def test_write_chance_based_cargo_single_item(self):
        item = SpawnableItem(name="Apple")
        cargo = CargoBlock(chance=0.5, items=[item])
        spawnable_type = SpawnableType(name="TestType", cargo_blocks=[cargo])
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<cargo chance="0.5">', xml)
        self.assertIn('<item name="Apple" />', xml)
        self.assertIn('</cargo>', xml)
    
    def test_write_chance_based_cargo_multiple_items(self):
        item1 = SpawnableItem(name="Apple", chance=0.8)
        item2 = SpawnableItem(name="Pear", chance=0.5)
        cargo = CargoBlock(chance=0.5, items=[item1, item2])
        spawnable_type = SpawnableType(name="TestType", cargo_blocks=[cargo])
        file_obj = SpawnableTypesFile(types=[spawnable_type])
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<item name="Apple" chance="0.8" />', xml)
        self.assertIn('<item name="Pear" chance="0.5" />', xml)
    
    def test_write_comment_preservation(self):
        spawnable_type = SpawnableType(name="TestType")
        file_obj = SpawnableTypesFile(
            types=[spawnable_type],
            header_comments=["Header comment"],
            footer_comments=["Footer comment"],
            type_comments={"TestType": ["Type comment"]}
        )
        
        xml = SpawnableTypesWriter.write(file_obj)
        
        self.assertIn('<!-- Header comment -->', xml)
        self.assertIn('<!-- Footer comment -->', xml)
        self.assertIn('<!-- Type comment -->', xml)
    
    def test_roundtrip_integrity(self):
        """Test that parse → write → parse produces identical data"""
        xml = '''<?xml version="1.0"?>
<!-- Test header -->
<spawnabletypes>
    <!-- Type comment -->
    <type name="TestZombie">
        <hoarder />
        <damage min="0.0" max="0.5" />
        <cargo preset="foodArmy" />
        <cargo chance="0.8">
            <item name="Apple" chance="0.5" />
            <item name="Pear" chance="0.3" />
        </cargo>
        <attachments preset="hatsArmy" />
        <attachments chance="1.0">
            <item name="Helmet" chance="1.0" />
        </attachments>
    </type>
</spawnabletypes>
<!-- Test footer -->'''
        
        # Parse
        parsed = SpawnableTypesParser.parse(xml, "test.xml")
        
        # Write
        written_xml = SpawnableTypesWriter.write(parsed)
        
        # Parse again
        reparsed = SpawnableTypesParser.parse(written_xml, "test.xml")
        
        # Verify data integrity
        self.assertEqual(len(parsed.types), len(reparsed.types))
        
        original_type = parsed.types[0]
        reparsed_type = reparsed.types[0]
        
        self.assertEqual(original_type.name, reparsed_type.name)
        self.assertEqual(original_type.hoarder, reparsed_type.hoarder)
        self.assertEqual(original_type.damage_min, reparsed_type.damage_min)
        self.assertEqual(original_type.damage_max, reparsed_type.damage_max)
        self.assertEqual(len(original_type.cargo_blocks), len(reparsed_type.cargo_blocks))
        self.assertEqual(len(original_type.attachments_blocks), len(reparsed_type.attachments_blocks))
        
        # Verify comments preserved
        self.assertEqual(len(parsed.header_comments), len(reparsed.header_comments))
        self.assertEqual(len(parsed.footer_comments), len(reparsed.footer_comments))


if __name__ == '__main__':
    unittest.main()
