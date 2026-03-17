"""
pytest configuration and fixtures for AutoMD tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary project directory for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def project_with_files(temp_project_dir: Path) -> Path:
    """Create a project directory with some test files"""
    # Create some test files
    (temp_project_dir / "main.py").write_text("print('hello')")
    (temp_project_dir / "README.md").write_text("# Test Project")
    
    # Create subdirectories
    src_dir = temp_project_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("def main(): pass")
    
    tests_dir = temp_project_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("def test_app(): pass")
    
    return temp_project_dir


@pytest.fixture
def project_with_gitignore(temp_project_dir: Path) -> Path:
    """Create a project directory with .gitignore file"""
    (temp_project_dir / ".gitignore").write_text("""
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
""")
    
    # Create some files that should be ignored
    venv_dir = temp_project_dir / "venv"
    venv_dir.mkdir()
    (venv_dir / "python").write_text("fake python")
    
    (temp_project_dir / ".DS_Store").write_text("mac file")
    
    # Create some files that should not be ignored
    (temp_project_dir / "main.py").write_text("print('hello')")
    
    return temp_project_dir
