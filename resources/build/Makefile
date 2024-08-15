# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 The Foundry Visionmongers Ltd

default: docker-image

##
# This Makefile builds and publishes the OpenAssetIO Docker image.
#
# NB. This file is sensitive to the current working directory, and
# should not be used with `make -f`.
##

# This container version mimicks the VFX reference platform versioning.
CONTAINER_VERSION=2024.5
CONTAINER_NAME=openassetio-build

##
## Container settings
##

# The following variables are considered when using Docker
# to build the documentation:
#
#  GITHUB_ORG: The organisation to publish to. If unspecified, then
#              `openassetio` will be used. Note: org names must be
#              lowercase.
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

.PHONY: clean-docker docker-image publish-docker

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


