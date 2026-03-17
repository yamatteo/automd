"""
Integration tests for AutoMD
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

from automd.commands import InitCommand, UpdateCommand
from automd.scanner import DirectoryScanner
from automd.gitignore import GitIgnore


class TestIntegration:
    """Integration tests for AutoMD components"""
    
    @pytest.mark.asyncio
    async def test_full_init_workflow(self, temp_project_dir: Path):
        """Test complete init workflow from scratch"""
        # Create some test files
        (temp_project_dir / "main.py").write_text("print('hello')")
        (temp_project_dir / "README.md").write_text("# Test Project")
        
        src_dir = temp_project_dir / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("def main(): pass")
        
        # Run init
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(temp_project_dir))
            
            assert "Successfully created" in result
            
            # Check that .auto.md files were created in all directories
            auto_md_files = list(temp_project_dir.rglob(".auto.md"))
            assert len(auto_md_files) == 2  # root and src
            
            # Check content of root .auto.md
            root_content = (temp_project_dir / ".auto.md").read_text()
            assert "# Folder content" in root_content
            assert "main.py" in root_content
            assert "README.md" in root_content
            assert "src/" in root_content
            
            # Check content of src/.auto.md
            src_content = (temp_project_dir / "src" / ".auto.md").read_text()
            assert "# Folder content" in src_content
            assert "app.py" in src_content
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_init_update_workflow(self, project_with_files: Path):
        """Test init followed by update workflow"""
        cmd_init = InitCommand()
        cmd_update = UpdateCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            # First run init
            init_result = await cmd_init.execute(str(project_with_files))
            assert "Successfully created" in init_result
            
            # Add a new file
            (project_with_files / "new_file.py").write_text("# New file")
            
            # Run update
            update_result = await cmd_update.execute(str(project_with_files))
            assert "Successfully updated" in update_result
            
            # Check that the new file is reflected in .auto.md
            root_content = (project_with_files / ".auto.md").read_text()
            assert "new_file.py" in root_content
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_gitignore_integration(self, project_with_gitignore: Path):
        """Test gitignore integration in full workflow"""
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(project_with_gitignore))
            assert "Successfully created" in result
            
            # Check that ignored files are not in .auto.md
            auto_md_content = (project_with_gitignore / ".auto.md").read_text()
            assert "main.py" in auto_md_content  # Should be included
            assert "venv/" not in auto_md_content  # Should be ignored
            assert ".DS_Store" not in auto_md_content  # Should be ignored
            
        finally:
            builtins.input = original_input
    
    def test_scanner_gitignore_integration(self, project_with_gitignore: Path):
        """Test scanner and gitignore integration"""
        scanner = DirectoryScanner(project_with_gitignore)
        gitignore = GitIgnore(project_with_gitignore)
        
        # Test that scanner respects gitignore
        directories = scanner.find_all_directories()
        
        # Should not include venv directory
        venv_dir = project_with_gitignore / "venv"
        if venv_dir.exists():
            assert venv_dir not in directories
        
        # Test scanning respects gitignore
        result = scanner.scan_directory(project_with_gitignore)
        items = result["items"]
        
        assert "main.py" in items  # Should be included
        assert "venv/" not in items  # Should be ignored
        assert ".DS_Store" not in items  # Should be ignored
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, temp_project_dir: Path):
        """Test error handling in complete workflow"""
        cmd = InitCommand()
        
        # Mock user input to say 'no' to test cancellation
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'n'
        
        try:
            result = await cmd.execute(str(temp_project_dir))
            assert "cancelled by user" in result.lower()
            
            # Should not have created any files
            auto_md_files = list(temp_project_dir.rglob(".auto.md"))
            assert len(auto_md_files) == 0
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_nested_directories_workflow(self, temp_project_dir: Path):
        """Test workflow with deeply nested directories"""
        # Create nested structure
        (temp_project_dir / "level1").mkdir()
        (temp_project_dir / "level1" / "level2").mkdir()
        (temp_project_dir / "level1" / "level2" / "level3").mkdir()
        
        # Add files at different levels
        (temp_project_dir / "root.py").write_text("# Root")
        (temp_project_dir / "level1" / "l1.py").write_text("# Level 1")
        (temp_project_dir / "level1" / "level2" / "l2.py").write_text("# Level 2")
        (temp_project_dir / "level1" / "level2" / "level3" / "l3.py").write_text("# Level 3")
        
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(temp_project_dir))
            assert "Successfully created" in result
            
            # Should have .auto.md files at all levels
            auto_md_files = list(temp_project_dir.rglob(".auto.md"))
            assert len(auto_md_files) == 4  # root + 3 levels
            
            # Check content at each level
            root_content = (temp_project_dir / ".auto.md").read_text()
            assert "root.py" in root_content
            assert "level1/" in root_content
            
            l1_content = (temp_project_dir / "level1" / ".auto.md").read_text()
            assert "l1.py" in l1_content
            assert "level2/" in l1_content
            
            l2_content = (temp_project_dir / "level1" / "level2" / ".auto.md").read_text()
            assert "l2.py" in l2_content
            assert "level3/" in l2_content
            
            l3_content = (temp_project_dir / "level1" / "level2" / "level3" / ".auto.md").read_text()
            assert "l3.py" in l3_content
            assert "(empty)" not in l3_content  # Should have the file
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_large_project_simulation(self, temp_project_dir: Path):
        """Test performance with simulated larger project"""
        # Create many files and directories
        for i in range(10):
            subdir = temp_project_dir / f"dir_{i}"
            subdir.mkdir()
            
            for j in range(5):
                (subdir / f"file_{j}.py").write_text(f"# File {i}-{j}")
        
        cmd = InitCommand()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            result = await cmd.execute(str(temp_project_dir))
            assert "Successfully created" in result
            
            # Should have created .auto.md files for all directories
            auto_md_files = list(temp_project_dir.rglob(".auto.md"))
            assert len(auto_md_files) == 11  # root + 10 subdirs
            
            # Check that each directory has correct content
            for i in range(10):
                auto_md_path = temp_project_dir / f"dir_{i}" / ".auto.md"
                assert auto_md_path.exists()
                
                content = auto_md_path.read_text()
                for j in range(5):
                    assert f"file_{j}.py" in content
                    
        finally:
            builtins.input = original_input
