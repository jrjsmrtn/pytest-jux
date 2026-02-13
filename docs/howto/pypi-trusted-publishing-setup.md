# PyPI Trusted Publishing Setup

This guide shows how to configure PyPI Trusted Publishing for pytest-jux, enabling automatic, keyless package publishing from GitHub Actions with SLSA attestations.

## What is PyPI Trusted Publishing?

PyPI Trusted Publishing uses OpenID Connect (OIDC) to authenticate GitHub Actions workflows without requiring API tokens. Benefits:

- ✅ **No API Tokens**: No secrets to manage or rotate
- ✅ **Automatic Authentication**: GitHub OIDC provides identity
- ✅ **SLSA Attestations**: Supports provenance attestations
- ✅ **Secure**: Short-lived tokens, scoped to specific workflows

## Prerequisites

- PyPI account with maintainer access to pytest-jux
- Repository admin access to github.com/jux-tools/pytest-jux
- Existing package published to PyPI (for first-time setup)

## Step 1: Configure PyPI Trusted Publishing

### 1.1 Login to PyPI

1. Go to https://pypi.org/
2. Login with your PyPI account (jrjsmrtn)
3. Navigate to "Your projects"

### 1.2 Add Trusted Publisher

1. Click on **pytest-jux** project
2. Go to "Manage" → "Publishing"
3. Scroll to "Trusted publishers" section
4. Click "Add a new publisher"

### 1.3 Enter GitHub Details

Fill in the form:

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `pytest-jux` |
| **Owner** | `jrjsmrtn` |
| **Repository name** | `pytest-jux` |
| **Workflow name** | `build-release.yml` |
| **Environment name** | `pypi` |

Click "Add".

### 1.4 Verify Configuration

You should see:

```
✓ Trusted publisher: github.com/jux-tools/pytest-jux (workflow: build-release.yml, environment: pypi)
```

## Step 2: Configure GitHub Environment

### 2.1 Create PyPI Environment

1. Go to https://github.com/jux-tools/pytest-jux
2. Click "Settings" → "Environments"
3. Click "New environment"
4. Name: `pypi`
5. Click "Configure environment"

### 2.2 Configure Environment Protection Rules (Optional but Recommended)

For production safety, add protection rules:

- **Required reviewers**: Add yourself (jrjsmrtn)
  - Requires manual approval before publishing
- **Wait timer**: 0 minutes (or 5 minutes for extra safety)
- **Deployment branches**: Only tagged branches
  - Click "Add deployment branch rule"
  - Select "Protected branches" or add pattern `refs/tags/v*`

Click "Save protection rules".

### 2.3 Verify Environment

The environment should show:

```
Environment: pypi
Protection rules:
  ✓ Required reviewers: jrjsmrtn
  ✓ Deployment branches: refs/tags/v*
```

## Step 3: Test the Setup

### 3.1 Create a Test Release

```bash
# Ensure you're on main branch with all changes
git checkout main
git pull origin main

# Create a test tag
git tag -a v0.1.5-alpha1 -m "Test SLSA L2 release"
git push github v0.1.5-alpha1
```

### 3.2 Monitor Workflow

1. Go to https://github.com/jux-tools/pytest-jux/actions
2. Watch the "Build and Release" workflow
3. The workflow should:
   - ✅ Build the package
   - ✅ Generate SLSA provenance
   - ⏸️  Wait for approval (if required reviewers configured)
   - ✅ Publish to PyPI with attestations

### 3.3 Approve Deployment (if configured)

If you configured required reviewers:

1. Go to the workflow run
2. Click "Review deployments"
3. Select "pypi"
4. Click "Approve and deploy"

### 3.4 Verify PyPI Upload

1. Go to https://pypi.org/project/pytest-jux/
2. Check that version `0.1.5a1` appears
3. Click on the version
4. Scroll to "Attestations" section
5. You should see: `✓ Attestations published by GitHub Actions`

### 3.5 Verify SLSA Provenance

```bash
# Install verifier
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@latest

# Download package
pip download pytest-jux==0.1.5a1 --no-deps

# Download provenance from GitHub Release
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.1.5-alpha1/pytest-jux-0.1.5a1.intoto.jsonl

# Verify
slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5a1.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  --source-tag v0.1.5-alpha1 \
  pytest_jux-0.1.5a1-py3-none-any.whl

# Expected: PASSED: Verified SLSA provenance
```

## Step 4: Production Release Process

### 4.1 Prepare Release

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Commit changes

git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.1.5"
git push github main
```

### 4.2 Create Release Tag

```bash
# Create and push tag
git tag -a v0.1.5 -m "Release version 0.1.5 with SLSA L2 compliance"
git push github v0.1.5
```

### 4.3 Monitor and Approve

1. Watch GitHub Actions workflow
2. Approve deployment when prompted
3. Verify PyPI upload
4. Verify GitHub Release created

### 4.4 Announce Release

Share release announcement with verification instructions:

```markdown
## pytest-jux v0.1.5 Released 🎉

### What's New
- SLSA Build Level 2 compliance
- Cryptographic provenance for all releases
- [Full changelog](https://github.com/jux-tools/pytest-jux/blob/main/CHANGELOG.md)

### Verify This Release
\`\`\`bash
pip download pytest-jux==0.1.5 --no-deps
curl -L -O https://github.com/jux-tools/pytest-jux/releases/download/v0.1.5/pytest-jux-0.1.5.intoto.jsonl

slsa-verifier verify-artifact \
  --provenance-path pytest-jux-0.1.5.intoto.jsonl \
  --source-uri github.com/jux-tools/pytest-jux \
  pytest_jux-0.1.5-py3-none-any.whl
\`\`\`

See [SLSA Verification Guide](https://github.com/jux-tools/pytest-jux/blob/main/docs/security/SLSA_VERIFICATION.md)
```

## Troubleshooting

### Error: "Publishing forbidden"

**Cause**: Trusted Publisher not configured correctly

**Solution**:
1. Verify PyPI trusted publisher configuration
2. Check owner, repository, workflow name match exactly
3. Ensure environment name is `pypi`

### Error: "OIDC token verification failed"

**Cause**: GitHub environment not configured

**Solution**:
1. Create `pypi` environment in GitHub repository settings
2. Ensure workflow uses `environment: pypi`

### Error: "Workflow requires approval"

**Cause**: Environment has required reviewers configured

**Solution**:
1. Go to workflow run
2. Click "Review deployments"
3. Approve the deployment
4. Or remove required reviewers from environment settings

### Attestations Not Visible on PyPI

**Cause**: PyPI attestations feature may not be enabled

**Solution**:
1. Ensure using `pypa/gh-action-pypi-publish@release/v1`
2. Ensure `attestations: true` in workflow
3. Wait a few minutes for PyPI to process
4. Check GitHub Actions logs for errors

## Security Best Practices

### API Token Removal

After setting up Trusted Publishing:

1. **Revoke old API tokens**:
   - Go to PyPI → Account settings → API tokens
   - Delete any tokens used for pytest-jux publishing

2. **Remove token from GitHub Secrets**:
   - Go to GitHub → Settings → Secrets and variables → Actions
   - Delete `PYPI_API_TOKEN` if it exists

### Environment Protection

**Recommended settings** for production environment:

- ✅ Required reviewers (yourself)
- ✅ Deployment branches: `refs/tags/v*` only
- ✅ Wait timer: 0-5 minutes
- ❌ Allow administrators to bypass: disabled

This prevents accidental publishes and requires conscious approval.

### Workflow Security

**Review workflow permissions**:

```yaml
# .github/workflows/build-release.yml
permissions:
  contents: read  # Minimal for checkout
  id-token: write  # Required for PyPI OIDC
```

Never grant `write` permissions unnecessarily.

## Rollback Plan

If Trusted Publishing fails:

### Emergency Manual Publish

1. Generate API token on PyPI (scoped to pytest-jux)
2. Add as GitHub Secret: `PYPI_API_TOKEN`
3. Modify workflow to use token:

```yaml
- name: Publish to PyPI (fallback)
  env:
    PYPI_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
  run: |
    pip install twine
    twine upload dist/* -u __token__ -p $PYPI_TOKEN
```

4. Remove attestations support temporarily

### Revert to Traditional Publishing

If SLSA provenance causes issues:

1. Comment out provenance job in workflow
2. Use traditional `twine upload`
3. Keep SLSA for GitHub Releases only

## Maintenance

### Rotate Nothing

Trusted Publishing uses short-lived OIDC tokens. No rotation required! 🎉

### Monitor PyPI Project

- Check PyPI project dashboard weekly
- Review attestations are being published
- Monitor download statistics

### Update Workflow

When updating the build workflow:

1. Test with alpha release first
2. Verify provenance generation still works
3. Update PyPI trusted publisher if workflow name changes

## Resources

- [PyPI Trusted Publishing Docs](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Docs](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPI Attestations](https://docs.pypi.org/attestations/)
- [SLSA GitHub Generator](https://github.com/slsa-framework/slsa-github-generator)

---

**Setup Date**: 2025-10-19
**Configured By**: jrjsmrtn
**Last Tested**: Pending first release
