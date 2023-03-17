#!/bin/bash

set -e

echo "!!! MOVING TO VIRTUAL ENV !!!"
python3 -m venv env
source env/bin/activate

python3 -m pip install --upgrade pip

#pip install --no-cache-dir docutils==0.18.1

echo "!!! BUILDING NEW BREATHE !!!"
if [ ! -d lib ]; then
    mkdir -p lib
    git clone https://github.com/JohnVidler/breathe.git lib/breathe
    cd lib/breathe
    python3 setup.py install
    cd ../../
fi

echo "!!! INSTALLING REQUIREMENTS !!!"
#pip install -r requirements.txt
pip install --no-cache-dir "Sphinx<5" exhale sphinx-book-theme sphinxcontrib-applehelp

echo "!!! BUILDING DOCUMENTATION !!!"
make html

echo "!!! EXITING VIRTUAL ENV !!!"
deactivate
