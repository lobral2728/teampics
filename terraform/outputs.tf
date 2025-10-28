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

output "backend_internal_url" {
  description = "Internal URL for backend (only accessible within Container Apps Environment)"
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "backend_note" {
  description = "Note about backend accessibility"
  value       = "🔒 Backend is INTERNAL ONLY - not accessible from Internet"
}

output "frontend_url" {
  description = "Public URL for frontend application"
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "storage_account_name" {
  description = "Storage account name for profile images"
  value       = azurerm_storage_account.profiles.name
}

output "storage_primary_blob_endpoint" {
  description = "Primary blob endpoint for storage account"
  value       = azurerm_storage_account.profiles.primary_blob_endpoint
}

output "profile_images_url" {
  description = "Base URL for profile images"
  value       = "${azurerm_storage_account.profiles.primary_blob_endpoint}profile-images/"
}

output "mapping_csv_url" {
  description = "URL for the profile mapping CSV file"
  value       = "${azurerm_storage_account.profiles.primary_blob_endpoint}mappings/profile_image_mapping.csv"
}

output "deployment_instructions" {
  description = "Next steps after Terraform apply"
  value       = <<-EOT
    
    ✅ Infrastructure deployed successfully with Azure Container Apps!
    
    🔒 Security Status:
    - Backend: INTERNAL ONLY (not accessible from Internet) ✅
    - Frontend: PUBLIC (accessible from Internet) ✅
    - Frontend connects to backend via internal FQDN within Container Apps Environment ✅
    
    Next steps:
    1. Push Docker images to ACR:
       az acr login --name ${var.acr_name}
       docker tag azuretest001-backend:latest ${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest
       docker tag azuretest001-frontend:latest ${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest
       docker push ${azurerm_container_registry.acr.login_server}/healthcheck-backend:latest
       docker push ${azurerm_container_registry.acr.login_server}/healthcheck-frontend:latest
    
    2. Update Container Apps to pull new images:
       az containerapp update --name healthcheck-backend --resource-group ${azurerm_resource_group.main.name}
       az containerapp update --name healthcheck-frontend --resource-group ${azurerm_resource_group.main.name}
    
    3. Access your application:
       Frontend: https://${azurerm_container_app.frontend.ingress[0].fqdn}
       Backend:  https://${azurerm_container_app.backend.ingress[0].fqdn} (INTERNAL - won't work from browser)
    
    4. Verify security:
       - Frontend URL should work from your browser ✅
       - Backend URL will NOT work from browser (404 or timeout) - this is expected! ✅
       - Frontend can communicate with backend internally ✅
    
    💰 Cost: ~$40-60/month (includes auto-scaling, better monitoring, and native security)
    
    EOT
}
