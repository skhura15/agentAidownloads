// ============================================================================
// User Managed Identity
// ============================================================================
// Creates a user-assigned managed identity for secure access to Azure resources
// This identity is used by Container Apps to pull images from ACR and access Key Vault

@description('Name of the managed identity')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of the managed identity')
output id string = managedIdentity.id

@description('Principal ID of the managed identity')
output principalId string = managedIdentity.properties.principalId

@description('Client ID of the managed identity')
output clientId string = managedIdentity.properties.clientId

@description('Name of the managed identity')
output name string = managedIdentity.name
