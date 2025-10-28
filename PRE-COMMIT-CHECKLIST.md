# Pre-Commit Checklist

Run through this checklist before pushing to remote repository.

## ✅ Security Checks

- [ ] **No secrets in code**: `git diff HEAD | Select-String -Pattern "secret|password|key|token" -CaseSensitive:$false`
- [ ] **Environment files ignored**: `git check-ignore .env terraform/terraform.tfvars`
- [ ] **No sensitive IDs**: Search for actual Tenant IDs, Client IDs (should only be in .example files)
- [ ] **Credentials removed**: No Azure connection strings, storage keys, or passwords

## ✅ Large Files Check

- [ ] **Model files ignored**: `git check-ignore backend/model/*.h5 backend/model/*.keras`
- [ ] **No large binaries**: `git status | Select-String -Pattern "\.h5|\.keras|\.weights|\.pkl"`
- [ ] **Terraform provider excluded**: `.terraform/` directory not tracked

## ✅ Generated Files Check

- [ ] **Python cache excluded**: `__pycache__/` not in `git status`
- [ ] **Node modules excluded**: `node_modules/` not in `git status`
- [ ] **Log files excluded**: No `*.log` files in `git status`

## ✅ Code Quality

- [ ] **No syntax errors**: Check recent file edits for syntax issues
- [ ] **TODO/FIXME reviewed**: `git diff HEAD | Select-String "TODO|FIXME"`
- [ ] **Debug code removed**: No `console.log` spam, debug prints for production

## ✅ Documentation

- [ ] **README updated**: Changes reflected in README.md
- [ ] **SECURITY.md current**: Secrets management guide is accurate
- [ ] **Comments added**: Complex logic has explanatory comments

## ✅ Git Hygiene

- [ ] **Commit message meaningful**: Describes what and why
- [ ] **Files staged correctly**: `git status` shows only intended files
- [ ] **No merge conflicts**: All conflicts resolved
- [ ] **Branch up to date**: Pulled latest changes if collaborating

## Quick Verification Commands

```powershell
# See what will be committed
git status

# Check file count (should be reasonable, not thousands)
git status --short | Measure-Object | Select-Object -ExpandProperty Count

# Verify model files are ignored
git check-ignore backend/model/*.h5 backend/model/*.keras

# Verify secrets are ignored
git check-ignore .env terraform/terraform.tfvars secrets.json

# Search for potential secrets in staged changes
git diff --cached | Select-String "secret|password|api.?key" -CaseSensitive:$false

# Check for large files about to be committed
git ls-files | ForEach-Object { if (Test-Path $_) { Get-Item $_ | Where-Object { $_.Length -gt 10MB } } }
```

## Final Step

After all checks pass:

```bash
git add .
git commit -m "Your meaningful commit message"
git push -u origin main
```

## Emergency: If Secrets Were Committed

1. **DO NOT PUSH** if you haven't yet
2. **Amend the commit**: `git commit --amend`
3. **Rotate the secret** immediately in Azure Portal
4. **If already pushed**: Contact repository admin, rotate secrets, force push history cleanup

## All Clear?

✅ All checks passed? Proceed with confidence!
❌ Any issues? Fix them before committing.

**Remember**: It's easier to prevent secrets from entering git than to remove them from history!
