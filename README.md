# AutoMD - Automatic Project Documentation via MCP

AutoMD is a Model Context Protocol (MCP) server that automatically generates project documentation by creating `.auto.md` files in each directory of your project.

## Features

- **🔒 Enterprise Security**: Path traversal protection, file validation, and secure directory handling
- **📋 Advanced Gitignore Support**: Complex patterns, negation, nested directory support
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

### Module Execution

You can also run AutoMD directly as a Python module:

```bash
python -m automd
```

## MCP Tools

AutoMD provides two main tools:

### `init`
Initialize AutoMD by creating `.auto.md` files in all directories of your project.

**Parameters:**
- `project_path` (optional): Path to the project directory to scan (default: current directory)

**Example:**
```json
{
  "tool": "init",
  "arguments": {
    "project_path": "/path/to/your/project"
  }
}
```

### `update`
Update all `.auto.md` files by rescanning the project.

**Parameters:**
- `project_path` (optional): Path to the project directory to update (default: current directory)

**Example:**
```json
{
  "tool": "update", 
  "arguments": {
    "project_path": "/path/to/your/project"
  }
}
```

## Generated Documentation

AutoMD creates `.auto.md` files in each directory with the following format:

```markdown
# Folder content

- file1.py
- file2.py
- subdir1/
- subdir2/
```

## Development

This project uses the official **python-mcp-sdk** from https://github.com/modelcontextprotocol/python-sdk.

### Dependencies

- `mcp` - Official Python SDK for Model Context Protocol
- `pathspec>=0.12.1` - Gitignore pattern matching

### Development Setup

```bash
# Install dependencies
uv add mcp pathspec

# Install development dependencies
uv add --dev pytest pytest-asyncio

# Run tests
pytest
```

## License

MIT License