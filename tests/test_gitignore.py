"""
Tests for the GitIgnore functionality
"""

import pytest
from pathlib import Path

from automd.gitignore import GitIgnore


class TestGitIgnore:
    """Test cases for GitIgnore"""
    
    def test_no_gitignore_file(self, temp_project_dir: Path):
        """Test behavior when no .gitignore file exists"""
        gitignore = GitIgnore(temp_project_dir)
        
        assert gitignore.spec is None
        assert not gitignore.should_ignore(temp_project_dir / "any_file.txt")
    
    def test_empty_gitignore(self, project_with_files: Path):
        """Test behavior with empty .gitignore file"""
        (project_with_files / ".gitignore").write_text("")
        
        gitignore = GitIgnore(project_with_files)
        
        # Should not ignore anything
        assert not gitignore.should_ignore(project_with_files / "file.txt")
        assert not gitignore.should_ignore(project_with_files / "dir")
    
    def test_simple_patterns(self, project_with_files: Path):
        """Test simple gitignore patterns"""
        gitignore_content = """
*.pyc
*.pyo
__pycache__/
.DS_Store
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        # Create the directories that should be ignored
        (project_with_files / "__pycache__").mkdir()
        
        gitignore = GitIgnore(project_with_files)
        
        # Should ignore .pyc files
        assert gitignore.should_ignore(project_with_files / "main.pyc")
        assert gitignore.should_ignore(project_with_files / "module.pyc")
        
        # Should ignore .pyo files
        assert gitignore.should_ignore(project_with_files / "main.pyo")
        
        # Should ignore __pycache__ directory
        assert gitignore.should_ignore(project_with_files / "__pycache__")
        assert gitignore.should_ignore(project_with_files / "__pycache__" / "file.pyc")
        
        # Should ignore .DS_Store
        assert gitignore.should_ignore(project_with_files / ".DS_Store")
        
        # Should not ignore .py files
        assert not gitignore.should_ignore(project_with_files / "main.py")
        assert not gitignore.should_ignore(project_with_files / "src" / "app.py")
    
    def test_negation_patterns(self, project_with_files: Path):
        """Test negation patterns"""
        gitignore_content = """
*.log
!important.log
temp/
!important/
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        # Create the directories
        (project_with_files / "temp").mkdir()
        (project_with_files / "important").mkdir()
        
        gitignore = GitIgnore(project_with_files)
        
        # Should ignore .log files except important.log
        assert gitignore.should_ignore(project_with_files / "debug.log")
        assert gitignore.should_ignore(project_with_files / "error.log")
        assert not gitignore.should_ignore(project_with_files / "important.log")
        
        # Should ignore temp/ directory except important/
        assert gitignore.should_ignore(project_with_files / "temp")
        assert gitignore.should_ignore(project_with_files / "temp" / "file.txt")
        assert not gitignore.should_ignore(project_with_files / "important")
        assert not gitignore.should_ignore(project_with_files / "important" / "file.txt")
    
    def test_directory_patterns(self, project_with_files: Path):
        """Test directory-specific patterns"""
        gitignore_content = """
src/*.pyc
tests/test_*.py
build/
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        # Create the build directory
        (project_with_files / "build").mkdir()
        
        gitignore = GitIgnore(project_with_files)
        
        # Should ignore .pyc files in src/
        assert gitignore.should_ignore(project_with_files / "src" / "module.pyc")
        assert not gitignore.should_ignore(project_with_files / "main.pyc")  # Not in src/
        
        # Should ignore test_*.py files in tests/
        assert gitignore.should_ignore(project_with_files / "tests" / "test_app.py")
        assert not gitignore.should_ignore(project_with_files / "tests" / "conftest.py")  # Doesn't match pattern
        assert not gitignore.should_ignore(project_with_files / "test_app.py")  # Not in tests/
        
        # Should ignore build/ directory
        assert gitignore.should_ignore(project_with_files / "build")
        assert gitignore.should_ignore(project_with_files / "build" / "output.txt")
    
    def test_comments_and_blank_lines(self, project_with_files: Path):
        """Test that comments and blank lines are ignored"""
        gitignore_content = """
# This is a comment
*.pyc

# Another comment
*.pyo

# Final comment
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        gitignore = GitIgnore(project_with_files)
        
        # Should still work with comments present
        assert gitignore.should_ignore(project_with_files / "main.pyc")
        assert gitignore.should_ignore(project_with_files / "main.pyo")
        assert not gitignore.should_ignore(project_with_files / "main.py")
    
    def test_complex_patterns(self, project_with_files: Path):
        """Test complex gitignore patterns"""
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        # Create some directories that should be ignored
        (project_with_files / "__pycache__").mkdir()
        (project_with_files / "env").mkdir()
        (project_with_files / "venv").mkdir()
        (project_with_files / ".venv").mkdir()
        (project_with_files / ".vscode").mkdir()
        (project_with_files / ".idea").mkdir()
        
        # Create the .Python file (not directory)
        (project_with_files / ".Python").write_text("Python build file")
        
        gitignore = GitIgnore(project_with_files)
        
        # Test Python patterns
        assert gitignore.should_ignore(project_with_files / "__pycache__")
        assert gitignore.should_ignore(project_with_files / "main.pyc")
        assert gitignore.should_ignore(project_with_files / "main.pyd")
        assert gitignore.should_ignore(project_with_files / "module.pyo")
        assert gitignore.should_ignore(project_with_files / "app.so")
        assert gitignore.should_ignore(project_with_files / ".Python")
        assert gitignore.should_ignore(project_with_files / "env")
        assert gitignore.should_ignore(project_with_files / "venv")
        assert gitignore.should_ignore(project_with_files / ".venv")
        
        # Test IDE patterns
        assert gitignore.should_ignore(project_with_files / ".vscode")
        assert gitignore.should_ignore(project_with_files / ".idea")
        assert gitignore.should_ignore(project_with_files / "file.swp")
        assert gitignore.should_ignore(project_with_files / "file.swo")
        
        # Test OS patterns
        assert gitignore.should_ignore(project_with_files / ".DS_Store")
        assert gitignore.should_ignore(project_with_files / "Thumbs.db")
        
        # Should not ignore normal files
        assert not gitignore.should_ignore(project_with_files / "main.py")
        assert not gitignore.should_ignore(project_with_files / "README.md")
    
    def test_gitignore_file_errors(self, project_with_files: Path):
        """Test handling of gitignore file read errors"""
        # Create a gitignore file with invalid encoding (binary)
        (project_with_files / ".gitignore").write_bytes(b'\x00\x01\x02')
        
        gitignore = GitIgnore(project_with_files)
        
        # Should handle gracefully - the spec might still be created but should work
        # Let's test that it doesn't crash and behaves reasonably
        result = gitignore.should_ignore(project_with_files / "any_file.txt")
        # The result should be a boolean, not an exception
        assert isinstance(result, bool)
    
    def test_nested_directory_patterns(self, project_with_files: Path):
        """Test patterns in nested directories"""
        gitignore_content = """
*.pyc
docs/*.html
src/**/*.tmp
"""
        (project_with_files / ".gitignore").write_text(gitignore_content)
        
        gitignore = GitIgnore(project_with_files)
        
        # Should ignore .pyc files anywhere
        assert gitignore.should_ignore(project_with_files / "main.pyc")
        assert gitignore.should_ignore(project_with_files / "src" / "module.pyc")
        assert gitignore.should_ignore(project_with_files / "deep" / "nested" / "file.pyc")
        
        # Should ignore .html files in docs/
        assert gitignore.should_ignore(project_with_files / "docs" / "index.html")
        assert not gitignore.should_ignore(project_with_files / "index.html")  # Not in docs/
        
        # Should ignore .tmp files in src/ and subdirectories
        assert gitignore.should_ignore(project_with_files / "src" / "temp.tmp")
        assert gitignore.should_ignore(project_with_files / "src" / "deep" / "nested.tmp")
