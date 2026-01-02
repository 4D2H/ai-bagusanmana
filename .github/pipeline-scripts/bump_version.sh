#!/bin/bash

# 1. Fetch all tags
git fetch --tags

# 2. Get the latest semantic version tag by sorting all tags
# This ensures we get the highest version, not just ancestor tags
LAST_TAG=$(git tag -l "v*" | sort -V | tail -n 1)
if [ -z "$LAST_TAG" ]; then
    LAST_TAG="v0.0.0"
fi
echo "Current Version: $LAST_TAG"

# ==========================================================
# 3. Analyze commits
# ==========================================================

# Logic: If LAST_TAG is "v0.0.0", it might not exist in git yet.
# We must check if it is valid before running git log.
if [ "$LAST_TAG" == "v0.0.0" ]; then
    echo "First run: No previous tags found. Analyzing full history."
    # Log everything from the beginning of time (include body for BREAKING CHANGE detection)
    LOGS=$(git log --pretty=format:"%s%n%b")
else
    # Standard behavior: Read logs between the last tag and HEAD
    LOGS=$(git log "$LAST_TAG"..HEAD --pretty=format:"%s%n%b")
fi
# ==========================================================

# Remove 'v' for math
VERSION_NO_V=${LAST_TAG#v}
IFS='.' read -r major minor patch <<< "$VERSION_NO_V"

# 4. Check if there are any commits to analyze
if [ -z "$LOGS" ]; then
    echo "No new commits since $LAST_TAG. Bumping PATCH as default."
    NEW_MAJOR=$major
    NEW_MINOR=$minor
    NEW_PATCH=$((patch + 1))
    NEW_TAG="v$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"
    echo "new_tag=$NEW_TAG"
    echo "new_tag=$NEW_TAG" >> $GITHUB_OUTPUT
    exit 0
fi

# 5. Determine the increment
# Check for BREAKING CHANGE (in commit body) or breaking change indicator (! before :)
# Patterns: "feat!:", "fix!:", "BREAKING CHANGE:", "BREAKING-CHANGE:"
if echo "$LOGS" | grep -qE "(^[a-zA-Z]+(\(.+\))?!:|BREAKING CHANGE:|BREAKING-CHANGE:)"; then
    NEW_MAJOR=$((major + 1))
    NEW_MINOR=0
    NEW_PATCH=0
    echo "Detected BREAKING CHANGE. Bumping MAJOR."
# Check for features: "feat:", "feat(scope):"
elif echo "$LOGS" | grep -qE "^feat(\(.+\))?:"; then
    NEW_MAJOR=$major
    NEW_MINOR=$((minor + 1))
    NEW_PATCH=0
    echo "Detected feature. Bumping MINOR."
else
    # This covers "fix:", "docs:", "chore:", etc.
    NEW_MAJOR=$major
    NEW_MINOR=$minor
    NEW_PATCH=$((patch + 1))
    echo "No features or breaking changes detected. Bumping PATCH."
fi

NEW_TAG="v$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"

# 6. Output result
echo "new_tag=$NEW_TAG"
echo "new_tag=$NEW_TAG" >> $GITHUB_OUTPUT