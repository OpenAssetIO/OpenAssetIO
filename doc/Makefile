default: html

##
# This Makefile builds the OAIO documentation bundle.
#
# Builds require `git`, `python3-venv`, `doxygen` and `graphviz` to be
# installed. See README.md for more information.
#
# The `tooling` target takes care of installing `sass` and `doxypy` if
# required.  They will be installed into the current working directory.
# The `clean-tooling` target (invoked by `clean`) will remove these if
# required.
#
# NB. This file is sensitive to the current working directory, and
# should not be used with `make -f`.
##


##
## PHONY TARGETS
##

.PHONY: clean clean-html clean-tooling html tooling

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

