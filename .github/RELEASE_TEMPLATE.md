# Release Checklist Template

Use this checklist when creating a new release of pytest-jux.

## Pre-Release Checklist

- [ ] All tests passing on `develop` branch
- [ ] Code coverage meets requirements (>85%, crypto code 100%)
- [ ] All GitHub Actions workflows passing
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md has [Unreleased] section with all changes
- [ ] No outstanding critical issues or security vulnerabilities

## Release Steps

### Version Number

**Releasing version**: `0.1.x` (update this)

### 1. Ensure Develop Branch is Clean

```bash
git checkout develop
git pull home develop
git status  # Should be clean
```

### 2. Create Release Branch

```bash
git checkout -b release/0.1.x develop
```

### 3. Update Version and Changelog

#### Edit pyproject.toml

```toml
[project]
name = "pytest-jux"
version = "0.1.x"  # Update this line
```

#### Edit CHANGELOG.md

Move items from `[Unreleased]` to new version section:

```markdown
## [Unreleased]

## [0.1.x] - YYYY-MM-DD

### Added
- Feature descriptions here

### Changed
- Change descriptions here

### Fixed
- Bug fix descriptions here
```

Update version comparison links at bottom:

```markdown
[Unreleased]: https://github.com/jrjsmrtn/pytest-jux/compare/v0.1.x...HEAD
[0.1.x]: https://github.com/jrjsmrtn/pytest-jux/compare/v0.1.PREVIOUS...v0.1.x
```

### 4. Commit Release Preparation

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.1.x"
```

- [ ] Version updated in pyproject.toml
- [ ] CHANGELOG.md updated with release date
- [ ] Version links updated in CHANGELOG.md
- [ ] Committed with "chore: bump version to 0.1.x"

### 5. Merge to Main and Tag

```bash
# Merge release branch to main
git checkout main
git pull home main  # Ensure up to date
git merge --no-ff release/0.1.x -m "Release version 0.1.x"

# Tag the release
git tag -a v0.1.x -m "Release version 0.1.x"

# Verify tag
git tag -v v0.1.x
```

- [ ] Merged to main with --no-ff (creates merge commit)
- [ ] Tagged with v0.1.x
- [ ] Tag has GPG signature

### 6. Push to Remotes

```bash
# Push to home remote (always works)
git push home main
git push home v0.1.x

# Push to github remote (may require disabling branch protection)
git push github main
git push github v0.1.x
```

**If GitHub push fails due to branch protection:**

Option 1: Temporarily disable branch protection
1. Go to GitHub Settings → Branches → Branch protection rules
2. Click "Edit" on main branch protection
3. Uncheck all options or delete rule
4. Push: `git push github main --force && git push github v0.1.x`
5. Re-enable branch protection

Option 2: Use temporary branch and PR
```bash
git push github release/0.1.x:temp-release-0.1.x
# Then create PR on GitHub from temp-release-0.1.x to main
# Merge with admin override if needed
```

- [ ] Pushed to home remote (main + tag)
- [ ] Pushed to github remote (main + tag)

### 7. Merge Back to Develop

```bash
git checkout develop
git pull home develop
git merge --no-ff release/0.1.x -m "Merge release/0.1.x back to develop"
git push home develop
```

- [ ] Merged release branch back to develop
- [ ] Pushed to home develop branch

### 8. Cleanup Release Branch

```bash
# Delete local release branch
git branch -d release/0.1.x

# Delete remote release branch (if pushed)
git push home --delete release/0.1.x
```

- [ ] Deleted local release branch
- [ ] Deleted remote release branch (if any)

### 9. Verify Release on GitHub

1. Go to https://github.com/jrjsmrtn/pytest-jux/releases
2. Verify tag v0.1.x appears
3. If needed, create GitHub Release from tag (optional)

- [ ] Tag visible on GitHub
- [ ] GitHub Release created (optional)

## Post-Release Checklist

- [ ] GitHub Actions workflows passing on main branch
- [ ] Tag is properly signed with GPG
- [ ] CHANGELOG.md is up to date
- [ ] Documentation matches released version
- [ ] Announced release (if applicable)

## Rollback Procedure

If the release needs to be rolled back:

```bash
# Delete the tag
git tag -d v0.1.x
git push home --delete v0.1.x
git push github --delete v0.1.x

# Revert main to previous release
git checkout main
git reset --hard v0.1.PREVIOUS
git push home main --force
# (GitHub may require disabling branch protection)
```

## Notes

**Current Remotes:**
- `home`: ssh://gm@yoda.local:2022/volume1/git/pytest-jux.git (all branches)
- `github`: git@github.com:jrjsmrtn/pytest-jux.git (main only)

**Branch Protection:**
- GitHub main branch has protection enabled
- May need to temporarily disable for force pushes
- Protection should be re-enabled after release

**Semantic Versioning:**
- During development: Increase patch level (0.1.x)
- Major changes successfully implemented and tested: Bump patch
- When ready for 1.0.0: Coordinate major version bump

---

**Release completed**: YYYY-MM-DD
**Released version**: v0.1.x
**Released by**: [Your name]
