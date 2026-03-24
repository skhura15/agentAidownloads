#!/bin/bash

# ============================================================================
# Frontend Deployment Script to Azure
# ============================================================================
# This script deploys the React frontend to Azure Static Web Apps
# Usage: ./scripts/deploy-frontend.sh <resource-group> [location] [app-name]
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Validate parameters
if [ $# -lt 1 ]; then
    print_error "Missing required parameter: resource-group"
    echo "Usage: ./scripts/deploy-frontend.sh <resource-group> [location] [app-name]"
    echo ""
    echo "Examples:"
    echo "  ./scripts/deploy-frontend.sh rg-dev                                    # Uses defaults"
    echo "  ./scripts/deploy-frontend.sh rg-dev westus2                            # With location"
    echo "  ./scripts/deploy-frontend.sh rg-dev westus2 my-agentic-coe-frontend   # With custom name"
    exit 1
fi

RESOURCE_GROUP=$1
LOCATION=${2:-"westus2"}
APP_NAME=${3:-"agentic-coe-frontend"}

print_info "Deploying frontend to Azure Static Web Apps"
print_info "Resource Group: $RESOURCE_GROUP"
print_info "Location: $LOCATION"
print_info "App Name: $APP_NAME"
echo ""

# Step 1: Check if resource group exists
print_info "Checking if resource group exists..."
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    print_error "Resource group '$RESOURCE_GROUP' not found"
    exit 1
fi
print_success "Resource group found"
echo ""

# Step 2: Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it from https://aka.ms/installazurecliwindows"
    exit 1
fi
print_success "Azure CLI found"

# Step 3: Check if user is logged in
if ! az account show &>/dev/null; then
    print_error "Not logged in to Azure. Running 'az login'..."
    az login
fi
print_success "Logged in to Azure"
echo ""

# Step 4: Navigate to frontend directory
print_info "Navigating to frontend directory..."
if [ ! -f "ui/frontend/package.json" ]; then
    print_error "package.json not found. Please run this script from the project root"
    exit 1
fi
print_success "Found frontend project"
echo ""

# Step 5: Build frontend
print_info "Building frontend..."
cd ui/frontend
npm run build
cd ../..
print_success "Frontend built successfully"
echo ""

# Step 6: Check if Static Web App already exists
print_info "Checking if Static Web App already exists..."
if az staticwebapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    print_info "Static Web App already exists, updating..."
    
    # Deploy updated content
    az staticwebapp update-build-info \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP"
    
    print_success "Static Web App updated successfully"
else
    print_info "Creating new Static Web App..."
    
    # Create Static Web App
    az staticwebapp create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --source . \
        --app-location "ui/frontend" \
        --output-location "dist" \
        --branch main \
        --github-token "" \
        --skip-github-workflow-file
    
    print_success "Static Web App created successfully"
fi
echo ""

# Step 7: Get the Static Web App URL
print_info "Retrieving Static Web App URL..."
APP_URL=$(az staticwebapp show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "defaultHostname" -o tsv)

print_success "Deployment completed successfully!"
echo ""
echo "=========================================="
echo "Frontend URL: https://$APP_URL"
echo "=========================================="
echo ""

# Step 8: Configuration reminder
print_info "Next steps:"
echo "  1. Update backend CORS settings to allow: https://$APP_URL"
echo "  2. Update environment variables in Azure Static Web Apps:"
echo "     - VITE_API_BASE_URL=<your-backend-api-url>"
echo "  3. Test the deployment by opening: https://$APP_URL"
echo ""

# Step 9: Get the backend URL
print_info "Attempting to find backend container app URL..."
if az containerapp show --name "azca*" --resource-group "$RESOURCE_GROUP" &>/dev/null 2>&1; then
    BACKEND_URL=$(az containerapp show --name "azca*" --resource-group "$RESOURCE_GROUP" \
        --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null || echo "")
    
    if [ ! -z "$BACKEND_URL" ]; then
        print_success "Found backend URL: https://$BACKEND_URL"
        echo ""
        print_info "To update CORS on backend, run:"
        echo "  az containerapp update \\
  --name <backend-app-name> \\
  --resource-group $RESOURCE_GROUP \\
  --set-env-vars CORS_ORIGINS=\"https://$APP_URL\""
    fi
fi

echo ""
print_success "Deployment script completed!"
