"""
MCP (Model Context Protocol) Manager for SideDesk
Handles tool registration and execution
Created by: Claude Sonnet 4.5
Date: 10-06-25
"""

from typing import Dict, List, Optional, Any, Callable
import json


class MCPTool:
    """Represents a single MCP tool."""

    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        """
        Initialize MCP tool.

        Args:
            name: Tool name
            description: Tool description
            function: Callable to execute
            parameters: JSON schema for parameters
        """
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

    def Execute(self, **kwargs) -> Any:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        try:
            return self.function(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def GetSchema(self) -> Dict[str, Any]:
        """
        Get tool schema for LLM.

        Returns:
            Tool schema dict
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class MCPManager:
    """
    Manager for MCP tools.
    Handles tool registration, discovery, and execution.
    """

    def __init__(self):
        """Initialize MCP manager."""
        self.tools: Dict[str, MCPTool] = {}
        self.enabled_tools: List[str] = []
        self.RegisterBuiltinTools()

    def RegisterTool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Register a new tool.

        Args:
            name: Tool name
            description: Tool description
            function: Callable to execute
            parameters: JSON schema for parameters

        Returns:
            True if successful
        """
        try:
            tool = MCPTool(name, description, function, parameters)
            self.tools[name] = tool
            return True
        except Exception:
            return False

    def UnregisterTool(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Tool name

        Returns:
            True if successful
        """
        if name in self.tools:
            del self.tools[name]
            if name in self.enabled_tools:
                self.enabled_tools.remove(name)
            return True
        return False

    def EnableTool(self, name: str) -> bool:
        """
        Enable a registered tool.

        Args:
            name: Tool name

        Returns:
            True if successful
        """
        if name in self.tools and name not in self.enabled_tools:
            self.enabled_tools.append(name)
            return True
        return False

    def DisableTool(self, name: str) -> bool:
        """
        Disable a tool.

        Args:
            name: Tool name

        Returns:
            True if successful
        """
        if name in self.enabled_tools:
            self.enabled_tools.remove(name)
            return True
        return False

    def ExecuteTool(
        self,
        name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        if name not in self.tools:
            return {"error": f"Tool {name} not found"}

        if name not in self.enabled_tools:
            return {"error": f"Tool {name} not enabled"}

        tool = self.tools[name]
        return tool.Execute(**parameters)

    def GetToolSchemas(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all enabled tools.

        Returns:
            List of tool schemas
        """
        schemas = []
        for name in self.enabled_tools:
            if name in self.tools:
                schemas.append(self.tools[name].GetSchema())
        return schemas

    def ListTools(self) -> List[str]:
        """
        List all registered tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def ListEnabledTools(self) -> List[str]:
        """
        List enabled tools.

        Returns:
            List of enabled tool names
        """
        return self.enabled_tools.copy()

    def RegisterBuiltinTools(self):
        """Register built-in tools."""

        def ReadFile(path: str) -> str:
            """Read a file from filesystem."""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"

        def WriteFile(path: str, content: str) -> str:
            """Write content to a file."""
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote to {path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        def ListDirectory(path: str = ".") -> str:
            """List contents of a directory."""
            try:
                import os
                items = os.listdir(path)
                return "\n".join(items)
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        self.RegisterTool(
            name="ReadFile",
            description="Read contents of a file",
            function=ReadFile,
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    }
                },
                "required": ["path"]
            }
        )

        self.RegisterTool(
            name="WriteFile",
            description="Write content to a file",
            function=WriteFile,
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        )

        self.RegisterTool(
            name="ListDirectory",
            description="List contents of a directory",
            function=ListDirectory,
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path"
                    }
                },
                "required": []
            }
        )
