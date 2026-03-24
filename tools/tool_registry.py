"""
Tool Registry

Manages registration and execution of tools that agents can use.
"""

from typing import Any, Callable, Dict, List, Optional
import inspect
import logging
from dataclasses import dataclass

from core.logging_service import LoggingService


@dataclass
class ToolDefinition:
    """Definition of a tool"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    category: str = "general"
    enabled: bool = True


class ToolRegistry:
    """
    Registry for agent tools with:
    - Tool registration and discovery
    - Parameter validation
    - Execution with error handling
    - Usage tracking
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize tool registry.
        
        Args:
            logger: Optional custom logger
        """
        self.logger = logger or LoggingService.get_logger("tool_registry")
        self.tools: Dict[str, ToolDefinition] = {}
        self.usage_stats: Dict[str, int] = {}
        
        self.logger.info("Initialized ToolRegistry")
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        category: str = "general"
    ) -> None:
        """
        Register a tool.
        
        Args:
            name: Tool name
            function: Tool function
            description: Tool description
            parameters: Parameter schema
            category: Tool category
        """
        # Auto-generate parameter schema if not provided
        if parameters is None:
            parameters = self._generate_parameter_schema(function)
        
        tool = ToolDefinition(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category
        )
        
        self.tools[name] = tool
        self.usage_stats[name] = 0
        
        self.logger.info(f"Registered tool: {name} (category: {category})")
    
    def _generate_parameter_schema(self, function: Callable) -> Dict[str, Any]:
        """Generate parameter schema from function signature"""
        sig = inspect.signature(function)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any",
                "required": param.default == inspect.Parameter.empty
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
            
            parameters[param_name] = param_info
        
        return parameters
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """
        Get tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool definition or None
        """
        return self.tools.get(name)
    
    def list_tools(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[ToolDefinition]:
        """
        List available tools.
        
        Args:
            category: Filter by category
            enabled_only: Only return enabled tools
            
        Returns:
            List of tool definitions
        """
        tools = list(self.tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        
        return tools
    
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        if not tool.enabled:
            raise ValueError(f"Tool is disabled: {tool_name}")
        
        try:
            self.logger.info(f"Executing tool: {tool_name}")
            
            # Validate parameters
            self._validate_parameters(tool, kwargs)
            
            # Execute tool
            if inspect.iscoroutinefunction(tool.function):
                result = await tool.function(**kwargs)
            else:
                result = tool.function(**kwargs)
            
            # Update usage stats
            self.usage_stats[tool_name] += 1
            
            self.logger.info(f"Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
            raise
    
    def _validate_parameters(
        self,
        tool: ToolDefinition,
        params: Dict[str, Any]
    ) -> None:
        """Validate tool parameters"""
        for param_name, param_info in tool.parameters.items():
            if param_info.get("required", False) and param_name not in params:
                raise ValueError(f"Missing required parameter: {param_name}")
    
    def enable_tool(self, tool_name: str) -> None:
        """Enable a tool"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = True
            self.logger.info(f"Enabled tool: {tool_name}")
    
    def disable_tool(self, tool_name: str) -> None:
        """Disable a tool"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = False
            self.logger.info(f"Disabled tool: {tool_name}")
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get tool usage statistics"""
        return self.usage_stats.copy()
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool schema in OpenAI function format.
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool schema or None
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        name: {
                            "type": info.get("type", "string"),
                            "description": info.get("description", "")
                        }
                        for name, info in tool.parameters.items()
                    },
                    "required": [
                        name for name, info in tool.parameters.items()
                        if info.get("required", False)
                    ]
                }
            }
        }
    
    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all enabled tools"""
        schemas = []
        for tool_name in self.tools:
            if self.tools[tool_name].enabled:
                schema = self.get_tool_schema(tool_name)
                if schema:
                    schemas.append(schema)
        return schemas
