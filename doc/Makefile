default: container-build

##
# This Makefile builds the OAIO documentation bundle.
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


##
## PHONY TARGETS
##

.PHONY: clean clean-html clean-tooling clean-docker container-build docker-image html tooling

#
# Container build - Runs this Makefile via docker
#

container-build: docker-image
	docker run --rm -v `pwd`/../:/src oaio-doc-build bash -c 'make -C /src/doc html'

docker-image: Dockerfile
	docker build . -t oaio-doc-build

clean-docker:
	docker image rm oaio-doc-build --force

#
# Local build - Invokes Doxygen locally
#

# Tooling paths
VENV = ./venv
SASS = ./node_modules/.bin/sass

# Force clean-html as we don't declare all the sources
html: clean-html src/styles.css tooling
	. $(VENV)/bin/activate && doxygen ./Doxyfile

tooling: $(SASS) $(VENV)

clean: clean-html clean-tooling

clean-html:
	rm -rf ./html

clean-tooling:
	rm -rf node_modules
	rm -rf $(VENV)


##
## File targets
##

src/styles.css: src/styles.scss $(SASS)
	./node_modules/.bin/sass --no-source-map ./src/styles.scss ./src/styles.css

#
# Tooling
#

$(SASS):
	npm install .

# `pip install wheel` avoids "error: invalid command 'bdist_wheel'"
$(VENV): requirements.txt
	rm -rf $@
	python3 -m venv $@
	. ./$@/bin/activate && pip install wheel && pip install -r requirements.txt

