// ============================================================================
// Azure Container Registry
// ============================================================================
// Creates Container Registry for storing container images
// Includes AcrPull role assignment for managed identity

@description('Name of the Container Registry')
param name string

@description('Location for the resource')
param location string

@description('Principal ID of the managed identity for AcrPull access')
param managedIdentityPrincipalId string

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false // Security: Disable anonymous pull
    publicNetworkAccess: 'Enabled'
    zoneRedundancy: 'Disabled'
  }
}

// MANDATORY: AcrPull role assignment for managed identity
// This must be defined BEFORE any container apps that use this registry
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, managedIdentityPrincipalId, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: containerRegistry
  properties: {
    principalId: managedIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of Container Registry')
output id string = containerRegistry.id

@description('Login server of Container Registry')
output loginServer string = containerRegistry.properties.loginServer

@description('Name of Container Registry')
output name string = containerRegistry.name
