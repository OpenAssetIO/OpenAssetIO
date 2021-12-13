#!/bin/bash

# Copyright 2013-2021 The Foundry Visionmongers Ltd
# SPDX-License-Identifier: Apache-2.0

# A script to deploy an existing documentation build in
# the current working directory to the target branch of
# the specifed local repository clone.
#
# The script expects the build to exist at `./html`,
# and the target repo to have a writable `docs` branch.

set -e

#
# Constants
#

# The target branch to be updated with the new build
target_branch=docs
# The path to store the docs under in the target branch
html_dir=docs

#
# Args
#

script_name=$0
repo_dir=$1

usage()
{
    echo "usage: $script_name <target-repo-path>"
}

if [[ -z "${repo_dir}" ]]; then
    echo "ERROR: No target repository path specified"
    usage
    exit 1
fi

#
# Deployment
#

# Ensure the checkout has no uncommited changes so we
# only deploy a commited version with an identifiable hash.
if ! git diff --quiet HEAD
then
    echo "ERROR: Please commit all changes and rebuild documentation before deploying"
    git status -s
    exit 1
fi

commit_hash=`git rev-parse --short HEAD`
target_dir="${repo_dir}/${html_dir}"

echo "Copying local build (commit ${commit_hash}) to ${target_dir}"

# Clean up any existing build in the target should files
# have been removed in the new build.
rm -rf "${target_dir}"
# Copy in the new build
cp -r ./html "${target_dir}"

# See if there are any resulting changes in the target
# branch, commit and push if so.

cd "${repo_dir}"

if git diff --quiet HEAD
then
    echo "WARNING: No changes to commit, skipping deployment"
    exit 0
fi

echo "Updated files:"
git status -s

git add .
git commit -s -m "Update docs to ${commit_hash}"
git push

cd -

# Pull the local docs branch, if one exists so it is up to date
git show-branch docs 2>/dev/null && git fetch origin docs:docs || true
