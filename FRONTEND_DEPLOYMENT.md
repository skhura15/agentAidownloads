# Frontend Deployment to Azure

Deploy your React frontend to the same resource group (`rg-dev`) as your backend.

## 🎯 Option 1: Azure Static Web Apps (Recommended for React SPAs)

### Prerequisites
- Azure CLI installed (`az login`)
- Resource group already created (`rg-dev`)
- Backend already deployed and accessible

### Deployment Steps

```bash
# 1. Navigate to the frontend directory
cd ui/frontend

# 2. Build the frontend
npm run build

# 3. Create Azure Static Web App
az staticwebapp create \
  --name agentic-coe-frontend \
  --resource-group rg-dev \
  --source . \
  --location westus2 \
  --branch main \
  --app-location "ui/frontend" \
  --output-location "dist"

# 4. Configure environment variables
az staticwebapp environment create \
  --name agentic-coe-frontend \
  --resource-group rg-dev \
  --environment-name production \
  -p VITE_API_BASE_URL="https://<backend-url>"
```

### Advantages
✅ Simple deployment (just upload built files)  
✅ Automatic SSL/HTTPS  
✅ Built-in CDN  
✅ Serverless (pay per use)  
✅ Free tier available  
✅ No container management needed  

---

## 🎯 Option 2: Azure Container Apps (Consistent with Backend)

### Prerequisites
- Backend already deployed to `rg-dev`
- Azure CLI with Container Apps extension
- Docker and container image already prepared

### 2a. Build and Push Docker Image

```bash
# 1. Build Docker image
cd ui/frontend
docker build -t agentic-coe-frontend:latest .

# 2. Get your container registry endpoint (from backend deployment)
$ACR_NAME = "azacr<your-unique-token>"
$ACR_LOGIN_SERVER = "$ACR_NAME.azurecr.io"

# 3. Login to ACR
az acr login --name $ACR_NAME

# 4. Tag the image
docker tag agentic-coe-frontend:latest "$ACR_LOGIN_SERVER/agentic-coe-frontend:latest"

# 5. Push to ACR
docker push "$ACR_LOGIN_SERVER/agentic-coe-frontend:latest"
```

### 2b. Deploy Container App

```bash
# Get environment variables from backend deployment
$BACKEND_URL = "https://<your-backend-container-app-url>"
$CONTAINER_APP_ENV = "azcae<your-unique-token>"

# Create frontend container app
az containerapp create \
  --name agentic-coe-frontend \
  --resource-group rg-dev \
  --environment $CONTAINER_APP_ENV \
  --image "$ACR_LOGIN_SERVER/agentic-coe-frontend:latest" \
  --target-port 80 \
  --ingress 'external' \
  --env-vars \
    VITE_API_BASE_URL=$BACKEND_URL \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-identity system
```

### Advantages
✅ Consistent with backend architecture  
✅ Full control over container  
✅ Same monitoring/logging as backend  
✅ Easy to manage alongside backend  

---

## 📋 Using Azure Developer CLI (azd)

### Prerequisites
- Azure Developer CLI (`azd`) installed
- Already initialized azd environment

### Update azure.yaml

Add frontend service to your `azure.yaml`:

```yaml
services:
  backend:
    project: .
    language: python
    host: containerapp
    docker:
      path: ./Dockerfile
      context: .

  frontend:
    project: .
    language: javascript
    host: staticwebapp
    docker:
      path: ./ui/frontend/Dockerfile
      context: ./ui/frontend
```

### Deploy Using azd

```bash
# 1. Set up Azure Developer environment
azd config set defaults.subscription <your-subscription-id>
azd config set defaults.location westus2

# 2. Deploy infrastructure and services
azd up

# 3. View deployment outputs
azd show
```

---

## 🔗 Post-Deployment Configuration

### Update CORS Settings
If using Container Apps and need to update CORS:

```bash
az containerapp update \
  --name agentic-coe-backend \
  --resource-group rg-dev \
  --set-env-vars CORS_ORIGINS="https://agentic-coe-frontend.azurecontainerapps.io"
```

### Update Environment Variables
For Static Web Apps, update the API base URL in configuration:

```bash
# Create staticwebapp.config.json in ui/frontend/
cat > ui/frontend/staticwebapp.config.json << 'EOF'
{
  "routes": [
    {
      "route": "/assets/*",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "route": "/*",
      "serve": "/index.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*"]
  }
}
EOF
```

---

## 🧪 Testing

After deployment:

```bash
# 1. Get frontend URL
az staticwebapp show \
  --name agentic-coe-frontend \
  --resource-group rg-dev \
  --query "defaultHostname" -o tsv

# 2. Test API connectivity
curl "https://<frontend-url>/api/health" \
  -H "Origin: https://<frontend-url>"
```

---

## 📊 Monitoring

### View Logs
```bash
# For Static Web Apps
az staticwebapp routes list \
  --name agentic-coe-frontend \
  --resource-group rg-dev

# For Container Apps
az containerapp logs show \
  --name agentic-coe-frontend \
  --resource-group rg-dev
```

---

## 🗺️ Next Steps

1. **Choose deployment option** (Static Web Apps or Container Apps)
2. **Build the frontend**: `npm run build`
3. **Run deployment commands** above
4. **Verify deployment** by accessing the frontend URL
5. **Update backend CORS** to allow frontend domain
6. **Test end-to-end** functionality

---

## ⚠️ Troubleshooting

### Static Web App not serving SPA correctly
→ Ensure `staticwebapp.config.json` exists with redirect rule

### Container App can't reach backend
→ Check CORS settings and network connectivity
→ Verify API_BASE_URL environment variable

### Build fails
→ Ensure `npm install` succeeds locally first
→ Check Node.js version (need 18+)

---

## 💰 Cost Optimization

- **Static Web Apps**: Free tier covers most use cases
- **Container Apps**: Shared infrastructure with backend saves costs
- **ACR**: Keep image retention low to reduce storage

---

## 📚 References

- [Azure Static Web Apps](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
