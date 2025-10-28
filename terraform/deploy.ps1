# PowerShell deployment script for Azure

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Azure deployment..." -ForegroundColor Green

# Variables
$RESOURCE_GROUP = "azuretest001"
$ACR_NAME = "azuretest001acr"

# Check if logged in to Azure
Write-Host "📋 Checking Azure login..." -ForegroundColor Yellow
try {
    az account show | Out-Null
    Write-Host "✅ Azure login verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Navigate to terraform directory
Set-Location $PSScriptRoot

# Terraform init
Write-Host "🔧 Initializing Terraform..." -ForegroundColor Yellow
terraform init

# Terraform plan
Write-Host "📝 Planning deployment..." -ForegroundColor Yellow
terraform plan -out=tfplan

# Confirm before apply
$confirm = Read-Host "Apply this plan? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Apply
Write-Host "🏗️  Creating Azure resources..." -ForegroundColor Yellow
terraform apply tfplan

# Get ACR server
$ACR_SERVER = terraform output -raw acr_login_server
Write-Host "📦 ACR Server: $ACR_SERVER" -ForegroundColor Cyan

# Login to ACR
Write-Host "🔐 Logging in to ACR..." -ForegroundColor Yellow
az acr login --name $ACR_NAME

# Tag and push images
Write-Host "🏷️  Tagging Docker images..." -ForegroundColor Yellow
docker tag azuretest001-backend:latest "$ACR_SERVER/healthcheck-backend:latest"
docker tag azuretest001-frontend:latest "$ACR_SERVER/healthcheck-frontend:latest"

Write-Host "⬆️  Pushing images to ACR..." -ForegroundColor Yellow
docker push "$ACR_SERVER/healthcheck-backend:latest"
docker push "$ACR_SERVER/healthcheck-frontend:latest"

# Restart containers
Write-Host "🔄 Restarting container instances..." -ForegroundColor Yellow
az container restart --resource-group $RESOURCE_GROUP --name healthcheck-backend
az container restart --resource-group $RESOURCE_GROUP --name healthcheck-frontend

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
$FRONTEND_URL = terraform output -raw frontend_url
$BACKEND_URL = terraform output -raw backend_url
Write-Host "Frontend URL: $FRONTEND_URL" -ForegroundColor Cyan
Write-Host "Backend URL:  $BACKEND_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 Your application is now running in Azure!" -ForegroundColor Green
