"""
Microsoft Agent Framework Client Wrapper

Provides integration with Microsoft Agent Framework for building
production-ready agentic systems with Azure OpenAI/Foundry.
"""

from typing import Any, AsyncIterator, Dict, List, Optional, Union, Callable
import logging
from datetime import datetime

from agent_framework import BaseAgent as ChatAgent  # type: ignore  # ChatAgent renamed to BaseAgent in newer versions
from agent_framework_azure_ai import AzureAIAgentClient  # type: ignore
from azure.identity.aio import DefaultAzureCredential  # type: ignore

from core.config_manager import ConfigManager
from core.logging_service import LoggingService


class AgentFrameworkClient:
    """
    Wrapper for Microsoft Agent Framework with Azure integration.
    
    Provides a simplified interface for creating and managing agents
    with Azure OpenAI or Microsoft Foundry models.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Agent Framework client.
        
        Args:
            config_manager: Configuration manager instance
            logger: Optional logger instance
        """
        self.config = config_manager
        self.logger = logger or LoggingService.get_logger(self.__class__.__name__)
        
        # Load configuration
        agent_config = self.config.get("agent_framework", {})
        azure_config = self.config.get("azure_openai", {})
        
        # Determine if using Foundry or Azure OpenAI
        self.use_foundry = agent_config.get("use_foundry", False)
        
        if self.use_foundry:
            # Microsoft Foundry (formerly Azure AI Foundry) configuration
            self.project_endpoint = agent_config.get("project_endpoint")
            self.model_deployment = agent_config.get("model_deployment_name")
            
            if not self.project_endpoint or not self.model_deployment:
                raise ValueError(
                    "Microsoft Foundry requires 'project_endpoint' and "
                    "'model_deployment_name' in configuration"
                )
        else:
            # Azure OpenAI configuration
            self.endpoint = azure_config.get("endpoint")
            self.api_key = azure_config.get("api_key")
            self.api_version = azure_config.get("api_version", "2024-08-01-preview")
            self.deployment = azure_config.get("deployment_name")
            
            if not self.endpoint or not self.deployment:
                raise ValueError(
                    "Azure OpenAI requires 'endpoint' and 'deployment_name' "
                    "in configuration"
                )
        
        self.logger.info("AgentFrameworkClient initialized successfully")
    
    def create_agent_client(
        self,
        agent_name: str,
        agent_id: Optional[str] = None
    ) -> AzureAIAgentClient:
        """
        Create an Azure AI Agent client.
        
        Args:
            agent_name: Name for the agent
            agent_id: Optional existing agent ID to reuse
            
        Returns:
            Configured AzureAIAgentClient instance
        """
        try:
            if self.use_foundry:
                # Microsoft Foundry client
                client = AzureAIAgentClient(
                    project_endpoint=self.project_endpoint,
                    model_deployment_name=self.model_deployment,
                    async_credential=DefaultAzureCredential(),
                    agent_name=agent_name,
                    agent_id=agent_id
                )
            else:
                # Azure OpenAI client
                from azure.core.credentials import AzureKeyCredential  # type: ignore
                
                credential = (
                    AzureKeyCredential(self.api_key) if self.api_key
                    else DefaultAzureCredential()
                )
                
                client = AzureAIAgentClient(
                    endpoint=self.endpoint,
                    model_deployment_name=self.deployment,
                    async_credential=credential,
                    agent_name=agent_name,
                    agent_id=agent_id,
                    api_version=self.api_version
                )
            
            self.logger.info(f"Created agent client for '{agent_name}'")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create agent client: {str(e)}", exc_info=True)
            raise
    
    async def create_chat_agent(
        self,
        agent_name: str,
        instructions: str,
        tools: Optional[List[Union[Callable, Any]]] = None,
        agent_id: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> ChatAgent:
        """
        Create a ChatAgent instance with the specified configuration.
        
        Args:
            agent_name: Name for the agent
            instructions: System instructions for the agent
            tools: Optional list of tools (functions or MCP tools)
            agent_id: Optional existing agent ID to reuse
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            **kwargs: Additional ChatAgent parameters
            
        Returns:
            Configured ChatAgent instance
            
        Example:
            ```python
            client = AgentFrameworkClient(config_manager)
            
            async with await client.create_chat_agent(
                agent_name="Customer Support",
                instructions="You are a helpful support agent",
                tools=[search_knowledge, create_ticket]
            ) as agent:
                async for chunk in agent.run_stream("Hello!"):
                    print(chunk.text, end="")
            ```
        """
        try:
            chat_client = self.create_agent_client(
                agent_name=agent_name,
                agent_id=agent_id
            )
            
            agent = ChatAgent(
                chat_client=chat_client,
                instructions=instructions,
                tools=tools or [],
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            
            self.logger.info(f"Created ChatAgent: {agent_name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create ChatAgent: {str(e)}", exc_info=True)
            raise
    
    async def run_agent_streaming(
        self,
        agent: ChatAgent,
        user_input: str,
        thread: Optional[Any] = None
    ) -> AsyncIterator[Any]:
        """
        Run agent with streaming responses.
        
        Args:
            agent: ChatAgent instance
            user_input: User's input message
            thread: Optional thread for conversation continuity
            
        Yields:
            Response chunks from the agent
        """
        try:
            async for chunk in agent.run_stream(user_input, thread=thread):
                yield chunk
                
        except Exception as e:
            self.logger.error(f"Error during agent streaming: {str(e)}", exc_info=True)
            raise
    
    async def run_agent(
        self,
        agent: ChatAgent,
        user_input: str,
        thread: Optional[Any] = None
    ) -> Any:
        """
        Run agent and wait for complete response.
        
        Args:
            agent: ChatAgent instance
            user_input: User's input message
            thread: Optional thread for conversation continuity
            
        Returns:
            Complete agent response
        """
        try:
            result = await agent.run(user_input, thread=thread)
            return result
            
        except Exception as e:
            self.logger.error(f"Error during agent execution: {str(e)}", exc_info=True)
            raise
    
    def create_tool_from_function(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Callable:
        """
        Prepare a function to be used as an agent tool.
        
        The function should have proper type hints and docstring.
        Agent Framework will automatically extract the schema.
        
        Args:
            func: The function to convert
            name: Optional custom name (uses function name by default)
            description: Optional description (uses docstring by default)
            
        Returns:
            Tool-ready function
            
        Example:
            ```python
            from typing import Annotated
            
            def search_kb(
                query: Annotated[str, "The search query"]
            ) -> str:
                \"\"\"Search the knowledge base for information.\"\"\"
                return f"Results for: {query}"
            
            tool = client.create_tool_from_function(search_kb)
            ```
        """
        # Agent Framework uses the function directly with type hints
        if name:
            func.__name__ = name
        if description:
            func.__doc__ = description
        
        return func
    
    def create_mcp_stdio_tool(
        self,
        name: str,
        description: str,
        command: str,
        args: Optional[List[str]] = None
    ):
        """
        Create an MCP Stdio tool.
        
        Args:
            name: Tool name
            description: Tool description
            command: Command to execute
            args: Command arguments
            
        Returns:
            MCPStdioTool instance
        """
        from agent_framework import MCPStdioTool  # type: ignore
        
        return MCPStdioTool(
            name=name,
            description=description,
            command=command,
            args=args or []
        )
    
    def create_mcp_http_tool(
        self,
        name: str,
        description: str,
        url: str
    ):
        """
        Create an MCP HTTP tool.
        
        Args:
            name: Tool name
            description: Tool description
            url: Tool endpoint URL
            
        Returns:
            MCPStreamableHTTPTool instance
        """
        from agent_framework import MCPStreamableHTTPTool  # type: ignore
        
        return MCPStreamableHTTPTool(
            name=name,
            description=description,
            url=url
        )


class TokenManager:
    """Manages token counting and usage tracking for Agent Framework"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            import tiktoken
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            import tiktoken
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def update_usage(self, prompt_tokens: int, completion_tokens: int):
        """Update usage statistics"""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        
        # Cost estimation (adjust based on your model)
        prompt_cost = (prompt_tokens / 1000) * 0.03
        completion_cost = (completion_tokens / 1000) * 0.06
        self.total_cost += prompt_cost + completion_cost
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "estimated_cost": round(self.total_cost, 4),
            "model": self.model
        }
    
    def reset(self):
        """Reset usage statistics"""
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
