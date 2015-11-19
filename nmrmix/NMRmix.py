#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NMRmix.py

Created by Jaime Stark on 2/12/14
Copyright (C) 2014  Jaime Stark
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to
redistribute it under certain conditions.
See 'LICENSE.txt' for details.

DESCRIPTION
NMRmix is a tool for generating optimal mixtures
for 1D NMR protein-ligand screening efforts,
such as line-broadening screens and STD experiments.
This tool utilizes the peak lists for each compound
in the library and generates mixtures that minimize
peak overlap.

REFERENCE
J.L. Stark, H. Eghbalnia, W.M. Westler, and J.L. Markley (2015). In preparation.

USAGE
python NMRmix.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtWidgets import QApplication

import sys
import os
from core import parameters
from gui import splash_screen, library_import

__VERSION__ = "0.9 (Build 2015.11.18)"

def startGUI(params_object):
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    params_object.initWindowSize(QApplication.desktop().availableGeometry())
    window = library_import.MainWindow(params_object)
    window.resize(int(params_object.size.width() * 0.85), int(params_object.size.height() * 0.7))
    splash_win = splash_screen.Window(__VERSION__)
    splash_win.accepted.connect(window.show)
    splash_win.show()
    sys.exit(app.exec_())


pref_dir = os.path.expanduser("~/.nmrmix")
pref_file = os.path.expanduser("~/.nmrmix/preferences.txt")
if not os.path.exists(pref_dir):
    os.mkdir(pref_dir)
if not os.path.isfile(pref_file):
    params = parameters.Parameters(False, pref_file)
else:
    params = parameters.Parameters(True, pref_file)
startGUI(params)