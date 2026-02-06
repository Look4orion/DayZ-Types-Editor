"""
Spawnable Types XML Writer
Generates cfgspawnabletypes.xml with comment preservation
"""
from models.spawnable_type import SpawnableTypesFile, SpawnableType, CargoBlock, AttachmentsBlock


class SpawnableTypesWriter:
    """Writer for cfgspawnabletypes.xml files"""
    
    @staticmethod
    def write(spawnable_types_file: SpawnableTypesFile) -> str:
        """
        Generate XML content from spawnable types file
        
        Args:
            spawnable_types_file: SpawnableTypesFile object
            
        Returns:
            XML string content
        """
        lines = []
        
        # XML declaration
        lines.append('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>')
        
        # Header comments (only add if not empty)
        if spawnable_types_file.header_comments:
            lines.append('')
            for comment in spawnable_types_file.header_comments:
                lines.append(f'<!-- {comment} -->')
        
        # Root element
        lines.append('')
        lines.append('<spawnabletypes>')
        
        # Write each type
        for spawnable_type in spawnable_types_file.types:
            # Type-specific comments
            if spawnable_type.name in spawnable_types_file.type_comments:
                for comment in spawnable_types_file.type_comments[spawnable_type.name]:
                    lines.append(f'\t<!-- {comment} -->')
            
            lines.extend(SpawnableTypesWriter._write_type(spawnable_type))
        
        # Close root element
        lines.append('</spawnabletypes>')
        
        # Footer comments (only add if not empty)
        if spawnable_types_file.footer_comments:
            for comment in spawnable_types_file.footer_comments:
                lines.append(f'<!-- {comment} -->')
        
        return '\n'.join(lines)
    
    @staticmethod
    def _write_type(spawnable_type: SpawnableType) -> list:
        """Write a single type element"""
        lines = []
        
        # Opening tag
        lines.append(f'\t<type name="{spawnable_type.name}">')
        
        # Hoarder
        if spawnable_type.hoarder:
            lines.append('\t\t<hoarder />')
        
        # Damage
        if spawnable_type.has_damage():
            damage_attrs = []
            if spawnable_type.damage_min is not None:
                damage_attrs.append(f'min="{spawnable_type.damage_min}"')
            if spawnable_type.damage_max is not None:
                damage_attrs.append(f'max="{spawnable_type.damage_max}"')
            lines.append(f'\t\t<damage {" ".join(damage_attrs)} />')
        
        # Tag (preserved but not editable)
        if spawnable_type.tag:
            lines.append(f'\t\t<tag name="{spawnable_type.tag}" />')
        
        # Cargo blocks
        for cargo_block in spawnable_type.cargo_blocks:
            lines.extend(SpawnableTypesWriter._write_cargo_block(cargo_block))
        
        # Attachments blocks
        for attachments_block in spawnable_type.attachments_blocks:
            lines.extend(SpawnableTypesWriter._write_attachments_block(attachments_block))
        
        # Closing tag
        lines.append('\t</type>')
        
        return lines
    
    @staticmethod
    def _write_cargo_block(cargo_block: CargoBlock) -> list:
        """Write a cargo block element"""
        lines = []
        
        if cargo_block.is_preset_based():
            # Preset-based cargo
            lines.append(f'\t\t<cargo preset="{cargo_block.preset}" />')
        
        elif cargo_block.is_chance_based():
            # Chance-based cargo with items
            if len(cargo_block.items) == 0:
                # Empty block (shouldn't happen due to validation, but handle it)
                lines.append(f'\t\t<cargo chance="{cargo_block.chance}" />')
            elif cargo_block.chance == 1.0:
                # Chance is 1.0 - omit the attribute (it's implicit)
                lines.append('\t\t<cargo>')
                for item in cargo_block.items:
                    if item.chance is not None:
                        lines.append(f'\t\t\t<item name="{item.name}" chance="{item.chance}" />')
                    else:
                        lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</cargo>')
            elif len(cargo_block.items) == 1 and cargo_block.items[0].chance is None:
                # Single item without chance - inline format
                item = cargo_block.items[0]
                lines.append(f'\t\t<cargo chance="{cargo_block.chance}">')
                lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</cargo>')
            else:
                # Multiple items or item with chance - multi-line format
                lines.append(f'\t\t<cargo chance="{cargo_block.chance}">')
                for item in cargo_block.items:
                    if item.chance is not None:
                        lines.append(f'\t\t\t<item name="{item.name}" chance="{item.chance}" />')
                    else:
                        lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</cargo>')
        
        return lines
    
    @staticmethod
    def _write_attachments_block(attachments_block: AttachmentsBlock) -> list:
        """Write an attachments block element"""
        lines = []
        
        if attachments_block.is_preset_based():
            # Preset-based attachments
            lines.append(f'\t\t<attachments preset="{attachments_block.preset}" />')
        
        elif attachments_block.is_chance_based():
            # Chance-based attachments with items
            if len(attachments_block.items) == 0:
                # Empty block (shouldn't happen due to validation, but handle it)
                lines.append(f'\t\t<attachments chance="{attachments_block.chance}" />')
            elif attachments_block.chance == 1.0:
                # Chance is 1.0 - omit the attribute (it's implicit)
                lines.append('\t\t<attachments>')
                for item in attachments_block.items:
                    if item.chance is not None:
                        lines.append(f'\t\t\t<item name="{item.name}" chance="{item.chance}" />')
                    else:
                        lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</attachments>')
            elif len(attachments_block.items) == 1 and attachments_block.items[0].chance is None:
                # Single item without chance - inline format
                item = attachments_block.items[0]
                lines.append(f'\t\t<attachments chance="{attachments_block.chance}">')
                lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</attachments>')
            else:
                # Multiple items or item with chance - multi-line format
                lines.append(f'\t\t<attachments chance="{attachments_block.chance}">')
                for item in attachments_block.items:
                    if item.chance is not None:
                        lines.append(f'\t\t\t<item name="{item.name}" chance="{item.chance}" />')
                    else:
                        lines.append(f'\t\t\t<item name="{item.name}" />')
                lines.append('\t\t</attachments>')
        
        return lines
    
    @staticmethod
    def write_to_file(spawnable_types_file: SpawnableTypesFile, filepath: str):
        """
        Write spawnable types to file
        
        Args:
            spawnable_types_file: SpawnableTypesFile object
            filepath: Output file path
        """
        xml_content = SpawnableTypesWriter.write(spawnable_types_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
