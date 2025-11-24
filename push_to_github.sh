#!/bin/bash
# Helper script to push to GitHub

echo "=========================================="
echo "Push to GitHub: xiq-edge-migration"
echo "=========================================="
echo ""
echo "You'll need a Personal Access Token from:"
echo "https://github.com/settings/tokens/new"
echo ""
echo "Required scope: 'repo' (full control)"
echo ""
echo "When prompted:"
echo "  Username: [your GitHub username]"
echo "  Password: [paste your token]"
echo ""
echo "=========================================="
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo ""
    echo "View your repository at:"
    echo "https://github.com/yourusername/xiq-edge-migration"
    echo ""
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "  1. Token has 'repo' scope"
    echo "  2. Token hasn't expired"
    echo "  3. Repository exists"
    echo ""
fi
