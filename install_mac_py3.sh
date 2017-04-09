#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor
brew install gcc python3 fontconfig py3cairo libsvg-cairo
brew tap rdkit/rdkit
brew install rdkit --with-pycairo --with-python3

pip3 install PyQt5 numpy matplotlib cairocffi beautifulsoup4 Pillow

python3 setup-mac.py /Applications