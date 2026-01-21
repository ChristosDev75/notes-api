#!/bin/bash
# Quick setup script for integrating c4-literate-python with notes-api

set -e

echo "🚀 Setting up C4 Architecture Diagram Generation"
echo ""

# Check we're in notes-api directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Run this from the notes-api root directory"
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p .github/workflows
mkdir -p docs/architecture

# Prompt for c4-literate-python repo URL
read -p "Enter your c4-literate-python repo URL (e.g., https://github.com/user/c4-literate-python.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repo URL required"
    exit 1
fi

# Ask which CI approach
echo ""
echo "Choose CI approach:"
echo "  1) Validation only (recommended for beta) - validates & uploads artifact"
echo "  2) Auto-commit - automatically commits updated diagrams"
read -p "Enter choice (1 or 2): " CHOICE

case $CHOICE in
    1)
        echo "📝 Creating validation-only CI workflow..."
        cat > .github/workflows/ci.yml << EOF
name: CI - Tests and Architecture Validation

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: |
        pip install -r requirements.txt
        pip install pytest
        pytest tests/ -v

  validate-architecture:
    name: Validate C4 Annotations
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - name: Install c4-literate-python
      run: pip install git+${REPO_URL}@main
    - name: Validate annotations
      run: c4-literate validate .
    - name: Generate diagrams
      run: |
        mkdir -p docs/architecture
        c4-literate tangle . -o docs/architecture/workspace.dsl
    - uses: actions/upload-artifact@v4
      with:
        name: architecture-diagrams
        path: docs/architecture/workspace.dsl
EOF
        ;;
    2)
        echo "📝 Creating auto-commit CI workflow..."
        cat > .github/workflows/ci.yml << EOF
name: CI - Tests and Architecture Diagrams

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main, dev ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: |
        pip install -r requirements.txt pytest
        pytest tests/ -v

  generate-diagrams:
    name: Generate Architecture Diagrams
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
      with:
        token: \${{ secrets.GITHUB_TOKEN }}
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    - run: pip install git+${REPO_URL}@main
    - run: |
        mkdir -p docs/architecture
        c4-literate tangle . -o docs/architecture/workspace.dsl
    - name: Commit changes
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add docs/architecture/workspace.dsl
        git diff --quiet && git diff --staged --quiet || \
          git commit -m "docs: update architecture diagrams [skip ci]"
        git push
EOF
        echo ""
        echo "⚠️  Remember to enable workflow write permissions:"
        echo "   GitHub → Settings → Actions → Workflow permissions → Read and write"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Create architecture docs README
echo "📄 Creating architecture documentation..."
cat > docs/architecture/README.md << 'EOF'
# Architecture Documentation

Auto-generated C4 architecture diagrams for notes-api.

## Viewing Diagrams

### With Docker
```bash
docker run -it --rm -p 8080:8080 \
  -v $(pwd):/usr/local/structurizr:Z \
  docker.io/structurizr/lite
```

Open http://localhost:8080

## Regenerating

```bash
pip install git+[your-c4-literate-python-repo-url]
c4-literate tangle . -o docs/architecture/workspace.dsl
```
EOF

# Add to .gitignore or not
echo ""
read -p "Add workspace.dsl to .gitignore? (y/N): " GITIGNORE

if [[ $GITIGNORE =~ ^[Yy]$ ]]; then
    echo "docs/architecture/workspace.dsl" >> .gitignore
    echo "✓ Added to .gitignore (will be downloadable from CI artifacts)"
else
    echo "✓ workspace.dsl will be committed (visible in repo)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review .github/workflows/ci.yml"
echo "  2. git add .github/workflows/ci.yml docs/architecture/"
echo "  3. git commit -m 'ci: add C4 diagram generation'"
echo "  4. git push"
echo ""
echo "Monitor at: https://github.com/your-repo/actions"
