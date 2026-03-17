"""
Tests for the AutoMD MCP Server
"""

import pytest
import asyncio
from pathlib import Path

from automd.server import AutoMDServer


class TestAutoMDServer:
    """Test cases for AutoMDServer"""
    
    def test_server_instantiation(self):
        """Test that server can be instantiated"""
        server = AutoMDServer()
        assert server is not None
        assert hasattr(server, 'server')
    
    def test_server_creation(self):
        """Test that MCP server is created correctly"""
        server = AutoMDServer()
        assert server.server.name == "automd"
    
    @pytest.mark.asyncio
    async def test_handle_init_tool(self, temp_project_dir: Path):
        """Test handling of init tool call"""
        server = AutoMDServer()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            arguments = {"project_path": str(temp_project_dir)}
            result = await server._handle_init(arguments)
            
            assert not result.isError
            assert len(result.content) == 1
            assert result.content[0].type == "text"
            assert "Successfully created" in result.content[0].text
            
            # Check that .auto.md file was created
            auto_md_file = temp_project_dir / ".auto.md"
            assert auto_md_file.exists()
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_handle_update_tool(self, project_with_files: Path):
        """Test handling of update tool call"""
        server = AutoMDServer()
        
        # Mock user input to say 'yes'
        import builtins
        original_input = builtins.input
        builtins.input = lambda prompt: 'y'
        
        try:
            arguments = {"project_path": str(project_with_files)}
            result = await server._handle_update(arguments)
            
            assert not result.isError
            assert len(result.content) == 1
            assert result.content[0].type == "text"
            assert "Successfully updated" in result.content[0].text
            
        finally:
            builtins.input = original_input
    
    @pytest.mark.asyncio
    async def test_handle_init_error(self):
        """Test handling of init tool with error"""
        server = AutoMDServer()
        
        # Pass invalid path to trigger error
        arguments = {"project_path": "/nonexistent/path"}
        result = await server._handle_init(arguments)
        
        # Should not be an error in the MCP sense, but should contain error message
        assert not result.isError
        assert "Error:" in result.content[0].text
    
    @pytest.mark.asyncio
    async def test_handle_update_error(self):
        """Test handling of update tool with error"""
        server = AutoMDServer()
        
        # Pass invalid path to trigger error
        arguments = {"project_path": "/nonexistent/path"}
        result = await server._handle_update(arguments)
        
        # Should not be an error in the MCP sense, but should contain error message
        assert not result.isError
        assert "Error:" in result.content[0].text
