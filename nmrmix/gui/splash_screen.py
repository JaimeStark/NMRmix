#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
splash_screen.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
import sys

class Window(QDialog):

    def __init__(self, __version__, parent=None):
        QDialog.__init__(self, parent)
        self.version = __version__
        if ".app" in str(__file__):
            self.resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__ ), '../../..', 'static'))
        else:
            self.resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__ ), '..', 'static'))
        self.setWindowTitle("NMRmix")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()


    def createWidgets(self):
        self.winWidget = QWidget()
        self.winWidget.setStyleSheet("QWidget{background-color: white;}")
        self.appLogo = QLabel()
        self.appLogo.setPixmap(QPixmap(os.path.join(self.resources_path, "nmrmix_logo.png")))
        self.appLogo.setAlignment(Qt.AlignCenter)
        self.appName = QLabel("NMRmix")
        self.appName.setStyleSheet("QLabel {font-size: 24px; color: red; font-weight:bold;}")
        self.appName.setAlignment(Qt.AlignCenter)
        self.appSubName = QLabel("<b>A tool for generating optimal small molecule mixtures</b>")
        self.appSubName.setAlignment(Qt.AlignCenter)
        self.versionLabel = QLabel("Version: %s\n" % self.version)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.nmrfamLogo = QLabel()
        self.nmrfamLogo.setPixmap(QPixmap(os.path.join(self.resources_path, "nmrfam_logo.png")))
        self.nmrfamLogo.setAlignment(Qt.AlignCenter)
        text = "http://www.nmrfam.wisc.edu<br>" \
               "<br>" \
               "J.L. Stark, H. Eghbalnia, W.M. Westler, and J.L. Markley (2015).<br>" \
               "<i>In Preparation</i><br>" \
               "<br>" \
               "Questions or Problems?<br>" \
               "Contact: jstark@nmrfam.wisc.edu"
        self.textLabel = QLabel(text)
        self.textLabel.setAlignment(Qt.AlignCenter)
        self.prefButton = QPushButton("Set Default Preferences")
        self.okButton = QPushButton("Continue")
        self.okButton.setStyleSheet("QPushButton {color: red; font-weight: bold;}")

    def layoutWidgets(self):
        winLayout = QVBoxLayout(self)
        widgetLayout = QVBoxLayout(self.winWidget)
        widgetLayout.addWidget(self.appLogo)
        widgetLayout.addWidget(self.appName)
        widgetLayout.addWidget(self.appSubName)
        widgetLayout.addWidget(self.versionLabel)
        widgetLayout.addWidget(self.nmrfamLogo)
        widgetLayout.addWidget(self.textLabel)
        winLayout.addWidget(self.winWidget)
        # TODO: Create preferences update window
        # winLayout.addWidget(self.prefButton)
        winLayout.addWidget(self.okButton)

    def createConnections(self):
        self.okButton.clicked.connect(self.accept)

    def showDefaultPrefs(self):
        pass

    def closeEvent(self, event):
        sys.exit()

class DefaultPreferences(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

    def createWidgets(self):
        pass

    def layoutWidgets(self):
        pass

    def createConnections(self):
        pass

