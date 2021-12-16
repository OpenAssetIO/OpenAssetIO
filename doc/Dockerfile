FROM ubuntu:20.04

#
# A docker container for building OpenAssetIO documentation.
# Provides Doxygen, doxypy and graphviz, plus npm and python 3 venvs.
#

# Prevent 'configure tzdata' cropping up and blocking install
ENV DEBIAN_FRONTEND=noninteractive

# Build tooling for make and git to allow pip install from GitHub
RUN apt-get update && \
    apt-get install -y build-essential curl git python3.8-venv && \
#
# Node.js so we can use npm to install sass in the Makefile
#
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
#
# Graphviz and plantuml for in-code diagrams
#
    apt-get install -y graphviz plantuml && \
#
# N.B. `configure && make install` is broken as doxytag is missing in the
# distribution for this version for unknown reasons.
#
    mkdir /tmp/doxygen && cd /tmp/doxygen && \
    curl -L https://downloads.sourceforge.net/project/doxygen/rel-1.8.11/doxygen-1.8.11.linux.bin.tar.gz | tar -xz --strip-components=1 && \
    /usr/bin/install -m 755 ./bin/doxygen /usr/local/bin && \
    cd / && rm -rf /tmp/doxygen
