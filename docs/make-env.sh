#!/bin/bash

set -e

echo "!!! MOVING TO VIRTUAL ENV !!!"
python3 -m venv env
source env/bin/activate

python3 -m pip install --upgrade pip

echo "!!! BUILDING NEW BREATHE !!!"
mkdir lib
git clone https://github.com/JohnVidler/breathe.git lib/breathe
cd lib/breathe
python3 setup.py install
cd ../../

echo "!!! INSTALLING REQUIREMENTS !!!"
#pip install -r requirements.txt
pip install docutils==0.18.1
pip install Sphinx exhale sphinx-book-theme

echo "!!! BUILDING DOCUMENTATION !!!"
make html

echo "!!! EXITING VIRTUAL ENV !!!"
deactivate
