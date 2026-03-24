"""
Customer Support Agent

A sample agent implementation demonstrating best practices for the Agentic CoE system.
"""

from typing import Dict, Any, Optional
import logging

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager
from core.azure_openai_client import AzureOpenAIClient
from tools.tool_registry import ToolRegistry
from tools import common_tools
from prompts.prompt_manager import PromptManager


class CustomerSupportAgent(BaseAgent):
    """
    Customer Support Agent that handles:
    - Answering product questions
    - Tracking orders
    - Creating support tickets
    - Escalating complex issues
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        state_manager: StateManager,
        logger: Optional[logging.Logger] = None
    ):
        # Agent configuration
        agent_config = config_manager.get("agents.customer_support", {})
        
        super().__init__(
            agent_id="customer_support",
            agent_name=agent_config.get("name", "Customer Support Agent"),
            description=agent_config.get("description", "Handles customer inquiries"),
            capabilities=agent_config.get("capabilities", []),
            config_manager=config_manager,
            state_manager=state_manager,
            logger=logger
        )
        
        # Initialize components
        self.openai_client: Optional[AzureOpenAIClient] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.prompt_manager: Optional[PromptManager] = None
        self.system_prompt: Optional[str] = None
    
    async def _load_configuration(self) -> None:
        """Load agent-specific configuration"""
        # Initialize Azure OpenAI client
        self.openai_client = AzureOpenAIClient(
            config_manager=self.config_manager,
            logger=self.logger
        )
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager(prompts_dir="prompts")
        
        # Load system prompt
        try:
            self.system_prompt = self.prompt_manager.render_template(
                "customer_support_system",
                company_name="Agentic CoE",
                support_email="support@agenticoe.com"
            )
        except Exception as e:
            self.logger.warning(f"Failed to load system prompt: {str(e)}")
            self.system_prompt = (
                "You are a helpful customer support agent. "
                "Assist customers with their questions and create tickets when needed."
            )
    
    async def _setup_tools(self) -> None:
        """Set up agent-specific tools"""
        self.tool_registry = ToolRegistry(logger=self.logger)
        
        # Register tools
        self.tool_registry.register_tool(
            name="search_knowledge_base",
            function=common_tools.search_knowledge_base,
            description="Search the knowledge base for relevant information",
            category="knowledge"
        )
        
        self.tool_registry.register_tool(
            name="create_ticket",
            function=common_tools.create_ticket,
            description="Create a support ticket",
            category="support"
        )
        
        self.tool_registry.register_tool(
            name="send_email",
            function=common_tools.send_email,
            description="Send an email",
            category="communication"
        )
        
        # Store tool references
        self.tools = self.tool_registry.list_tools()
    
    async def _execute_logic(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Execute customer support agent logic.
        
        Args:
            user_input: User's message
            context: Additional context
            
        Returns:
            AgentResponse with the result
        """
        try:
            # Build conversation messages
            messages = []
            
            # Add system prompt
            if self.system_prompt:
                messages.append({
                    "role": "system",
                    "content": self.system_prompt
                })
            
            # Add conversation history (last 5 messages)
            for msg in self.conversation_history[-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Get tool schemas for function calling
            tool_schemas = self.tool_registry.get_all_tool_schemas()
            
            # Call Azure OpenAI
            response = await self.openai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                tools=tool_schemas if tool_schemas else None
            )
            
            # Extract response
            assistant_message = response.choices[0].message
            content = assistant_message.content or ""
            
            # Handle tool calls
            tools_used = []
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tools_used.append(tool_name)
                    
                    try:
                        import json
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Execute tool
                        tool_result = await self.tool_registry.execute_tool(
                            tool_name,
                            **tool_args
                        )
                        
                        self.logger.info(f"Tool {tool_name} executed successfully")
                        
                        # Add tool result to content
                        content += f"\n\n[Tool {tool_name} executed: {tool_result}]"
                        
                    except Exception as e:
                        self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            
            # Determine if handoff is needed
            handoff_to = None
            if "technical issue" in user_input.lower() or "bug" in user_input.lower():
                handoff_to = "technical_support"
            
            # Create response
            return AgentResponse(
                content=content,
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.COMPLETED,
                metadata={
                    "model": self.openai_client.model,
                    "temperature": 0.7
                },
                tools_used=tools_used,
                handoff_to=handoff_to
            )
            
        except Exception as e:
            self.logger.error(f"Error in customer support agent: {str(e)}", exc_info=True)
            
            return AgentResponse(
                content="I apologize, but I encountered an error processing your request. "
                        "Let me create a support ticket for you.",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    async def _execute_streaming(
        self,
        user_input: str,
        context: Dict[str, Any]
    ):
        """
        Stream agent responses in real-time.
        
        Args:
            user_input: User's message
            context: Additional context
            
        Yields:
            Chunks of the response
        """
        try:
            # Build messages
            messages = []
            
            if self.system_prompt:
                messages.append({
                    "role": "system",
                    "content": self.system_prompt
                })
            
            for msg in self.conversation_history[-5:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Stream response
            async for chunk in self.openai_client.chat_completion_streaming(
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            ):
                yield chunk
                
        except Exception as e:
            self.logger.error(f"Error in streaming: {str(e)}")
            yield f"Error: {str(e)}"
