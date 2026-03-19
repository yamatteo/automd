# AutoMD - Automatic Project Documentation via MCP

AutoMD is a production-ready Model Context Protocol (MCP) server that automatically generates project documentation by creating `.auto.md` files in each directory of your project.

## Features

- **🔒 Enterprise Security**: Path traversal protection, file validation, and secure directory handling
- **📋 Advanced Gitignore Support**: Complex patterns, negation, nested directory support, and error resilience
- **🛡️ Robust Error Handling**: Comprehensive validation, timeout handling, and graceful failure recovery
- **⚡ High Performance**: Optimized for large projects with 20+ directories and deep nesting
- **🔄 MCP Protocol**: Fully-fledged MCP server with JSON-RPC communication and async safety
- **👤 Interactive Authorization**: Commands require user permission by default with 30s timeout
- **🔍 Recursive Scanning**: Scans entire project directory structure efficiently
- **📝 Clean Documentation**: Generates simple, readable `.auto.md` files with proper markdown formatting

## Installation

```bash
pip install -e .
```

## Usage

### As MCP Server

AutoMD is designed to work as an MCP server with AI agents. Configure your agent to use the `automd` MCP server.

### MCP Setup for Claude Code

1. **Install AutoMD** (choose one method):

   **Method A: pip installation**
   ```bash
   git clone https://github.com/yamatteo/automd.git
   cd automd
   pip install -e .
   ```

   **Method B: uv installation (managed environment)**
   ```bash
   # From local source
   uv add --dev automd@/path/to/automd
   
   # Or from GitHub repository
   uv add --dev automd@git+https://github.com/yamatteo/automd.git
   ```

2. **Configure Claude Code**:
   - Open Claude Code settings
   - Navigate to MCP Servers section
   - Add to following configuration:

   **For pip installation:**
   ```json
   {
     "name": "automd",
     "command": "python",
     "args": ["-m", "automd"],
     "env": {}
   }
   ```

   **For uv installation:**
   ```json
   {
     "name": "automd",
     "command": "uv",
     "args": ["run", "python", "-m", "automd"],
     "env": {}
   }
   ```

3. **Restart Claude Code** to load MCP server

4. **Usage in Claude Code**:
   ```
   Please run automd init to document this project
   ```
   Claude will ask for permission before executing the command.

### MCP Setup for Windsurf IDE

1. **Install AutoMD** (choose one method):

   **Method A: pip installation**
   ```bash
   git clone https://github.com/yamatteo/automd.git
   cd automd
   pip install -e .
   ```

   **Method B: uv installation (managed environment)**
   ```bash
   # From local source
   uv add --dev automd@/path/to/automd
   
   # Or from GitHub repository
   uv add --dev automd@git+https://github.com/yamatteo/automd.git
   ```

2. **Configure Windsurf**:
   - Open Windsurf settings (`Ctrl/Cmd + ,`)
   - Search for "MCP" or "Model Context Protocol"
   - Add new MCP server with:

   **For pip installation:**
   - **Name**: `automd`
   - **Command**: `python`
   - **Arguments**: `-m automd`
   - **Working Directory**: `/path/to/your/project`

   **For uv installation:**
   - **Name**: `automd`
   - **Command**: `uv`
   - **Arguments**: `run python -m automd`
   - **Working Directory**: `/path/to/your/project`

3. **Restart Windsurf** to activate MCP server

4. **Usage in Windsurf**:
   - Use the chat interface to request AutoMD operations
   - Example: "Initialize AutoMD for this project"
   - Windsurf will prompt for authorization before running commands

### Available Commands

#### `init`
Initialize AutoMD by creating `.auto.md` files in all directories.

- **Fails** if any `.auto.md` files already exist
- Creates `.auto.md` in each directory with folder contents
- Requires interactive authorization (30s timeout)
- **Security**: Validates paths, prevents overwriting important files
- **Performance**: Efficiently handles large project structures

#### `update`
Smart update of `.auto.md` files using git change detection.

- **Intelligent Updates**: Only updates directories that have changed since last update
- **Git Integration**: Uses git history to detect modified files and directories
- **Timestamp Tracking**: Each `.auto.md` file includes `last_updated: YYYY-MM-DD` header
- **Fallback Mode**: Works in non-git repositories (updates all files)
- **Performance**: Dramatically faster for large projects with minimal changes
- Requires interactive authorization (30s timeout)
- **Security**: Same validation and protection as init

### Example `.auto.md` File Content

```markdown
last_updated: 2026-03-16

# Folder content

- README.md
- pyproject.toml
- src/
- test_automd.py
```

## Configuration

### Gitignore Support
AutoMD respects your project's `.gitignore` file with advanced pattern matching:

- **Basic patterns**: `*.pyc`, `__pycache__`, `.env`
- **Complex patterns**: Negation with `!important.log`, special characters, brackets
- **Directory patterns**: `build/`, `logs/` for directory-specific ignoring
- **Nested support**: Pattern inheritance in subdirectories
- **Error resilience**: Graceful handling of corrupted/unreadable `.gitignore` files

Files and directories matching patterns in `.gitignore` will be excluded from scanning and documentation.

### Security Features
AutoMD includes comprehensive security protections:

- **Path traversal protection**: Blocks access to system directories (`/etc`, `/usr`, `/bin`, etc.)
- **File overwrite protection**: Prevents overwriting important files (`README.md`, `pyproject.toml`, `setup.py`, etc.)
- **Hidden directory protection**: Secure handling of hidden directories with exceptions for `.git` and `.github`
- **Input validation**: Comprehensive validation of all user inputs and file paths
- **Permission handling**: Graceful handling of permission denied scenarios

## Development

### Running Tests

AutoMD includes a comprehensive test suite with 50+ tests covering all functionality:

```bash
# Install development dependencies
uv add --dev pytest pytest-asyncio

# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/test_init_command.py     # Test init functionality
uv run pytest tests/test_scanner.py          # Test directory scanning
uv run pytest tests/test_gitignore.py        # Test gitignore patterns
uv run pytest tests/test_server.py           # Test MCP server
uv run pytest tests/test_integration.py      # Test end-to-end workflows

# Run with coverage
uv run pytest --cov=src/automd
```

### Test Coverage
The test suite covers:
- ✅ **Init/Update commands** - Full workflow testing
- ✅ **Directory scanning** - Simple to complex structures
- ✅ **Gitignore patterns** - Basic to advanced pattern matching
- ✅ **MCP server** - Tool registration and execution
- ✅ **Security features** - Path validation and file protection
- ✅ **Error handling** - Edge cases and failure scenarios
- ✅ **Performance** - Large project structures (20+ directories)
- ✅ **Integration** - End-to-end workflow testing

### Project Structure

```
src/automd/
├── __init__.py         # Main entry point
├── server.py           # MCP server implementation
├── commands.py         # Command implementations (init, update)
├── scanner.py          # Directory scanning logic
└── gitignore.py        # Gitignore parsing

tests/
├── conftest.py         # Test fixtures and utilities
├── test_init_command.py    # Init functionality tests
├── test_scanner.py         # Directory scanning tests
├── test_gitignore.py       # Gitignore pattern tests
├── test_server.py          # MCP server tests
└── test_integration.py     # End-to-end integration tests
```

### Performance & Scalability

AutoMD is optimized for production use:

- **Large Projects**: Tested with 20+ directories and deep nesting
- **Memory Efficiency**: Optimized directory traversal with gitignore filtering
- **Async Safety**: Full async/await implementation for concurrent operations
- **Error Recovery**: Graceful handling of file system errors and permission issues

### Security Considerations

AutoMD implements multiple layers of security:

- **Input Validation**: All user inputs are validated before processing
- **Path Sanitization**: Prevents path traversal attacks
- **File Protection**: Important files cannot be overwritten
- **Permission Checks**: Respects file system permissions
- **Timeout Protection**: Interactive prompts have 30-second timeouts

## Documentation

For detailed implementation information about smart update feature, see [Smart Update Feature Documentation](docs/smart_update_feature.md).

## License

Add your license information here.