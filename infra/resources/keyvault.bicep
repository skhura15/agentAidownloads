// ============================================================================
// Azure Key Vault
// ============================================================================
// Creates Key Vault for secure secrets storage
// Stores Azure OpenAI credentials securely

@description('Name of the Key Vault')
param name string

@description('Location for the resource')
param location string

@description('Principal ID of the managed identity for access')
param managedIdentityPrincipalId string

@description('Azure OpenAI endpoint to store')
@secure()
param azureOpenAiEndpoint string = ''

@description('Azure OpenAI API key to store')
@secure()
param azureOpenAiApiKey string = ''

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
  }
}

// Key Vault Secrets User role assignment for managed identity
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentityPrincipalId, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    principalId: managedIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalType: 'ServicePrincipal'
  }
}

// Store Azure OpenAI endpoint if provided
resource azureOpenAiEndpointSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(azureOpenAiEndpoint)) {
  parent: keyVault
  name: 'azure-openai-endpoint'
  properties: {
    value: azureOpenAiEndpoint
  }
}

// Store Azure OpenAI API key if provided
resource azureOpenAiApiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(azureOpenAiApiKey)) {
  parent: keyVault
  name: 'azure-openai-api-key'
  properties: {
    value: azureOpenAiApiKey
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of Key Vault')
output id string = keyVault.id

@description('URI of Key Vault')
output uri string = keyVault.properties.vaultUri

@description('Name of Key Vault')
output name string = keyVault.name
