#!/bin/bash
#
# Hopx Repository Setup Script
# Run this after creating the GitHub repository
#

set -e

echo "══════════════════════════════════════════════"
echo "  🚀 HOPX REPOSITORY SETUP"
echo "══════════════════════════════════════════════"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "⚠️  Git not initialized yet!"
    echo ""
    echo "Run these commands first:"
    echo "  git init"
    echo "  git add README.md"
    echo "  git commit -m 'first commit'"
    echo "  git branch -M main"
    echo "  git remote add origin git@github.com:hopx-ai/hopx.git"
    echo ""
    exit 1
fi

echo "✅ Git repository detected"
echo ""

# Add all the new files
echo "📦 Adding open source files..."
git add LICENSE
git add README.md
git add .gitignore
git add CONTRIBUTING.md
git add CODE_OF_CONDUCT.md
git add SECURITY.md
git add .github/

echo "✅ Files staged"
echo ""

# Show status
echo "📋 Git status:"
git status --short
echo ""

# Add Python SDK
echo "📦 Adding Python SDK..."
git add python/

echo "✅ Python SDK staged"
echo ""

# Add JavaScript SDK  
echo "📦 Adding JavaScript SDK..."
git add javascript/

echo "✅ JavaScript SDK staged"
echo ""

# Add Cookbooks
echo "📦 Adding Cookbooks..."
git add cookbook/

echo "✅ Cookbooks staged"
echo ""

# Show final status
echo "══════════════════════════════════════════════"
echo "  📋 FINAL STATUS"
echo "══════════════════════════════════════════════"
git status

echo ""
echo "══════════════════════════════════════════════"
echo "  ✅ READY TO COMMIT!"
echo "══════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Review the changes above"
echo "2. Commit:"
echo "   git commit -m 'feat: add complete open source structure"
echo ""
echo "   - Add LICENSE (MIT)"
echo "   - Add README.md with full documentation"  
echo "   - Add .gitignore for Python/JavaScript"
echo "   - Add CONTRIBUTING.md guide"
echo "   - Add CODE_OF_CONDUCT.md"
echo "   - Add SECURITY.md policy"
echo "   - Add GitHub issue/PR templates"
echo "   - Add Python SDK (v0.1.19)"
echo "   - Add JavaScript SDK (v0.1.21)"
echo "   - Add cookbooks and examples'"
echo ""
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Enable on GitHub:"
echo "   - Issues"
echo "   - Discussions"
echo "   - Wiki (optional)"
echo ""
echo "🎉 Your repository will be ready for the community!"

