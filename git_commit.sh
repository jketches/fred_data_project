#!/bin/bash

# Navigate to the project directory (optional if you're already in the right folder)
# cd /path/to/your/project

# Stage all changes (you can modify this to be more specific if needed)
git add .

# Prompt the user for a commit message
echo "Enter your commit message:"
read commit_message

# Check if the commit message is empty
if [ -z "$commit_message" ]; then
  echo "Error: Commit message cannot be empty. Commit aborted."
  exit 1
fi

# Commit changes with the provided message
git commit -m "$commit_message"

# Push changes to the remote repository (optional if you want to push immediately)
git push

# Provide feedback to the user
echo "Commit successfully pushed with message: $commit_message"
