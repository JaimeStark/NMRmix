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
J.L. Stark, H. Eghbalnia, W. Lee, W.M. Westler, and J.L. Markley (2016). Submitted.

USAGE
python NMRmix.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import sys
import os
import time
import inspect

from core import parameters
from gui import title_screen, library_import

def get_script_dir(follow_symlinks = True):
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def startGUI(params_object):
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    params_object.initWindowSize(QApplication.desktop().availableGeometry())
    resources_path = os.path.abspath(os.path.join(params_object.app_directory,'static'))
    # if ".app" in str(__file__):
    #     resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'static'))
    # else:
    #     resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__ ), '.', 'static'))
    splash_pix = QPixmap(os.path.join(resources_path, 'nmrfam_splash.png'))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    time.sleep(2)
    title_win = title_screen.Window(__VERSION__, params_object, resources_path)
    title_win.resize(475, 750)
    title_win.show()
    splash.finish(title_win)
    window = library_import.MainWindow(params_object)
    window.resize(int(params_object.size.width() * 0.85), int(params_object.size.height() * 0.7))
    title_win.accepted.connect(window.show)
    sys.exit(app.exec_())

nmrmix_directory = get_script_dir()
os.chdir(nmrmix_directory)
__VERSION__ = open('VERSION', 'rU').read()
params = parameters.Parameters(nmrmix_directory)
startGUI(params)