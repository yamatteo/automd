#!/usr/bin/env python3
"""
AutoMD MCP Server - Automatic project documentation via MCP protocol
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp import ServerSession, stdio_server
from mcp.types import Tool, TextContent, CallToolResult

from .commands import InitCommand, UpdateCommand


class AutoMDServer:
    """AutoMD MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("automd")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="init",
                    description="Initialize AutoMD by creating .auto.md files in all directories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to the project directory to scan (default: current directory)",
                                "default": "."
                            }
                        }
                    }
                ),
                Tool(
                    name="update",
                    description="Update all .auto.md files by rescanning the project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to the project directory to update (default: current directory)",
                                "default": "."
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "init":
                    return await self._handle_init(arguments)
                elif name == "update":
                    return await self._handle_update(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")],
                    isError=True
                )
    
    async def _handle_init(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle init tool call"""
        project_path = arguments.get("project_path", ".")
        
        command = InitCommand()
        result = await command.execute(project_path)
        
        return CallToolResult(
            content=[TextContent(type="text", text=result)]
        )
    
    async def _handle_update(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle update tool call"""
        project_path = arguments.get("project_path", ".")
        
        command = UpdateCommand()
        result = await command.execute(project_path)
        
        return CallToolResult(
            content=[TextContent(type="text", text=result)]
        )


async def main():
    """Main entry point for the MCP server"""
    server_instance = AutoMDServer()
    
    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        session = ServerSession(read_stream, write_stream)
        await session.run(server_instance.server)


if __name__ == "__main__":
    asyncio.run(main())
