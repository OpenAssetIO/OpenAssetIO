default: container-build

##
# This Makefile builds the OpenAssetIO documentation bundle.
#
# By default it uses a Docker container and builds into the working
# directory. A local build can be run using `make html`.
#
# Docker builds solely require docker itself, local builds require
# `git`, `python3-venv`, `doxygen` and `graphviz` to be installed. See
# README.md for more information.
#
# The `tooling` target takes care of installing `sass` and `doxypy` if
# required.  They will be installed into the current working directory
# for both Docker and local builds. The `clean-tooling` target (invoked
# by `clean`) will remove these if required.
#
# NB. This file is sensitive to the current working directory, and
# should not be used with `make -f`.
##

CONTAINER_VERSION=1.1.1
OPENASSETIO_CORE_ABI_VERSION=v1
CONTAINER_NAME=openassetio-doc-build

##
## Container settings
##

# The following variables are considered when using Docker
# to build the documentation:
#
#  GITHUB_ORG: The organisation to pull containers from (and publish
#              to). If unspecified, then `openassetio` will
#              be used. Note: org names must be lowercase.
#
# When publishing, the following additional vars MUST be set:
#
#  GITHUB_PAT:      A GitHub Personal Access Token with the following
#                   permissions: write:packages.
#  GITHUB_USERNAME: The GitHub username whose token is being used.
#
# eg:
#  GITHUB_USERNAME=<username> GITHUB_PAT=<token> make publish-docker
#
ifndef GITHUB_ORG
GITHUB_ORG = openassetio
endif

# Docker images are published to the GitHub container registry
CONTAINER_PATH = ghcr.io/$(GITHUB_ORG)/$(CONTAINER_NAME)
CONTAINER_TAG = $(CONTAINER_PATH):$(CONTAINER_VERSION)

##
## PHONY TARGETS
##

.PHONY: clean clean-html clean-tooling clean-docker container-build deploy docker-image html \
        publish-docker todo tooling

#
# Container build - Runs this Makefile via docker
#

container-build:
	docker run --rm -v `pwd`/../:/src $(CONTAINER_TAG) bash -c 'make -C /src/doc html'

# Targets for building/tagging/publishing the container

docker-image: Dockerfile
	docker build . -t $(CONTAINER_TAG)

clean-docker:
	docker image rm $(CONTAINER_TAG) --force

publish-docker: docker-image
	echo $(GITHUB_PAT) | docker login ghcr.io --username $(GITHUB_USERNAME) --password-stdin
	docker push $(CONTAINER_TAG)
	# Update the 'latest' tag
	docker tag $(CONTAINER_TAG) $(CONTAINER_PATH):latest
	docker push $(CONTAINER_PATH):latest

#
# Local build - Invokes Doxygen locally
#

# Tooling paths
VENV = ./venv
SASS = ./node_modules/.bin/sass

# Force clean-html as we don't declare all the sources
html: clean-html src/styles.css tooling
	. $(VENV)/bin/activate && OPENASSETIO_CORE_ABI_VERSION=$(OPENASSETIO_CORE_ABI_VERSION) doxygen ./Doxyfile

tooling: $(SASS) $(VENV)

#
# Deployment to GH Pages
#

# $OPENASSETIO_DOCS_REPO_DIR can be set to point to an existing checkout
# of the target branch to deploy to.
# If unset, a temporary checkout will be created.
ifndef OPENASSETIO_DOCS_REPO_DIR
OPENASSETIO_DOCS_REPO_DIR = /tmp/repo
DOCSREPO_CLEANUP = true
else
DOCSREPO_CLEANUP = false
endif

# Docs repo constants for GitHub Pages branch.
DOCSREPO_BRANCH = docs
DOCSREPO_HTML_DIR = docs

# The `deploy` target takes an existing `html` directory and updates
# the `docs` branch on `origin` via a temporary checkout.
deploy: $(OPENASSETIO_DOCS_REPO_DIR)
	# Deploy the local docs build to the target repo
	./deploy.sh $(OPENASSETIO_DOCS_REPO_DIR)
	# Remove the clone if we made it.
	$(DOCSREPO_CLEANUP) && rm -rf $(OPENASSETIO_DOCS_REPO_DIR) || true


$(OPENASSETIO_DOCS_REPO_DIR):
	# Get origin remote URL for use in pushing updated docs branch.
	$(eval remote_url=$(shell git remote get-url origin))
	# Create a clone of this repo with the docs branch checked out.
	git clone --no-tags --depth 1 --branch $(DOCSREPO_BRANCH) $(remote_url) $(OPENASSETIO_DOCS_REPO_DIR)

#
# Cleaning
#

clean: clean-html clean-tooling

clean-html:
	rm -rf ./html

clean-tooling:
	rm -rf node_modules
	rm -rf $(VENV)

#
# Docs TODO list
# As annotated by @needsref, outputs a unique file -> ref table.
#
todo:
	@grep -Eor "@needsref [a-zA-Z._-]+" ../ | sort | uniq | sed 's|..//||' | column -s ':' -t

##
## File targets
##

src/styles.css: src/styles.scss $(SASS)
	./node_modules/.bin/sass --no-source-map ./src/styles.scss ./src/styles.css

#
# Tooling
#

$(SASS):
	npm ci

# `pip install wheel` avoids "error: invalid command 'bdist_wheel'"
$(VENV): requirements.txt
	rm -rf $@
	python3 -m venv $@
	. ./$@/bin/activate && pip install wheel && pip install -r requirements.txt

