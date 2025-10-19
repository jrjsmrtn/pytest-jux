#!/bin/bash
# Initialize pytest-jux git repository
# This script sets up the git repository following gitflow workflow

set -e

echo "Initializing pytest-jux git repository..."

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Create .git/info/exclude for local ignores if needed
mkdir -p .git/info

# Initial commit on main branch
git checkout -b main 2>/dev/null || git checkout main
git add .
git commit -m "chore: initialize pytest-jux project

- Foundation ADR Sequence (ADR-0001 through ADR-0004)
- Apache License 2.0 adoption
- Complete project structure (Diátaxis, C4 DSL)
- Development configuration (ruff, mypy, pre-commit)
- Python package structure initialized

Follows AI-Assisted Project Orchestration pattern language.
" 2>/dev/null || echo "✓ Already committed"

# Create develop branch
git checkout -b develop 2>/dev/null || git checkout develop
echo "✓ Created develop branch"

# Show status
echo ""
echo "Git repository initialized with gitflow structure:"
echo "  main branch: Production releases"
echo "  develop branch: Active development (current)"
echo ""
echo "Next steps:"
echo "  1. Add remote: git remote add origin <repository-url>"
echo "  2. Push branches: git push -u origin main develop"
echo "  3. Start feature: git checkout -b feature/xml-signing"
echo ""
echo "Project initialization complete! 🎉"
