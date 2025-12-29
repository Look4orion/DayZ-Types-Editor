"""
Local File Manager
Handles reading/writing files from local filesystem (mirrors SFTP manager interface)
"""
from pathlib import Path
from typing import List, Tuple, Optional
import os

class LocalFileManager:
    def __init__(self):
        self.connected = False
        self.mission_path = None
    
    def connect(self, mission_path: str) -> Tuple[bool, str]:
        """
        Connect to local mission folder
        Returns: (success: bool, message: str)
        """
        try:
            path = Path(mission_path)
            
            if not path.exists():
                return False, f"Path does not exist: {mission_path}"
            
            if not path.is_dir():
                return False, f"Path is not a directory: {mission_path}"
            
            # Check for cfgeconomycore.xml
            economy_file = path / 'cfgeconomycore.xml'
            if not economy_file.exists():
                return False, f"cfgeconomycore.xml not found in {mission_path}"
            
            self.mission_path = str(path)
            self.connected = True
            
            return True, f"Opened local mission folder: {mission_path}"
            
        except Exception as e:
            self.disconnect()
            return False, f"Error opening folder: {str(e)}"
    
    def disconnect(self):
        """Disconnect from local folder"""
        self.connected = False
        self.mission_path = None
    
    def is_connected(self) -> bool:
        """Check if currently connected"""
        return self.connected
    
    def get_connection_info(self) -> str:
        """Get formatted connection info string"""
        if self.is_connected():
            return f"Local: {self.mission_path}"
        return "Not connected"
    
    def read_file(self, relative_path: str) -> str:
        """
        Read a file from the local mission folder
        Returns file contents as string
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to local folder")
        
        try:
            # Handle both absolute and relative paths
            if Path(relative_path).is_absolute():
                full_path = Path(relative_path)
            else:
                full_path = Path(self.mission_path) / relative_path
            
            # Try exact path first
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Try case-insensitive match
            dir_path = full_path.parent
            file_name = full_path.name
            
            if dir_path.exists():
                for f in dir_path.iterdir():
                    if f.name.lower() == file_name.lower():
                        with open(f, 'r', encoding='utf-8') as file:
                            return file.read()
            
            raise FileNotFoundError(f"File not found: {relative_path}")
            
        except Exception as e:
            raise IOError(f"Failed to read file {relative_path}: {str(e)}")
    
    def write_file(self, relative_path: str, content: str):
        """
        Write a file to the local mission folder
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to local folder")
        
        try:
            if Path(relative_path).is_absolute():
                full_path = Path(relative_path)
            else:
                # Start with mission path
                full_path = Path(self.mission_path)
                
                # Navigate through each path component with case-insensitive matching
                parts = relative_path.replace('\\', '/').split('/')
                for part in parts:
                    if not part:
                        continue
                    
                    # Try to find existing directory/file with case-insensitive match
                    matched = None
                    if full_path.exists():
                        for item in full_path.iterdir():
                            if item.name.lower() == part.lower():
                                matched = item
                                break
                    
                    if matched:
                        # Use the actual case-sensitive name
                        full_path = matched
                    else:
                        # Doesn't exist yet, use the provided case
                        full_path = full_path / part
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise IOError(f"Failed to write file {relative_path}: {str(e)}")
    
    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists"""
        if not self.is_connected():
            return False
        
        try:
            if Path(relative_path).is_absolute():
                full_path = Path(relative_path)
            else:
                full_path = Path(self.mission_path) / relative_path
            
            return full_path.exists()
        except:
            return False
    
    def get_file_mtime(self, relative_path: str) -> Optional[float]:
        """Get file modification time (Unix timestamp)"""
        if not self.is_connected():
            return None
        
        try:
            if Path(relative_path).is_absolute():
                full_path = Path(relative_path)
            else:
                # Use case-insensitive resolution
                full_path = Path(self.mission_path)
                parts = relative_path.replace('\\', '/').split('/')
                for part in parts:
                    if not part:
                        continue
                    matched = None
                    if full_path.exists():
                        for item in full_path.iterdir():
                            if item.name.lower() == part.lower():
                                matched = item
                                break
                    if matched:
                        full_path = matched
                    else:
                        full_path = full_path / part
            
            if full_path.exists():
                return full_path.stat().st_mtime
            return None
        except Exception:
            return None
    
    def list_directory(self, relative_path: str = "") -> List[str]:
        """List files in a directory"""
        if not self.is_connected():
            raise ConnectionError("Not connected to local folder")
        
        try:
            if relative_path:
                full_path = Path(self.mission_path) / relative_path
            else:
                full_path = Path(self.mission_path)
            
            return [f.name for f in full_path.iterdir()]
        except Exception as e:
            raise IOError(f"Failed to list directory {relative_path}: {str(e)}")
