#!/bin/bash

set -e

echo "!!! MOVING TO VIRTUAL ENV !!!"
python3 -m venv _env
source _env/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

#echo "!!! BUILDING NEW BREATHE !!!"
#if [ ! -d lib ]; then
#    mkdir -p _lib
#    git clone https://github.com/JohnVidler/breathe.git _lib/breathe
#    cd _lib/breathe
#    python3 setup.py install
#    cd ../../
#fi

echo "!!! BUILDING DOCUMENTATION !!!"
make html

echo "!!! EXITING VIRTUAL ENV !!!"
deactivate
