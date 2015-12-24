#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mixtures_view.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import os
import time
import random
import datetime
import codecs
if sys.version > '3':
    import csv
else:
    import unicodecsv as csv
import copy

from nmrmix.core import mixtures
from nmrmix.gui import mixture_spectra, compound_info, optimize, move_compounds, compounds_ranked
# from gui import compound_info
# from gui import optimize
# from gui import move_compounds
# from gui import compounds_ranked

class Window(QDialog):
    def __init__(self, params_object, library_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.setWindowTitle("NMRmix: Mixture Creation")
        self.mixtures = mixtures.Mixtures(self.params, self.library)
        self.need_reset = False
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.mixtures.generateSolventLists()
        self.mixtures.generateInitialMixtures()
        self.initTable()
        self.initScoreParams()
        self.initMixParams()
        self.initRefinement()
        self.initStats()
        self.updateMixing()
        self.updateScoring()
        self.updateStats()
        self.setTable()
        self.need_reset = False
        # Window Buttons
        self.backButton = QPushButton("Return To Library Info")
        self.backButton.setStyleSheet("QPushButton{font-size:20px; color: blue; font-weight: bold;}")
        self.backButton.setFixedHeight(50)
        self.backButton.setFixedWidth(350)
        self.saveButton = QPushButton("Save Results")
        self.saveButton.setStyleSheet("QPushButton{font-size:20px; color: green; font-weight: bold;}")
        self.saveButton.setFixedHeight(50)
        self.saveButton.setFixedWidth(350)
        self.quitButton = QPushButton("Quit NMRmix")
        self.quitButton.setStyleSheet("QPushButton{font-size:20px; color: red; font-weight: bold;}")
        self.quitButton.setFixedHeight(50)
        self.quitButton.setFixedWidth(350)

    def initTable(self):
        self.mixtable = QTableWidget(0, 25, self)
        self.mixtable.setSelectionMode(QAbstractItemView.NoSelection)
        self.mixtable.setSortingEnabled(True)

        self.mixtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mixtable.setFocusPolicy(Qt.NoFocus)
        self.mixtable.horizontalHeader().setDefaultSectionSize(105)
        self.mixtable.sortByColumn(2, Qt.AscendingOrder)
        self.mixtable.verticalHeader().setDefaultSectionSize(40)
        self.mixtable.setColumnWidth(0, 60)
        self.mixtable.setColumnWidth(1, 70)
        self.mixtable.setColumnWidth(2, 80)
        self.mixtable.setColumnWidth(3, 90)
        self.mixtable.setColumnWidth(4, 75)
        self.mixtable.horizontalHeader().setStretchLastSection(True)
        self.mixtable_header = ['Lock', 'Spectra', 'Mixture\nNumber', 'Total\nScore', 'Solvent',
                                'Compound 1', 'Compound 2', 'Compound 3', 'Compound 4', 'Compound 5',
                                'Compound 6', 'Compound 7', 'Compound 8', 'Compound 9', 'Compound 10',
                                'Compound 11', 'Compound 12', 'Compound 13', 'Compound 14', 'Compound 15',
                                'Compound 16', 'Compound 17', 'Compound 18', 'Compound 19', 'Compound 20',]
        self.mixtable.setHorizontalHeaderLabels(self.mixtable_header)
        self.mixtable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.mixtable.verticalHeader().hide()

        self.paramTabs = QTabWidget()
        self.paramTabs.setMinimumWidth(325)
        self.paramTabs.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.paramTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')
        self.paramtab1 = QWidget()
        self.paramtab2 = QWidget()
        self.paramtab3 = QWidget()
        self.paramtab4 = QWidget()

        self.lockCheckBox = QCheckBox()
        self.lockLabel = QLabel("Lock/Unlock All Mixtures")
        self.lockLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lockLabel.setStyleSheet("QLabel {font-size: 10px; font-weight: bold;}")
        instructions = "Left-click on compounds for information / Right-click on compounds to manually move"
        self.tableInstructions = QLabel(instructions)
        self.tableInstructions.setStyleSheet("QLabel {font-size: 10px;}")



        self.mixButton = QPushButton("Optimize Mixtures")
        self.mixButton.setStyleSheet("QPushButton {color: red;}")
        self.mixButton.setDefault(True)
        self.emptyButton = QPushButton("Add Empty Mixture")
        self.emptyButton.setStyleSheet("QPushButton {color: blue;}")
        self.resetButton = QPushButton("Reset Mixtures")
        self.resetButton.setStyleSheet("QPushButton {color: orange;}")
        self.importButton = QPushButton("Import Mixtures")
        self.importButton.setStyleSheet("QPushButton {color: purple;}")

    def initScoreParams(self):
        self.scoreHLine = QFrame()
        self.scoreHLine.setFrameShape(QFrame.HLine)
        self.scoringLabel = QLabel("Scoring Parameters")
        self.scoringLabel.setStyleSheet('QLabel{color: red; font-weight: bold; qproperty-alignment: AlignCenter; '
                                        'font-size: 14px;}')
        self.rangeLabel = QLabel("Overlap Range")
        self.rangeLabel.setAlignment(Qt.AlignCenter)
        self.rangeSpinBox = QDoubleSpinBoxScore()
        self.rangeSpinBox.setKeyboardTracking(False)
        self.rangeSpinBox.setAlignment(Qt.AlignCenter)
        self.rangeSpinBox.setRange(0.001, 1.000)
        self.rangeSpinBox.setSingleStep(0.005)
        self.rangeSpinBox.setDecimals(3)
        self.rangeSpinBox.setValue(self.params.peak_range)
        self.scorepowerLabel = QLabel("Score Exponent")
        self.scorepowerLabel.setAlignment(Qt.AlignCenter)
        self.scorepowerSpinBox = QSpinBoxScore()
        self.scorepowerSpinBox.setKeyboardTracking(False)
        self.scorepowerSpinBox.setAlignment(Qt.AlignCenter)
        self.scorepowerSpinBox.setRange(1, 10)
        self.scorepowerSpinBox.setValue(self.params.score_power)
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

    def initMixParams(self):
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
        self.extramixSpinBox.setRange(0, 100)
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
        self.starttempSpinBox.setRange(self.params.final_temp+1, 100000)
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
        self.maxstepsSpinBox.setRange(1, 5000000)
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
            if self.params.solvent_specific_ignored_region:
                self.usesolventCheckBox.setDisabled(True)
        else:
            self.usesolventCheckBox.setCheckState(Qt.Unchecked)
        self.randomizeLabel = QLabel("Randomize Initial Mixtures")
        self.randomizeLabel.setAlignment(Qt.AlignCenter)
        self.randomizeCheckBox = QCheckBox()
        if self.params.randomize_initial:
            self.randomizeCheckBox.setCheckState(Qt.Checked)
        else:
            self.randomizeCheckBox.setCheckState(Qt.Unchecked)
        self.resetLabel = QLabel("Reset Mixtures to see changes")
        self.resetLabel.setStyleSheet("QLabel {color: red;}")
        self.resetLabel.setAlignment(Qt.AlignCenter)
        self.resetLabel.hide()

    def initRefinement(self):
        self.userefineLabel = QLabel("Use Refinement")
        self.userefineLabel.setAlignment(Qt.AlignCenter)
        self.userefineCheckBox = QCheckBox()
        if self.params.use_refine:
            self.userefineCheckBox.setChecked(True)
            disabled = False
        else:
            self.userefineCheckBox.setChecked(False)
            disabled = True
        self.refinecoolingLabel = QLabel("Cooling Rate")
        self.refinecoolingLabel.setAlignment(Qt.AlignCenter)
        self.refinecoolingLabel.setDisabled(disabled)
        self.refinecoolingComboBox = QComboBox()
        self.refinecoolingComboBox.setEditable(True)
        self.refinecoolingComboBox.lineEdit().setReadOnly(True)
        self.refinecoolingComboBox.lineEdit().setAlignment(Qt.AlignCenter)
        self.refinecoolingComboBox.addItems(['Exponential', 'Linear'])
        if self.params.refine_cooling == "exponential":
            self.refinecoolingComboBox.setCurrentIndex(0)
        elif self.params.refine_cooling == "linear":
            self.refinecoolingComboBox.setCurrentIndex(1)
        self.refinecoolingComboBox.setDisabled(disabled)
        self.refinestarttempLabel = QLabel("Start Temp")
        self.refinestarttempLabel.setAlignment(Qt.AlignCenter)
        self.refinestarttempLabel.setDisabled(disabled)
        self.refinestarttempSpinBox = QSpinBox()
        self.refinestarttempSpinBox.setKeyboardTracking(False)
        self.refinestarttempSpinBox.setAlignment(Qt.AlignCenter)
        self.refinestarttempSpinBox.setRange(self.params.refine_final_temp+1, 100000)
        self.refinestarttempSpinBox.setSingleStep(1.0)
        # self.refinestarttempSpinBox.setDecimals(3)
        self.refinestarttempSpinBox.setValue(self.params.refine_start_temp)
        self.refinestarttempSpinBox.setDisabled(disabled)
        self.refinefinaltempLabel = QLabel("Final Temp")
        self.refinefinaltempLabel.setAlignment(Qt.AlignCenter)
        self.refinefinaltempLabel.setDisabled(disabled)
        self.refinefinaltempSpinbox = QDoubleSpinBox()
        self.refinefinaltempSpinbox.setKeyboardTracking(False)
        self.refinefinaltempSpinbox.setAlignment(Qt.AlignCenter)
        self.refinefinaltempSpinbox.setRange(1, self.params.refine_start_temp-1)
        self.refinefinaltempSpinbox.setSingleStep(1)
        # self.refinefinaltempSpinbox.setDecimals(3)
        self.refinefinaltempSpinbox.setValue(self.params.refine_final_temp)
        self.refinefinaltempSpinbox.setDisabled(disabled)
        self.refinemaxstepsLabel = QLabel("Max Steps")
        self.refinemaxstepsLabel.setAlignment(Qt.AlignCenter)
        self.refinemaxstepsLabel.setDisabled(disabled)
        self.refinemaxstepsSpinBox = QSpinBox()
        self.refinemaxstepsSpinBox.setKeyboardTracking(False)
        self.refinemaxstepsSpinBox.setAlignment(Qt.AlignCenter)
        self.refinemaxstepsSpinBox.setRange(1, 5000000)
        self.refinemaxstepsSpinBox.setValue(self.params.refine_max_steps)
        self.refinemaxstepsSpinBox.setSingleStep(self.params.refine_max_steps)
        self.refinemaxstepsSpinBox.setDisabled(disabled)
        self.refinemixrateLabel = QLabel("Mix Rate")
        self.refinemixrateLabel.setAlignment(Qt.AlignCenter)
        self.refinemixrateLabel.setDisabled(disabled)
        self.refinemixrateSpinBox = QSpinBox()
        self.refinemixrateSpinBox.setKeyboardTracking(False)
        self.refinemixrateSpinBox.setAlignment(Qt.AlignCenter)
        self.refinemixrateSpinBox.setRange(1, 100)
        self.refinemixrateSpinBox.setValue(self.params.refine_mix_rate)
        self.refinemixrateSpinBox.setDisabled(disabled)

    def initStats(self):
        self.mixtures.calcPeakStats()
        self.mixtures.total_score, self.mixtures.total_overlaps = self.mixtures.calculateTotalScore(self.mixtures.mixtures)
        self.totalcompoundsLabel = QLabel("Total Number of Compounds:")
        self.totalcompoundsLabel.setAlignment(Qt.AlignCenter)
        self.totalcompounds = QLabel("%d" % len(self.library.library))
        self.totalcompounds.setAlignment(Qt.AlignCenter)
        self.totalscoreLabel = QLabel("Total Mixtures Score: ")
        self.totalscoreLabel.setAlignment(Qt.AlignCenter)
        self.totalscore = QLabel("%0.1f" % self.mixtures.total_score)
        self.totalscore.setAlignment(Qt.AlignCenter)
        self.totalmixLabel = QLabel("Total Number of Mixtures: ")
        self.totalmixLabel.setAlignment(Qt.AlignCenter)
        self.totalmix = QLabel("%d" % len(self.mixtures.mixtures))
        self.totalmix.setAlignment(Qt.AlignCenter)
        self.totaloverlapLabel = QLabel("Total Number of Overlapped Peaks: ")
        self.totaloverlapLabel.setAlignment(Qt.AlignCenter)
        self.totaloverlap = QLabel("%d" % self.mixtures.peak_overlap_count)
        self.totaloverlap.setAlignment(Qt.AlignCenter)
        self.totalpeaksLabel = QLabel("Total Number of Peaks: ")
        self.totalpeaksLabel.setAlignment(Qt.AlignCenter)
        self.totalpeaks = QLabel("%d" % self.mixtures.num_peaks)
        self.totalpeaks.setAlignment(Qt.AlignCenter)
        self.meanoverlapLabel = QLabel("Overlapped Peaks Per Compound: ")
        self.meanoverlapLabel.setAlignment(Qt.AlignCenter)
        self.meanoverlap = QLabel("%0.1f" % (self.mixtures.peak_overlap_count / len(self.library.library)))
        self.meanoverlap.setAlignment(Qt.AlignCenter)
        self.meanscoreLabel = QLabel("Score Per Compound: ")
        self.meanscoreLabel.setAlignment(Qt.AlignCenter)
        self.meanscore = QLabel("%0.1f" % (self.mixtures.total_score / len(self.library.library)))
        self.meanscore.setAlignment(Qt.AlignCenter)
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setPlaceholderText("Compound ID or Exact Name")
        self.searchButton = QPushButton("Search")
        self.searchResults = QLabel("")
        self.searchResults.setAlignment(Qt.AlignCenter)
        self.statsHLine = QFrame()
        self.statsHLine.setFrameShape(QFrame.HLine)
        #self.showmixturehist = QPushButton("Show Mixtures Peak Plot")
        self.showrankedcompounds = QPushButton("Show Compounds Ranked by Score")

    def updateStats(self):
        self.mixtures.calcPeakStats()
        self.mixtures.total_score, self.mixtures.total_overlaps = self.mixtures.calculateTotalScore(self.mixtures.mixtures)
        self.totalscore.setText("%0.1f" % self.mixtures.total_score)
        self.totalmix.setText("%d" % len(self.mixtures.mixtures))
        self.totaloverlap.setText("%d" % self.mixtures.peak_overlap_count)
        self.totalpeaks.setText("%d" % self.mixtures.num_peaks)
        self.meanscore.setText("%0.1f" % (self.mixtures.total_score / len(self.library.library)))
        self.meanoverlap.setText("%0.1f" % (self.mixtures.peak_overlap_count / len(self.library.library)))

    def layoutWidgets(self):
        winLayout = QGridLayout(self)
        winLayout.addWidget(self.mixtable, 1, 0)

        scoreLayout = QGridLayout()
        scoreLayout.addWidget(self.rangeLabel, 2, 0)
        scoreLayout.addWidget(self.rangeSpinBox, 2, 1)
        scoreLayout.addWidget(self.scorepowerLabel, 3, 0)
        scoreLayout.addWidget(self.scorepowerSpinBox, 3, 1)
        scoreLayout.addWidget(self.scorescaleLabel, 4, 0)
        scoreLayout.addWidget(self.scorescaleSpinBox, 4, 1)
        scoreLayout.addWidget(self.useintensityLabel, 5, 0)
        checkbox1Layout = QHBoxLayout()
        checkbox1Layout.addWidget(self.useintensityCheckBox)
        scoreLayout.addLayout(checkbox1Layout, 5, 1, Qt.AlignCenter)
        scoreLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 6, 0)

        self.paramtab1.setLayout(scoreLayout)
        self.paramTabs.addTab(self.paramtab1, "Scoring")
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
        mixLayout.addWidget(self.resetLabel, 14, 0, 1, 2)
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
        self.paramtab4.setLayout(refineLayout)
        self.paramTabs.addTab(self.paramtab4, "Refining")

        statsLayout = QGridLayout()
        statsLayout.addItem(QSpacerItem(0, 15), 0, 0)
        statsLayout.addWidget(self.totalmixLabel, 1, 0)
        statsLayout.addWidget(self.totalmix, 1, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 2, 0)
        statsLayout.addWidget(self.totalcompoundsLabel, 3, 0)
        statsLayout.addWidget(self.totalcompounds, 3, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 4, 0)
        statsLayout.addWidget(self.totalpeaksLabel, 5, 0)
        statsLayout.addWidget(self.totalpeaks, 5, 1)
        statsLayout.addItem(QSpacerItem(0, 10), 6, 0)
        statsLayout.addWidget(self.statsHLine, 7, 0, 1, 2)
        statsLayout.addItem(QSpacerItem(0, 10), 8, 0)
        statsLayout.addWidget(self.totaloverlapLabel, 9, 0)
        statsLayout.addWidget(self.totaloverlap, 9, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 10, 0)
        statsLayout.addWidget(self.totalscoreLabel, 11, 0)
        statsLayout.addWidget(self.totalscore, 11, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 12, 0)
        statsLayout.addWidget(self.meanoverlapLabel, 13, 0)
        statsLayout.addWidget(self.meanoverlap, 13, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 14, 0)
        statsLayout.addWidget(self.meanscoreLabel, 15, 0)
        statsLayout.addWidget(self.meanscore, 15, 1)
        statsLayout.addItem(QSpacerItem(0, 15), 16, 0)
        statsLayout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding), 17, 0)
        statsLayout.addWidget(self.searchLineEdit, 18, 0)
        statsLayout.addWidget(self.searchButton, 18, 1)
        statsLayout.addWidget(self.searchResults, 19, 0, 1, 2)
        #statsLayout.addWidget(self.showmixturehist, 16, 0, 1, 2)
        statsLayout.addWidget(self.showrankedcompounds, 20, 0, 1, 2)
        self.paramtab3.setLayout(statsLayout)
        self.paramTabs.addTab(self.paramtab3, "Stats")

        tableinstructionLayout = QHBoxLayout()
        tableinstructionLayout.addItem(QSpacerItem(24,0))
        tableinstructionLayout.addWidget(self.lockCheckBox)
        tableinstructionLayout.addWidget(self.lockLabel)
        tableinstructionLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
        tableinstructionLayout.addWidget(self.tableInstructions)
        tableinstructionLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))

        tablebuttonLayout = QHBoxLayout()
        tablebuttonLayout.addWidget(self.mixButton)
        tablebuttonLayout.addWidget(self.emptyButton)
        tablebuttonLayout.addWidget(self.resetButton)
        tablebuttonLayout.addWidget(self.importButton)

        winbuttonLayout = QHBoxLayout()
        winbuttonLayout.addWidget(self.backButton)
        winbuttonLayout.addItem(QSpacerItem(15, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        winbuttonLayout.addWidget(self.saveButton)
        winbuttonLayout.addItem(QSpacerItem(15, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        winbuttonLayout.addWidget(self.quitButton)

        winLayout.addItem(QSpacerItem(15, 0), 1, 1)
        winLayout.addWidget(self.paramTabs, 1, 2, 3, 1)
        winLayout.addLayout(tableinstructionLayout, 2, 0)
        winLayout.addLayout(tablebuttonLayout, 3, 0)
        winLayout.addItem(QSpacerItem(0, 30, QSizePolicy.Maximum), 4, 0, 1, 3)
        winLayout.addLayout(winbuttonLayout, 5, 0, 1, 3)

    def createConnections(self):
        self.rangeSpinBox.valueChanged.connect(self.updateTable)
        self.scorepowerSpinBox.valueChanged.connect(self.updateTable)
        self.scorescaleSpinBox.valueChanged.connect(self.updateTable)
        self.useintensityCheckBox.clicked.connect(self.updateTable)

        self.startnumSpinBox.valueChanged.connect(self.updateMixing)
        self.mixsizeSpinBox.valueChanged.connect(self.updateMixing)
        self.extramixSpinBox.valueChanged.connect(self.updateMixing)
        self.coolingComboBox.currentTextChanged.connect(self.updateMixing)
        self.starttempSpinBox.valueChanged.connect(self.updateMixing)
        self.finaltempSpinbox.valueChanged.connect(self.updateMixing)
        self.maxstepsSpinBox.valueChanged.connect(self.updateMixing)
        self.mixrateSpinBox.valueChanged.connect(self.updateMixing)
        self.usesolventCheckBox.clicked.connect(self.updateSolventMixing)
        self.iterationsSpinBox.valueChanged.connect(self.updateMixing)
        self.randomizeCheckBox.clicked.connect(self.updateMixing)

        self.userefineCheckBox.clicked.connect(self.updateRefine)
        self.refinecoolingComboBox.currentTextChanged.connect(self.updateRefine)
        self.refinestarttempSpinBox.valueChanged.connect(self.updateRefine)
        self.refinefinaltempSpinbox.valueChanged.connect(self.updateRefine)
        self.refinemaxstepsSpinBox.valueChanged.connect(self.updateRefine)
        self.refinemixrateSpinBox.valueChanged.connect(self.updateRefine)

        self.showrankedcompounds.clicked.connect(self.openCompoundList)
        self.searchButton.clicked.connect(self.searchTable)
        self.searchLineEdit.returnPressed.connect(self.searchTable)

        self.lockCheckBox.clicked.connect(self.lockAll)
        self.mixButton.clicked.connect(self.optimizeMixtures)
        self.emptyButton.clicked.connect(self.addEmptyMixture)
        self.importButton.clicked.connect(self.importMixtures)
        self.resetButton.clicked.connect(self.resetTable)

        self.backButton.clicked.connect(self.backToPeakInfo)
        self.saveButton.clicked.connect(self.saveResults)
        self.quitButton.clicked.connect(self.close)

    def setTable(self):
        self.clearTable()
        self.mixtable.setSortingEnabled(False)
        rows = len(self.mixtures.mixtures)
        columns = 25
        self.mixtable.setRowCount(rows)
        self.mixtable.setColumnCount(columns)
        self.lock_mixture = {}
        for row, mixture in enumerate(sorted(list(self.mixtures.mixtures.keys()))):
            mixture_num = QTableWidgetItem(str(mixture))
            mixture_num.setTextAlignment(Qt.AlignCenter)
            self.mixtable.setItem(row, 2, mixture_num)
            lockWidget = QWidget()
            lockLayout = QHBoxLayout(lockWidget)
            self.lock_mixture[mixture] = QCheckBox()
            if mixture in self.mixtures.mixtures_lock:
                self.lock_mixture[mixture].setCheckState(Qt.Checked)
            else:
                self.lock_mixture[mixture].setCheckState(Qt.Unchecked)
            lockLayout.addStretch()
            lockLayout.addWidget(self.lock_mixture[mixture])
            lockLayout.addStretch()
            self.mixtable.setCellWidget(row, 0, lockWidget)
            view_spectra = QPushButton("View")
            self.mixtable.setCellWidget(row, 1, view_spectra)
            view_spectra.clicked.connect(self.handleMixtureButton)
            mixture_solvent = []
            self.compoundButtons = {}
            mix_state = 0
            for i, compound in enumerate(self.mixtures.mixtures[mixture]):
                compound_solvent = self.library.library[compound].solvent
                if compound_solvent not in mixture_solvent:
                    mixture_solvent.append(compound_solvent)
                compound_id = str(compound)
                compound_score = self.mixtures.compound_scores[compound][0]
                peak_overlap = self.mixtures.compound_scores[compound][1]
                total_peaks = self.mixtures.compound_scores[compound][2]
                self.compoundButtons[compound_id] = QPushButtonRight("%s\n%0.1f (%d/%d)"
                                                                % (compound_id, compound_score,
                                                                   peak_overlap, total_peaks))
                if float(compound_score) >= (0.75 * self.params.score_scale):
                    if mix_state < 4:
                        mix_state = 4
                    self.compoundButtons[compound_id].setStyleSheet('QPushButton {color: red;}')
                elif float(compound_score) >= (0.50 * self.params.score_scale):
                    if mix_state < 3:
                        mix_state = 3
                    self.compoundButtons[compound_id].setStyleSheet('QPushButton {color: orange;}')
                elif float(compound_score) >= (0.25 * self.params.score_scale):
                    if mix_state < 2:
                        mix_state = 2
                    self.compoundButtons[compound_id].setStyleSheet('QPushButton {color: purple;}')
                elif float(compound_score) > (0.00 * self.params.score_scale):
                    if mix_state < 1:
                        mix_state = 1
                    self.compoundButtons[compound_id].setStyleSheet('QPushButton {color: blue;}')
                else:
                    self.compoundButtons[compound_id].setStyleSheet('QPushButton {color: green;}')

                self.mixtable.setCellWidget(row, i+5, self.compoundButtons[compound_id])
                self.compoundButtons[compound_id].leftClicked.connect(self.handleCompoundButtonLeft)
                self.compoundButtons[compound_id].rightClicked.connect(self.handleCompoundButtonRight)
            mixture_score = "%0.1f" % self.mixtures.mixture_scores[tuple(self.mixtures.mixtures[mixture])]
            score = QTableWidgetItem()
            score.setTextAlignment(Qt.AlignCenter)
            score.setData(Qt.DisplayRole, float(mixture_score))
            if mix_state == 4:
                score.setForeground(QColor('red'))
            elif mix_state == 3:
                score.setForeground(QColor('orange'))
            elif mix_state == 2:
                score.setForeground(QColor('purple'))
            elif mix_state == 1:
                score.setForeground(QColor('blue'))
            else:
                score.setForeground(QColor('green'))
            self.mixtable.setItem(row, 3, score)
            if len(mixture_solvent) >= 2:
                solvent = QTableWidgetItem("Mixed")
                if self.params.use_solvent:
                    solvent.setForeground(QColor('red'))
            elif not mixture_solvent:
                if self.params.use_solvent:
                    for solvent_type in self.mixtures.solvent_mixnum:
                        if mixture in self.mixtures.solvent_mixnum[solvent_type]:
                            solvent_text = str(solvent_type)
                            solvent = QTableWidgetItem(solvent_text)
            else:
                solvent = QTableWidgetItem(mixture_solvent[0])
            solvent.setTextAlignment(Qt.AlignCenter)
            self.mixtable.setItem(row, 4, solvent)
        self.mixtable.setSortingEnabled(True)

    def updateTable(self):
        self.updateScoring()
        self.updateStats()
        self.setTable()

    def clearTable(self):
        """Deletes all rows in the table."""
        while self.mixtable.rowCount() > 0:
            self.mixtable.removeRow(0)

    def lockAll(self):
        rows = self.mixtable.rowCount()
        if self.lockCheckBox.isChecked():
            for row in range(rows):
                self.mixtable.cellWidget(row, 0).findChild(QCheckBox).setCheckState(Qt.Checked)
        else:
            for row in range(rows):
                self.mixtable.cellWidget(row, 0).findChild(QCheckBox).setCheckState(Qt.Unchecked)

    def updateScoring(self):
        self.mixtures.resetScores()
        range = self.rangeSpinBox.value()
        power = self.scorepowerSpinBox.value()
        scale = self.scorescaleSpinBox.value()
        self.params.setPeakRange(float(range))
        self.params.setScorePower(int(power))
        self.params.setScoreScale(int(scale))
        if self.useintensityCheckBox.isChecked():
            self.params.useIntensity()
        else:
            self.params.noIntensity()
        self.mixtures.calculateTotalScore(self.mixtures.mixtures)

    def updateMixing(self):
        start_num = self.startnumSpinBox.value()
        if int(start_num) != self.params.start_num:
            self.params.setStartingMixtureNum(int(start_num))
            self.need_reset = True
        mix_size = self.mixsizeSpinBox.value()
        if int(mix_size) != self.params.mix_size:
            self.params.setMixSize(int(mix_size))
            self.need_reset = True
        extra_mix = self.extramixSpinBox.value()
        if int(extra_mix) != self.params.extra_mixtures:
            self.params.setExtraMixtures(int(extra_mix))
            self.need_reset = True
        start_temp = self.starttempSpinBox.value()
        self.params.setStartingTemp(float(start_temp))

        final_temp = self.finaltempSpinbox.value()
        self.params.setFinalTemp(float(final_temp))
        self.starttempSpinBox.setRange(self.params.final_temp+1, 100000)
        self.finaltempSpinbox.setRange(1, self.params.start_temp-1)
        max_steps = self.maxstepsSpinBox.value()
        self.params.setMaxSteps(int(max_steps))
        mix_rate = self.mixrateSpinBox.value()
        self.params.setMixRate(int(mix_rate))
        self.mixrateSpinBox.setRange(2, len(self.mixtures.mixtures))
        cooling = self.coolingComboBox.currentText()
        if cooling == 'Exponential':
            self.params.useExponentialCooling()
        elif cooling == 'Linear':
            self.params.useLinearCooling()

        iterations = self.iterationsSpinBox.value()
        if int(iterations) != self.params.iterations:
            self.params.setNumIterations(int(iterations))
            self.need_reset = True

        if self.randomizeCheckBox.isChecked():
            self.params.randomize_initial = True
        else:
            self.params.randomize_initial = False

        if self.need_reset:
            self.resetLabel.show()

    def updateRefine(self):
        if self.userefineCheckBox.isChecked():
            self.params.use_refine = True
            disabled = False
        else:
            disabled = True
            self.params.use_refine = False
        self.refinecoolingLabel.setDisabled(disabled)
        self.refinecoolingComboBox.setDisabled(disabled)
        self.refinestarttempLabel.setDisabled(disabled)
        self.refinestarttempSpinBox.setDisabled(disabled)
        self.refinefinaltempLabel.setDisabled(disabled)
        self.refinefinaltempSpinbox.setDisabled(disabled)
        self.refinemaxstepsLabel.setDisabled(disabled)
        self.refinemaxstepsSpinBox.setDisabled(disabled)
        self.refinemixrateLabel.setDisabled(disabled)
        self.refinemixrateSpinBox.setDisabled(disabled)

        start_temp = self.refinestarttempSpinBox.value()
        self.params.setRefineStartingTemp(float(start_temp))
        final_temp = self.refinefinaltempSpinbox.value()
        self.params.setRefineFinalTemp(float(final_temp))
        self.refinestarttempSpinBox.setRange(self.params.refine_final_temp+1, 100000)
        self.refinefinaltempSpinbox.setRange(1, self.params.refine_start_temp-1)
        max_steps = self.refinemaxstepsSpinBox.value()
        self.params.setRefineMaxSteps(int(max_steps))
        mix_rate = self.refinemixrateSpinBox.value()
        self.params.setRefineMixRate(int(mix_rate))
        self.refinemixrateSpinBox.setRange(2, len(self.mixtures.mixtures))
        cooling = self.refinecoolingComboBox.currentText()
        if cooling == 'Exponential':
            self.params.useRefineExponentialCooling()
        elif cooling == 'Linear':
            self.params.useRefineLinearCooling()

    def updateSolventMixing(self):
        if self.usesolventCheckBox.isChecked():
            self.params.useSolvent()
            self.mixtures.resetScores()
            self.mixtures.generateSolventLists()
            self.mixtures.generateInitialMixtures()
            self.updateMixing()
            self.updateScoring()
            self.updateStats()
            self.setTable()
            self.need_reset = False
        else:
            self.params.noSolvent()
            self.updateMixing()
            self.updateScoring()
            self.updateStats()

    def resetTable(self):
        reset_message = "Are you sure you want to reset the mixture? The current mixture table will be lost."
        reply = QMessageBox.question(self, "Reset Mixtures?", reset_message, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mixtures.resetScores()
            self.mixtures.generateSolventLists()
            self.mixtures.generateInitialMixtures()
            self.updateMixing()
            self.updateScoring()
            self.updateStats()
            self.setTable()
            self.resetLabel.hide()
            self.need_reset = False

    def addEmptyMixture(self):
        """Adds an new empty row at the end of the table."""
        mixnum_list = sorted(list(self.mixtures.mixtures))
        new_mixnum = int(mixnum_list[-1]) + 1
        if self.params.use_solvent:
            solvent = ""
            newmix_win = NewMixtureSolvent(self.mixtures, new_mixnum)
            if newmix_win.exec_():
                solvent = newmix_win.solvent
        else:
            solvent = "Any"
        if solvent:
            if solvent == "Any":
                solvent_name = ""
            else:
                solvent_name = solvent
            self.mixtures.mixtures[new_mixnum] = []
            self.mixtures.solvent_mixnum[solvent_name].append(new_mixnum)
            self.mixtures.num_mixtures += 1
            self.mixtures.resetScores()
            self.updateScoring()
            self.updateStats()
            self.setTable()
            rows = self.mixtable.rowCount()
            self.mixtable.scrollToItem(self.mixtable.item(rows, 2))

    def handleCompoundButtonLeft(self):
        button = self.sender()
        index = self.mixtable.indexAt(button.pos())
        if index.isValid():
            compound_text = self.mixtable.cellWidget(index.row(), index.column()).text()
            compound_text_list = compound_text.split()
            compound_id = compound_text_list[0]
            mixture_id = self.mixtable.item(index.row(), 2).text()
            self.openCompoundWindow(compound_id, mixture_id)

    def handleCompoundButtonRight(self):
        button = self.sender()
        index = self.mixtable.indexAt(button.pos())
        if index.isValid():
            compound_text = self.mixtable.cellWidget(index.row(), index.column()).text()
            compound_text_list = compound_text.split()
            compound_id = compound_text_list[0]
            mixture_id = self.mixtable.item(index.row(), 2).text()
            movecompound_win = move_compounds.Window(self.params, self.library, self.mixtures, compound_id, mixture_id)
            movecompound_win.resize(325, 300)
            if movecompound_win.exec_():
                self.updateScoring()
                self.updateStats()
                self.setTable()
                self.need_reset = False


    def handleMixtureButton(self):
        button = self.sender()
        index = self.mixtable.indexAt(button.pos())
        if index.isValid():
            mixture = self.mixtable.item(index.row(), 2).text()
            # print(self.mixtures.mixtures[int(mixture)])
            self.viewMixtureSpectra(mixture)

    def searchTable(self):
        query = self.searchLineEdit.text()
        query_success = False
        print(query, query_success)
        if query:
            print("if query")
            for mixture in self.mixtures.mixtures:
                for compound in self.mixtures.mixtures[mixture]:
                    name = self.library.library[compound].name
                    search_options = [compound, compound.upper(), compound.lower(),
                                      name, name.upper(), name.lower(), name.capitalize()]
                    if query in search_options:
                        print("query in search_options")
                        self.searchResults.setText("%s Found in Mixture %d" % (query, mixture))
                        self.searchResults.setStyleSheet("QLabel {color: blue;}")
                        rows = self.mixtable.rowCount()
                        for row in range(rows):
                            if self.mixtable.item(row, 2).text() == str(mixture):
                                self.mixtable.scrollToItem(self.mixtable.item(row, 2))
                                break
                        query_success = True
                        break
                if query_success:
                    self.searchLineEdit.setText("")
                    break
            if not query_success:
                self.searchResults.setText("No matches found")
                self.searchResults.setStyleSheet("QLabel {color: black;}")

    def updateLockMixtures(self):
        self.mixtures.mixtures_lock = []
        rows = self.mixtable.rowCount()
        for row in range(rows):
            is_checked = self.mixtable.cellWidget(row, 0).findChild(QCheckBox).isChecked()
            if is_checked:
                self.mixtures.mixtures_lock.append(int(self.mixtable.item(row,2).text()))

    def saveResults(self):
        results_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
        results_folder = results_time + "_Results"
        self.results_path = os.path.join(self.params.work_dir, results_folder)
        if not os.path.exists(self.results_path):
            os.mkdir(self.results_path)
        self.mixtures.exportSimpleMixturesTXT(self.results_path)
        self.mixtures.exportMixturesCSV(self.results_path)
        self.mixtures.exportRoiCSV(self.results_path)
        self.mixtures.exportFullRoiCSV(self.results_path)
        self.mixtures.exportIgnoreRegion(self.results_path)
        self.mixtures.exportScores(self.results_path)
        self.mixtures.exportPeakListCSV(self.results_path)
        self.library.exportLibraryCSV(self.results_path)
        self.library.exportImportLog(self.results_path)
        # self.library.exportPeaklistCSV(self.results_path)
        self.params.exportScoringParams(self.results_path)
        output_msg = "Mixture results output to:<br><font color='blue'>%s</font>" % self.results_path
        QMessageBox.information(self, 'Results Saved', output_msg)

    def importMixtures(self):
        dir = self.params.work_dir



        fileObj = QFileDialog.getOpenFileName(self, "Open Mixtures CSV", directory=dir, filter="CSV Files: (*.csv)")
        if fileObj[0]:
            import_extras_win = ExtrasImport()
            if import_extras_win.exec_():
                use_extras = import_extras_win.checkbox.checkState()
            import_win = MixtureImport(self.params, fileObj[0], self.library, self.mixtures, use_extras)
            if import_win.exec_():
                self.updateScoring()
                self.updateStats()
                self.setTable()
                self.lockCheckBox.setChecked(True)
                self.usesolventCheckBox.setChecked(self.params.use_solvent)
                self.startnumSpinBox.setValue(self.params.start_num)
                self.mixsizeSpinBox.setValue(self.params.mix_size)
                self.lockAll()
                # TODO: Determine how to lock only the mixtures in the imported file

    def optimizeMixtures(self):
        self.updateLockMixtures()
        optimize_msg = "Are you sure you want to optimize mixtures?\nAny unlocked mixtures will be changed."
        reply = QMessageBox.question(self, 'Optimize Mixtures', optimize_msg, QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            if self.need_reset:
                self.mixtures.resetScores()
                self.mixtures.generateSolventLists()
                self.mixtures.generateInitialMixtures()
            optimize_win = optimize.Window(self.params, self.library, self.mixtures)
            if optimize_win.exec_():
                self.updateScoring()
                self.updateStats()
                self.setTable()
        # TODO: Check for value errors

    def openCompoundWindow(self, compound_id, mixture_id):
        compound_object = self.library.library[compound_id]
        compound_win = compound_info.Window(self.params, compound_object)
        if compound_win.exec_():
            pass

    def openCompoundList(self):
        compoundlist_win = compounds_ranked.Window(self.params, self.library, self.mixtures)
        compoundlist_win.resize(680, int(self.params.size.height() * 0.7))
        compoundlist_win.exec_()

    def viewMixtureSpectra(self, mixture):
        compound_list = list(self.mixtures.mixtures[int(mixture)])
        mixture_win = mixture_spectra.Window(self.params, self.library, compound_list, mixture)
        mixture_win.exec_()

    def backToPeakInfo(self):
        del self.mixtures
        QDialog.reject(self)

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to quit NMRmix?\nAny unsaved information will be lost."
        reply = QMessageBox.question(self, 'Quit NMRmix?', quit_msg, QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.backToPeakInfo()

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

class QPushButtonRight(QPushButton):
    rightClicked = pyqtSignal()
    leftClicked = pyqtSignal()

    def __init__(self, string):
        QPushButton.__init__(self, string)

    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit()

class NewMixtureSolvent(QDialog):
    def __init__(self, mixtures_object, mixnum, parent=None):
        QDialog.__init__(self, parent)
        self.mixtures = mixtures_object
        self.mixnum = mixnum
        self.setWindowTitle("Solvent for New Mixture")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.questionLabel = QLabel("Select solvent type for mixture:")
        self.solventComboBox = QComboBox()
        for solvent in self.mixtures.solvent_dict:
            self.solventComboBox.addItem(solvent)
        self.cancelButton = QPushButton("Cancel")
        self.acceptButton = QPushButton("Accept")


    def layoutWidgets(self):
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.acceptButton)
        vbox.addWidget(self.questionLabel)
        vbox.addWidget(self.solventComboBox)
        vbox.addLayout(hbox)

    def createConnections(self):
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.acceptSolvent)

    def acceptSolvent(self):
        self.solvent = str(self.solventComboBox.currentText())
        QDialog.accept(self)

class MixtureImport(QDialog):
    def __init__(self, params_object, filepath, library_object, mixtures_object, use_extras=True, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.mixtures = mixtures_object
        self.filepath = filepath
        self.use_extras = use_extras
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.importMixturesCSV()

    def createWidgets(self):
        self.importLog = QTextEdit()
        self.cancelButton = QPushButton("Cancel")
        self.acceptButton = QPushButton("Accept")
        self.acceptButton.setDisabled(True)

    def layoutWidgets(self):
        winLayout = QVBoxLayout(self)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.acceptButton)
        winLayout.addWidget(self.importLog)
        winLayout.addLayout(buttonLayout)

    def createConnections(self):
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.acceptMixtures)

    def importMixturesCSV(self):
        self.unused_list = []
        self.new_mixtures = {}
        self.solvent_mixnum = {}
        for compound in list(self.library.library.keys()):
            self.unused_list.append(compound)
        random.shuffle(self.unused_list)
        mix_size = 0
        import_error = False
        with codecs.open(self.filepath, 'rU') as mixtures_csv:
            reader = csv.reader(mixtures_csv)
            try:
                self.use_solvent = True
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    else:
                        if row[2] == "Mixed":
                            self.use_solvent = False
                            break
                        if row[2] is None or row[2] is False:
                            self.use_solvent = False
                            break
                mixtures_csv.seek(0)
                if not self.use_solvent:
                    self.solvent_mixnum[""] = []
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    mixnum = int(row[0])
                    if mixnum not in self.new_mixtures:
                        self.new_mixtures[mixnum] = []
                        if self.use_solvent:
                            if row[2] not in self.solvent_mixnum:
                                self.solvent_mixnum[row[2]] = []
                                self.solvent_mixnum[row[2]].append(mixnum)
                            else:
                                self.solvent_mixnum[row[2]].append(mixnum)
                        else:
                            self.solvent_mixnum[""].append(mixnum)
                        for compound in row[3:]:
                            if not compound:
                                continue
                            if compound not in self.unused_list:
                                self.importLog.append("Compound %s not in library...skipped" % compound)
                                import_error = True
                            else:
                                self.unused_list.remove(compound)
                                self.new_mixtures[int(row[0])].append(compound)
                                if len(row)-3 > mix_size:
                                    mix_size = len(row[3:])
                    else:
                        self.importLog.append("Mixture number %d is a duplicate." % int(row[0]))
                        import_error = True
            except Exception as e:
                self.importLog.append("Mixture format not recognized.")
                import_error = True
            if not import_error:
                self.importLog.append("No detected errors in mixture import.")
                self.params.setStartingMixtureNum(min(list(self.new_mixtures.keys())))
                self.params.setMixSize(mix_size)
                self.params.use_solvent = self.use_solvent
                if self.use_extras:
                    if len(self.unused_list) > 0:
                        if self.use_solvent:
                            solvent_dict = {}
                            for compound in self.unused_list:
                                solvent = self.library.library[compound].solvent
                                if solvent not in solvent_dict:
                                    solvent_dict[solvent] = []
                                    solvent_dict[solvent].append(compound)
                                else:
                                    solvent_dict[solvent].append(compound)
                            for solvent in solvent_dict:
                                self.assignUnused(solvent_dict[solvent], solvent)
                        else:
                            self.assignUnused(self.unused_list, solvent="")

                self.acceptButton.setDisabled(False)

    def assignUnused(self, compound_list, solvent):
        mix_numbers = list(self.new_mixtures.keys())
        mix_num = max(mix_numbers) + 1
        self.new_mixtures[mix_num] = []
        for compound in compound_list:
            if len(self.new_mixtures[mix_num]) >= self.params.mix_size:
                self.new_mixtures[mix_num].sort()
                self.solvent_mixnum[solvent].append(mix_num)
                mix_num += 1
                self.new_mixtures[mix_num] = []
                self.new_mixtures[mix_num].append(compound)
            else:
                self.new_mixtures[mix_num].append(compound)
        self.new_mixtures[mix_num].sort()

    def acceptMixtures(self):
        self.mixtures.mixtures = copy.deepcopy(self.new_mixtures)
        self.mixtures.solvent_mixnum = copy.deepcopy(self.solvent_mixnum)
        if not self.use_extras:
            if len(self.unused_list) > 0:
                for compound in self.unused_list:
                    self.library.removeLibraryCompound(self.library.library[compound])
        QDialog.accept(self)

class ExtrasImport(QMessageBox):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setIcon(QMessageBox.Question)
        self.setWindowTitle("Use Extra Compounds?")
        import_extras_msg = "\n\n<font color='red'>Warning: If the extra compounds are not included, they will be removed\n" \
                            "from the available list of compounds.</font>"
        self.setText("Would you like to include any extra active compounds that are not in the imported mixtures?")
        self.checkbox = QCheckBox()
        self.checkbox.setText("Use extra compounds in new mixtures")
        self.checkbox.setCheckState(Qt.Checked)
        self.warningText = QLabel(import_extras_msg)
        self.warningText.setWordWrap(True)
        winLayout = self.layout()
        messageLayout = QVBoxLayout()
        messageLayout.addWidget(self.warningText)
        messageLayout.addWidget(self.checkbox)
        winLayout.addLayout(messageLayout, 1, 2)
        self.setStandardButtons(QMessageBox.Ok)

