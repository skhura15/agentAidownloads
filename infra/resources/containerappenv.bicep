// ============================================================================
// Azure Container Apps Environment
// ============================================================================
// Creates Container Apps Environment for hosting container apps
// Connected to Log Analytics for centralized logging

@description('Name of the Container Apps Environment')
param name string

@description('Location for the resource')
param location string

@description('Customer ID of the Log Analytics workspace')
param logAnalyticsCustomerId string

@description('Primary shared key of the Log Analytics workspace')
@secure()
param logAnalyticsPrimaryKey string

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsPrimaryKey
      }
    }
    zoneRedundant: false
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of Container Apps Environment')
output id string = containerAppEnv.id

@description('Default domain of Container Apps Environment')
output defaultDomain string = containerAppEnv.properties.defaultDomain

@description('Name of Container Apps Environment')
output name string = containerAppEnv.name
