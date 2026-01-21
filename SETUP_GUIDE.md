# Setting Up C4 Literate Python with notes-api CI

This guide walks through setting up c4-literate-python (beta) under
source control and integrating it with the notes-api CI pipeline.

## Step 1: Initialize c4-literate-python Repository

```bash
cd c4-literate-python

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - c4-literate-python v0.9.0 beta"

# Create GitHub repo (via GitHub CLI or web interface)
gh repo create c4-literate-python --public --source=. --remote=origin

# Or add remote manually
git remote add origin https://github.com/yourusername/c4-literate-python.git

# Push to GitHub
git push -u origin main
```

## Step 2: Tag Beta Release

```bash
# Tag the beta release
git tag -a v0.9.0-beta.1 -m "Beta release 0.9.0"
git push origin v0.9.0-beta.1

# Create a GitHub release (optional but recommended)
gh release create v0.9.0-beta.1 \
  --title "v0.9.0 Beta 1" \
  --notes "Initial beta release with core tangler functionality" \
  --prerelease
```

## Step 3: Set Up notes-api Repository

```bash
cd /path/to/notes-api

# Create docs/architecture directory
mkdir -p docs/architecture

# Add .gitignore entry for generated DSL (optional)
echo "# Generated architecture diagrams" >> .gitignore
echo "docs/architecture/workspace.dsl" >> .gitignore

# Or commit the DSL file (recommended for visibility)
# (skip the .gitignore addition above)
```

## Step 4: Add GitHub Actions Workflow to notes-api

Choose one of two approaches:

### Option A: Validation Only (Recommended for Beta)

This validates that C4 annotations are correct and can generate
diagrams, but doesn't auto-commit. Safer for beta testing.

```bash
cd /path/to/notes-api

# Create workflow directory
mkdir -p .github/workflows

# Copy the validation-only workflow
cp /path/to/notes-api-ci-validation-only.yml \
   .github/workflows/ci.yml

# Edit to update repo URL
vim .github/workflows/ci.yml
# Change: https://github.com/yourusername/c4-literate-python.git
# To your actual repo URL
```

**What it does:**
- ✅ Runs tests
- ✅ Validates C4 annotations
- ✅ Generates workspace.dsl
- ✅ Uploads as artifact (downloadable)
- ✅ Comments on PRs with success message
- ❌ Does NOT auto-commit (manual process)

### Option B: Auto-commit (For Production Use)

This automatically commits updated diagrams back to the repo.

```bash
cd /path/to/notes-api

# Copy the auto-commit workflow
cp /path/to/notes-api-ci-workflow.yml \
   .github/workflows/ci.yml

# Edit to update repo URL
vim .github/workflows/ci.yml
```

**What it does:**
- ✅ Everything from Option A
- ✅ Auto-commits workspace.dsl to main branch
- ⚠️ Requires write permissions

**Setup for auto-commit:**
1. Ensure workflow has write permissions:
   - GitHub repo → Settings → Actions → General
   - Workflow permissions → "Read and write permissions"
2. The `[skip ci]` in commit message prevents infinite loops

## Step 5: Update notes-api README

Add a section about architecture diagrams:

```markdown
## Architecture

This project uses [C4 model](https://c4model.com/) annotations
embedded in the source code to generate architecture diagrams.

### Viewing Diagrams

Diagrams are automatically generated in CI and uploaded as artifacts.

To generate locally:

```bash
# Install c4-literate-python
pip install git+https://github.com/yourusername/c4-literate-python.git

# Generate diagrams
c4-literate tangle . -o docs/architecture/workspace.dsl

# View with Structurizr Lite
docker run -it --rm -p 8080:8080 \
  -v $(pwd):/usr/local/structurizr:Z \
  docker.io/structurizr/lite

# Open http://localhost:8080
```

### Modifying Architecture

Architecture is documented using C4 annotations in Python docstrings.
See the [c4-literate-python schema](https://github.com/ChristosDev75/c4-literate-python/blob/main/SCHEMA.md)
for annotation reference.

Example:
```python
"""
@c4-container: API Application
@c4-technology: Python 3.12, FastAPI
@c4-description: REST API providing CRUD operations
"""
```
```

## Step 6: Test the Setup

```bash
cd /path/to/notes-api

# Commit workflow
git add .github/workflows/ci.yml
git commit -m "ci: add C4 architecture diagram generation"

# Push to trigger CI
git push origin dev  # or main
```

**Monitor the workflow:**
1. Go to GitHub → Actions tab
2. Watch the workflow run
3. Check for validation success
4. Download artifact (if using validation-only approach)

## Step 7: Document the Integration

Add to notes-api docs:

```bash
cd /path/to/notes-api

cat > docs/architecture/README.md << 'EOF'
# Architecture Documentation

## Overview

This directory contains auto-generated C4 architecture diagrams for
the notes-api project.

## Files

- `workspace.dsl` - Structurizr DSL (auto-generated from code
  annotations)

## Viewing Diagrams

### Option 1: Structurizr Lite (Docker)

```bash
docker run -it --rm -p 8080:8080 \
  -v $(pwd):/usr/local/structurizr:Z \
  docker.io/structurizr/lite
```

Open http://localhost:8080

### Option 2: Download from CI

If using validation-only CI approach:
1. Go to GitHub Actions
2. Find the latest successful workflow run
3. Download "architecture-diagrams" artifact
4. Extract and view with Structurizr Lite

## Regenerating Diagrams

Diagrams are automatically generated in CI. To generate locally:

```bash
pip install git+https://github.com/yourusername/c4-literate-python.git
c4-literate tangle . -o docs/architecture/workspace.dsl
```

## Modifying Architecture

Edit the C4 annotations in Python source files. See:
- [C4 Annotation Schema](https://github.com/yourusername/c4-literate-python/blob/main/SCHEMA.md)
- [Example annotations](../app/main.py)
EOF

git add docs/architecture/README.md
git commit -m "docs: add architecture documentation README"
```

## Troubleshooting

### "c4-literate command not found" in CI

Check that the workflow is installing c4-literate-python correctly:
```yaml
pip install git+https://github.com/yourusername/c4-literate-python.git@v0.9.0-beta.1
```

### "Permission denied" when auto-committing

Ensure workflow has write permissions:
- Repo Settings → Actions → General → Workflow permissions
- Enable "Read and write permissions"

### Validation fails

Run locally to debug:
```bash
c4-literate validate .
```

This will show specific annotation errors.

## Next Steps

Once comfortable with the beta:

1. **Publish to PyPI** (when ready for v1.0):
   ```bash
   cd c4-literate-python
   python -m build
   twine upload dist/*
   ```

2. **Simplify CI to use PyPI**:
   ```yaml
   pip install c4-literate-python
   ```

3. **Add to requirements.txt** (optional):
   ```
   c4-literate-python>=0.9.0
   ```

4. **Enable auto-commit** if desired

## References

- [c4-literate-python](https://github.com/yourusername/c4-literate-python)
- [C4 Model](https://c4model.com/)
- [Structurizr DSL](https://github.com/structurizr/dsl)
