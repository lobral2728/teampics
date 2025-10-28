# Security & Secrets Management

## Protected Secrets

This repository has been configured to prevent accidentally committing sensitive information.

### What's Protected

1. **Environment Variables** (`.env` files)
   - `.env`
   - `.env.*` (except `.env.example`)
   
2. **Terraform Variable Files** (`*.tfvars`)
   - `terraform.tfvars`
   - `*.tfvars.json`
   - Exception: `terraform.tfvars.example` (template only)

3. **Azure Credentials**
   - `*.publishsettings`
   - `*.azureProfile`
   - `.azure/` directory

4. **Secret Files**
   - `*.secret`
   - `secrets/` directory
   - `secrets.json`
   - `credentials.json`

5. **Terraform State** (may contain sensitive outputs)
   - `*.tfstate`
   - `*.tfstate.*`
   - `.terraform/`

### Required Environment Variables

#### Frontend (`frontend/server.js`)
- `BACKEND_URL_EXTERNAL` - Backend API URL
- `STORAGE_BASE_URL` - Azure Storage account URL
- `TENANT_ID` - Azure AD Tenant ID (optional, for authentication)
- `CLIENT_ID` - Azure AD Client ID (optional, for authentication)
- `CLIENT_SECRET` - Azure AD Client Secret (optional, for authentication)

#### Backend (`backend/app.py`)
- `PORT` - Service port (default: 5000)

#### Terraform (`terraform/variables.tf`)
- `aad_client_id` - Azure AD Client ID
- `aad_client_secret` - Azure AD Client Secret (marked as sensitive)
- `tenant_id` - Azure AD Tenant ID

### Setup Instructions

1. **Copy example files:**
   ```bash
   cp .env.example .env
   cp terraform/terraform.tfvars.example terraform/terraform.tfvars
   ```

2. **Fill in your actual values** in the copied files (NOT the .example files)

3. **Verify .gitignore:**
   ```bash
   git status
   ```
   Ensure `.env` and `terraform.tfvars` are NOT listed as untracked files

4. **Never commit secrets:**
   - Use `.example` files for templates
   - Use environment variables in CI/CD
   - Consider Azure Key Vault for production

### Azure Deployment

Secrets are managed in Azure Container Apps as:
- **Environment Variables**: Set via `az containerapp update --env-vars`
- **Secrets**: Stored in Container App configuration (not in code)

Current deployment sets these via Azure CLI:
```bash
az containerapp update --name healthcheck-frontend \
  --env-vars \
    BACKEND_URL_EXTERNAL=https://... \
    STORAGE_BASE_URL=https://... \
    TENANT_ID=secretRef:tenant-id \
    CLIENT_ID=secretRef:client-id \
    CLIENT_SECRET=secretRef:graph-client-secret
```

### What's Safe to Commit

✅ **Safe to commit:**
- `.env.example` - Template file
- `terraform.tfvars.example` - Template file
- Application code referencing `process.env.*`
- Terraform files using `var.*` references
- Documentation with placeholder values

❌ **Never commit:**
- `.env` - Actual environment variables
- `terraform.tfvars` - Actual Terraform variables
- Any file with actual Client IDs, Secrets, or Tenant IDs
- Azure storage account keys
- Container registry passwords

### Checking for Leaked Secrets

Before committing, always verify:

```bash
# Check what's being tracked
git status

# Search for potential secrets
git diff HEAD | grep -i "secret\|password\|key\|token"

# Verify .gitignore is working
git check-ignore .env terraform/terraform.tfvars
```

### If Secrets Were Committed

If secrets were accidentally committed:

1. **Rotate the secrets immediately** (generate new ones)
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch PATH_TO_FILE" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if already pushed to remote)
4. **Notify your team** to re-clone the repository

### Best Practices

1. ✅ Use `.example` files for templates
2. ✅ Reference environment variables in code
3. ✅ Mark sensitive Terraform variables as `sensitive = true`
4. ✅ Use Azure Key Vault for production secrets
5. ✅ Rotate secrets regularly
6. ✅ Use managed identities when possible
7. ❌ Never hardcode secrets in source code
8. ❌ Never commit `.env` or `.tfvars` files
9. ❌ Never share secrets in chat, email, or docs

### Current Status

✅ All secrets are properly excluded from git
✅ Template files created (`.env.example`, `terraform.tfvars.example`)
✅ Hardcoded values removed from source code
✅ Environment variables required for all sensitive values
✅ Terraform sensitive variables marked appropriately
✅ `.gitignore` configured for all secret file types
