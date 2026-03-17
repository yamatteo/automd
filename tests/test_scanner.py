"""
Tests for the DirectoryScanner
"""

import pytest
from pathlib import Path

from automd.scanner import DirectoryScanner


class TestDirectoryScanner:
    """Test cases for DirectoryScanner"""
    
    def test_find_all_directories(self, project_with_files: Path):
        """Test finding all directories in project"""
        scanner = DirectoryScanner(project_with_files)
        
        directories = scanner.find_all_directories()
        
        # Should find root, src, and tests directories
        dir_paths = [d.relative_to(project_with_files) for d in directories]
        assert Path(".") in dir_paths
        assert Path("src") in dir_paths
        assert Path("tests") in dir_paths
    
    def test_scan_directory_with_files(self, project_with_files: Path):
        """Test scanning a directory with files"""
        scanner = DirectoryScanner(project_with_files)
        
        result = scanner.scan_directory(project_with_files)
        
        assert "items" in result
        assert "errors" in result
        
        items = result["items"]
        assert "main.py" in items
        assert "README.md" in items
        assert "src/" in items
        assert "tests/" in items
        assert len(result["errors"]) == 0
    
    def test_scan_empty_directory(self, temp_project_dir: Path):
        """Test scanning an empty directory"""
        scanner = DirectoryScanner(temp_project_dir)
        
        result = scanner.scan_directory(temp_project_dir)
        
        assert len(result["items"]) == 0
        assert len(result["errors"]) == 0
    
    def test_scan_subdirectory(self, project_with_files: Path):
        """Test scanning a subdirectory"""
        scanner = DirectoryScanner(project_with_files)
        
        src_dir = project_with_files / "src"
        result = scanner.scan_directory(src_dir)
        
        assert "app.py" in result["items"]
        assert len(result["errors"]) == 0
    
    def test_check_existing_automd_files(self, project_with_files: Path):
        """Test checking for existing .auto.md files"""
        # Create some .auto.md files
        (project_with_files / ".auto.md").write_text("Root content")
        (project_with_files / "src" / ".auto.md").write_text("Src content")
        
        scanner = DirectoryScanner(project_with_files)
        
        existing_files = scanner.check_existing_automd_files()
        
        assert len(existing_files) == 2
        assert project_with_files / ".auto.md" in existing_files
        assert project_with_files / "src" / ".auto.md" in existing_files
    
    def test_scan_ignores_auto_md_files(self, project_with_files: Path):
        """Test that scanning ignores .auto.md files"""
        # Create .auto.md file
        (project_with_files / ".auto.md").write_text("Content")
        
        scanner = DirectoryScanner(project_with_files)
        result = scanner.scan_directory(project_with_files)
        
        assert ".auto.md" not in result["items"]
    
    def test_scan_ignores_hidden_files(self, project_with_files: Path):
        """Test that scanning ignores hidden files"""
        # Create hidden files
        (project_with_files / ".hidden").write_text("Hidden file")
        (project_with_files / ".hidden_dir").mkdir()
        (project_with_files / ".hidden_dir" / "file.txt").write_text("Hidden dir file")
        
        scanner = DirectoryScanner(project_with_files)
        result = scanner.scan_directory(project_with_files)
        
        assert ".hidden" not in result["items"]
        assert ".hidden_dir/" not in result["items"]
    
    def test_scan_respects_gitignore(self, project_with_gitignore: Path):
        """Test that scanning respects gitignore patterns"""
        scanner = DirectoryScanner(project_with_gitignore)
        result = scanner.scan_directory(project_with_gitignore)
        
        items = result["items"]
        
        # Should not include ignored files/directories
        assert "venv/" not in items
        assert ".DS_Store" not in items
        
        # Should include non-ignored files
        assert "main.py" in items
    
    def test_scan_permission_error(self, project_with_files: Path):
        """Test handling of permission errors"""
        # Create a directory without read permissions
        no_access_dir = project_with_files / "no_access"
        no_access_dir.mkdir()
        
        # Remove read permissions (if possible)
        try:
            no_access_dir.chmod(0o000)
            
            scanner = DirectoryScanner(project_with_files)
            result = scanner.scan_directory(no_access_dir)
            
            # Should have an error
            assert len(result["errors"]) > 0
            assert any("permission" in error.lower() for error in result["errors"])
            
        except PermissionError:
            # Skip test if we can't change permissions
            pytest.skip("Cannot change directory permissions")
        finally:
            # Restore permissions for cleanup
            try:
                no_access_dir.chmod(0o755)
            except PermissionError:
                pass
