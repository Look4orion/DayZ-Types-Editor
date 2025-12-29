"""
Backup Manager
Handles creating and managing local backups of types.xml files
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import json

class BackupManager:
    """Manages local backups of server files"""
    
    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file if it doesn't exist
        self.metadata_file = self.backup_dir / 'backup_metadata.json'
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _load_metadata(self) -> dict:
        """Load backup metadata"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_metadata(self, metadata: dict):
        """Save backup metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def create_backup(self, file_path: str, content: str) -> str:
        """
        Create a backup of a file
        Args:
            file_path: Relative path of the file (e.g., "types.xml" or "CustomMods/mod/types.xml")
            content: File content to backup
        Returns:
            Path to the backup file
        """
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create backup filename
        # Replace path separators with underscores for flat storage
        safe_name = file_path.replace('/', '_').replace('\\', '_')
        backup_name = f"{timestamp}_{safe_name}"
        
        # Create backup path
        backup_path = self.backup_dir / backup_name
        
        # Write backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update metadata
        metadata = self._load_metadata()
        if file_path not in metadata:
            metadata[file_path] = []
        
        metadata[file_path].append({
            'timestamp': timestamp,
            'backup_file': backup_name,
            'size': len(content)
        })
        
        self._save_metadata(metadata)
        
        return str(backup_path)
    
    def get_backup_history(self, file_path: str) -> List[dict]:
        """Get backup history for a specific file"""
        metadata = self._load_metadata()
        return metadata.get(file_path, [])
    
    def get_all_backups(self) -> List[Tuple[str, List[dict]]]:
        """Get all backups grouped by file"""
        metadata = self._load_metadata()
        return [(file_path, backups) for file_path, backups in metadata.items()]
    
    def get_backup_statistics(self) -> dict:
        """Get statistics about backups"""
        metadata = self._load_metadata()
        total_backups = sum(len(backups) for backups in metadata.values())
        
        # Calculate total size
        total_size = 0
        for backups in metadata.values():
            for backup in backups:
                backup_file = self.backup_dir / backup['backup_file']
                if backup_file.exists():
                    total_size += backup_file.stat().st_size
        
        return {
            'total_backups': total_backups,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'files_tracked': len(metadata)
        }
    
    def cleanup_old_backups(self, keep_last_n: int = 10) -> int:
        """
        Clean up old backups, keeping only the last N for each file
        Returns: Number of backups deleted
        """
        metadata = self._load_metadata()
        deleted_count = 0
        
        for file_path in metadata:
            backups = metadata[file_path]
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Delete old backups
            for backup in backups[keep_last_n:]:
                backup_file = self.backup_dir / backup['backup_file']
                if backup_file.exists():
                    backup_file.unlink()
                    deleted_count += 1
            
            # Keep only recent backups in metadata
            metadata[file_path] = backups[:keep_last_n]
        
        self._save_metadata(metadata)
        return deleted_count
    
    def restore_backup(self, file_path: str, timestamp: str) -> str:
        """
        Restore a backup
        Returns: Content of the backup file
        """
        metadata = self._load_metadata()
        backups = metadata.get(file_path, [])
        
        for backup in backups:
            if backup['timestamp'] == timestamp:
                backup_file = self.backup_dir / backup['backup_file']
                if backup_file.exists():
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        raise ValueError(f"No backup found for {file_path} at {timestamp}")
    
    def delete_backup(self, file_path: str, timestamp: str) -> bool:
        """Delete a specific backup"""
        metadata = self._load_metadata()
        backups = metadata.get(file_path, [])
        
        for i, backup in enumerate(backups):
            if backup['timestamp'] == timestamp:
                backup_file = self.backup_dir / backup['backup_file']
                if backup_file.exists():
                    backup_file.unlink()
                
                del backups[i]
                metadata[file_path] = backups
                self._save_metadata(metadata)
                return True
        
        return False
