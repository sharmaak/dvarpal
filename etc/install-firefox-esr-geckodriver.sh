#!/bin/bash

# ------- BEGIN: Install Firefox ESR -------
# 1. First, install the required tool if missing:
sudo apt install -y software-properties-common
# 2. Add Mozilla Team’s PPA:
sudo add-apt-repository -y ppa:mozillateam/ppa
sudo apt update
# 3. Install Firefox ESR:
sudo apt install -y firefox-esr

# run command `firefox-esr --version` on command line to verify installation sanity.
# ------- END: Install Firefox ESR -------

# # ------- BEGIN: Install Gecko Driver -------
GECKO_VERSION="v0.36.0"
# Download and extract
wget https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz
tar -xvzf geckodriver-${GECKO_VERSION}-linux64.tar.gz

# Make it executable and move to system path
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/

# Clean up
rm geckodriver-${GECKO_VERSION}-linux64.tar.gz

# run command `geckodriver --version` on command line to verify installation sanity.
# # ------- END: Install Gecko Driver -------