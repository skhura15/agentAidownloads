// ============================================================================
// Main Bicep Template for Agentic-CoE Azure Container Apps Deployment
// ============================================================================
// This template provisions:
// - Azure Container Registry for storing container images
// - Azure Container Apps Environment with Log Analytics
// - Azure Container App for the FastAPI backend
// - Key Vault for secure secrets storage
// - Application Insights for monitoring
// - User Managed Identity for secure access
// ============================================================================

targetScope = 'subscription'

// ============================================================================
// Parameters
// ============================================================================

@description('Name of the Azure environment')
param environmentName string

@description('Primary location for all resources')
param location string

@description('Name of the resource group')
param resourceGroupName string = 'rg-${environmentName}'

@description('Azure OpenAI endpoint')
@secure()
param azureOpenAiEndpoint string = ''

@description('Azure OpenAI API key')
@secure()
param azureOpenAiApiKey string = ''

@description('Azure OpenAI deployment name')
param azureOpenAiDeployment string = 'gpt-4o'

@description('Allowed CORS origins')
param corsOrigins string = '*'

// ============================================================================
// Variables
// ============================================================================

// Resource token for unique naming (max 32 chars total)
var resourceToken = uniqueString(subscription().id, location, environmentName)

// Resource names following Azure naming conventions
var containerRegistryName = 'azacr${resourceToken}'
var containerAppEnvName = 'azcae${resourceToken}'
var containerAppName = 'azca${resourceToken}'
var keyVaultName = 'azkv${resourceToken}'
var logAnalyticsName = 'azlaw${resourceToken}'
var appInsightsName = 'azai${resourceToken}'
var managedIdentityName = 'azmi${resourceToken}'

// ============================================================================
// Resource Group
// ============================================================================

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
  }
}

// ============================================================================
// Modules
// ============================================================================

// User Managed Identity - Required for secure access to ACR and Key Vault
module managedIdentity 'resources/managedidentity.bicep' = {
  name: 'managedIdentity'
  scope: rg
  params: {
    name: managedIdentityName
    location: location
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Log Analytics Workspace - Required for Container Apps Environment
module logAnalytics 'resources/loganalytics.bicep' = {
  name: 'logAnalytics'
  scope: rg
  params: {
    name: logAnalyticsName
    location: location
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Application Insights - For APM and telemetry
module appInsights 'resources/appinsights.bicep' = {
  name: 'appInsights'
  scope: rg
  params: {
    name: appInsightsName
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Key Vault - For secure secrets storage
module keyVault 'resources/keyvault.bicep' = {
  name: 'keyVault'
  scope: rg
  params: {
    name: keyVaultName
    location: location
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
    azureOpenAiEndpoint: azureOpenAiEndpoint
    azureOpenAiApiKey: azureOpenAiApiKey
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Container Registry - For storing container images
module containerRegistry 'resources/containerregistry.bicep' = {
  name: 'containerRegistry'
  scope: rg
  params: {
    name: containerRegistryName
    location: location
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Container Apps Environment - Hosting environment for container apps
module containerAppEnv 'resources/containerappenv.bicep' = {
  name: 'containerAppEnv'
  scope: rg
  params: {
    name: containerAppEnvName
    location: location
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsPrimaryKey: logAnalytics.outputs.primaryKey
    tags: {
      'azd-env-name': environmentName
    }
  }
}

// Container App - The FastAPI backend application
module containerApp 'resources/containerapp.bicep' = {
  name: 'containerApp'
  scope: rg
  params: {
    name: containerAppName
    location: location
    containerAppEnvId: containerAppEnv.outputs.id
    containerRegistryLoginServer: containerRegistry.outputs.loginServer
    managedIdentityId: managedIdentity.outputs.id
    managedIdentityClientId: managedIdentity.outputs.clientId
    keyVaultUri: keyVault.outputs.uri
    appInsightsConnectionString: appInsights.outputs.connectionString
    azureOpenAiDeployment: azureOpenAiDeployment
    corsOrigins: corsOrigins
    tags: {
      'azd-env-name': environmentName
      'azd-service-name': 'backend'
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource group ID')
output RESOURCE_GROUP_ID string = rg.id

@description('Container registry endpoint')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer

@description('Container app URL')
output BACKEND_URL string = containerApp.outputs.url

@description('Application Insights connection string')
output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString

@description('Key Vault URI')
output AZURE_KEY_VAULT_URI string = keyVault.outputs.uri
