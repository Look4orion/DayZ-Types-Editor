"""
Random Presets Writer
Writes RandomPresetsFile objects back to cfgrandompresets.xml format
"""
from models.random_preset import RandomPresetsFile

class RandomPresetsWriter:
    """Writer for cfgrandompresets.xml files"""
    
    @staticmethod
    def write(presets_file: RandomPresetsFile, pretty_print: bool = True) -> str:
        """
        Convert RandomPresetsFile to XML string with comments preserved
        
        Args:
            presets_file: RandomPresetsFile object to write
            pretty_print: If True, format XML with indentation
            
        Returns:
            XML content as string
        """
        lines = []
        
        # Add XML declaration
        lines.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        
        # Add header comments
        for comment in presets_file.header_comments:
            lines.append(comment)
        
        # Start randompresets tag
        lines.append('<randompresets>')
        
        # Add cargo presets with their comments
        for preset in presets_file.cargo_presets:
            # Add preset comments if any
            if preset.name in presets_file.preset_comments:
                for comment in presets_file.preset_comments[preset.name]:
                    lines.append(f'    {comment}')
            
            # Add preset
            lines.append(f'    <cargo name="{preset.name}" chance="{preset.chance:.2f}">')
            for item in preset.items:
                lines.append(f'        <item name="{item.name}" chance="{item.chance:.2f}"/>')
            lines.append('    </cargo>')
        
        # Add attachments presets with their comments
        for preset in presets_file.attachments_presets:
            # Add preset comments if any
            if preset.name in presets_file.preset_comments:
                for comment in presets_file.preset_comments[preset.name]:
                    lines.append(f'    {comment}')
            
            # Add preset
            lines.append(f'    <attachments name="{preset.name}" chance="{preset.chance:.2f}">')
            for item in preset.items:
                lines.append(f'        <item name="{item.name}" chance="{item.chance:.2f}"/>')
            lines.append('    </attachments>')
        
        # Close randompresets tag
        lines.append('</randompresets>')
        
        # Add footer comments
        for comment in presets_file.footer_comments:
            lines.append(comment)
        
        return '\n'.join(lines)
    
    @staticmethod
    def write_to_file(presets_file: RandomPresetsFile, filepath: str, pretty_print: bool = True):
        """
        Write RandomPresetsFile to a file
        
        Args:
            presets_file: RandomPresetsFile object to write
            filepath: Path to write file to
            pretty_print: If True, format XML with indentation
        """
        xml_content = RandomPresetsWriter.write(presets_file, pretty_print)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
