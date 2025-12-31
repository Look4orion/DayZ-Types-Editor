"""
SFTP Manager
Handles SFTP connections and file operations
"""
import paramiko
from pathlib import Path
from typing import Optional, List, Tuple
import io

class SFTPManager:
    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.connected = False
        self.host = None
        self.port = None
        self.username = None
        self.mission_path = None
    
    def connect(self, host: str, port: int, username: str, password: str, mission_path: str) -> Tuple[bool, str]:
        """
        Connect to SFTP server
        Returns: (success: bool, message: str)
        """
        try:
            self.disconnect()  # Close any existing connection
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10
            )
            
            self.sftp = self.client.open_sftp()
            self.connected = True
            self.host = host
            self.port = port
            self.username = username
            self.mission_path = mission_path
            
            # Verify mission path exists
            try:
                self.sftp.stat(mission_path)
            except FileNotFoundError:
                self.disconnect()
                return False, f"Mission path not found: {mission_path}"
            
            return True, f"Connected to {host}:{port}"
            
        except paramiko.AuthenticationException:
            self.disconnect()
            return False, "Authentication failed - check username/password"
        except paramiko.SSHException as e:
            self.disconnect()
            return False, f"SSH error: {str(e)}"
        except Exception as e:
            self.disconnect()
            return False, f"Connection error: {str(e)}"
    
    def disconnect(self):
        """Disconnect from SFTP server"""
        if self.sftp:
            try:
                self.sftp.close()
            except:
                pass
            self.sftp = None
        
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        
        self.connected = False
        self.host = None
        self.port = None
        self.username = None
        self.mission_path = None
    
    def is_connected(self) -> bool:
        """Check if currently connected"""
        return self.connected and self.sftp is not None
    
    def get_connection_info(self) -> str:
        """Get formatted connection info string"""
        if self.is_connected():
            return f"{self.username}@{self.host}:{self.port}"
        return "Not connected"
    
    def list_directory(self, path: str) -> List[str]:
        """List files in a directory"""
        if not self.is_connected():
            raise ConnectionError("Not connected to SFTP server")
        
        try:
            full_path = f"{self.mission_path}/{path}" if path else self.mission_path
            return self.sftp.listdir(full_path)
        except Exception as e:
            raise IOError(f"Failed to list directory {path}: {str(e)}")
    
    def read_file(self, remote_path: str) -> str:
        """
        Read a file from the server
        Returns file contents as string
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to SFTP server")
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                # Absolute path
                full_path = remote_path
            else:
                # Relative path - prepend mission path
                mission = self.mission_path.rstrip('/')
                full_path = f"{mission}/{remote_path}"
            
            # Try to read the file directly first
            try:
                with self.sftp.open(full_path, 'r') as f:
                    return f.read().decode('utf-8')
            except FileNotFoundError:
                # File not found - try case-insensitive search
                # Split path into directory and filename
                import posixpath
                parts = remote_path.split('/')
                
                # Start from mission path
                current_path = self.mission_path.rstrip('/')
                
                # Navigate through each directory part with case-insensitive matching
                for i, part in enumerate(parts):
                    if not part:
                        continue
                    
                    try:
                        # List current directory
                        entries = self.sftp.listdir(current_path)
                        
                        # Find case-insensitive match
                        matched = None
                        for entry in entries:
                            if entry.lower() == part.lower():
                                matched = entry
                                break
                        
                        if matched:
                            current_path = posixpath.join(current_path, matched)
                        else:
                            # No match found
                            raise FileNotFoundError(f"Path component '{part}' not found in {current_path}")
                    except:
                        raise
                
                # Try reading with corrected path
                with self.sftp.open(current_path, 'r') as f:
                    return f.read().decode('utf-8')
                
        except Exception as e:
            raise IOError(f"Failed to read file {remote_path}: {str(e)}")
    
    def write_file(self, remote_path: str, content: str):
        """
        Write a file to the server
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to SFTP server")
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                # Absolute path
                full_path = remote_path
            else:
                # Relative path - prepend mission path
                mission = self.mission_path.rstrip('/')
                full_path = f"{mission}/{remote_path}"
            
            # Resolve path with case-insensitive matching
            resolved_path = self._resolve_path_case_insensitive(full_path)
            
            # Ensure parent directory exists
            import posixpath
            parent_dir = posixpath.dirname(resolved_path)
            try:
                self.sftp.stat(parent_dir)
            except FileNotFoundError:
                # Create parent directories if they don't exist
                self._makedirs(parent_dir)
            
            # Write file
            with self.sftp.open(resolved_path, 'w') as f:
                f.write(content.encode('utf-8'))
        except Exception as e:
            raise IOError(f"Failed to write file {remote_path}: {str(e)}")
    
    def _resolve_path_case_insensitive(self, path: str) -> str:
        """
        Resolve a path using case-insensitive matching for existing directories.
        Returns the path with actual casing from the server.
        """
        parts = path.split('/')
        current = ''
        
        for i, part in enumerate(parts):
            if not part:
                current += '/'
                continue
            
            parent = current or '/'
            
            # Try exact match first
            test_path = f"{current}/{part}" if current and not current.endswith('/') else f"{current}{part}"
            try:
                self.sftp.stat(test_path)
                current = test_path
                continue
            except:
                pass
            
            # Try case-insensitive match for existing items
            try:
                entries = self.sftp.listdir(parent)
                matched = None
                for entry in entries:
                    if entry.lower() == part.lower():
                        matched = entry
                        break
                
                if matched:
                    # Use actual case from server
                    current = f"{current}/{matched}" if current and not current.endswith('/') else f"{current}{matched}"
                else:
                    # Doesn't exist - use provided case for new files/dirs
                    current = test_path
            except:
                # Can't list directory - use provided case
                current = test_path
        
        return current
    
    def _makedirs(self, path: str):
        """Recursively create directories"""
        parts = path.split('/')
        current = ''
        for part in parts:
            if not part:
                continue
            current += '/' + part if current else part
            try:
                self.sftp.stat(current)
            except FileNotFoundError:
                try:
                    self.sftp.mkdir(current)
                except OSError:
                    # Directory might already exist, ignore
                    pass
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if a file exists on the server"""
        if not self.is_connected():
            return False
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                full_path = remote_path
            else:
                mission = self.mission_path.rstrip('/')
                full_path = f"{mission}/{remote_path}"
            
            self.sftp.stat(full_path)
            return True
        except FileNotFoundError:
            return False
    
    def get_file_mtime(self, remote_path: str) -> Optional[float]:
        """Get file modification time (Unix timestamp)"""
        if not self.is_connected():
            return None
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                full_path = remote_path
            else:
                mission = self.mission_path.rstrip('/')
                full_path = f"{mission}/{remote_path}"
            
            # Resolve path case-insensitively
            resolved_path = self._resolve_path_case_insensitive(full_path)
            stat = self.sftp.stat(resolved_path)
            return float(stat.st_mtime)
        except Exception:
            return None
    
    def download_file(self, remote_path: str, local_path: str):
        """Download a file from server to local path"""
        if not self.is_connected():
            raise ConnectionError("Not connected to SFTP server")
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                full_remote_path = remote_path
            else:
                mission = self.mission_path.rstrip('/')
                full_remote_path = f"{mission}/{remote_path}"
            
            # Ensure local directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.sftp.get(full_remote_path, local_path)
        except Exception as e:
            raise IOError(f"Failed to download file {remote_path}: {str(e)}")
    
    def upload_file(self, local_path: str, remote_path: str):
        """Upload a file from local path to server"""
        if not self.is_connected():
            raise ConnectionError("Not connected to SFTP server")
        
        try:
            # Handle both absolute and relative paths
            if remote_path.startswith('/'):
                full_remote_path = remote_path
            else:
                mission = self.mission_path.rstrip('/')
                full_remote_path = f"{mission}/{remote_path}"
            
            # Ensure remote directory exists
            import posixpath
            parent_dir = posixpath.dirname(full_remote_path)
            try:
                self.sftp.stat(parent_dir)
            except FileNotFoundError:
                self._makedirs(parent_dir)
            
            self.sftp.put(local_path, full_remote_path)
        except Exception as e:
            raise IOError(f"Failed to upload file {remote_path}: {str(e)}")
