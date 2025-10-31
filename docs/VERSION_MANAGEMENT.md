# Version Management Guide

**How to use the IAM versioning system**

---

## Quick Start

```bash
# Bump revision (1.1.0 -> 1.1.1) - bugfixes, patches
python3 tools/bump_version.py rev

# Bump minor (1.1.0 -> 1.2.0) - new features
python3 tools/bump_version.py minor

# Bump major (1.1.0 -> 2.0.0) - breaking changes
python3 tools/bump_version.py major
```

---

## What Gets Updated

The `bump_version.py` script automatically updates:

1. **docs/iam_changelog.md** - Current version and adds placeholder entry
2. **README.md** - Version header
3. **iam_client.py** - Version string in docstring
4. **app/__init__.py** - Version in module docstring
5. **SETUP.md** - Version header
6. **INTEGRATION_SUMMARY.md** - Version header
7. **DELIVERABLES_SUMMARY.md** - Version header

---

## Workflow

### 1. Make Your Changes

```bash
# Edit files, add features, fix bugs
vim app/auth/models.py
```

### 2. Bump Version

```bash
# Choose the appropriate bump type
python3 tools/bump_version.py rev
```

This updates all version headers and creates a placeholder in the changelog.

### 3. Fill in Changelog

Edit `docs/iam_changelog.md` and fill in the placeholder:

```markdown
### 🧩 v1.1.2 – 2025-11-01
**Author:** Your Name  
**Type:** Edit  
**Scope:** models.py / password hashing  
**Summary:** Fixed password hashing to use bcrypt with proper salt rounds
```

### 4. Commit

```bash
git add .
git commit -m "fix(iam): improved password hashing security [v1.1.2]"
```

### 5. Tag Release

```bash
# Tag the release
git tag -a iam-v1.1.2 -m "IAM v1.1.2 - improved password security"

# Push tags
git push origin iam-v1.1.2
```

---

## Version Number Meanings

| Type | Example | When to Use |
|------|---------|-------------|
| **Major** | 1.0.0 → 2.0.0 | Breaking changes, architecture redesign, API incompatibility |
| **Minor** | 1.1.0 → 1.2.0 | New features, significant enhancements, new API endpoints |
| **Revision** | 1.1.0 → 1.1.1 | Bugfixes, security patches, refactoring, documentation |

---

## Examples

### Bugfix Release

```bash
# Found a bug in login logic
# Fixed it
python3 tools/bump_version.py rev

# Version: 1.1.1 -> 1.1.2

# Fill in changelog, commit, tag
git commit -m "fix(auth): corrected login redirect logic [v1.1.2]"
git tag -a iam-v1.1.2 -m "IAM v1.1.2 - login bugfix"
```

### Feature Release

```bash
# Added new MFA endpoint
python3 tools/bump_version.py minor

# Version: 1.1.2 -> 1.2.0

git commit -m "feat(mfa): added SMS OTP support [v1.2.0]"
git tag -a iam-v1.2.0 -m "IAM v1.2.0 - SMS MFA support"
```

### Major Release

```bash
# Migrated from Flask to FastAPI
python3 tools/bump_version.py major

# Version: 1.2.0 -> 2.0.0

git commit -m "refactor: migrate to FastAPI [v2.0.0]"
git tag -a iam-v2.0.0 -m "IAM v2.0.0 - FastAPI migration"
```

---

## Changelog Format

Each version entry must include:

```markdown
### 🧩 vX.Y.Z – YYYY-MM-DD
**Author:** Your Name  
**Type:** Insert / Edit / Remove  
**Scope:** [module/files changed]  
**Summary:** [what changed and why]
```

---

## Dependencies

Other projects depending on IAM should specify versions:

```python
# In other project's requirements.txt
iam-client>=1.1.2,<2.0.0
```

Or in Docker:

```dockerfile
FROM python:3.11
RUN pip install iam-client==1.1.2
```

---

## Automated CI/CD

For production, automate version bumping in CI:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [ main ]
    tags: [ 'iam-v*' ]

jobs:
  bump-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Bump version
        run: python3 tools/bump_version.py rev
      - name: Create Release
        run: |
          VERSION=$(grep -m1 "IAM v" docs/iam_changelog.md | cut -d' ' -f2)
          gh release create $VERSION --generate-notes
```

---

## Best Practices

1. ✅ **Always use the bump script** - Don't manually edit versions
2. ✅ **Review changelog placeholder** - Make sure it's in the right place
3. ✅ **Fill in all fields** - Author, Type, Scope, Summary
4. ✅ **Commit frequently** - Small, logical changes per version
5. ✅ **Tag releases** - Always tag production releases
6. ✅ **Update dependencies** - If IAM changes affect other projects, bump their versions

---

## Troubleshooting

### "Could not find version in changelog"

Make sure `docs/iam_changelog.md` has the format:
```markdown
## 🔢 CURRENT ACTIVE VERSION
**IAM v1.1.0 (2025-11-01)** – Description
```

### "Version header not found in X"

Add a version header to the file:
```markdown
**Version:** v1.1.0
```

Or in Python:
```python
"""Version: v1.1.0"""
```

### Changelog formatting issues

The script inserts placeholder entries. If formatting looks wrong, check:
1. Indentation in placeholder
2. Newlines after "---" separators
3. Proper section markers (## 🔢 CURRENT ACTIVE VERSION)

---

## See Also

- `docs/iam_changelog.md` - Full version history
- `tools/bump_version.py` - Source code for bump script
- `docs/iam_prd.md` - Product requirements with version references

---

**Last updated:** 2025-11-01  
**Current version:** v1.1.1

