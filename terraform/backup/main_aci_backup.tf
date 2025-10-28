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
  sku                 = "Basic"  # Most cost-effective option
  admin_enabled       = true
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = "azuretest001-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Subnet for Container Instances
resource "azurerm_subnet" "container_subnet" {
  name                 = "container-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
  
  delegation {
    name = "container-delegation"
    
    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

# Backend Container Instance (Private - No Public IP)
resource "azurerm_container_group" "backend" {
  name                = "healthcheck-backend"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Private"
  subnet_ids          = [azurerm_subnet.container_subnet.id]
  os_type             = "Linux"
  
  container {
    name   = "backend"
    image  = "${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest"
    cpu    = "0.5"
    memory = "1.5"
    
    ports {
      port     = 5000
      protocol = "TCP"
    }
    
    environment_variables = {
      FLASK_ENV = "production"
    }
  }
  
  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
}

# Frontend Container Instance (Public IP, connects to backend via internal VNet DNS)
resource "azurerm_container_group" "frontend" {
  name                = "healthcheck-frontend"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = "${var.dns_prefix}-frontend"
  os_type             = "Linux"
  
  container {
    name   = "frontend"
    image  = "${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest"
    cpu    = "0.5"
    memory = "0.5"
    
    ports {
      port     = 3000
      protocol = "TCP"
    }
    
    environment_variables = {
      # Use private IP of backend container
      BACKEND_URL_EXTERNAL = "http://${azurerm_container_group.backend.ip_address}:5000"
    }
  }
  
  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }
  
  tags = {
    Environment = "Development"
    Project     = "AzureTest001"
  }
  
  depends_on = [azurerm_container_group.backend]
}
