"""
Directory scanning functionality for AutoMD
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from .gitignore import GitIgnore


class DirectoryScanner:
    """Scans directories and generates file listings"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.gitignore = GitIgnore(project_root)
    
    def find_all_directories(self) -> List[Path]:
        """Find all directories in the project root"""
        directories = []
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Skip hidden directories (except .git for gitignore support)
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']
            
            # Check if current directory should be processed
            if self.gitignore.should_ignore(root_path):
                continue
                
            directories.append(root_path)
        
        return directories
    
    def scan_directory(self, directory: Path) -> Dict[str, Any]:
        """Scan a single directory and return its contents"""
        items = []
        errors = []
        
        try:
            for entry in directory.iterdir():
                # Skip .auto.md files (they're our output)
                if entry.name == '.auto.md':
                    continue
                
                # Skip hidden files and directories
                if entry.name.startswith('.'):
                    continue
                
                # Get relative path for gitignore checking
                rel_path = entry.relative_to(self.project_root)
                if self.gitignore.should_ignore(entry):
                    continue
                
                # Format the item
                if entry.is_dir():
                    items.append(f"{entry.name}/")
                else:
                    items.append(entry.name)
        
        except PermissionError as e:
            errors.append(f"Permission denied: {e}")
        except OSError as e:
            errors.append(f"System error: {e}")
        
        return {
            "items": sorted(items),
            "errors": errors
        }
    
    def check_existing_automd_files(self) -> List[Path]:
        """Check for existing .auto.md files in the project"""
        existing_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            if '.auto.md' in files:
                existing_files.append(Path(root) / '.auto.md')
        
        return existing_files
