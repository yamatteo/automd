"""
Gitignore pattern matching and git integration functionality
"""

import os
from pathlib import Path
from typing import List, Optional, Set
import pathspec
import subprocess
from datetime import datetime


class GitIgnore:
    """Handles gitignore pattern matching"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.spec = self._load_gitignore()
    
    def _load_gitignore(self) -> Optional[pathspec.PathSpec]:
        """Load gitignore patterns from .gitignore file"""
        gitignore_path = self.project_root / '.gitignore'
        
        if not gitignore_path.exists():
            return None
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
                
                if patterns:
                    return pathspec.PathSpec.from_lines('gitignore', patterns)
        
        except (OSError, UnicodeDecodeError):
            # If we can't read the gitignore file, fall back to no patterns
            pass
        
        return None
    
    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns"""
        if self.spec is None:
            return False
        
        # Convert to relative path string for pattern matching
        try:
            rel_path_str = str(path.relative_to(self.project_root))
        except ValueError:
            # If path is not relative to project root, don't ignore
            return False
        
        # For directories, check if the directory pattern matches (with and without trailing slash)
        if path.is_dir():
            # Check if any pattern matches this directory (with and without trailing slash)
            return self.spec.match_file(rel_path_str) or self.spec.match_file(rel_path_str + "/")
        
        # For files, use normal matching
        return self.spec.match_file(rel_path_str)


class GitTracker:
    """Handles git operations for smart updates"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.is_git_repo = self._check_git_repo()
    
    def _check_git_repo(self) -> bool:
        """Check if the project root is a git repository"""
        git_dir = self.project_root / '.git'
        return git_dir.exists() and git_dir.is_dir()
    
    def _run_git_command(self, args: List[str], timeout: int = 30) -> str:
        """Run a git command with timeout protection"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Git command timed out after {timeout} seconds")
        except subprocess.CalledProcessError as e:
            # If git command fails, return empty string (graceful degradation)
            return ""
        except FileNotFoundError:
            # Git not installed
            return ""
    
    def get_changed_files_since(self, date: datetime) -> Set[Path]:
        """Get files that have changed since a given date"""
        if not self.is_git_repo:
            return set()
        
        date_str = date.strftime('%Y-%m-%d')
        
        # Get list of changed files since the given date
        output = self._run_git_command([
            'log', '--name-only', '--since', date_str, '--pretty=format:'
        ])
        
        if not output:
            return set()
        
        changed_files = set()
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith(' '):  # Skip empty lines and commit messages
                file_path = self.project_root / line
                if file_path.exists():  # Only include files that still exist
                    changed_files.add(file_path)
        
        return changed_files
    
    def get_changed_directories_since(self, date: datetime) -> Set[Path]:
        """Get directories that contain changed files since a given date"""
        changed_files = self.get_changed_files_since(date)
        changed_dirs = set()
        
        for file_path in changed_files:
            # Add the file's directory and all parent directories up to project root
            current_dir = file_path.parent
            while current_dir != self.project_root.parent and current_dir != self.project_root:
                if current_dir == self.project_root:
                    changed_dirs.add(current_dir)
                    break
                changed_dirs.add(current_dir)
                current_dir = current_dir.parent
        
        return changed_dirs
