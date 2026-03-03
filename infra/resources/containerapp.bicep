// ============================================================================
// Azure Container App
// ============================================================================
// Creates Container App for the FastAPI backend
// Uses managed identity for secure ACR access

@description('Name of the Container App')
param name string

@description('Location for the resource')
param location string

@description('Resource ID of the Container Apps Environment')
param containerAppEnvId string

@description('Login server of the Container Registry')
param containerRegistryLoginServer string

@description('Resource ID of the managed identity')
param managedIdentityId string

@description('Client ID of the managed identity')
param managedIdentityClientId string

@description('URI of Key Vault')
param keyVaultUri string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Azure OpenAI deployment name')
param azureOpenAiDeployment string = 'gpt-4o'

@description('Allowed CORS origins')
param corsOrigins string = '*'

@description('Tags for the resource')
param tags object = {}

// ============================================================================
// Resources
// ============================================================================

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnvId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        corsPolicy: {
          allowedOrigins: split(corsOrigins, ',')
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: true
          maxAge: 86400
        }
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          // MANDATORY: Use base container image, will be replaced by azd deploy
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'ENVIRONMENT'
              value: 'prod'
            }
            {
              name: 'LOG_LEVEL'
              value: 'INFO'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: azureOpenAiDeployment
            }
            {
              name: 'AZURE_KEY_VAULT_URI'
              value: keyVaultUri
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentityClientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
            {
              name: 'API_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'API_PORT'
              value: '8000'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Resource ID of Container App')
output id string = containerApp.id

@description('URL of Container App')
output url string = 'https://${containerApp.properties.configuration.ingress.fqdn}'

@description('Name of Container App')
output name string = containerApp.name

@description('FQDN of Container App')
output fqdn string = containerApp.properties.configuration.ingress.fqdn
