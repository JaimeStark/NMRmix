#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor
brew install gcc python fontconfig py2cairo libsvg-cairo gtk pyqt5
brew tap rdkit/rdkit
brew install rdkit --with-pycairo

pip install numpy matplotlib cairocffi beautifulsoup4 Pillow unicodecsv

python setup-mac.py /Applications