variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "azuretest001"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"  # One of the most cost-effective regions
}

variable "acr_name" {
  description = "Name of the Azure Container Registry (must be globally unique, alphanumeric only)"
  type        = string
  default     = "azuretest001acr"
}

variable "dns_prefix" {
  description = "DNS prefix for container instances (must be globally unique)"
  type        = string
  default     = "azuretest001"
}

variable "aad_client_id" {
  description = "Azure AD App Registration Client ID for frontend authentication"
  type        = string
  # No default - must be provided via environment variable or tfvars file
}

variable "aad_client_secret" {
  description = "Azure AD App Registration Client Secret for frontend authentication"
  type        = string
  sensitive   = true
  # No default - must be provided via environment variable or tfvars file
}

variable "tenant_id" {
  description = "Azure AD Tenant ID"
  type        = string
  # No default - must be provided via environment variable or tfvars file
}
