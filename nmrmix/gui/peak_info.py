#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
peak_info.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import *

import sys

from gui import mixtures_view, peak_histogram, peak_count, peak_aromaticity, compounds_list

class Window(QDialog):
    def __init__(self, params_object, library_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.ignored_regions = {}
        self.setWindowTitle("NMRmix: Library Peak Info")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        # Stats Table
        self.statsTabs = QTabWidget()
        self.statsTabs.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.statsTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')

        self.statstab1 = QWidget()
        numcols = len(self.library.groups) + 2
        self.statstable = QTableWidget(10, numcols, self)
        self.statstable.setSelectionMode(QAbstractItemView.NoSelection)
        self.statstable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.statstable.setFocusPolicy(Qt.NoFocus)
        self.statstable.verticalHeader().setDefaultSectionSize(60)
        self.statstable.setColumnWidth(0, 175)
        self.header = ["","ALL"]
        for group in self.library.groups:
            self.header.append(group)
        self.statstable.setHorizontalHeaderLabels(self.header)
        self.statstable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.statstable.horizontalHeader().setStretchLastSection(True)
        self.statstable.verticalHeader().hide()
        self.statlabels = ['Total Compounds', 'Total Peaks', 'Peaks per Compound\n(Mean)',
                           'Peaks per Compound\n(Median)', 'Most/Least Peaks per Compound',
                           'Aromatic Compounds', 'Aliphatic Compounds',
                           'Number of Compounds with Ignored Peaks (Total Peaks)',
                           'Number of Compounds with Ignored Intense Peaks (Total Peaks)',
                           'Number of Compounds with All Peaks Ignored']
        for row, label in enumerate(self.statlabels):
            font = QFont()
            font.setBold(True)
            statitem = QTableWidgetItem(label)

            statitem.setFont(font)
            statitem.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.statstable.setItem(row, 0, statitem)
            if row == 9:
                self.statstable.setRowHeight(row, 75)

        self.statstable.item(0,0).setToolTip("The total number of compounds in the library with successfully\n"
                                             "imported peaklists.")
        self.statstable.item(1,0).setToolTip("The total number peaks that were successfully imported.")
        self.statstable.item(2,0).setToolTip("Represents the mean number of peaks per compound with the\n"
                                             "standard deviation.")
        self.statstable.item(3,0).setToolTip("Represents the median number of peaks per compound.")
        self.statstable.item(4,0).setToolTip("Shows the most number of peaks found for a compound and the least\n"
                                             "number of peaks found for a compound.")
        self.statstable.item(5,0).setToolTip("Characterizes the peak lists based on chemical shifts.\n"
                                             "Aromatic compounds are composed of more aromatic peaks.\n"
                                             "Aromatic peaks are above the Aro/Ali Cutoff.")
        self.statstable.item(6,0).setToolTip("Characterizes the peak lists based on chemical shifts.\n"
                                             "Aliphatic compounds are composed of more aliphatic peaks.\n"
                                             "Aliphatic peaks are below the Aro/Ali Cutoff.")
        self.statstable.item(7,0).setToolTip("Represents the number of compounds with at least one peak that\n"
                                             "overlaps with an ignored region.\n"
                                             "The total number of peaks for the library is in parenthesis.")
        self.statstable.item(8,0).setToolTip("Represents the number of compounds with at least one intense peak that\n"
                                             "overlaps with an ignored region.\n"
                                             "The total number of intense peaks for the library is in parenthesis.\n"
                                             "An intense peak is any peak with a height greater than a specified\n"
                                             "percentage of the largest peak for that compound.\n"
                                             "The percentage is set by the Intensity Cutoff.\n"
                                             "For example, at Intensity Cutoff = 0.90, all peaks at 90% or higher\n"
                                             "of the largest peak is considered an intense peak.")
        self.statstable.item(9,0).setToolTip("Represents the number of compounds where all of the peaks overlap\n"
                                             "with an ignored region, thus effectively deleting the compound from\n"
                                             "the library.\n"
                                             "Click the number to pop up a list of the ignored compounds.")

        self.updateStats()

        self.statstblIntensityLbl = QLabel("<b>Intensity Cutoff (%)</b>")
        self.statstblIntensityLbl.setToolTip('Sets the percentage of the most intense peak\n'
                                             'that is still characterized as an intense peak.\n'
                                             'For example: 90% means all peaks of intensity 90% or greater\n'
                                             'of the most intense peak is considered an intense peak for\n'
                                             'the statistics.\n'
                                             'Click number to manually edit.')
        self.statstblIntensity = QDoubleSpinBox()
        self.statstblIntensity.setRange(0.0, 100.0)
        self.statstblIntensity.setSingleStep(5.0)
        self.statstblIntensity.setDecimals(1)
        self.statstblIntensity.setAlignment(Qt.AlignCenter)
        self.statstblIntensity.setValue((self.params.intense_peak_cutoff*100))
        self.statstblIntensity.setToolTip('Sets the percentage of the most intense peak\n'
                                          'that is still characterized as an intense peak.\n'
                                          'For example: 90% means all peaks of intensity 90% or greater\n'
                                          'of the most intense peak is considered an intense peak for\n'
                                          'the statistics.\n'
                                          'Click number to manually edit.')
        self.statstblAromaticLbl = QLabel("<b>Aro/Ali Cutoff (ppm)")
        self.statstblAromaticLbl.setToolTip("Sets the ppm cutoff between characterizing a peak\n"
                                            "as aromatic or aliphatic for statistical purposes.\n"
                                            "Default is set to water (4.700 ppm).\n"
                                            "Click number to manually edit.")
        self.statstblAromatic = QDoubleSpinBox()
        self.statstblAromatic.setRange(0.000, 12.000)
        self.statstblAromatic.setSingleStep(0.100)
        self.statstblAromatic.setDecimals(3)
        self.statstblAromatic.setAlignment(Qt.AlignCenter)
        self.statstblAromatic.setValue(self.params.aromatic_cutoff)
        self.statstblAromatic.setToolTip("Sets the ppm cutoff between characterizing a peak\n"
                                         "as aromatic or aliphatic for statistical purposes.\n"
                                         "Default is set to water (4.700 ppm).\n"
                                         "Click number to manually edit.")

        # Ignored Regions Table
        self.ignoreTabs = QTabWidget()
        self.ignoreTabs.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.ignoreTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                      'QTabBar::tab {color: black;}'
                                      'QTabBar::tab:selected {color: red;}')
        self.ignoretab1 = QWidget()

        self.ignoretablelabel = QLabel('<b><center>Regions to Ignore for Peak Overlaps</center></b>')
        self.ignoretablelabel.setToolTip('Any peaks in these regions will be ignored for the\n'
                                         'purposes of determining peak overlap.\n'
                                         'Ideal ranges to add to the list are regions containing peaks\n'
                                         'that occur in every sample (i.e. water, DSS, buffers, internal standards')
        self.ignoretable = QTableWidget(0, 4, self)
        self.ignoretable.setSelectionMode(QAbstractItemView.NoSelection)
        self.ignoretable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ignoretable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ignoretable.setSortingEnabled(False)
        self.ignoretable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ignoretable.setColumnWidth(0, 125)
        self.ignoretable.setColumnWidth(1, 90)
        self.ignoretable.setColumnWidth(2, 90)
        self.ignoretable.setColumnWidth(3, 90)
        self.ignoretable.horizontalHeader().setStretchLastSection(True)
        self.ignoreheader = ['Name', 'Lower Limit\n(ppm)', 'Upper Limit\n(ppm)', 'Group\nSpecificity']
        self.ignoretable.setHorizontalHeaderLabels(self.ignoreheader)
        self.ignoretable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.ignoretable.verticalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.ignoretable.horizontalHeaderItem(0).setToolTip('Enter a name to represent this ignore region\n'
                                                            'Must be a unique name.')
        self.ignoretable.horizontalHeaderItem(1).setToolTip('The lower limit of the ignore range in ppm.')
        self.ignoretable.horizontalHeaderItem(2).setToolTip('The upper limit of the ignore range in ppm.')
        self.ignoretable.horizontalHeaderItem(3).setToolTip('This sets whether this ignore region should only\n'
                                                            'be used for compounds in this group.\n'
                                                            'Default is set to use the ignore region for all\n'
                                                            'compounds regardless of group.')
        self.ignoretable.selectRow(0)
        #
        # # Ignored Regions Table Buttons and Parameters
        self.ignoretblbtnAdd = QPushButton("Add Region")
        self.ignoretblbtnAdd.setToolTip('Add a new ignore region.\n'
                                        'Remember, the names should be unique.')
        self.ignoretblbtnRemove = QPushButton("Delete Region")
        self.ignoretblbtnRemove.setToolTip('Remove the selected row/region from the table.')
        self.ignoretblbtnEdit = QPushButton("Edit Region")
        self.ignoretblbtnEdit.setToolTip('Allows for the selected row/region to be edited.')
        self.ignoretblbtnClear = QPushButton("Clear Regions")
        self.ignoretblbtnClear.setToolTip("Clears the table of all ignored regions")
        self.ignoretblbtnImport = QPushButton("Import Regions")
        self.ignoretblbtnImport.setToolTip("Clear table and import a csv containing the ignored regions")

        self.btnwidget = QWidget()
        self.buttonContinue = QPushButton("Continue to Mixture Generation")
        self.buttonContinue.setStyleSheet("QPushButton{font-size:20px; color: green; font-weight: bold;}")
        self.buttonContinue.setFixedHeight(50)
        self.buttonContinue.setFixedWidth(350)
        self.buttonContinue.setToolTip('Tooltip.')
        self.buttonContinue.setDefault(True)
        self.buttonBack = QPushButton("Return to Library Setup")
        self.buttonBack.setStyleSheet("QPushButton{font-size:20px; color: blue; font-weight: bold;}")
        self.buttonBack.setFixedHeight(50)
        self.buttonBack.setFixedWidth(350)
        self.buttonBack.setToolTip('Tooltip.')

    def layoutWidgets(self):
        winLayout = QGridLayout(self)

        statstabLayout = QVBoxLayout()
        statstabLayout.addWidget(self.statstable)
        self.statstab1.setLayout(statstabLayout)
        self.statsTabs.addTab(self.statstab1, "Peak Statistics for Library")
        winLayout.addWidget(self.statsTabs, 0, 0)

        statsLayout = QHBoxLayout()
        statsLayout.addWidget(self.statstblIntensityLbl)
        statsLayout.addWidget(self.statstblIntensity)
        statsLayout.addItem((QSpacerItem(30, 0, QSizePolicy.Maximum)))
        statsLayout.addWidget(self.statstblAromaticLbl)
        statsLayout.addWidget(self.statstblAromatic)
        winLayout.addLayout(statsLayout, 1, 0)

        winLayout.addItem(QSpacerItem(15, 0), 1, 1)

        ignoretabLayout = QVBoxLayout()
        ignoretabLayout.addWidget(self.ignoretable)
        self.ignoretab1.setLayout(ignoretabLayout)
        self.ignoreTabs.addTab(self.ignoretab1, "Regions to Ignore for Peak Overlaps")
        winLayout.addWidget(self.ignoreTabs, 0, 2)

        ignoreLayout = QHBoxLayout()
        ignoreLayout.addWidget(self.ignoretblbtnAdd)
        ignoreLayout.addWidget(self.ignoretblbtnEdit)
        ignoreLayout.addWidget(self.ignoretblbtnRemove)
        ignoreLayout.addWidget(self.ignoretblbtnClear)
        ignoreLayout.addWidget(self.ignoretblbtnImport)
        winLayout.addLayout(ignoreLayout, 1, 2)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonBack)
        buttonLayout.addItem(QSpacerItem(15, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        buttonLayout.addWidget(self.buttonContinue)
        winLayout.addItem(QSpacerItem(0, 30, QSizePolicy.Maximum), 2, 0, 1, 3)
        winLayout.addLayout(buttonLayout, 3, 0, 1, 3)


    def createConnections(self):
        self.statstblIntensity.valueChanged.connect(self.updateIntensityCutoff)
        self.statstblAromatic.valueChanged.connect(self.updateAromaticCutoff)
        self.ignoretblbtnAdd.clicked.connect(self.addRegion)
        self.ignoretblbtnRemove.clicked.connect(self.removeRegion)
        self.ignoretblbtnEdit.clicked.connect(self.editRegion)
        self.ignoretblbtnClear.clicked.connect(self.clearRegions)
        self.ignoretblbtnImport.clicked.connect(self.importRegions)
        self.buttonBack.clicked.connect(self.backToLibrary)
        self.buttonContinue.clicked.connect(self.continueToMixtures)
        self.statstable.itemClicked.connect(self.stat_clicked)

    def updateIntensityCutoff(self):
        cutoff = self.statstblIntensity.value()
        try:
            self.params.setIntensePeakCutoff(cutoff/100)
            self.updateStats()
        except:
            error = QMessageBox(self)
            error.setWindowTitle("Intensity Cutoff Value Error!")
            error.setText("%s is not an appropriate value.\nValue needs to be a number between 0 and 1." % cutoff)
            error.exec_()

    def updateAromaticCutoff(self):
        cutoff = self.statstblAromatic.value()
        try:
            self.params.setAromaticCutoff(cutoff)
            self.updateStats()
        except:
            error = QMessageBox(self)
            error.setWindowTitle("Aromatic Cutoff Value Error!")
            error.setText("%s is not an appropriate value.\nValue needs to be a number, typically between 0 and 10."
                          % cutoff)
            error.exec_()

    def addRegion(self):
        addregion_win = RegionWindow(self.library.groups, self.ignored_regions)
        if addregion_win.exec_():
            self.acceptedRegion(addregion_win.table_values)

    def acceptedRegion(self, table_values):
        """Adds an new empty row at the end of the table, and selects it."""
        rows = self.ignoretable.rowCount()
        self.ignoretable.insertRow(rows)
        name = QTableWidgetItem(table_values[0])
        name.setTextAlignment(Qt.AlignCenter)
        lowerl = QTableWidgetItem("%.3f" % float(table_values[1]))
        lowerl.setTextAlignment(Qt.AlignCenter)
        upperl = QTableWidgetItem("%.3f" % float(table_values[2]))
        upperl.setTextAlignment(Qt.AlignCenter)
        group = QTableWidgetItem(table_values[3])
        group.setTextAlignment(Qt.AlignCenter)
        self.ignoretable.setItem(rows, 0, name)
        self.ignoretable.setItem(rows, 1, lowerl)
        self.ignoretable.setItem(rows, 2, upperl)
        self.ignoretable.setItem(rows, 3, group)
        self.ignored_regions[table_values[0]] = (float(lowerl.text()), float(upperl.text()), table_values[3])
        self.ignoretable.scrollToItem(self.ignoretable.item(rows, 1))
        self.ignoretable.selectRow(rows)
        self.updateStats()

    def removeRegion(self):
        """Deletes the selected row from the table."""
        selected = self.ignoretable.currentRow()
        name = self.ignoretable.item(selected, 0).text()
        self.ignoretable.removeRow(selected)
        del self.ignored_regions[name]
        self.updateStats()

    def editRegion(self):
        selected = self.ignoretable.currentRow()
        name = self.ignoretable.item(selected, 0).text()
        lowerl = self.ignoretable.item(selected, 1).text()
        upperl = self.ignoretable.item(selected, 2).text()
        group = self.ignoretable.item(selected, 3).text()
        table_values = [name, lowerl, upperl, group]
        editregion_win = RegionWindow(self.library.groups, self.ignored_regions, table_values)
        if editregion_win.exec_():
            self.changeRegion(editregion_win.table_values)

    def clearRegions(self):
        while self.ignoretable.rowCount() > 0:
            self.ignoretable.selectRow(0)
            self.removeRegion()
        self.ignored_regions = {}
        self.updateStats()

    def importRegions(self):
        dir = self.params.work_dir
        fileObj = QFileDialog.getOpenFileName(self, "Open Ignore Regions CSV", directory=dir,
                                              filter = "CSV Files: (*.csv)")
        if fileObj[0]:
            ignore_regions, message_log = self.library.importIgnoreRegions(fileObj[0])
            if not ignore_regions:
                QMessageBox.critical(self, "Import Error!", message_log[0], QMessageBox.Ok)
            else:
                message_string = ''
                for i in message_log:
                    message_string = message_string + "\n" + i
                QMessageBox.information(self, "Ignore Regions Imported", message_string)
                self.clearRegions()
                for region in ignore_regions:
                    self.acceptedRegion(region)

    def changeRegion(self, table_values):
        selected = self.ignoretable.currentRow()
        oldname = self.ignoretable.item(selected,0).text()
        del self.ignored_regions[oldname]
        name = QTableWidgetItem(table_values[0])
        name.setTextAlignment(Qt.AlignCenter)
        lowerl = QTableWidgetItem("%.3f" % float(table_values[1]))
        lowerl.setTextAlignment(Qt.AlignCenter)
        upperl = QTableWidgetItem("%.3f" % float(table_values[2]))
        upperl.setTextAlignment(Qt.AlignCenter)
        group = QTableWidgetItem(table_values[3])
        group.setTextAlignment(Qt.AlignCenter)
        self.ignoretable.setItem(selected, 0, name)
        self.ignoretable.setItem(selected, 1, lowerl)
        self.ignoretable.setItem(selected, 2, upperl)
        self.ignoretable.setItem(selected, 3, group)
        self.ignored_regions[table_values[0]] = (float(lowerl.text()), float(upperl.text()), table_values[3])
        self.ignoretable.scrollToItem(self.ignoretable.item(selected, 1))
        self.ignoretable.selectRow(selected)
        self.updateStats()

    def updateStats(self):
        self.library.calcStats(self.ignored_regions)
        rows = self.statstable.rowCount()
        cols = self.statstable.columnCount()
        row_colors = ['blue', 'blue', 'green', 'green', 'green', 'maroon', 'maroon', 'orange', 'orange', 'red']
        #row_colors = ['black', 'green', 'blue', 'cyan', 'maroon', 'teal', 'magenta', 'gold', 'orange', 'red']
        for row in range(rows):
            for col in range(cols):
                if col == 0:
                    continue
                else:
                    group = self.statstable.horizontalHeaderItem(col).text()
                    text = self.library.stats[str(group)][row]
                    item = QTableWidgetItem(text)
                    item.setForeground(QColor('%s' % row_colors[row]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.statstable.setItem(row, col, item)

    def stat_clicked(self, item):
        group = self.statstable.horizontalHeaderItem(item.column()).text()
        if item.column() == 0:
            pass
        elif item.row() == 0:
            compound_list = self.library.stats[group]['Compound List']
            if group == 'ALL':
                title = 'All Compounds in All Groups'
            else:
                title = 'All Compounds in %s Group' % group
            compound_win = compounds_list.Window(self.params, self.library, compound_list, title)
            compound_win.resize(680, int(self.params.size.height() * 0.7))
            if compound_win.exec_():
                if compound_win.modified:
                    self.updateStats()
        elif item.row() == 1:
            histogram_win = peak_histogram.Window(self.params, self.library, group)
            histogram_win.exec_()
        elif item.row() in [2, 3, 4]:
            histogram_win = peak_count.Window(self.params, self.library, group)
            histogram_win.exec_()
        elif item.row() in [5,6]:
            aromaticity_win = peak_aromaticity.Window(self.params, self.library, group)
            aromaticity_win.exec_()
        elif item.row() == 7:
            compound_list = self.library.stats[group]['Ignored Peak Compounds']
            if group == 'ALL':
                title = 'Compounds with Ignored Peaks in All Groups'
            else:
                title = 'Compounds with Ignored Peaks in %s Group' % group
            compound_win = compounds_list.Window(self.params, self.library, compound_list, title)
            compound_win.resize(680, int(self.params.size.height() * 0.7))
            if compound_win.exec_():
                if compound_win.modified:
                    self.updateStats()
        elif item.row() == 8:
            compound_list = self.library.stats[group]['Ignored Intense Peak Compounds']
            if group == 'ALL':
                title = 'Compounds with Ignored Intense Peaks in All Groups'
            else:
                title = 'Compounds with Ignored Intense Peaks in %s Group' % group
            compound_win = compounds_list.Window(self.params, self.library, compound_list, title)
            compound_win.resize(680, int(self.params.size.height() * 0.7))
            if compound_win.exec_():
                if compound_win.modified:
                    self.updateStats()
        elif item.row() == 9:
            compound_list = self.library.stats[group]['Ignored Compounds']
            if group == 'ALL':
                title = 'Completely Ignored Compounds in All Groups'
            else:
                title = 'Completely Ignored Compounds in %s Group' % group
            compound_win = compounds_list.Window(self.params, self.library, compound_list, title)
            compound_win.resize(680, int(self.params.size.height() * 0.7))
            if compound_win.exec_():
                if compound_win.modified:
                    self.updateStats()

    def showIgnoredCompounds(self):
        ignored_win = RegionWindow(self.library)
        ignored_win.exec_()

    def backToLibrary(self):
        self.library.library = {}
        self.reject()

    def continueToMixtures(self):
        self.updateStats()
        # TODO: Export stats and histograms
        rows = self.ignoretable.rowCount()
        self.params.group_specific_ignored_region = False
        for row in range(rows):
            if self.ignoretable.item(row,3).text() != 'ALL':
                self.params.useGroup()
                self.params.group_specific_ignored_region = True
        self.hide()
        self.mixtures_win = mixtures_view.Window(self.params, self.library)
        self.mixtures_win.resize(int(self.params.size.width() * 0.85), int(self.params.size.height() * 0.7))
        self.mixtures_win.rejected.connect(self.show)
        self.mixtures_win.show()

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to quit NMRmix?\nAny unsaved information will be lost."
        reply = QMessageBox.question(self, 'Quit NMRmix?', quit_msg, QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            sys.exit()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()


class RegionWindow(QDialog):
    def __init__(self, group_list, ignored_dict, table_values=[], parent=None):
        QDialog.__init__(self, parent)
        self.group_list = list(group_list)
        self.name_list = list(ignored_dict.keys())
        self.table_values = list(table_values)
        if self.table_values:
            self.name_list.remove(self.table_values[0])
        self.setWindowTitle("Add Ignore Region")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.nameLabel = QLabel("<b>Name</b>")
        self.nameLabel.setToolTip("")
        self.name = QLineEdit()
        self.name.setToolTip("")

        self.lowerLimitLabel = QLabel("<b>Lower Limit (ppm)</b>")
        self.lowerLimitLabel.setToolTip("")
        self.lowerLimit = QDoubleSpinBox()
        self.lowerLimit.setRange(-5.000, 12.000)
        self.lowerLimit.setSingleStep(0.100)
        self.lowerLimit.setDecimals(3)

        self.upperLimitLabel = QLabel("<b>Upper Limit (ppm)</b>")
        self.upperLimitLabel.setToolTip("")
        self.upperLimit = QDoubleSpinBox()
        self.upperLimit.setRange(-5.000, 12.000)
        self.upperLimit.setSingleStep(0.100)
        self.upperLimit.setDecimals(3)

        self.groupLabel = QLabel("<b>Group Specificity</b>")
        self.groupLabel.setToolTip("")
        self.group = QComboBox()
        self.group_list.insert(0, 'ALL')
        self.group.addItems(self.group_list)

        if self.table_values:
            self.name.setText(self.table_values[0])
            self.lowerLimit.setValue(float(self.table_values[1]))
            self.upperLimit.setValue(float(self.table_values[2]))
            self.group.setCurrentIndex(self.group_list.index(self.table_values[3]))
        else:
            self.name.setPlaceholderText("Unique Name")
            self.lowerLimit.setValue(4.500)
            self.upperLimit.setValue(5.000)
            self.group.setCurrentIndex(self.group_list.index('ALL'))

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.okButton = QPushButton("Accept")
        self.okButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        self.okButton.setDefault(True)

    def layoutWidgets(self):
        layout = QGridLayout(self)
        layout.addWidget(self.nameLabel, 0, 0)
        layout.addWidget(self.lowerLimitLabel, 0, 1)
        layout.addWidget(self.upperLimitLabel, 0, 2)
        layout.addWidget(self.groupLabel, 0, 3)
        layout.addWidget(self.name, 1, 0)
        layout.addWidget(self.lowerLimit, 1, 1)
        layout.addWidget(self.upperLimit, 1, 2)
        layout.addWidget(self.group, 1, 3)
        layout.addWidget(self.cancelButton, 2, 1)
        layout.addWidget(self.okButton, 2, 2)

    def createConnections(self):
        self.cancelButton.clicked.connect(self.reject)
        self.okButton.clicked.connect(self.acceptRegion)

    def acceptRegion(self):
        if self.checkTableValues():
            QDialog.accept(self)

    def checkTableValues(self):
        if not self.name.text():
            error = QMessageBox(self)
            error.setWindowTitle("Region Needs a Name!")
            error.setText("Please enter a unique name for the region.")
            error.exec_()
            return(False)
        if self.name.text() in self.name_list:
            error = QMessageBox(self)
            error.setWindowTitle("Duplicate Name!")
            error.setText('"%s" is a duplicate name of an already existing region.\n\nNames MUST be unique.'
                          % self.name.text())
            error.exec_()
            return(False)
        if self.lowerLimit.value() >= self.upperLimit.value():
            error = QMessageBox(self)
            error.setWindowTitle("Inappropriate Limits!")
            error.setText("The lower limit must have a lower ppm than the upper limit.")
            error.exec_()
            return(False)
        else:
            self.setTableValues()
            return(True)

    def setTableValues(self):
        self.table_values = []
        self.table_values.append(self.name.text())
        self.table_values.append(float(self.lowerLimit.value()))
        self.table_values.append(float(self.upperLimit.value()))
        self.table_values.append(self.group.currentText())