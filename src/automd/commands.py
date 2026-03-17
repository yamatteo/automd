"""
Command implementations for init and update operations
"""

import asyncio
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Tuple
import signal

from .scanner import DirectoryScanner
from .gitignore import GitTracker


class BaseCommand:
    """Base class for AutoMD commands"""
    
    def __init__(self):
        self.scanner = None
        self.git_tracker = None
    
    async def execute(self, project_path: str) -> str:
        """Execute the command"""
        raise NotImplementedError
    
    def _get_user_permission(self, action: str) -> bool:
        """Get interactive user permission for an action"""
        def timeout_handler(signum, frame):
            raise TimeoutError("Input timeout")
        
        while True:
            try:
                # Set a 30-second timeout for input
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                response = input(f"Do you want to {action}? (y/n): ").strip().lower()
                
                # Cancel the alarm after successful input
                signal.alarm(0)
                
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' or 'n'")
                    
            except Exception as e:
                print(f"Error reading input: {e}. Defaulting to 'no' for safety.")
                return False
    
    def _generate_automd_content(self, directory: Path) -> str:
        """Generate content for .auto.md file with timestamp header"""
        scan_result = self.scanner.scan_directory(directory)
        items = scan_result["items"]
        errors = scan_result["errors"]
        
        # Generate content with timestamp header
        content = f"last_updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        content += "# Folder content\n\n"
        
        # Add errors first if any
        if errors:
            for error in errors:
                content += f"{error}\n"
            content += "\n"
        
        # Add directory contents
        if items:
            for item in items:
                content += f"- {item}\n"
        else:
            content += "(empty)\n"
        
        return content
    
    def _parse_last_updated(self, automd_path: Path) -> Optional[date]:
        """Parse the last_updated date from an existing .auto.md file"""
        try:
            if not automd_path.exists():
                return None
            
            with open(automd_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('last_updated:'):
                date_str = first_line.split(':', 1)[1].strip()
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            
            return None
        
        except (ValueError, IndexError, OSError):
            return None
    
    def _should_update_directory(self, directory: Path, automd_path: Path) -> Tuple[bool, str]:
        """Determine if a directory should be updated based on git changes"""
        # If no git tracker, always update (fallback behavior)
        if not self.git_tracker or not self.git_tracker.is_git_repo:
            return True, "No git repository available"
        
        # Parse last updated date from existing file
        last_updated = self._parse_last_updated(automd_path)
        if last_updated is None:
            return True, "No last_updated date found"
        
        # Get changed directories since last update
        changed_dirs = self.git_tracker.get_changed_directories_since(
            datetime.combine(last_updated, datetime.min.time())
        )
        
        # Check if this directory or any subdirectory has changes
        if directory in changed_dirs:
            return True, f"Directory has direct changes since {last_updated}"
        
        # Check if any subdirectory has changes (hierarchical update)
        for changed_dir in changed_dirs:
            try:
                if changed_dir.is_relative_to(directory):
                    return True, f"Subdirectory {changed_dir.relative_to(directory)} has changes since {last_updated}"
            except ValueError:
                # Not a subdirectory
                pass
        
        return False, f"No changes since {last_updated}"


class InitCommand(BaseCommand):
    """Initialize AutoMD by creating .auto.md files"""
    
    async def execute(self, project_path: str) -> str:
        """Execute init command"""
        project_root = Path(project_path).resolve()
        
        if not project_root.exists():
            return f"Error: Project path '{project_path}' does not exist"
        
        self.scanner = DirectoryScanner(project_root)
        self.git_tracker = GitTracker(project_root)
        
        # Check for existing .auto.md files
        existing_files = self.scanner.check_existing_automd_files()
        if existing_files:
            file_list = '\n'.join(str(f) for f in sorted(existing_files))
            return f"Error: Found existing .auto.md files. Init cannot proceed:\n{file_list}"
        
        # Get user permission
        if not self._get_user_permission(f"initialize AutoMD in '{project_root}'"):
            return "Init cancelled by user"
        
        # Find all directories and create .auto.md files
        directories = self.scanner.find_all_directories()
        created_files = []
        errors = []
        
        for directory in directories:
            try:
                content = self._generate_automd_content(directory)
                automd_path = directory / ".auto.md"
                
                with open(automd_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                created_files.append(str(automd_path.relative_to(project_root)))
            
            except Exception as e:
                errors.append(f"Error creating {directory}/.auto.md: {str(e)}")
        
        # Generate result message
        result_parts = []
        if created_files:
            result_parts.append(f"Successfully created {len(created_files)} .auto.md files:")
            result_parts.extend(f"  {file}" for file in sorted(created_files))
        
        if errors:
            result_parts.append(f"\nEncountered {len(errors)} errors:")
            result_parts.extend(f"  {error}" for error in errors)
        
        return '\n'.join(result_parts) if result_parts else "No files were created"


class UpdateCommand(BaseCommand):
    """Update .auto.md files with smart git-based change detection"""
    
    async def execute(self, project_path: str) -> str:
        """Execute smart update command"""
        project_root = Path(project_path).resolve()
        
        if not project_root.exists():
            return f"Error: Project path '{project_path}' does not exist"
        
        self.scanner = DirectoryScanner(project_root)
        self.git_tracker = GitTracker(project_root)
        
        # Get user permission
        if not self._get_user_permission(f"update AutoMD files in '{project_root}'"):
            return "Update cancelled by user"
        
        # Find all directories and check which need updating
        directories = self.scanner.find_all_directories()
        updated_files = []
        skipped_files = []
        errors = []
        
        for directory in directories:
            automd_path = directory / ".auto.md"
            
            try:
                # Check if directory should be updated
                should_update, reason = self._should_update_directory(directory, automd_path)
                
                if should_update:
                    content = self._generate_automd_content(directory)
                    
                    with open(automd_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    updated_files.append(str(automd_path.relative_to(project_root)))
                else:
                    skipped_files.append(str(automd_path.relative_to(project_root)))
                
            except Exception as e:
                errors.append(f"Error updating {directory}/.auto.md: {str(e)}")
        
        # Generate result message
        result_parts = []
        
        if updated_files:
            result_parts.append(f"Successfully updated {len(updated_files)} .auto.md files:")
            result_parts.extend(f"  {file}" for file in sorted(updated_files))
        
        if skipped_files:
            result_parts.append(f"\nSkipped {len(skipped_files)} unchanged files:")
            result_parts.extend(f"  {file}" for file in sorted(skipped_files))
        
        if errors:
            result_parts.append(f"\nEncountered {len(errors)} errors:")
            result_parts.extend(f"  {error}" for error in errors)
        
        # Add git status information
        if self.git_tracker.is_git_repo:
            result_parts.append(f"\nGit integration: Enabled")
        else:
            result_parts.append(f"\nGit integration: Not available (updated all files)")
        
        return '\n'.join(result_parts) if result_parts else "No files were updated"
