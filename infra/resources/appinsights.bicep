// ============================================================================
// Application Insights
// ============================================================================
// Creates Application Insights for APM and telemetry
// Connected to Log Analytics workspace

@description('Name of Application Insights')
param name string

@description('Location for the resource')
param location string

@description('Resource ID of the Log Analytics workspace')
param logAnalyticsWorkspaceId string

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspaceId
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of Application Insights')
output id string = appInsights.id

@description('Connection string for Application Insights')
output connectionString string = appInsights.properties.ConnectionString

@description('Instrumentation key for Application Insights')
output instrumentationKey string = appInsights.properties.InstrumentationKey

@description('Name of Application Insights')
output name string = appInsights.name
