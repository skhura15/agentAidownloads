# Agent Development Guide

**Internal guide for developing agents in the Multi-AI-Agents project.**

This guide provides step-by-step instructions for creating new agents using Microsoft Agent Framework.

## Table of Contents

1. [Understanding Agents](#understanding-agents)
2. [Creating Your First Agent](#creating-your-first-agent)
3. [Agent Lifecycle](#agent-lifecycle)
4. [Working with Tools](#working-with-tools)
5. [Prompt Management](#prompt-management)
6. [State Management](#state-management)
7. [Testing Your Agent](#testing-your-agent)
8. [Best Practices](#best-practices)

## Understanding Agents

An agent in the Agentic CoE system is a self-contained AI component that:
- Processes user input
- Makes decisions
- Uses tools to accomplish tasks
- Maintains conversation state
- Can hand off to other agents

All agents inherit from the `BaseAgent` class which provides common functionality.

## Creating Your First Agent

### Step 1: Create Agent Class

Create a new file `agents/my_agent.py`:

```python
from typing import Dict, Any, Optional
import logging

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager
from core.azure_openai_client import AzureOpenAIClient
from tools.tool_registry import ToolRegistry
from prompts.prompt_manager import PromptManager


class MyCustomAgent(BaseAgent):
    """
    Custom agent for [describe purpose].
    
    Capabilities:
    - [Capability 1]
    - [Capability 2]
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        state_manager: StateManager,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(
            agent_id="my_custom_agent",
            agent_name="My Custom Agent",
            description="Brief description of what this agent does",
            capabilities=[
                "capability_1",
                "capability_2"
            ],
            config_manager=config_manager,
            state_manager=state_manager,
            logger=logger
        )
        
        self.openai_client: Optional[AzureOpenAIClient] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self.prompt_manager: Optional[PromptManager] = None
```

### Step 2: Implement Configuration Loading

```python
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
            "my_agent_system",
            agent_name=self.agent_name,
            # Add more variables as needed
        )
    except Exception as e:
        self.logger.warning(f"Failed to load system prompt: {str(e)}")
        self.system_prompt = "You are a helpful AI assistant."
```

### Step 3: Setup Tools

```python
async def _setup_tools(self) -> None:
    """Set up agent-specific tools"""
    self.tool_registry = ToolRegistry(logger=self.logger)
    
    # Register tools this agent can use
    from tools import common_tools
    
    self.tool_registry.register_tool(
        name="search_knowledge",
        function=common_tools.search_knowledge_base,
        description="Search the knowledge base",
        category="knowledge"
    )
    
    # Register custom tool
    async def custom_tool(param1: str, param2: int) -> Dict:
        """Your custom tool implementation"""
        result = f"Processed {param1} with {param2}"
        return {"result": result}
    
    self.tool_registry.register_tool(
        name="custom_tool",
        function=custom_tool,
        description="Description of what the tool does",
        parameters={
            "param1": {"type": "string", "required": True},
            "param2": {"type": "integer", "required": True}
        }
    )
    
    self.tools = self.tool_registry.list_tools()
```

### Step 4: Implement Agent Logic

```python
async def _execute_logic(
    self,
    user_input: str,
    context: Dict[str, Any]
) -> AgentResponse:
    """
    Execute agent logic.
    
    Args:
        user_input: User's message
        context: Additional context
        
    Returns:
        AgentResponse with the result
    """
    try:
        # Build conversation messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add conversation history (last N messages)
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
            tools=tool_schemas
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
                
                # Execute tool and add result to content
                import json
                tool_args = json.loads(tool_call.function.arguments)
                tool_result = await self.tool_registry.execute_tool(
                    tool_name,
                    **tool_args
                )
                
                content += f"\n\n[Used {tool_name}: {tool_result}]"
        
        # Determine if handoff is needed
        handoff_to = None
        if "needs_escalation" in user_input.lower():
            handoff_to = "escalation_agent"
        
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
        self.logger.error(f"Error in agent: {str(e)}", exc_info=True)
        
        return AgentResponse(
            content="I apologize, but I encountered an error.",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.ERROR,
            error=str(e)
        )
```

## Agent Lifecycle

1. **Initialization**: `__init__()` - Create agent instance
2. **Setup**: `initialize()` - Load config, setup tools
3. **Execution**: `execute()` - Process user input
4. **Cleanup**: `cleanup()` - Release resources
5. **Reset**: `reset()` - Clear state

## Working with Tools

### Registering Tools

```python
self.tool_registry.register_tool(
    name="tool_name",
    function=tool_function,
    description="What the tool does",
    parameters={
        "param_name": {
            "type": "string",
            "required": True,
            "description": "Parameter description"
        }
    }
)
```

### Creating Custom Tools

```python
async def my_custom_tool(
    input_text: str,
    option: str = "default"
) -> Dict[str, Any]:
    """
    Custom tool implementation.
    
    Args:
        input_text: Input to process
        option: Processing option
        
    Returns:
        Processing result
    """
    # Your implementation
    result = f"Processed: {input_text} with {option}"
    
    return {
        "result": result,
        "metadata": {}
    }
```

## Prompt Management

### Creating Prompt Templates

Create `prompts/my_agent_system.yaml`:

```yaml
name: my_agent_system
version: "1.0.0"
description: "System prompt for my custom agent"
variables:
  - agent_name
  - company_name
template: |
  You are {agent_name}, an AI assistant for {company_name}.
  
  Your responsibilities:
  - [Responsibility 1]
  - [Responsibility 2]
  
  Guidelines:
  - [Guideline 1]
  - [Guideline 2]
  
  Always be helpful and professional.
metadata:
  category: "system"
  language: "en"
```

### Using Prompts

```python
prompt = self.prompt_manager.render_template(
    "my_agent_system",
    agent_name="My Agent",
    company_name="Acme Corp"
)
```

## State Management

### Updating State

```python
await self.state_manager.update_agent_state(
    self.agent_id,
    {
        "last_user_input": user_input,
        "processing_status": "in_progress",
        "custom_data": {"key": "value"}
    }
)
```

### Retrieving State

```python
state = await self.state_manager.get_agent_state(self.agent_id)
if state:
    last_input = state.get("last_user_input")
```

## Testing Your Agent

Create `tests/test_my_agent.py`:

```python
import pytest
from agents.my_agent import MyCustomAgent


@pytest.mark.asyncio
async def test_agent_initialization(config_manager, state_manager):
    """Test agent initializes correctly"""
    agent = MyCustomAgent(config_manager, state_manager)
    await agent.initialize()
    
    assert agent.agent_id == "my_custom_agent"
    assert agent.agent_name == "My Custom Agent"


@pytest.mark.asyncio
async def test_agent_execution(config_manager, state_manager):
    """Test agent executes successfully"""
    agent = MyCustomAgent(config_manager, state_manager)
    await agent.initialize()
    
    response = await agent.execute("Test message")
    
    assert response is not None
    assert response.status == AgentStatus.COMPLETED
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_agent_tool_usage(config_manager, state_manager):
    """Test agent uses tools correctly"""
    agent = MyCustomAgent(config_manager, state_manager)
    await agent.initialize()
    
    response = await agent.execute("Use the custom tool")
    
    assert "custom_tool" in response.tools_used
```

Run tests:

```bash
pytest tests/test_my_agent.py -v
```

## Best Practices

### 1. Error Handling

Always handle exceptions gracefully:

```python
try:
    result = await risky_operation()
except SpecificException as e:
    self.logger.error(f"Specific error: {str(e)}")
    return error_response
except Exception as e:
    self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return generic_error_response
```

### 2. Logging

Use appropriate log levels:

```python
self.logger.debug("Detailed diagnostic info")
self.logger.info("General information")
self.logger.warning("Warning about potential issue")
self.logger.error("Error occurred")
self.logger.critical("Critical system error")
```

### 3. Type Hints

Always use type hints:

```python
async def process_data(
    self,
    data: str,
    options: Dict[str, Any]
) -> AgentResponse:
    pass
```

### 4. Documentation

Write comprehensive docstrings:

```python
async def complex_method(self, param: str) -> Dict:
    """
    Brief description of what the method does.
    
    More detailed explanation if needed.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param is invalid
    """
    pass
```

### 5. State Management

Keep state minimal and clear:

```python
# Good: Specific, minimal state
state = {
    "user_preference": "detailed",
    "last_query": "status check"
}

# Bad: Too much state, unclear purpose
state = {
    "data1": {...},
    "temp": "something",
    "stuff": [...]
}
```

### 6. Tool Design

Make tools focused and reusable:

```python
# Good: Specific purpose
async def send_notification(recipient: str, message: str):
    pass

# Bad: Too generic
async def do_something(data: Any):
    pass
```

## Complete Example

See `examples/agent_framework_customer_support.py` for a complete working example using Microsoft Agent Framework.

## Next Steps

1. Review the Agent Framework Quick Start guide
2. Create your agent class
3. Implement required methods
4. Create prompt templates
5. Register tools
6. Write tests
7. Add documentation

## Resources

- **Repository**: https://github.com/sachidanand/Multi-AI-Agents.git
- [Agent Framework Quick Start](AGENT_FRAMEWORK_QUICKSTART.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [Team Guidelines](../CONTRIBUTING.md)

---

**Multi-AI-Agents Team** | Internal Documentation | 2026
