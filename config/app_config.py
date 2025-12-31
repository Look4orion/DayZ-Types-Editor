"""
App Configuration Manager
Handles loading and saving application settings to JSON
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64

class AppConfig:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to user's home directory
            config_dir = Path.home() / '.dayz_types_editor'
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / 'config.json'
        else:
            self.config_path = Path(config_path)
        
        self.key_file = self.config_path.parent / '.key'
        self._encryption_key = self._get_or_create_key()
        self.config = self._load_config()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for credentials"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Make key file read-only
            os.chmod(self.key_file, 0o600)
            return key
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        f = Fernet(self._encryption_key)
        return f.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt sensitive data"""
        f = Fernet(self._encryption_key)
        return f.decrypt(data.encode()).decode()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'sftp': {
                'host': '',
                'port': 22,
                'username': '',
                'password_encrypted': '',
                'mission_path': '',
                'save_credentials': False,
                'last_connected': None
            },
            'file_cache': {},  # path -> {'timestamp': ..., 'content': ...}
            'map_profiles': [],
            'active_map_profile': None,
            'backup_location': str(Path.home() / 'DayZEditor' / 'Backups'),
            'window_geometry': None,
            'window_state': None
        }
    
    def save(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    # SFTP Settings
    def get_sftp_config(self) -> Dict[str, Any]:
        """Get SFTP configuration"""
        config = self.config['sftp'].copy()
        if config.get('password_encrypted') and config.get('save_credentials'):
            try:
                config['password'] = self._decrypt(config['password_encrypted'])
            except Exception:
                config['password'] = ''
        else:
            config['password'] = ''
        return config
    
    def set_sftp_config(self, host: str, port: int, username: str, 
                        password: str, mission_path: str, save_credentials: bool):
        """Set SFTP configuration"""
        self.config['sftp'] = {
            'host': host,
            'port': port,
            'username': username,
            'password_encrypted': self._encrypt(password) if save_credentials else '',
            'mission_path': mission_path,
            'save_credentials': save_credentials,
            'last_connected': self.config['sftp'].get('last_connected')
        }
        self.save()
    
    def update_last_connected(self):
        """Update last connected timestamp"""
        from datetime import datetime
        self.config['sftp']['last_connected'] = datetime.now().isoformat()
        self.save()
    
    # Map Profile Settings
    def get_map_profiles(self) -> list:
        """Get all map profiles"""
        return self.config.get('map_profiles', [])
    
    def add_map_profile(self, profile: Dict[str, Any]):
        """Add a new map profile"""
        if 'map_profiles' not in self.config:
            self.config['map_profiles'] = []
        self.config['map_profiles'].append(profile)
        self.save()
    
    def update_map_profile(self, index: int, profile: Dict[str, Any]):
        """Update an existing map profile"""
        if 0 <= index < len(self.config['map_profiles']):
            self.config['map_profiles'][index] = profile
            self.save()
    
    def delete_map_profile(self, index: int):
        """Delete a map profile"""
        if 0 <= index < len(self.config['map_profiles']):
            del self.config['map_profiles'][index]
            if self.config['active_map_profile'] == index:
                self.config['active_map_profile'] = None
            elif self.config['active_map_profile'] and self.config['active_map_profile'] > index:
                self.config['active_map_profile'] -= 1
            self.save()
    
    def get_active_map_profile(self) -> Optional[Dict[str, Any]]:
        """Get the currently active map profile"""
        idx = self.config.get('active_map_profile')
        if idx is not None and 0 <= idx < len(self.config['map_profiles']):
            return self.config['map_profiles'][idx]
        return None
    
    def set_active_map_profile(self, index: Optional[int]):
        """Set the active map profile"""
        self.config['active_map_profile'] = index
        self.save()
    
    # Backup Settings
    def get_backup_location(self) -> str:
        """Get backup directory location"""
        return self.config.get('backup_location', str(Path.home() / 'DayZEditor' / 'Backups'))
    
    def set_backup_location(self, path: str):
        """Set backup directory location"""
        self.config['backup_location'] = path
        self.save()
    
    # Window State
    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.config.get('window_geometry')
    
    def set_window_geometry(self, geometry):
        """Save window geometry"""
        self.config['window_geometry'] = geometry
        self.save()
    
    def get_window_state(self):
        """Get saved window state"""
        return self.config.get('window_state')
    
    def set_window_state(self, state):
        """Save window state"""
        self.config['window_state'] = state
        self.save()
    
    # File Cache
    def get_cached_file(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cached file data if it exists"""
        if 'file_cache' not in self.config:
            self.config['file_cache'] = {}
        return self.config['file_cache'].get(path)
    
    def set_cached_file(self, path: str, timestamp: float, content: str):
        """Cache a file with its timestamp"""
        if 'file_cache' not in self.config:
            self.config['file_cache'] = {}
        self.config['file_cache'][path] = {
            'timestamp': timestamp,
            'content': content
        }
        self.save()
    
    def clear_file_cache(self):
        """Clear all cached files"""
        self.config['file_cache'] = {}
        self.save()
