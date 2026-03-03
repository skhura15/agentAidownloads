# Team Development Guidelines

**Internal development guidelines for the Multi-AI-Agents project.**

**Repository:** https://github.com/sachidanand/Multi-AI-Agents.git

---

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Agent Development Guidelines](#agent-development-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Git Workflow](#git-workflow)

## 🚀 Getting Started

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/sachidanand/Multi-AI-Agents.git
cd Multi-AI-Agents/Source-Code

# Run automated setup
./scripts/setup.sh
```

### Create Feature Branch

```bash
# Always create a new branch for your work
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 💻 Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- Docker (optional)
- Azure OpenAI account

### Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Development dependencies
pip install -e ".[dev]"

# Frontend dependencies
cd ui/frontend && npm install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py
```

## 📝 Coding Standards

### Python

- **Style Guide**: Follow [PEP 8](https://pep8.org/)
- **Line Length**: Maximum 100 characters
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Required for all function signatures
- **Formatting**: Use `black` for code formatting

```python
from typing import Dict, List, Optional

def process_agent_response(
    response: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Process agent response and extract relevant information.
    
    Args:
        response: Raw response from the agent
        metadata: Optional metadata dictionary
        
    Returns:
        List of processed response chunks
        
    Raises:
        ValueError: If response is empty
    """
    if not response:
        raise ValueError("Response cannot be empty")
    
    # Implementation here
    return processed_chunks
```

### TypeScript/JavaScript

- **Style Guide**: Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **Formatting**: Use Prettier
- **Linting**: Use ESLint
- **Type Safety**: Use TypeScript for all new code

```typescript
interface AgentResponse {
  content: string;
  agentId: string;
  status: string;
  metadata?: Record<string, any>;
}

async function processAgentResponse(
  response: AgentResponse
): Promise<string[]> {
  // Implementation here
  return processedChunks;
}
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `CustomerSupportAgent`)
- **Functions/Methods**: snake_case (e.g., `execute_agent_logic`)
- **Variables**: snake_case (e.g., `user_message`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private Methods**: Prefix with `_` (e.g., `_internal_helper`)

## 🤖 Agent Development Guidelines

### Creating a New Agent

1. **Inherit from BaseAgent**:

```python
from agents.base_agent import BaseAgent, AgentResponse

class MyCustomAgent(BaseAgent):
    def __init__(self, config_manager, state_manager):
        super().__init__(
            agent_id="my_custom_agent",
            agent_name="My Custom Agent",
            description="What this agent does",
            capabilities=["capability1", "capability2"],
            config_manager=config_manager,
            state_manager=state_manager
        )
```

2. **Implement Required Methods**:

```python
async def _load_configuration(self) -> None:
    """Load agent-specific configuration"""
    # Initialize clients, load prompts, etc.
    pass

async def _setup_tools(self) -> None:
    """Set up agent-specific tools"""
    # Register tools the agent can use
    pass

async def _execute_logic(
    self,
    user_input: str,
    context: Dict[str, Any]
) -> AgentResponse:
    """Execute agent logic"""
    # Your agent implementation
    pass
```

3. **Add Tests**:

```python
# tests/test_my_custom_agent.py
import pytest
from examples.my_custom_agent import MyCustomAgent

@pytest.mark.asyncio
async def test_agent_initialization():
    agent = MyCustomAgent(config_manager, state_manager)
    await agent.initialize()
    assert agent.agent_id == "my_custom_agent"

@pytest.mark.asyncio
async def test_agent_execution():
    agent = MyCustomAgent(config_manager, state_manager)
    response = await agent.execute("Test message")
    assert response.status == AgentStatus.COMPLETED
```

4. **Add Documentation**:
   - Update `docs/AGENT_DEVELOPMENT_GUIDE.md`
   - Add example usage in `examples/`
   - Create prompt templates in `prompts/`

### Best Practices

- **Error Handling**: Always handle exceptions gracefully
- **Logging**: Use the logging service for all log messages
- **State Management**: Use state manager for conversation state
- **Tool Integration**: Register tools through the tool registry
- **Prompt Templates**: Use prompt manager for all prompts
- **Configuration**: Load settings from config manager
- **Testing**: Write comprehensive tests for all agent behavior

## 📤 Git Workflow

### Commit Guidelines

Use conventional commits format:

```bash
# Feature
git commit -m "feat: add customer feedback agent"

# Bug fix
git commit -m "fix: resolve token counting issue"

# Documentation
git commit -m "docs: update agent development guide"

# Refactor
git commit -m "refactor: simplify orchestration logic"

# Test
git commit -m "test: add tests for tool registry"
```

### Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update relevant docs in `docs/`

2. **Run Tests and Linting**
   ```bash
   # Python
   black .
   flake8 .
   isort .
   pytest
   
   # TypeScript
   cd ui/frontend
   npm run lint
   npm run build
   ```

3. **Push Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Request review from team members
   ```
   
   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Build/tooling changes

4. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template
   - Link any related issues

### Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what and why
- **Screenshots**: Include for UI changes
- **Breaking Changes**: Clearly document any breaking changes
- **Tests**: Ensure all tests pass
- **Documentation**: Update relevant documentation

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_orchestration.py
├── integration/       # Integration tests
│   ├── test_api.py
│   └── test_workflows.py
└── conftest.py       # Pytest configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
async def sample_agent(config_manager, state_manager):
    """Fixture for creating a sample agent"""
    agent = CustomerSupportAgent(config_manager, state_manager)
    await agent.initialize()
    yield agent
    await agent.cleanup()

@pytest.mark.asyncio
async def test_agent_response(sample_agent):
    """Test agent returns valid response"""
    response = await sample_agent.execute("Hello")
    
    assert response is not None
    assert response.status == AgentStatus.COMPLETED
    assert len(response.content) > 0
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_agents.py

# With coverage
pytest --cov=. --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int, param3: Optional[Dict] = None) -> List[str]:
    """
    Brief description of what the function does.
    
    More detailed explanation if needed. This can span
    multiple lines and include implementation details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Optional parameter description. Defaults to None.
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        RuntimeError: When operation fails
        
    Example:
        >>> result = complex_function("test", 5)
        >>> print(result)
        ['processed', 'test']
    """
    pass
```

### Documentation Updates

When making changes, update:

1. **Code Comments**: Explain complex logic
2. **Docstrings**: Keep function/class docstrings current
3. **README.md**: Update if adding major features
4. **docs/**: Update relevant documentation files
5. **Examples**: Add usage examples when appropriate

## 📚 Key Resources

- **Repository**: https://github.com/sachidanand/Multi-AI-Agents.git
- **Microsoft Agent Framework**: https://github.com/microsoft/agent-framework
- **Azure OpenAI Docs**: https://learn.microsoft.com/azure/ai-services/openai/

---

**Multi-AI-Agents Team** | Internal Development Guidelines | 2026
