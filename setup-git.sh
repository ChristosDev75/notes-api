#!/bin/bash

# Notes API - Git Setup Script
# This script initializes the git repository and prepares it for GitHub

echo "🚀 Setting up Notes API Git Repository..."
echo ""

# Initialize git repo
echo "📦 Initializing git repository..."
git init

# Add all files
echo "➕ Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Notes API with FastAPI, SQLite, tests, and CI

- FastAPI REST API with CRUD endpoints
- SQLite database backend
- Comprehensive pytest test suite
- GitHub Actions CI pipeline
- Auto-generated API documentation"

# Rename to main branch
echo "🌿 Renaming branch to main..."
git branch -M main

# Create dev branch
echo "🌿 Creating dev branch..."
git branch dev

echo ""
echo "✅ Git repository initialized!"
echo ""
echo "📝 Next steps:"
echo "1. Create a new repository on GitHub (https://github.com/new)"
echo "2. Run these commands (replace YOUR_USERNAME with your GitHub username):"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/notes-api.git"
echo "   git push -u origin main"
echo "   git push -u origin dev"
echo ""
echo "3. Go to your GitHub repo and check the Actions tab to see CI running!"
echo ""
echo "🎉 Ready to vibe code!"
