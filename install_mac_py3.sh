#!/usr/bin/env bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor
brew install gcc python3 fontconfig py3cairo libsvg-cairo
brew install sip --with-python3
brew install pyqt5 --with-python3
brew tap rdkit/rdkit
brew install rdkit --with-pycairo --with-python3

pip3 install numpy matplotlib cairocffi beautifulsoup4 Pillow

python3 setup-mac.py /Applications