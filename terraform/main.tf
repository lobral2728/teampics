terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Storage Account for profile images
resource "azurerm_storage_account" "profiles" {
  name                     = "${var.resource_group_name}profiles"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"  # Locally redundant storage (most cost-effective)
  
  # Enable static website hosting for direct access to images
  static_website {
    index_document = "index.html"
  }
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Blob container for profile images
resource "azurerm_storage_container" "images" {
  name                  = "profile-images"
  storage_account_name  = azurerm_storage_account.profiles.name
  container_access_type = "blob"  # Public read access for blobs
}

# Blob container for mapping CSV
resource "azurerm_storage_container" "mappings" {
  name                  = "mappings"
  storage_account_name  = azurerm_storage_account.profiles.name
  container_access_type = "blob"  # Public read access
}

# Log Analytics Workspace (required for Container Apps)
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "azuretest001-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Container Apps Environment
resource "azurerm_container_app_environment" "env" {
  name                       = "azuretest001-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Backend Container App (Internal ingress only - not accessible from Internet)
resource "azurerm_container_app" "backend" {
  name                         = "healthcheck-backend"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }
  
  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }
  
  template {
    container {
      name   = "backend"
      image  = "${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest"
      cpu    = 0.5
      memory = "1Gi"
      
      env {
        name  = "FLASK_ENV"
        value = "production"
      }
    }
    
    min_replicas = 1
    max_replicas = 2
  }
  
  ingress {
    external_enabled = false  # Internal only - not accessible from Internet
    target_port      = 5000
    transport        = "http"
    
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Frontend Container App (External ingress - accessible from Internet)
resource "azurerm_container_app" "frontend" {
  name                         = "healthcheck-frontend"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  
  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }
  
  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }
  
  secret {
    name  = "graph-client-secret"
    value = var.aad_client_secret
  }
  
  template {
    container {
      name   = "frontend"
      image  = "${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest"
      cpu    = 0.5
      memory = "1Gi"
      
      env {
        name  = "BACKEND_URL_EXTERNAL"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
      }
    }
    
    min_replicas = 1
    max_replicas = 3
  }
  
  ingress {
    external_enabled = true  # External - accessible from Internet
    target_port      = 3000
    transport        = "http"
    
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
  
  depends_on = [azurerm_container_app.backend]
}
