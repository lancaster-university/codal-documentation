#!/bin/bash

echo "!!! MOVING TO VIRTUAL ENV !!!"
python3 -m venv env
source env/bin/activate

echo "!!! INSTALLING REQUIREMENTS !!!"
pip install -r requirements.txt

pip uninstall -y breathe

echo "!!! BUILDING NEW BREATHE !!!"
mkdir lib
git clone https://github.com/JohnVidler/breathe.git lib/breathe
cd lib/breathe
make clean
make
python3 setup.py build
python3 setup.py install
cd ../../

echo "!!! BUILDING DOCUMENTATION !!!"
make html

echo "!!! EXITING VIRTUAL ENV !!!"
deactivate