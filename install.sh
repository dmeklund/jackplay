#!/bin/bash -x

# virtualenv -p python3 ~/venv_jack
# . ~/venv_jack/bin/activate
# pip install --upgrade pip
# pip install wheel
# pip-compile

pip wheel -w ~/wheelhouse/ --use-wheel --find-links ~/wheelhouse/ --requirement requirements.txt
pip install --find-links ~/wheelhouse/ --requirement requirements.txt
