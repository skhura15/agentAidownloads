#!/bin/bash

# Setup script for local development
# This script sets up the development environment for the Agentic CoE project

set -e

echo "🚀 Setting up Agentic CoE development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. You have $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed ($PYTHON_VERSION)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p configs
mkdir -p prompts
mkdir -p examples
mkdir -p tests

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Azure credentials!"
else
    echo "✅ .env file already exists"
fi

# Setup frontend if Node.js is installed
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d. -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "📦 Setting up React frontend..."
        cd ui/frontend
        
        if [ ! -d "node_modules" ]; then
            echo "Installing npm dependencies..."
            npm install
        else
            echo "✅ npm dependencies already installed"
        fi
        
        cd ../..
        echo "✅ Frontend setup complete"
    else
        echo "⚠️  Node.js 18+ required for frontend. You have v$NODE_VERSION"
    fi
else
    echo "⚠️  Node.js not found. Skipping frontend setup."
fi

# Check Docker installation
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose is installed"
    else
        echo "⚠️  Docker Compose not found. Install it for containerized development."
    fi
else
    echo "⚠️  Docker not found. Install it for containerized development."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure credentials"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Run './scripts/run_dev.sh' to start the development servers"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo "5. Visit http://localhost:3000 for the React UI"
echo "6. Visit http://localhost:8501 for the Streamlit UI"
echo ""
echo "For more information, see README.md"
