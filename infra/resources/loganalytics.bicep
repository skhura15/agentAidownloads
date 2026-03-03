// ============================================================================
// Log Analytics Workspace
// ============================================================================
// Creates a Log Analytics workspace for centralized logging
// Required for Container Apps Environment

@description('Name of the Log Analytics workspace')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: 1
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of the Log Analytics workspace')
output id string = logAnalytics.id

@description('Customer ID of the Log Analytics workspace')
output customerId string = logAnalytics.properties.customerId

@description('Primary shared key of the Log Analytics workspace')
output primaryKey string = logAnalytics.listKeys().primarySharedKey

@description('Name of the Log Analytics workspace')
output name string = logAnalytics.name
