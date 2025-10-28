output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "Login server for Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "Admin username for ACR"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "backend_private_ip" {
  description = "Private IP address for backend (not accessible from Internet)"
  value       = azurerm_container_group.backend.ip_address
}

output "backend_note" {
  description = "Note about backend accessibility"
  value       = "Backend is NOT publicly accessible - only reachable from within VNet"
}

output "frontend_fqdn" {
  description = "Frontend public IP address (no FQDN when using VNet)"
  value       = azurerm_container_group.frontend.ip_address
}

output "frontend_url" {
  description = "Full URL for frontend application"
  value       = "http://${azurerm_container_group.frontend.ip_address}:3000"
}

output "deployment_instructions" {
  description = "Next steps after Terraform apply"
  value       = <<-EOT
    
    ✅ Infrastructure deployed successfully!
    
    🔒 Security Status:
    - Backend: PRIVATE (not accessible from Internet)
    - Frontend: PUBLIC (accessible from Internet)
    - Frontend connects to backend via private VNet
    
    Next steps:
    1. Push Docker images to ACR:
       docker tag azuretest001-backend:latest ${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest
       docker tag azuretest001-frontend:latest ${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest
       docker push ${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest
       docker push ${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest
    
    2. Access your application:
       Frontend: http://${azurerm_container_group.frontend.ip_address}:3000
       Backend:  Private IP ${azurerm_container_group.backend.ip_address}:5000 (VNet only)
    
    3. Verify security:
       - Frontend URL should work from browser
       - Backend is NOT accessible from Internet
       - Frontend communicates with backend internally
    
    EOT
}
