# Git Workflow

## Branch Strategy

### Main Branch
- `master` - Production-ready code
- Always stable and deployable
- Protected branch (no direct commits for major changes)

### Feature Branches
For **major changes**, always work in a feature branch:

```bash
# Create feature branch
git checkout -b feature/typescript-migration
git checkout -b feature/new-game-mode
git checkout -b refactor/state-management

# Work on feature
git add .
git commit -m "Add TypeScript support"

# Push to remote
git push -u origin feature/typescript-migration

# Merge when ready (after testing)
git checkout master
git merge feature/typescript-migration
git push
```

## What Qualifies as a "Major Change"?

**Use a branch for:**
- ✅ New features (new game modes, multiplayer, etc.)
- ✅ Major refactors (TypeScript migration, state management)
- ✅ Breaking changes (API changes, architecture changes)
- ✅ Experimental features (might not ship)
- ✅ Large file reorganizations

**Direct to master is OK for:**
- ✅ Bug fixes (small, isolated)
- ✅ Documentation updates
- ✅ CSS/styling tweaks
- ✅ Test additions
- ✅ Dependency updates

## Benefits of Feature Branches

1. **Safety** - Master stays stable
2. **Experimentation** - Try things without risk
3. **Code Review** - Review before merging
4. **Rollback** - Easy to abandon if needed
5. **Parallel Work** - Multiple features at once

## Example Workflow

```bash
# Starting TypeScript migration
git checkout -b feature/typescript-migration

# Make changes incrementally
git commit -m "Add tsconfig.json"
git commit -m "Convert logger.js to TypeScript"
git commit -m "Convert websocket.js to TypeScript"

# Test thoroughly
npm run validate

# Merge when confident
git checkout master
git merge feature/typescript-migration
git push

# Delete feature branch
git branch -d feature/typescript-migration
```

## Pull Request Workflow (Future)

When working with a team or for major changes:

1. Create feature branch
2. Push to GitHub
3. Open Pull Request
4. Code review
5. CI/CD runs tests
6. Merge to master

## Current Practice

**Going forward:**
- Small fixes/docs → direct to master
- Major changes → feature branch first
- Test in branch before merging
- Keep master stable

This protects production while allowing experimentation! 🚀
