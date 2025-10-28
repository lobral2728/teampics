#!/bin/bash
# Deployment script for Azure - use with Git Bash or WSL

set -e

echo "🚀 Starting Azure deployment..."

# Variables
RESOURCE_GROUP="azuretest001"
ACR_NAME="azuretest001acr"

# Check if logged in to Azure
echo "📋 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✅ Azure login verified"

# Navigate to terraform directory
cd "$(dirname "$0")"

# Terraform init
echo "🔧 Initializing Terraform..."
terraform init

# Terraform plan
echo "📝 Planning deployment..."
terraform plan -out=tfplan

# Confirm before apply
read -p "Apply this plan? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

# Apply
echo "🏗️  Creating Azure resources..."
terraform apply tfplan

# Get ACR server
ACR_SERVER=$(terraform output -raw acr_login_server)
echo "📦 ACR Server: $ACR_SERVER"

# Login to ACR
echo "🔐 Logging in to ACR..."
az acr login --name $ACR_NAME

# Tag and push images
echo "🏷️  Tagging Docker images..."
docker tag azuretest001-backend:latest ${ACR_SERVER}/healthcheck-backend:latest
docker tag azuretest001-frontend:latest ${ACR_SERVER}/healthcheck-frontend:latest

echo "⬆️  Pushing images to ACR..."
docker push ${ACR_SERVER}/healthcheck-backend:latest
docker push ${ACR_SERVER}/healthcheck-frontend:latest

# Restart containers
echo "🔄 Restarting container instances..."
az container restart --resource-group $RESOURCE_GROUP --name healthcheck-backend
az container restart --resource-group $RESOURCE_GROUP --name healthcheck-frontend

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Frontend URL: $(terraform output -raw frontend_url)"
echo "Backend URL:  $(terraform output -raw backend_url)"
echo ""
echo "🎉 Your application is now running in Azure!"
