# Networking Limitations with Azure Container Instances

## Current Architecture Challenge

Azure Container Instances (ACI) has limitations when trying to mix public and private networking:

1. **Private IP with VNet**: Backend can be private in a VNet ✅ (Working)
2. **Public IP with VNet**: Frontend cannot be public AND in the VNet ❌ (Not supported by ACI)
3. **Cross-VNet Communication**: Public frontend cannot reach private backend in VNet ❌

## Options to Achieve Secure Backend

### Option 1: Both Containers Public (Current Working State)
- ✅ Simplest and working
- ❌ Backend exposed to Internet
- **Cost**: ~$28-35/month

### Option 2: Network Security Groups (NSG) on Backend
- Keep both containers public
- Add NSG rules to only allow traffic from frontend IP to backend
- ✅ Backend effectively secured
- ✅ Works with current ACI setup
- **Cost**: ~$28-35/month (NSG is free)

### Option 3: Azure Container Apps (Recommended for Production)
- Modern serverless container platform
- ✅ Built-in ingress control
- ✅ Native VNet integration
- ✅ Internal/external endpoints supported
- ✅ Auto-scaling, better monitoring
- **Cost**: ~$40-60/month

### Option 4: Azure Kubernetes Service (AKS)
- Full Kubernetes cluster
- ✅ Complete network control
- ✅ Production-grade security
- ❌ More complex to manage
- **Cost**: ~$70-100/month minimum

### Option 5: Application Gateway + Private ACI
- Both containers private in VNet
- Application Gateway provides public ingress to frontend only
- ✅ True private backend
- ❌ Application Gateway is expensive
- **Cost**: ~$150-200/month

## Recommended Approach for This Project

Given the requirements and cost constraints, **Option 2 (NSG)**  is the best balance:

1. Backend has private IP in VNet (already done)
2. Frontend public (revert change)
3. Add NSG to restrict backend access to frontend IP only

This achieves the security goal at minimal cost.

## Implementation for NSG Approach

See `main_with_nsg.tf` for the Terraform configuration that implements Option 2.
