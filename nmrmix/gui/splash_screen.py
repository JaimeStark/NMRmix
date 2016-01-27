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

    def __init__(self, __version__, params_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
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
        self.appSubName = QLabel("<b>A tool for generating optimal small molecule mixtures for "
                                 "1D <sup>1</sup>H-NMR ligand affinity screens</b>")
        self.appSubName.setAlignment(Qt.AlignCenter)
        self.appSubName.setWordWrap(True)
        self.versionLabel = QLabel("Version: %s\n" % self.version)
        self.versionLabel.setAlignment(Qt.AlignCenter)
        self.nmrfamLogo = QLabel()
        self.nmrfamLogo.setPixmap(QPixmap(os.path.join(self.resources_path, "nmrfam_logo.png")))
        self.nmrfamLogo.setAlignment(Qt.AlignCenter)
        text = "http://www.nmrfam.wisc.edu<br>" \
               "<br>" \
               "J.L. Stark, W. Lee, H. Eghbalnia, W.M. Westler, and J.L. Markley (2015).<br>" \
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
        winLayout.addWidget(self.prefButton)
        winLayout.addWidget(self.okButton)

    def createConnections(self):
        self.okButton.clicked.connect(self.accept)
        self.prefButton.clicked.connect(self.showDefaultPrefs)

    def showDefaultPrefs(self):
        pref_win = DefaultPreferences(self.params)
        pref_win.exec_()

    def closeEvent(self, event):
        sys.exit()

class DefaultPreferences(QDialog):
    def __init__(self, params_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.paramTabs = QTabWidget()
        self.paramTabs.setMinimumWidth(500)
        self.paramTabs.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.paramTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')
        self.paramtab1 = QWidget()
        self.paramtab2 = QWidget()
        self.paramtab3 = QWidget()
        self.paramtab4 = QWidget()

        # System and Scoring Parameters
        self.wdirLabel = QLabel("<b>Working Directory</b>")
        self.wdirButton = QPushButton("Browse")
        self.wdirLine = QLineEdit(self.params.work_dir)
        self.wdirLine.setCursorPosition(0)
        self.wdirLine.setReadOnly(True)
        self.wdirTip = "Sets the directory where any results files will be placed.\n" \
                       "Also determines the initial directory to look for the library CSV file."
        self.wdirLine.setToolTip(self.wdirTip)
        self.wdirLabel.setToolTip(self.wdirTip)
        self.wdirButton.setToolTip(self.wdirTip)
        self.pdirLabel = QLabel("<b>Local Peak List Directory</b>")
        self.pdirButton = QPushButton("Browse")
        self.pdirLine = QLineEdit(self.params.peaklist_dir)
        self.pdirLine.setCursorPosition(0)
        self.pdirLine.setReadOnly(True)
        self.pdirTip = "Sets the directory where local peak list files are stored."
        self.pdirLine.setToolTip(self.pdirTip)
        self.pdirLabel.setToolTip(self.pdirTip)
        self.pdirButton.setToolTip(self.pdirTip)

        self.scoreHLine1 = QFrame()
        self.scoreHLine1.setFrameShape(QFrame.HLine)
        self.rangeLabel = QLabel("Overlap Range")
        self.rangeLabel.setAlignment(Qt.AlignCenter)
        self.rangeSpinBox = QDoubleSpinBoxScore()
        self.rangeSpinBox.setKeyboardTracking(False)
        self.rangeSpinBox.setAlignment(Qt.AlignCenter)
        self.rangeSpinBox.setRange(0.001, 1.000)
        self.rangeSpinBox.setSingleStep(0.005)
        self.rangeSpinBox.setDecimals(3)
        self.rangeSpinBox.setValue(self.params.peak_range)
        self.scorescaleLabel = QLabel("Score Scaling")
        self.scorescaleLabel.setAlignment(Qt.AlignCenter)
        self.scorescaleSpinBox = QSpinBoxScore()
        self.scorescaleSpinBox.setKeyboardTracking(False)
        self.scorescaleSpinBox.setAlignment(Qt.AlignCenter)
        self.scorescaleSpinBox.setRange(1, 10000000)
        self.scorescaleSpinBox.setSingleStep(1000)
        self.scorescaleSpinBox.setValue(self.params.score_scale)
        self.useintensityLabel = QLabel("Use Intensity Scoring")
        self.useintensityLabel.setAlignment(Qt.AlignCenter)
        self.useintensityCheckBox = QCheckBox()
        if self.params.use_intensity:
            self.useintensityCheckBox.setCheckState(Qt.Checked)
        else:
            self.useintensityCheckBox.setCheckState(Qt.Unchecked)
        self.useautosaveLabel = QLabel("Autosave Results")
        self.useautosaveLabel.setAlignment(Qt.AlignCenter)
        self.useautosaveLabel.setToolTip("Turns on/off the autosaving of results after optimizing mixtures.")
        self.useautosaveCheckBox = QCheckBox()
        self.useautosaveCheckBox.setToolTip("Turns on/off the autosaving of results after optimizing mixtures.")
        if self.params.autosave:
            self.useautosaveCheckBox.setCheckState(Qt.Checked)
        else:
            self.useautosaveCheckBox.setCheckState(Qt.Unchecked)


        # Optimization Parameters
        self.startnumLabel = QLabel("Starting Mixture Number")
        self.startnumLabel.setAlignment(Qt.AlignCenter)
        self.startnumSpinBox = QSpinBox()
        self.startnumSpinBox.setKeyboardTracking(False)
        self.startnumSpinBox.setAlignment(Qt.AlignCenter)
        self.startnumSpinBox.setRange(1, 10000000)
        self.startnumSpinBox.setValue(self.params.start_num)
        self.mixsizeLabel = QLabel("Max Mixture Size")
        self.mixsizeLabel.setAlignment(Qt.AlignCenter)
        self.mixsizeSpinBox = QSpinBox()
        self.mixsizeSpinBox.setKeyboardTracking(False)
        self.mixsizeSpinBox.setAlignment(Qt.AlignCenter)
        self.mixsizeSpinBox.setRange(1, 20)
        self.mixsizeSpinBox.setValue(self.params.mix_size)
        self.extramixLabel = QLabel("Extra Mixtures")
        self.extramixLabel.setAlignment(Qt.AlignCenter)
        self.extramixSpinBox = QSpinBox()
        self.extramixSpinBox.setKeyboardTracking(False)
        self.extramixSpinBox.setAlignment(Qt.AlignCenter)
        self.extramixSpinBox.setRange(0, 1000)
        self.extramixSpinBox.setValue(self.params.extra_mixtures)
        self.coolingLabel = QLabel("Cooling Rate")
        self.coolingLabel.setAlignment(Qt.AlignCenter)
        self.coolingComboBox = QComboBox()
        self.coolingComboBox.setEditable(True)
        self.coolingComboBox.lineEdit().setReadOnly(True)
        self.coolingComboBox.lineEdit().setAlignment(Qt.AlignCenter)
        self.coolingComboBox.addItems(['Exponential', 'Linear'])
        if self.params.cooling == "exponential":
            self.coolingComboBox.setCurrentIndex(0)
        elif self.params.cooling == "linear":
            self.coolingComboBox.setCurrentIndex(1)
        self.starttempLabel = QLabel("Start Temp")
        self.starttempLabel.setAlignment(Qt.AlignCenter)
        self.starttempSpinBox = QSpinBox()
        self.starttempSpinBox.setKeyboardTracking(False)
        self.starttempSpinBox.setAlignment(Qt.AlignCenter)
        self.starttempSpinBox.setRange(self.params.final_temp+1, 500000)
        self.starttempSpinBox.setSingleStep(1)
        # self.starttempSpinBox.setDecimals(3)
        self.starttempSpinBox.setValue(self.params.start_temp)
        self.finaltempLabel = QLabel("Final Temp")
        self.finaltempLabel.setAlignment(Qt.AlignCenter)
        self.finaltempSpinbox = QSpinBox()
        self.finaltempSpinbox.setKeyboardTracking(False)
        self.finaltempSpinbox.setAlignment(Qt.AlignCenter)
        self.finaltempSpinbox.setRange(1, self.params.start_temp-1)
        self.finaltempSpinbox.setSingleStep(1)
        # self.finaltempSpinbox.setDecimals(3)
        self.finaltempSpinbox.setValue(self.params.final_temp)
        self.maxstepsLabel = QLabel("Max Steps")
        self.maxstepsLabel.setAlignment(Qt.AlignCenter)
        self.maxstepsSpinBox = QSpinBox()
        self.maxstepsSpinBox.setKeyboardTracking(False)
        self.maxstepsSpinBox.setAlignment(Qt.AlignCenter)
        self.maxstepsSpinBox.setRange(1, 10000000)
        self.maxstepsSpinBox.setValue(self.params.max_steps)
        self.maxstepsSpinBox.setSingleStep(self.params.max_steps)
        self.mixrateLabel = QLabel("Mix Rate")
        self.mixrateLabel.setAlignment(Qt.AlignCenter)
        self.mixrateSpinBox = QSpinBox()
        self.mixrateSpinBox.setKeyboardTracking(False)
        self.mixrateSpinBox.setAlignment(Qt.AlignCenter)
        self.mixrateSpinBox.setRange(1, 100)
        self.mixrateSpinBox.setValue(self.params.mix_rate)
        self.iterationsLabel = QLabel("Iterations")
        self.iterationsLabel.setAlignment(Qt.AlignCenter)
        self.iterationsSpinBox = QSpinBox()
        self.iterationsSpinBox.setKeyboardTracking(False)
        self.iterationsSpinBox.setAlignment(Qt.AlignCenter)
        self.iterationsSpinBox.setRange(1, 100)
        self.iterationsSpinBox.setValue(self.params.iterations)
        self.usesolventLabel = QLabel("Restrict by Solvent")
        self.usesolventLabel.setAlignment(Qt.AlignCenter)
        self.usesolventCheckBox = QCheckBox()
        if self.params.use_solvent:
            self.usesolventCheckBox.setCheckState(Qt.Checked)
        else:
            self.usesolventCheckBox.setCheckState(Qt.Unchecked)
        self.randomizeLabel = QLabel("Randomize Initial Mixtures")
        self.randomizeLabel.setAlignment(Qt.AlignCenter)
        self.randomizeCheckBox = QCheckBox()
        if self.params.randomize_initial:
            self.randomizeCheckBox.setCheckState(Qt.Checked)
        else:
            self.randomizeCheckBox.setCheckState(Qt.Unchecked)

        # Refinement Parameters
        self.userefineLabel = QLabel("Use Refinement")
        self.userefineLabel.setAlignment(Qt.AlignCenter)
        self.userefineCheckBox = QCheckBox()
        if self.params.use_refine:
            self.userefineCheckBox.setChecked(True)
        else:
            self.userefineCheckBox.setChecked(False)
        self.refinecoolingLabel = QLabel("Cooling Rate")
        self.refinecoolingLabel.setAlignment(Qt.AlignCenter)
        self.refinecoolingComboBox = QComboBox()
        self.refinecoolingComboBox.setEditable(True)
        self.refinecoolingComboBox.lineEdit().setReadOnly(True)
        self.refinecoolingComboBox.lineEdit().setAlignment(Qt.AlignCenter)
        self.refinecoolingComboBox.addItems(['Exponential', 'Linear'])
        if self.params.refine_cooling == "exponential":
            self.refinecoolingComboBox.setCurrentIndex(0)
        elif self.params.refine_cooling == "linear":
            self.refinecoolingComboBox.setCurrentIndex(1)
        self.refinestarttempLabel = QLabel("Start Temp")
        self.refinestarttempLabel.setAlignment(Qt.AlignCenter)
        self.refinestarttempSpinBox = QSpinBox()
        self.refinestarttempSpinBox.setKeyboardTracking(False)
        self.refinestarttempSpinBox.setAlignment(Qt.AlignCenter)
        self.refinestarttempSpinBox.setRange(self.params.refine_final_temp+1, 500000)
        self.refinestarttempSpinBox.setSingleStep(1.0)
        self.refinestarttempSpinBox.setValue(self.params.refine_start_temp)
        self.refinefinaltempLabel = QLabel("Final Temp")
        self.refinefinaltempLabel.setAlignment(Qt.AlignCenter)
        self.refinefinaltempSpinbox = QDoubleSpinBox()
        self.refinefinaltempSpinbox.setKeyboardTracking(False)
        self.refinefinaltempSpinbox.setAlignment(Qt.AlignCenter)
        self.refinefinaltempSpinbox.setRange(1, self.params.refine_start_temp-1)
        self.refinefinaltempSpinbox.setSingleStep(1)
        self.refinefinaltempSpinbox.setValue(self.params.refine_final_temp)
        self.refinemaxstepsLabel = QLabel("Max Steps")
        self.refinemaxstepsLabel.setAlignment(Qt.AlignCenter)
        self.refinemaxstepsSpinBox = QSpinBox()
        self.refinemaxstepsSpinBox.setKeyboardTracking(False)
        self.refinemaxstepsSpinBox.setAlignment(Qt.AlignCenter)
        self.refinemaxstepsSpinBox.setRange(1, 10000000)
        self.refinemaxstepsSpinBox.setValue(self.params.refine_max_steps)
        self.refinemaxstepsSpinBox.setSingleStep(self.params.refine_max_steps)
        self.refinemixrateLabel = QLabel("Mix Rate")
        self.refinemixrateLabel.setAlignment(Qt.AlignCenter)
        self.refinemixrateSpinBox = QSpinBox()
        self.refinemixrateSpinBox.setKeyboardTracking(False)
        self.refinemixrateSpinBox.setAlignment(Qt.AlignCenter)
        self.refinemixrateSpinBox.setRange(1, 100)
        self.refinemixrateSpinBox.setValue(self.params.refine_mix_rate)

        # Graphs and Stats


        self.closeButton = QPushButton("Close")
        self.closeButton.setToolTip("Closes the window without saving any changes")
        self.closeButton.setStyleSheet("QPushButton {color: red;}")
        self.resetButton = QPushButton("Reset")
        self.resetButton.setToolTip("Resets all preferences to factory defaults")
        self.resetButton.setStyleSheet("QPushButton {color: orange;}")
        self.restoreButton = QPushButton("Restore")
        self.restoreButton.setToolTip("Restores all preferences to previously save values")
        self.restoreButton.setStyleSheet("QPushButton {color: blue;}")
        self.saveButton = QPushButton("Save")
        self.saveButton.setToolTip("Saves all current preferences as default values")
        self.saveButton.setStyleSheet("QPushButton {color: green;}")

    def layoutWidgets(self):
        winLayout = QVBoxLayout(self)

        scoreLayout = QGridLayout()
        wdirLayout = QGridLayout()
        wdirLayout.addWidget(self.wdirLabel, 0, 0)
        wdirLayout.addWidget(self.wdirLine, 1, 0)
        wdirLayout.addWidget(self.wdirButton, 1, 1)
        pdirLayout = QGridLayout()
        pdirLayout.addWidget(self.pdirLabel, 0, 0)
        pdirLayout.addWidget(self.pdirLine, 1, 0)
        pdirLayout.addWidget(self.pdirButton, 1, 1)
        scoreLayout.addLayout(wdirLayout, 0, 0, 1, 2)
        scoreLayout.addLayout(pdirLayout, 1, 0, 1, 2)
        scoreLayout.addItem(QSpacerItem(0, 8), 2, 0)
        scoreLayout.addWidget(self.scoreHLine1, 3, 0, 1, 2)
        scoreLayout.addItem(QSpacerItem(0, 8), 4, 0)
        scoreLayout.addWidget(self.rangeLabel, 5, 0)
        scoreLayout.addWidget(self.rangeSpinBox, 5, 1)
        scoreLayout.addWidget(self.scorescaleLabel, 6, 0)
        scoreLayout.addWidget(self.scorescaleSpinBox, 6, 1)
        scoreLayout.addWidget(self.useintensityLabel, 7, 0)
        checkbox1Layout = QHBoxLayout()
        checkbox1Layout.addWidget(self.useintensityCheckBox)
        scoreLayout.addLayout(checkbox1Layout, 7, 1, Qt.AlignCenter)
        scoreLayout.addItem(QSpacerItem(0, 8), 8, 0)
        scoreLayout.addWidget(self.useautosaveLabel, 11, 0)
        checkbox2Layout = QHBoxLayout()
        checkbox2Layout.addWidget(self.useautosaveCheckBox)
        scoreLayout.addLayout(checkbox2Layout, 11, 1, Qt.AlignCenter)
        scoreLayout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 12, 0)
        self.paramtab1.setLayout(scoreLayout)
        self.paramTabs.addTab(self.paramtab1, 'Directories/Scoring')

        mixLayout = QGridLayout()
        mixLayout.addWidget(self.startnumLabel, 2, 0)
        mixLayout.addWidget(self.startnumSpinBox, 2, 1)
        mixLayout.addWidget(self.mixsizeLabel, 3, 0)
        mixLayout.addWidget(self.mixsizeSpinBox, 3, 1)
        mixLayout.addWidget(self.extramixLabel, 4, 0)
        mixLayout.addWidget(self.extramixSpinBox, 4, 1)
        mixLayout.addWidget(self.coolingLabel, 5, 0)
        mixLayout.addWidget(self.coolingComboBox, 5, 1)
        mixLayout.addWidget(self.starttempLabel, 6, 0)
        mixLayout.addWidget(self.starttempSpinBox, 6, 1)
        mixLayout.addWidget(self.finaltempLabel, 7, 0)
        mixLayout.addWidget(self.finaltempSpinbox, 7, 1)
        mixLayout.addWidget(self.maxstepsLabel, 8, 0)
        mixLayout.addWidget(self.maxstepsSpinBox, 8, 1)
        mixLayout.addWidget(self.mixrateLabel, 9, 0)
        mixLayout.addWidget(self.mixrateSpinBox, 9, 1)
        mixLayout.addWidget(self.iterationsLabel, 10, 0)
        mixLayout.addWidget(self.iterationsSpinBox, 10, 1)
        mixLayout.addWidget(self.usesolventLabel, 11, 0)
        checkbox3Layout = QHBoxLayout()
        checkbox3Layout.addWidget(self.usesolventCheckBox)
        mixLayout.addLayout(checkbox3Layout, 11, 1, Qt.AlignCenter)
        mixLayout.addWidget(self.randomizeLabel, 12, 0)
        checkbox4Layout = QHBoxLayout()
        checkbox4Layout.addWidget(self.randomizeCheckBox)
        mixLayout.addLayout(checkbox4Layout, 12, 1, Qt.AlignCenter)
        mixLayout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 13, 0)
        self.paramtab2.setLayout(mixLayout)
        self.paramTabs.addTab(self.paramtab2, "Optimizing")

        refineLayout = QGridLayout()
        refineLayout.addWidget(self.userefineLabel, 0, 0)
        checkbox5Layout = QHBoxLayout()
        checkbox5Layout.addWidget(self.userefineCheckBox)
        refineLayout.addLayout(checkbox5Layout, 0, 1, Qt.AlignCenter)
        refineLayout.addWidget(self.refinecoolingLabel, 2, 0)
        refineLayout.addWidget(self.refinecoolingComboBox, 2, 1)
        refineLayout.addWidget(self.refinestarttempLabel, 3, 0)
        refineLayout.addWidget(self.refinestarttempSpinBox, 3, 1)
        refineLayout.addWidget(self.refinefinaltempLabel, 4, 0)
        refineLayout.addWidget(self.refinefinaltempSpinbox, 4, 1)
        refineLayout.addWidget(self.refinemaxstepsLabel, 5, 0)
        refineLayout.addWidget(self.refinemaxstepsSpinBox, 5, 1)
        refineLayout.addWidget(self.refinemixrateLabel, 6, 0)
        refineLayout.addWidget(self.refinemixrateSpinBox, 6, 1)
        refineLayout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 7, 0)
        self.paramtab3.setLayout(refineLayout)
        self.paramTabs.addTab(self.paramtab3, "Refining")

        statsLayout = QGridLayout()
        self.paramtab4.setLayout(statsLayout)
        self.paramTabs.addTab(self.paramtab4, "Graphs/Statistics")

        winbuttonLayout = QHBoxLayout()
        winbuttonLayout.addWidget(self.closeButton)
        winbuttonLayout.addWidget(self.resetButton)
        winbuttonLayout.addWidget(self.restoreButton)
        winbuttonLayout.addWidget(self.saveButton)

        winLayout.addWidget(self.paramTabs)
        winLayout.addLayout(winbuttonLayout)


    def createConnections(self):
        self.wdirButton.clicked.connect(self.setWorkingDir)
        self.pdirButton.clicked.connect(self.setPeakListDir)
        self.rangeSpinBox.valueChanged.connect(self.updateParams)
        self.scorescaleSpinBox.valueChanged.connect(self.updateParams)
        self.useintensityCheckBox.clicked.connect(self.updateParams)
        self.useautosaveCheckBox.clicked.connect(self.updateParams)

        self.startnumSpinBox.valueChanged.connect(self.updateParams)
        self.mixsizeSpinBox.valueChanged.connect(self.updateParams)
        self.extramixSpinBox.valueChanged.connect(self.updateParams)
        self.coolingComboBox.currentTextChanged.connect(self.updateParams)
        self.starttempSpinBox.valueChanged.connect(self.updateParams)
        self.finaltempSpinbox.valueChanged.connect(self.updateParams)
        self.maxstepsSpinBox.valueChanged.connect(self.updateParams)
        self.mixrateSpinBox.valueChanged.connect(self.updateParams)
        self.usesolventCheckBox.clicked.connect(self.updateParams)
        self.iterationsSpinBox.valueChanged.connect(self.updateParams)
        self.randomizeCheckBox.clicked.connect(self.updateParams)

        self.userefineCheckBox.clicked.connect(self.updateParams)
        self.refinecoolingComboBox.currentTextChanged.connect(self.updateParams)
        self.refinestarttempSpinBox.valueChanged.connect(self.updateParams)
        self.refinefinaltempSpinbox.valueChanged.connect(self.updateParams)
        self.refinemaxstepsSpinBox.valueChanged.connect(self.updateParams)
        self.refinemixrateSpinBox.valueChanged.connect(self.updateParams)

        self.closeButton.clicked.connect(self.closeWindow)
        self.resetButton.clicked.connect(self.resetParams)
        self.restoreButton.clicked.connect(self.restoreParams)
        self.saveButton.clicked.connect(self.saveParams)


    def updateParams(self):
        ## System and Scoring
        self.params.setPeakRange(self.rangeSpinBox.value())
        self.params.setScoreScale(self.scorescaleSpinBox.value())
        if self.useintensityCheckBox.isChecked():
            self.params.useIntensity()
        else:
            self.params.noIntensity()
        if self.useautosaveCheckBox.isChecked():
            self.params.useAutosave()
        else:
            self.params.noAutosave()

        ## Optimization
        self.params.setStartingMixtureNum(self.startnumSpinBox.value())
        self.params.setMixSize(self.mixsizeSpinBox.value())
        self.params.setExtraMixtures(self.extramixSpinBox.value())
        if self.coolingComboBox.currentText() == 'Linear':
            self.params.useLinearCooling()
        elif self.coolingComboBox.currentText() == 'Exponential':
            self.params.useExponentialCooling()
        self.params.setStartingTemp(self.starttempSpinBox.value())
        self.params.setFinalTemp(self.finaltempSpinbox.value())
        self.params.setMaxSteps(self.maxstepsSpinBox.value())
        self.params.setMixRate(self.mixrateSpinBox.value())
        if self.usesolventCheckBox.isChecked():
            self.params.useSolvent()
        else:
            self.params.noSolvent()
        self.params.setNumIterations(self.iterationsSpinBox.value())
        if self.randomizeCheckBox.isChecked():
            self.params.randomize_initial = True
        else:
            self.params.randomize_initial = False

        ## Refine
        if self.userefineCheckBox.isChecked():
            self.params.use_refine = True
        else:
            self.params.use_refine = False
        if self.refinecoolingComboBox.currentText() == 'Linear':
            self.params.useRefineLinearCooling()
        elif self.refinecoolingComboBox.currentText() == 'Exponential':
            self.params.useRefineExponentialCooling()
        self.params.setRefineStartingTemp(self.refinestarttempSpinBox.value())
        self.params.setRefineFinalTemp(self.refinefinaltempSpinbox.value())
        self.params.setRefineMaxSteps(self.refinemaxstepsSpinBox.value())
        self.params.setRefineMixRate(self.refinemixrateSpinBox.value())


        ## Graphs and Stats


    def updateValues(self):
        self.wdirLine.setText(self.params.work_dir)
        self.pdirLine.setText(self.params.peaklist_dir)
        self.rangeSpinBox.setValue(self.params.peak_range)
        self.scorescaleSpinBox.setValue(self.params.score_scale)
        if self.params.use_intensity:
            self.useintensityCheckBox.setCheckState(Qt.Checked)
        else:
            self.useintensityCheckBox.setCheckState(Qt.Unchecked)

        self.startnumSpinBox.setValue(self.params.start_num)
        self.mixsizeSpinBox.setValue(self.params.mix_size)
        self.extramixSpinBox.setValue(self.params.extra_mixtures)
        if self.params.cooling == "exponential":
            self.coolingComboBox.setCurrentIndex(0)
        elif self.params.cooling == "linear":
            self.coolingComboBox.setCurrentIndex(1)
        self.starttempSpinBox.setValue(self.params.start_temp)
        self.finaltempSpinbox.setValue(self.params.final_temp)
        self.maxstepsSpinBox.setValue(self.params.max_steps)
        self.mixrateSpinBox.setValue(self.params.mix_rate)
        self.iterationsSpinBox.setValue(self.params.iterations)
        if self.params.use_solvent:
            self.usesolventCheckBox.setCheckState(Qt.Checked)
            if self.params.solvent_specific_ignored_region:
                self.usesolventCheckBox.setDisabled(True)
        else:
            self.usesolventCheckBox.setCheckState(Qt.Unchecked)
        if self.params.randomize_initial:
            self.randomizeCheckBox.setCheckState(Qt.Checked)
        else:
            self.randomizeCheckBox.setCheckState(Qt.Unchecked)

        if self.params.use_refine:
            self.userefineCheckBox.setChecked(True)
        else:
            self.userefineCheckBox.setChecked(False)
        if self.params.refine_cooling == "exponential":
            self.refinecoolingComboBox.setCurrentIndex(0)
        elif self.params.refine_cooling == "linear":
            self.refinecoolingComboBox.setCurrentIndex(1)
        self.refinestarttempSpinBox.setValue(self.params.refine_start_temp)
        self.refinefinaltempSpinbox.setValue(self.params.refine_final_temp)
        self.refinemaxstepsSpinBox.setValue(self.params.refine_max_steps)
        self.refinemixrateSpinBox.setValue(self.params.refine_mix_rate)


    def setWorkingDir(self):
        """Sets the directory where results files and logs will be placed."""
        dir = self.params.work_dir
        dirObj = QFileDialog.getExistingDirectory(self, "Set Working Directory", directory=dir)
        if dirObj:
            self.params.setWorkingDirectory(dirObj)
            self.wdirLine.setText(self.params.work_dir)

    def setPeakListDir(self):
        """Sets the directory where the peak list files are stored."""
        dir = self.params.peaklist_dir
        dirObj = QFileDialog.getExistingDirectory(self, "Set Local Peaklist Directory", directory=dir)
        if dirObj:
            self.params.setPeakListDirectory(dirObj)
            self.pdirLine.setText(self.params.peaklist_dir)


    def closeWindow(self):
        if self.params.exists:
            self.params.readPreferences(self.params.pref_file)
        else:
            self.params.setDefaultParams()
        self.reject()

    def resetParams(self):
        self.params.setDefaultParams()
        self.updateValues()

    def restoreParams(self):
        if self.params.exists:
            self.params.readPreferences(self.params.pref_file)
        else:
            self.params.setDefaultParams()
        self.updateValues()

    def saveParams(self):
        try:
            self.params.writePreferences(self.params.pref_file)
        except:
            QMessageBox.critical(self, 'Preferences NOT Saved!',
                                 "Saving preferences to file was unsuccessful.\n"
                                 "Please check folder permissions.\n"
                                 "Saved preferences will be lost when NMRmix is quit.")
        self.accept()


class QDoubleSpinBoxScore(QDoubleSpinBox):
    def __init__(self, parent=None):
        QDoubleSpinBox.__init__(self, parent)

    def timerEvent(self, event):
        return

class QSpinBoxScore(QSpinBox):
    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent)

    def timerEvent(self, event):
        return