# Azure Deployment Guide

This directory contains Terraform configuration to deploy the Health Check application to Azure.

## Architecture

- **Azure Container Registry (ACR)**: Stores Docker images (Basic tier - most cost-effective)
- **Azure Container Instances (ACI)**: Runs containers (minimal resources for cost optimization)
  - Backend: 0.5 CPU, 1.5GB RAM (TensorFlow needs more memory)
  - Frontend: 0.5 CPU, 0.5GB RAM
- **Public IPs**: Both containers initially accessible from Internet

## Cost Estimate

With this configuration running 24/7:
- ACR Basic: ~$5/month
- Backend ACI: ~$15-20/month
- Frontend ACI: ~$8-10/month
- **Total: ~$28-35/month**

💡 **To save costs**: Stop container instances when not in use with `az container stop`

## Prerequisites

1. **Azure CLI** installed and logged in:
   ```powershell
   az login
   az account show  # Verify correct subscription
   ```

2. **Terraform** installed:
   ```powershell
   terraform --version
   ```

3. **Docker images** built locally (already done):
   ```powershell
   docker images | Select-String "azuretest001"
   ```

## Deployment Steps

### 1. Customize Variables (Optional)

Edit `variables.tf` or create `terraform.tfvars`:

```hcl
resource_group_name = "azuretest001"
location            = "eastus"
acr_name            = "azuretest001acr"      # Must be globally unique
dns_prefix          = "azuretest001"         # Must be globally unique
```

**Important**: `acr_name` and `dns_prefix` must be globally unique across all Azure. If deployment fails, try adding your initials or random numbers.

### 2. Initialize Terraform

```powershell
cd terraform
terraform init
```

### 3. Plan Deployment

```powershell
terraform plan
```

Review the resources that will be created.

### 4. Apply Configuration

```powershell
terraform apply
```

Type `yes` when prompted. This creates:
- Resource group
- Container Registry
- Two Container Instances (will initially fail to start - images not yet pushed)

**Note outputs** - you'll need the ACR login server for the next step.

### 5. Push Docker Images to ACR

Get ACR credentials:
```powershell
# Get ACR login server (from terraform output)
$ACR_SERVER = terraform output -raw acr_login_server

# Login to ACR
az acr login --name azuretest001acr
```

Tag and push images:
```powershell
# Tag images
docker tag azuretest001-backend:latest ${ACR_SERVER}/healthcheck-backend:latest
docker tag azuretest001-frontend:latest ${ACR_SERVER}/healthcheck-frontend:latest

# Push images
docker push ${ACR_SERVER}/healthcheck-backend:latest
docker push ${ACR_SERVER}/healthcheck-frontend:latest
```

### 6. Restart Container Instances

After pushing images, restart the containers:
```powershell
az container restart --resource-group azuretest001 --name healthcheck-backend
az container restart --resource-group azuretest001 --name healthcheck-frontend
```

### 7. Access Your Application

Get URLs from Terraform output:
```powershell
terraform output frontend_url
terraform output backend_url
```

Or manually:
```powershell
# Frontend
$FRONTEND_FQDN = terraform output -raw frontend_fqdn
echo "http://${FRONTEND_FQDN}:3000"

# Backend
$BACKEND_FQDN = terraform output -raw backend_fqdn
echo "http://${BACKEND_FQDN}:5000/health"
```

Open the frontend URL in your browser and test the TensorFlow version check!

## Verify Deployment

```powershell
# Check container status
az container show --resource-group azuretest001 --name healthcheck-backend --query instanceView.state
az container show --resource-group azuretest001 --name healthcheck-frontend --query instanceView.state

# View container logs
az container logs --resource-group azuretest001 --name healthcheck-backend
az container logs --resource-group azuretest001 --name healthcheck-frontend
```

## Management Commands

### View All Resources
```powershell
az resource list --resource-group azuretest001 --output table
```

### Stop Containers (Save Money!)
```powershell
az container stop --resource-group azuretest001 --name healthcheck-backend
az container stop --resource-group azuretest001 --name healthcheck-frontend
```

### Start Containers
```powershell
az container start --resource-group azuretest001 --name healthcheck-backend
az container start --resource-group azuretest001 --name healthcheck-frontend
```

### View Costs
```powershell
az consumption usage list --start-date 2025-10-01 --end-date 2025-10-31
```

## Updating the Application

When you make code changes:

1. Rebuild Docker images locally:
   ```powershell
   docker-compose build
   ```

2. Tag and push to ACR:
   ```powershell
   docker tag azuretest001-backend:latest ${ACR_SERVER}/healthcheck-backend:latest
   docker tag azuretest001-frontend:latest ${ACR_SERVER}/healthcheck-frontend:latest
   docker push ${ACR_SERVER}/healthcheck-backend:latest
   docker push ${ACR_SERVER}/healthcheck-frontend:latest
   ```

3. Restart containers:
   ```powershell
   az container restart --resource-group azuretest001 --name healthcheck-backend
   az container restart --resource-group azuretest001 --name healthcheck-frontend
   ```

## Securing the Backend (Next Phase)

After verifying the deployment works, we'll:
1. Change backend to `ip_address_type = "Private"`
2. Create Azure Virtual Network
3. Place both containers in the same VNet
4. Update frontend to use private backend URL
5. Only frontend will be publicly accessible

## Troubleshooting

### Container won't start
```powershell
# Check logs for errors
az container logs --resource-group azuretest001 --name healthcheck-backend --tail 50

# Check container events
az container show --resource-group azuretest001 --name healthcheck-backend --query instanceView.events
```

### Can't push to ACR
```powershell
# Re-login to ACR
az acr login --name azuretest001acr

# Check ACR credentials
az acr credential show --name azuretest001acr
```

### DNS name already taken
If `dns_prefix` is taken, modify `variables.tf` or override:
```powershell
terraform apply -var="dns_prefix=azuretest001-yourname"
```

## Cleanup

To destroy all resources:
```powershell
terraform destroy
```

Type `yes` when prompted. This will delete:
- Container instances
- Container registry (and all images)
- Resource group

**Warning**: This cannot be undone!

## Next Steps

Once verified working in Azure:
1. Secure backend (make it private)
2. Add Azure Key Vault for secrets
3. Set up Azure Monitor for logging
4. Configure auto-scaling
5. Add custom domain with HTTPS
