#!/bin/bash
# Quick deployment script for Azure Static Web Apps (Fastest option)

RESOURCE_GROUP="rg-dev"
LOCATION="eastus"
APP_NAME="agentic-coe-frontend"

echo "🚀 Quick Frontend Deployment"
echo "=============================="

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not installed. Install from https://aka.ms/azure-cli"
    exit 1
fi

# Login if needed
az account show > /dev/null 2>&1 || az login

# Build frontend
echo -e "\n📦 Building frontend..."
cd ui/frontend
npm run build
cd ../..

# Option 1: Static Web Apps (RECOMMENDED - Fastest)
echo -e "\n🌐 RECOMMENDED: Deploy to Azure Static Web Apps"
echo "=================================================="
echo "Commands to run:"
echo ""
echo "# Create Static Web App"
echo "az staticwebapp create \\"
echo "  --name $APP_NAME \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --location $LOCATION \\"
echo "  --app-location ui/frontend/dist \\"
echo "  --output-location ''"
echo ""
echo "# Grant access (follow the link that appears)"
echo ""

# Option 2: Container Apps
echo -e "\n🐳 ALTERNATIVE: Deploy to Container Apps"
echo "=========================================="

ACR_NAME="agenticcoeacr"

echo "1️⃣  Building Docker image..."
az acr build \
  -r $ACR_NAME \
  -f ui/frontend/Dockerfile \
  -t "$APP_NAME:latest" \
  . --only-show-errors

if [ $? -eq 0 ]; then
  echo -e "\n2️⃣  Deploying to Container Apps..."
  
  REGISTRY_URL="$ACR_NAME.azurecr.io"
  PASSWD=$(az acr credential show -n $ACR_NAME --query "passwords[0].value" -o tsv)
  
  az containerapp create \
    -n $APP_NAME \
    -g $RESOURCE_GROUP \
    --environment cae-dev \
    --image "$REGISTRY_URL/$APP_NAME:latest" \
    --registry-server $REGISTRY_URL \
    --registry-username "00000000-0000-0000-0000-000000000000" \
    --registry-password $PASSWD \
    --target-port 80 \
    --ingress external \
    --cpu 0.5 --memory 1.0Gi
  
  if [ $? -eq 0 ]; then
    URL=$(az containerapp show -n $APP_NAME -g $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)
    echo -e "\n✅ Deployed! Access at: https://$URL"
  else
    echo "❌ Deployment failed"
    exit 1
  fi
else
  echo "❌ Image build failed"
  exit 1
fi
