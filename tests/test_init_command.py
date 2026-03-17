"""
Tests for the InitCommand
"""

import pytest
import asyncio
from pathlib import Path

from automd.commands import InitCommand


class TestInitCommand:
    """Test cases for InitCommand"""
    
    @pytest.mark.asyncio
    async def test_init_success(self, project_with_files: Path):
        """Test successful initialization"""
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(project_with_files))
            
            assert "Successfully created" in result
            assert ".auto.md files" in result
            
            # Check that .auto.md files were created
            auto_md_files = list(project_with_files.rglob(".auto.md"))
            assert len(auto_md_files) > 0
            
            # Check content of root .auto.md
            root_auto_md = project_with_files / ".auto.md"
            assert root_auto_md.exists()
            content = root_auto_md.read_text()
            assert "# Folder content" in content
            assert "main.py" in content
            assert "README.md" in content
            assert "src/" in content
            assert "tests/" in content
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_init_nonexistent_path(self):
        """Test initialization with non-existent path"""
        cmd = InitCommand()
        
        result = await cmd.execute("/nonexistent/path")
        
        assert "Error:" in result
        assert "does not exist" in result
    
    @pytest.mark.asyncio
    async def test_init_cancelled_by_user(self, project_with_files: Path):
        """Test initialization when user cancels"""
        cmd = InitCommand()
        
        # Mock user input to say 'no'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'n'
        
        try:
            result = await cmd.execute(str(project_with_files))
            
            assert "cancelled by user" in result.lower()
            
            # Check that no .auto.md files were created
            auto_md_files = list(project_with_files.rglob(".auto.md"))
            assert len(auto_md_files) == 0
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_init_existing_auto_md_files(self, project_with_files: Path):
        """Test initialization when .auto.md files already exist"""
        # Create an existing .auto.md file
        (project_with_files / ".auto.md").write_text("Existing content")
        
        cmd = InitCommand()
        
        result = await cmd.execute(str(project_with_files))
        
        assert "Error:" in result
        assert "existing .auto.md files" in result.lower()
    
    @pytest.mark.asyncio
    async def test_init_empty_directory(self, temp_project_dir: Path):
        """Test initialization of empty directory"""
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(temp_project_dir))
            
            assert "Successfully created" in result
            
            # Check that .auto.md file was created
            auto_md_file = temp_project_dir / ".auto.md"
            assert auto_md_file.exists()
            content = auto_md_file.read_text()
            assert "# Folder content" in content
            assert "(empty)" in content
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_init_with_gitignore(self, project_with_gitignore: Path):
        """Test initialization respects gitignore patterns"""
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(project_with_gitignore))
            
            assert "Successfully created" in result
            
            # Check that ignored files are not listed
            auto_md_content = (project_with_gitignore / ".auto.md").read_text()
            assert "venv/" not in auto_md_content  # Should be ignored
            assert ".DS_Store" not in auto_md_content  # Should be ignored
            assert "main.py" in auto_md_content  # Should not be ignored
            
        finally:
            builtins.input = original_input
