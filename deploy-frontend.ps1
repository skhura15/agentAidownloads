# Deploy Frontend to Azure
param(
    [string]$ResourceGroup = "rg-dev",
    [string]$Location = "eastus",
    [string]$AppName = "agentic-coe-frontend",
    [string]$RegistryName = "agenticcoeacr"
)

Write-Host "Starting Frontend Deployment..." -ForegroundColor Cyan

# Build the frontend
Write-Host ""
Write-Host "Building frontend..." -ForegroundColor Cyan
Push-Location ui/frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
Pop-Location
Write-Host "Build successful" -ForegroundColor Green

# Check resource group
Write-Host ""
Write-Host "Checking resource group..." -ForegroundColor Cyan
$rgExists = az group exists -n $ResourceGroup
if ($rgExists -eq "true") {
    Write-Host "Resource group exists: $ResourceGroup" -ForegroundColor Green
}

# Login to registry
Write-Host ""
Write-Host "Logging in to registry: $RegistryName" -ForegroundColor Cyan
az acr login -n $RegistryName 2>&1 | Out-Null

# Build image in ACR
$registryUrl = "$RegistryName.azurecr.io"
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Cyan
Write-Host "Image: $registryUrl/$AppName`:latest"

az acr build `
  -r $RegistryName `
  -f ui/frontend/Dockerfile `
  -t "$AppName`:latest" `
  .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Image build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Image built successfully" -ForegroundColor Green

# Check environment
Write-Host ""
Write-Host "Checking Container Apps environment..." -ForegroundColor Cyan
$envName = "cae-dev"
$envExists = az containerapp env show -n $envName -g $ResourceGroup 2>$null
if ($envExists) {
    Write-Host "Environment exists: $envName" -ForegroundColor Green
}

# Get registry password
$registryPassword = az acr credential show -n $RegistryName --query "passwords[0].value" -o tsv

# Deploy
Write-Host ""
Write-Host "Deploying container app..." -ForegroundColor Cyan

az containerapp create `
  -n $AppName `
  -g $ResourceGroup `
  --environment $envName `
  --image "$registryUrl/$AppName`:latest" `
  --registry-server $registryUrl `
  --registry-username "00000000-0000-0000-0000-000000000000" `
  --registry-password $registryPassword `
  --target-port 80 `
  --ingress external `
  --cpu 0.5 --memory 1.0Gi

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    $url = az containerapp show -n $AppName -g $ResourceGroup --query "properties.configuration.ingress.fqdn" -o tsv
    Write-Host ""
    Write-Host "Frontend URL: https://$url" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Update your backend API URL and you're all set!" -ForegroundColor Green
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
