#!/bin/bash

python3 -m venv env
source env/bin/activate

pip install -r requirements.txt

pip uninstall -y breathe

mkdir lib
git clone https://github.com/JohnVidler/breathe.git lib/breathe
cd lib/breathe
python3 setup.py build
python3 setup.py install
cd ../../

make html

deactivate