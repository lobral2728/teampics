# Entra ID Authentication Setup

## Overview
The frontend application is secured with Azure Entra ID (formerly Azure Active Directory) authentication. Users must authenticate with valid Azure AD credentials before accessing the application.

## Configuration Details

### Azure AD App Registration
- **Display Name**: HealthCheck Frontend
- **Client ID**: `bcb23656-c671-4286-92c8-d7cf61700da3`
- **Tenant ID**: `c96c7906-9aec-46c8-8bfb-e035dec27fe5`
- **Redirect URI**: `https://healthcheck-frontend.greenocean-51d12335.eastus.azurecontainerapps.io/.auth/login/aad/callback`

### Authentication Behavior
- **Unauthenticated Action**: Redirect to Login Page
- **Provider**: Azure Active Directory
- **Audience**: Frontend application URL
- **Sign-in Audience**: Single tenant (AzureADMyOrg)

## How It Works

1. **User Access**: When a user navigates to the frontend URL, they are automatically redirected to Azure AD login
2. **Authentication**: User logs in with their Azure AD credentials
3. **Authorization**: Azure AD validates the user belongs to the tenant
4. **Token Issuance**: ID token is issued and stored in session
5. **Access Granted**: User is redirected back to the application

## Managing Access

### Adding Users
Users must be part of your Azure AD tenant to access the application. To add users:

```bash
# Invite external users (guests)
az ad user create --display-name "User Name" --user-principal-name user@yourdomain.com --password "SecurePassword123!"

# Or invite from another organization
az ad user invite --invited-user-email-address external@example.com --send-invitation-message true
```

### Restricting to Specific Users (Optional)
By default, all users in the tenant can access the app. To restrict to specific users:

1. Navigate to Azure Portal → Entra ID → App Registrations
2. Select "HealthCheck Frontend"
3. Go to "Token Configuration" → Add "groups" claim
4. In your app code, validate user groups

### Assigning App Roles (Optional)
Create specific roles for fine-grained access control:

```bash
# This requires updating the app manifest to define roles
# Then assign users to roles via the Enterprise Application
```

## Configuration Files

### Terraform Variables
The authentication settings are configured in `terraform/variables.tf`:
- `aad_client_id`: Azure AD Client ID
- `aad_client_secret`: Azure AD Client Secret (sensitive)
- `tenant_id`: Azure AD Tenant ID

### Container App Authentication
Configured via Azure Container Apps Easy Auth in `terraform/main.tf`.

## Accessing User Information

The application can access authenticated user information via headers:
- `X-MS-CLIENT-PRINCIPAL-NAME`: User's email/UPN
- `X-MS-CLIENT-PRINCIPAL-ID`: User's object ID
- `X-MS-TOKEN-AAD-ID-TOKEN`: ID token (JWT)

Example in Node.js:
```javascript
app.get('/', (req, res) => {
    const userName = req.headers['x-ms-client-principal-name'];
    const userId = req.headers['x-ms-client-principal-id'];
    console.log(`Authenticated user: ${userName} (${userId})`);
});
```

## Testing Authentication

1. **Access the app**: https://healthcheck-frontend.greenocean-51d12335.eastus.azurecontainerapps.io
2. **Login redirect**: You'll be redirected to Microsoft login page
3. **Authenticate**: Enter valid Azure AD credentials
4. **Access granted**: You'll be redirected back to the application

## Logout

Users can log out by navigating to:
```
https://healthcheck-frontend.greenocean-51d12335.eastus.azurecontainerapps.io/.auth/logout
```

## Troubleshooting

### "AADSTS50011: The reply URL does not match"
- Verify the redirect URI in the app registration matches exactly
- Ensure protocol is HTTPS

### "AADSTS700016: Application not found"
- Check the Client ID is correct
- Verify app registration exists in the correct tenant

### Users can't sign in
- Verify users exist in your Azure AD tenant
- Check if app requires admin consent for your tenant
- Review app registration permissions

## Security Best Practices

1. **Client Secret Rotation**: Rotate the client secret periodically
   ```bash
   az ad app credential reset --id bcb23656-c671-4286-92c8-d7cf61700da3
   # Update the secret in Container App
   ```

2. **Use Azure Key Vault**: Store secrets in Key Vault instead of directly in Terraform
3. **Enable Conditional Access**: Apply policies for additional security (MFA, device compliance)
4. **Monitor Sign-ins**: Review Azure AD sign-in logs regularly
5. **Least Privilege**: Only grant necessary permissions to the app registration

## Cost Implications

Easy Auth is included with Azure Container Apps at no additional cost. However:
- Azure AD Premium P1/P2 features (Conditional Access, PIM) require licensing
- External guest users may incur small per-user costs depending on your agreement

## References

- [Azure Container Apps Authentication](https://learn.microsoft.com/en-us/azure/container-apps/authentication)
- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [Easy Auth Overview](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
