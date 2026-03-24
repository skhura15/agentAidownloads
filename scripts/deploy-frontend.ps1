# ============================================================================
# Frontend Deployment Script to Azure (PowerShell)
# ============================================================================
# This script deploys the React frontend to Azure Static Web Apps
# Usage: .\scripts\deploy-frontend.ps1 -ResourceGroup <rg-name> [-Location <location>] [-AppName <name>]
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "westus2",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "agentic-coe-frontend"
)

# Function to print colored output
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# ============================================================================
# Validation
# ============================================================================

Write-Info "Deploying frontend to Azure Static Web Apps"
Write-Info "Resource Group: $ResourceGroup"
Write-Info "Location: $Location"
Write-Info "App Name: $AppName"
Write-Host ""

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Azure CLI is not installed. Please install from https://aka.ms/installazurecliwindows"
    exit 1
}
Write-Success "Azure CLI found"

# Check if resource group exists
Write-Info "Checking if resource group exists..."
$rgExists = az group show --name $ResourceGroup 2>$null
if (-not $rgExists) {
    Write-Error-Custom "Resource group '$ResourceGroup' not found"
    exit 1
}
Write-Success "Resource group found"
Write-Host ""

# Check if logged in
Write-Info "Checking Azure login status..."
$loggedIn = az account show 2>$null
if (-not $loggedIn) {
    Write-Info "Logging in to Azure..."
    az login
}
Write-Success "Logged in to Azure"
Write-Host ""

# ============================================================================
# Build Frontend
# ============================================================================

Write-Info "Building frontend..."
if (-not (Test-Path "ui\frontend\package.json")) {
    Write-Error-Custom "package.json not found. Please run this script from the project root"
    exit 1
}

Push-Location "ui\frontend"
npm run build
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Frontend build failed"
    exit 1
}
Write-Success "Frontend built successfully"
Write-Host ""

# ============================================================================
# Create or Update Static Web App
# ============================================================================

Write-Info "Checking if Static Web App already exists..."
$appExists = az staticwebapp show --name $AppName --resource-group $ResourceGroup 2>$null

if ($appExists) {
    Write-Info "Static Web App already exists, updating..."
    az staticwebapp update-build-info `
        --name $AppName `
        --resource-group $ResourceGroup
    Write-Success "Static Web App updated successfully"
} else {
    Write-Info "Creating new Static Web App..."
    az staticwebapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --location $Location `
        --source . `
        --app-location "ui\frontend" `
        --output-location "dist" `
        --branch main `
        --skip-github-workflow-file
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to create Static Web App"
        exit 1
    }
    Write-Success "Static Web App created successfully"
}
Write-Host ""

# ============================================================================
# Get URLs and Display Results
# ============================================================================

Write-Info "Retrieving Static Web App details..."
$appUrl = az staticwebapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query "defaultHostname" -o tsv

Write-Success "Deployment completed successfully!"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Frontend URL: https://$appUrl" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# ============================================================================
# Configuration Instructions
# ============================================================================

Write-Info "Next steps:"
Write-Host "  1. Update backend CORS settings to allow: https://$appUrl"
Write-Host "  2. Update environment variables in Azure Static Web Apps:"
Write-Host "     - VITE_API_BASE_URL=<your-backend-api-url>"
Write-Host "  3. Test the deployment by opening: https://$appUrl"
Write-Host ""

# ============================================================================
# Find and Display Backend URL
# ============================================================================

Write-Info "Attempting to find backend container app..."
$backendApps = az containerapp list -g $ResourceGroup --query "[].{name:name, fqdn:properties.configuration.ingress.fqdn}" -o json | ConvertFrom-Json

if ($backendApps -and $backendApps.Count -gt 0) {
    foreach ($app in $backendApps) {
        if ($app.name -like "*backend*" -or $app.name -like "*api*") {
            Write-Success "Found backend: $($app.name)"
            Write-Host "  URL: https://$($app.fqdn)"
            Write-Host ""
            Write-Info "To update CORS on backend, run:"
            Write-Host "  az containerapp update \`"
            Write-Host "    --name $($app.name) \`"
            Write-Host "    --resource-group $ResourceGroup \`"
            Write-Host "    --set-env-vars CORS_ORIGINS=`"https://$appUrl`""
            Write-Host ""
            break
        }
    }
}

# ============================================================================
# Post-Deployment Configuration
# ============================================================================

$configApp = Read-Host "Would you like to configure environment variables now? (y/n)"
if ($configApp -eq 'y') {
    $apiUrl = Read-Host "Enter backend API URL (e.g., https://azca....azurecontainerapps.io)"
    
    if ($apiUrl) {
        Write-Info "Setting environment variable VITE_API_BASE_URL=$apiUrl"
        # Note: Static Web Apps don't have direct env var support like Container Apps
        # You need to use Configuration in the Azure Portal or through build configuration
        Write-Info "Please set the following in Azure Portal > Static Web Apps > $AppName > Configuration:"
        Write-Host "  VITE_API_BASE_URL = $apiUrl"
    }
}

Write-Host ""
Write-Success "Deployment script completed!"
