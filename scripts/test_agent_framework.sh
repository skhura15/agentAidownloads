#!/bin/bash

# Test Agent Framework Installation
# This script verifies the Agent Framework setup

set -e  # Exit on error

echo "🔍 Testing Microsoft Agent Framework Installation"
echo "=================================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Check if agent-framework is installed
echo ""
echo "✓ Checking Agent Framework installation..."
if python -c "import agent_framework" 2>/dev/null; then
    echo "  ✅ agent-framework is installed"
    version=$(python -c "import agent_framework; print(getattr(agent_framework, '__version__', 'unknown'))" 2>/dev/null || echo "version info not available")
    echo "  Version: $version"
else
    echo "  ❌ agent-framework is NOT installed"
    echo "  Please run: pip install agent-framework-azure-ai --pre"
    exit 1
fi

# Check if agent-framework-azure-ai is installed
echo ""
echo "✓ Checking Agent Framework Azure AI integration..."
if python -c "import agent_framework_azure_ai" 2>/dev/null; then
    echo "  ✅ agent-framework-azure-ai is installed"
else
    echo "  ❌ agent-framework-azure-ai is NOT installed"
    echo "  Please run: pip install agent-framework-azure-ai --pre"
    exit 1
fi

# Check Azure dependencies
echo ""
echo "✓ Checking Azure dependencies..."
deps=("azure.identity" "azure.core")
for dep in "${deps[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        echo "  ✅ $dep is installed"
    else
        echo "  ❌ $dep is NOT installed"
        echo "  Please run: pip install -r requirements.txt"
        exit 1
    fi
done

# Check environment configuration
echo ""
echo "✓ Checking environment configuration..."
if [ -f ".env" ]; then
    echo "  ✅ .env file exists"
    
    # Check for required variables
    if grep -q "AZURE_OPENAI_ENDPOINT" .env || grep -q "FOUNDRY_PROJECT_ENDPOINT" .env; then
        echo "  ✅ Azure configuration found"
    else
        echo "  ⚠️  Warning: No Azure configuration found in .env"
        echo "     Make sure to configure either:"
        echo "     - Azure OpenAI: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY"
        echo "     - Microsoft Foundry: FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL_DEPLOYMENT"
    fi
else
    echo "  ⚠️  Warning: .env file not found"
    echo "     Run: cp .env.example .env and configure it"
fi

# Test import of core modules
echo ""
echo "✓ Testing core module imports..."
modules=("core.agent_framework_client" "core.config_manager" "core.state_manager")
for module in "${modules[@]}"; do
    if python -c "import sys; sys.path.insert(0, '.'); import $module" 2>/dev/null; then
        echo "  ✅ $module imported successfully"
    else
        echo "  ❌ Failed to import $module"
        exit 1
    fi
done

# Test simple Agent Framework code
echo ""
echo "✓ Testing Agent Framework basic functionality..."
cat > /tmp/test_agent_framework.py << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from agent_framework import ChatAgent
    from agent_framework_azure_ai import AzureAIAgentClient
    print("✅ Agent Framework imports successful")
except Exception as e:
    print(f"❌ Agent Framework import failed: {e}")
    sys.exit(1)
EOF

if python /tmp/test_agent_framework.py; then
    echo "  Agent Framework is working correctly!"
else
    echo "  ❌ Agent Framework test failed"
    exit 1
fi

rm /tmp/test_agent_framework.py

echo ""
echo "=================================================="
echo "✅ All checks passed!"
echo ""
echo "Next steps:"
echo "  1. Configure your .env file with Azure credentials"
echo "  2. Run the example: python examples/agent_framework_customer_support.py"
echo "  3. Or start the API: python -m api.main"
echo ""
echo "📚 Documentation:"
echo "  - Quick Start: docs/AGENT_FRAMEWORK_QUICKSTART.md"
echo "  - Agent Guide: docs/AGENT_DEVELOPMENT_GUIDE.md"
echo "=================================================="
