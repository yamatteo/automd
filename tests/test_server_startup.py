#!/usr/bin/env python3
"""
Test that AutoMD server can start properly and respond to basic requests using FastMCP
"""

import asyncio
import json
import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestServerStartup:
    """Test server startup and basic functionality with FastMCP"""

    @pytest.mark.asyncio
    async def test_server_starts_and_lists_tools(self):
        """Test that server starts and can list available tools"""
        
        # Start server as subprocess
        import subprocess
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "automd"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        try:
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            server_proc.stdin.write(json.dumps(init_request) + "\n")
            server_proc.stdin.flush()
            response_line = server_proc.stdout.readline()
            
            assert response_line is not None, "No initialization response"
            
            response = json.loads(response_line.strip())
            server_name = response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
            assert server_name == "automd", f"Expected server name 'automd', got '{server_name}'"
            
            # List tools
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            server_proc.stdin.write(json.dumps(tools_request) + "\n")
            server_proc.stdin.flush()
            response_line = server_proc.stdout.readline()
            
            assert response_line is not None, "No tools response"
            
            response = json.loads(response_line.strip())
            tools = response.get('result', {}).get('tools', [])
            
            # Verify tools are returned
            assert len(tools) > 0, "No tools returned"
            
            # Check for expected tools
            tool_names = [tool.get('name') for tool in tools]
            assert "init" in tool_names, "Missing 'init' tool"
            assert "update" in tool_names, "Missing 'update' tool"
            
            # Verify tool structure
            for tool in tools:
                assert 'name' in tool, f"Tool missing 'name': {tool}"
                assert 'description' in tool, f"Tool missing 'description': {tool}"
                assert 'inputSchema' in tool, f"Tool missing 'inputSchema': {tool}"
                    
        except Exception as e:
            pytest.fail(f"Server test failed: {e}")
            
        finally:
            # Clean up
            try:
                server_proc.terminate()
                server_proc.wait(timeout=5)
            except:
                server_proc.kill()
                server_proc.wait()

    @pytest.mark.asyncio
    async def test_server_handles_init_command(self):
        """Test that server can handle init command"""
        
        import subprocess
        import tempfile
        
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "automd"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        
        try:
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            server_proc.stdin.write(json.dumps(init_request) + "\n")
            server_proc.stdin.flush()
            response_line = server_proc.stdout.readline()
            assert response_line is not None, "No initialization response"
            
            # Call init tool with test directory
            with tempfile.TemporaryDirectory() as temp_dir:
                init_tool_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "init",
                        "arguments": {
                            "project_path": temp_dir
                        }
                    }
                }
                
                server_proc.stdin.write(json.dumps(init_tool_request) + "\n")
                server_proc.stdin.flush()
                response_line = server_proc.stdout.readline()
                
                assert response_line is not None, "No response for init tool"
                
                response = json.loads(response_line.strip())
                
                # Verify response
                assert 'result' in response, f"Expected result, got: {response}"
                content = response['result'].get('content', [])
                assert len(content) > 0, "Empty response content"
                
                # Check response content
                text_content = content[0].get('text', '')
                assert "Successfully initialized" in text_content or "created" in text_content.lower(), \
                    f"Unexpected response: {text_content}"
                
                # Verify .auto.md file was created
                auto_md_path = Path(temp_dir) / ".auto.md"
                assert auto_md_path.exists(), ".auto.md file not created"
                    
        except Exception as e:
            pytest.fail(f"Server init test failed: {e}")
            
        finally:
            # Clean up
            try:
                server_proc.terminate()
                server_proc.wait(timeout=5)
            except:
                server_proc.kill()
                server_proc.wait()

    def test_server_imports_successfully(self):
        """Test that server module can be imported without errors"""
        from automd.server import mcp, main
        assert mcp is not None
        assert main is not None

    def test_server_class_instantiation(self):
        """Test that FastMCP server can be instantiated"""
        from automd.server import mcp
        assert mcp is not None
        assert hasattr(mcp, 'run')
        assert hasattr(mcp, 'tool')  # FastMCP uses 'tool' decorator, not 'tools' attribute


if __name__ == "__main__":
    # Run a simple test if executed directly
    async def simple_test():
        test = TestServerStartup()
        try:
            await test.test_server_starts_and_lists_tools()
            print("✅ Server startup test passed")
        except Exception as e:
            print(f"❌ Server startup test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(simple_test())
