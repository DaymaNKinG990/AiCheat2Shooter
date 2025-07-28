import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class FileManager:
    """File management system for AiCheat2Shooter application"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.uploads_path = self.base_path / "uploads"
        self.exports_path = self.base_path / "exports"
        self.temp_path = self.base_path / "temp"
        
        # Create necessary directories
        self._create_directories()
        
        # File tracking
        self.files_db = self._load_files_db()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for path in [self.base_path, self.uploads_path, self.exports_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _load_files_db(self) -> Dict:
        """Load files database"""
        db_file = self.base_path / "files_db.json"
        if db_file.exists():
            with open(db_file, 'r') as f:
                return json.load(f)
        return {"files": [], "folders": []}
    
    def _save_files_db(self):
        """Save files database"""
        db_file = self.base_path / "files_db.json"
        with open(db_file, 'w') as f:
            json.dump(self.files_db, f, indent=2)
    
    def add_file(self, file_path: str, category: str = "general") -> Dict:
        """Add a file to the application"""
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = source_path.suffix
        filename = f"{timestamp}_{source_path.stem}{file_ext}"
        dest_path = self.uploads_path / filename
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        # Create file record
        file_record = {
            "id": len(self.files_db["files"]) + 1,
            "original_name": source_path.name,
            "stored_name": filename,
            "path": str(dest_path),
            "size": source_path.stat().st_size,
            "category": category,
            "upload_date": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        self.files_db["files"].append(file_record)
        self._save_files_db()
        
        return file_record
    
    def get_files(self, category: Optional[str] = None) -> List[Dict]:
        """Get list of files, optionally filtered by category"""
        files = self.files_db["files"]
        if category:
            files = [f for f in files if f["category"] == category]
        return files
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict]:
        """Get file by ID"""
        for file in self.files_db["files"]:
            if file["id"] == file_id:
                return file
        return None
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a file"""
        file_record = self.get_file_by_id(file_id)
        if not file_record:
            return False
        
        # Remove file from disk
        file_path = Path(file_record["path"])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from database
        self.files_db["files"] = [f for f in self.files_db["files"] if f["id"] != file_id]
        self._save_files_db()
        
        return True
    
    def create_folder(self, folder_name: str, parent_path: str = None) -> Dict:
        """Create a new folder"""
        if parent_path:
            folder_path = Path(parent_path) / folder_name
        else:
            folder_path = self.base_path / folder_name
        
        folder_path.mkdir(parents=True, exist_ok=True)
        
        folder_record = {
            "id": len(self.files_db["folders"]) + 1,
            "name": folder_name,
            "path": str(folder_path),
            "created_date": datetime.now().isoformat(),
            "parent": parent_path
        }
        
        self.files_db["folders"].append(folder_record)
        self._save_files_db()
        
        return folder_record
    
    def get_folders(self) -> List[Dict]:
        """Get list of folders"""
        return self.files_db["folders"]
    
    def export_results(self, data: Dict, filename: str, format: str = "json") -> str:
        """Export analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            export_file = self.exports_path / f"{timestamp}_{filename}.json"
            with open(export_file, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == "txt":
            export_file = self.exports_path / f"{timestamp}_{filename}.txt"
            with open(export_file, 'w') as f:
                f.write(str(data))
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return str(export_file)
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get detailed file information"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_directory": path.is_dir()
        }
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_path.glob("*"):
            if temp_file.is_file():
                temp_file.unlink()
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        total_files = len(self.files_db["files"])
        total_size = sum(f["size"] for f in self.files_db["files"])
        total_folders = len(self.files_db["folders"])
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_folders": total_folders,
            "categories": list(set(f["category"] for f in self.files_db["files"]))
        } 