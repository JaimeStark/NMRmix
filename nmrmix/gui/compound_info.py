#!/usr/bin/env python3
# encoding: utf-8
"""
compound_info.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import sys
import numpy as np
if sys.version > '3':
    import csv
else:
    try:
        import unicodecsv as csv
    except:
        from core import unicodecsv as csv

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2

class Window(QDialog):
    def __init__(self, params_object, compound_object, library_object, editable=False, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.compound = compound_object
        self.library = library_object
        self.editable = editable
        self.modified = False
        self.setWindowTitle("NMRmix: Information for Compound %s" % self.compound.id)
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.drawData()
        self.setTable()

    def createWidgets(self):
        self.compoundTabs = QTabWidget()
        self.compoundTabs.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.compoundTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')
        self.initInfo()
        self.initSpectrum()
        self.initPeaklistTable()

    def initInfo(self):
        # Compound Info Tab
        self.compoundtab1 = QWidget()
        self.compoundtab1.setStyleSheet("QWidget{background-color: white;}")
        self.idLabel = QLabel("<h2><font color='red'>%s</font></h2>" % self.compound.id)
        self.idLabel.setAlignment(Qt.AlignCenter)
        self.nameLabel = QLabel("<b>Name:</b> %s" % self.compound.name)
        self.groupLabel = QLabel("<b>Group:</b> %s" % self.compound.group)
        self.bmrbLabel = QLabel("<b>BMRB ID:</b> %s" % self.compound.bmrb_id)
        self.bmrbLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.bmrbLabel.setOpenExternalLinks(True)
        self.hmdbLabel = QLabel("<b>HMDB ID:</b> %s" % self.compound.hmdb_id)
        self.hmdbLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.hmdbLabel.setOpenExternalLinks(True)
        self.pubchemLabel = QLabel("<b>PubChem CID:</b> <a href='https://pubchem.ncbi.nlm.nih.gov/compound/%s'>%s</a>"
                                   % (self.compound.pubchem_id, self.compound.pubchem_id))
        self.pubchemLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.pubchemLabel.setOpenExternalLinks(True)
        self.keggLabel = QLabel("<b>KEGG ID:</b> <a href='http://www.genome.jp/dbget-bin/www_bget?cpd:%s'>%s</a>"
                                % (self.compound.kegg_id, self.compound.kegg_id))
        self.keggLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.keggLabel.setOpenExternalLinks(True)
        self.structureLabel = QLabel("<b>Structure: </b>")
        self.structure = QLabel()


        if self.compound.smiles:
            self.smilesLabel = QLabel("<b>SMILES:</b> %s" % self.compound.smiles)
            try:
                self.compound.set2DStructure()
                molformula = ""
                for count, i in enumerate(self.compound.molformula):
                    try:
                        if count > 0:
                            if self.compound.molformula[count-1] == "-" or self.compound.molformula[count-1] == "+":
                                j = "<sup>%d</sup>" % int(i)
                            else:
                                j = "<sub>%d</sub>" % int(i)
                        else:
                            j = i
                    except:
                        if i == "-" or i == "+":
                            j = "<sup>%s</sup>" % i
                        else:
                            j = i
                    molformula += j
                if self.compound.molwt and self.compound.molformula:
                    self.molformulaLabel = QLabel("<b>Mol. Formula:</b> %s" % molformula)
                    self.molwtLabel = QLabel("<b>Mol. Weight:</b> %0.3f" % self.compound.molwt)
                else:
                    self.molformulaLabel = QLabel("<b>Mol. Formula:</b> Unknown")
                    self.molwtLabel = QLabel("<b>Mol. Weight:</b> Unknown")
                if self.compound.structure_image:
                    self.pixmap = QPixmap.fromImage(self.compound.structure_qt)
                    self.structure.setText("")
                    self.structure.setPixmap(self.pixmap)
                    self.structure.setAlignment(Qt.AlignCenter)
                else:
                    self.structure.setText("No Structure Available")
                    self.structure.setAlignment(Qt.AlignCenter)
            except:
                self.molformulaLabel = QLabel("<b>Mol. Formula:</b> Unknown")
                self.molwtLabel = QLabel("<b>Mol. Weight:</b> Unknown")
                self.structure.setText("No Structure Available")
                self.structure.setAlignment(Qt.AlignCenter)

        else:
            self.smilesLabel = QLabel("<b>SMILES:</b> Unknown")
            self.molformulaLabel = QLabel("<b>Mol. Formula:</b> Unknown")
            self.molwtLabel = QLabel("<b>Mol. Weight:</b> Unknown")
            self.structure.setText("No Structure Available")
            self.structure.setAlignment(Qt.AlignCenter)

        self.editinfoButton = QPushButton('Edit Compound Info')
        self.editinfoButton.setToolTip("Opens a window to edit compound information") # TODO: Set tooltip
        self.restoreinfoButton = QPushButton('Restore Compound Info')
        self.restoreinfoButton.setToolTip("Resets compound information to original imported values") # TODO: Set tooltip
        self.savestructureButton = QPushButton('Save Structure Image')
        self.savestructureButton.setToolTip("Tooltip") # TODO: Set tooltip


    def initSpectrum(self):
        # Compound Spectrum Tab
        matplotlib.projections.register_projection(My_Axes)
        self.scale = 1.05
        self.show_ignored = True
        self.show_ignored_peaks = True
        self.compoundtab2 = QWidget()
        self.compoundtab2.setStyleSheet("QWidget{background-color: white;}")
        self.fig = plt.gcf()
        self.fig.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.canvas.setMinimumHeight(100)
        self.canvas.setMinimumWidth(100)
        self.mpl_toolbar = NavigationToolbar2(self.canvas, self)
        self.mpl_toolbar.hide()
        self.mpl_toolbar.pan()
        self.canvas.mpl_connect('scroll_event', self.zooming)
        ins = "Left-click+drag to pan x-axis / Right-click+drag to zoom x-axis / Scroll-wheel to change intensity scale"
        self.instructionLabel = QLabel(ins)
        self.instructionLabel.setStyleSheet('QLabel{qproperty-alignment: AlignCenter; font-size: 10px;}')
        self.showignoredregionsCheckBox = QCheckBox("Show Ignored Regions")
        self.showignoredregionsCheckBox.setToolTip("Shows the ranges set by the solvent/buffer ignore regions, if any.")
        self.showignoredregionsCheckBox.setLayoutDirection(Qt.RightToLeft)
        self.showignoredregionsCheckBox.setChecked(True)
        self.showignoredpeaksCheckBox = QCheckBox("Show Ignored Peaks")
        self.showignoredpeaksCheckBox.setToolTip("Shows any compound peaks that are in the solvent/buffer ignore regions, if any.\n"
                                                 "These peaks are ignored and are not evaluated during mixing.")
        self.showignoredpeaksCheckBox.setLayoutDirection(Qt.RightToLeft)
        self.showignoredpeaksCheckBox.setChecked(True)
        self.resetviewButton = QPushButton("Reset View")
        self.resetviewButton.setToolTip("Resets the spectrum to the default view.")
        self.savespectrumButton = QPushButton("Save Spectrum")
        self.savespectrumButton.setToolTip("Saves the image in the spectrum window.")

    def initPeaklistTable(self):
        # Compound Peaklist Tab
        self.compoundtab3 = QWidget()
        self.compoundtab3.setStyleSheet("QWidget{background-color: white;}")
        self.peakTable = QTableWidget(0, 4, self)
        # self.peakTable.setMinimumWidth(400)
        self.peakTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.peakTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.peakTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.peakTable.setSortingEnabled(True)
        self.peakTable.sortByColumn(1, Qt.AscendingOrder)
        self.peakTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.peakTable.setColumnWidth(0, 100)
        self.peakTable.setColumnWidth(1, 200)
        self.peakTable.setColumnWidth(2, 150)
        self.peakTable.setColumnWidth(3, 100)
        self.peakTable.horizontalHeader().setStretchLastSection(True)
        self.tableheader = ['Status', 'Chemical Shift', 'Intensity', 'Width']
        self.peakTable.setHorizontalHeaderLabels(self.tableheader)
        self.peakTable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.peakTable.verticalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.addButton = QPushButton("Add")
        self.addButton.setToolTip("Opens a window to add a new peak to the table")

        self.editButton = QPushButton("Edit")
        self.editButton.setToolTip("Opens a window to edit the currently selected peak.")

        self.removeButton = QPushButton("Remove")
        self.removeButton.setToolTip("Inactivates the currently selected peak.")

        self.restorepeaklistButton = QPushButton("Restore")
        self.restorepeaklistButton.setToolTip("Restores the original peak list.")

        self.savepeaksButton = QPushButton("Save")
        self.savepeaksButton.setToolTip("Saves the current peak list as a custom peak list file.\n"
                                        "This file can be used as the peak list for future library imports.")
        if not self.editable:
            self.removeButton.hide()
            self.restorepeaklistButton.hide()
            self.savepeaksButton.hide()
            self.editButton.hide()
            self.addButton.hide()

        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight:bold;}")
        self.closeButton.setFixedWidth(200)

    def layoutWidgets(self):
        winLayout = QVBoxLayout(self)

        infoLayout = QVBoxLayout(self.compoundtab1)
        infoLayout.addWidget(self.idLabel)
        infoLayout.addWidget(self.nameLabel)
        infoLayout.addWidget(self.groupLabel)
        infoLayout.addWidget(self.bmrbLabel)
        infoLayout.addWidget(self.hmdbLabel)
        infoLayout.addWidget(self.pubchemLabel)
        infoLayout.addWidget(self.keggLabel)
        infoLayout.addWidget(self.smilesLabel)
        infoLayout.addWidget(self.molformulaLabel)
        infoLayout.addWidget(self.molwtLabel)
        infoLayout.addWidget(self.structureLabel)
        infoLayout.addItem(QSpacerItem(400, 20, QSizePolicy.Maximum, QSizePolicy.Maximum))
        infoLayout.addWidget(self.structure)
        infoLayout.addItem(QSpacerItem(400, 20, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        infobuttonLayout = QHBoxLayout()
        infobuttonLayout.addWidget(self.editinfoButton)
        infobuttonLayout.addWidget(self.restoreinfoButton)
        infobuttonLayout.addWidget(self.savestructureButton)
        infoLayout.addLayout(infobuttonLayout)
        self.compoundtab1.setLayout(infoLayout)
        self.compoundTabs.addTab(self.compoundtab1, "Compound Info")

        spectraLayout = QVBoxLayout(self.compoundtab2)
        spectraLayout.addWidget(self.canvas)
        spectraLayout.addWidget(self.instructionLabel)
        spectraCheckBoxLayout = QHBoxLayout()
        spectraCheckBoxLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
        spectraCheckBoxLayout.addWidget(self.showignoredregionsCheckBox)
        spectraCheckBoxLayout.addItem(QSpacerItem(15, 0, QSizePolicy.Maximum))
        spectraCheckBoxLayout.addWidget(self.showignoredpeaksCheckBox)
        spectraCheckBoxLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
        spectraLayout.addLayout(spectraCheckBoxLayout)
        spectraButtonLayout = QHBoxLayout()
        spectraButtonLayout.addWidget(self.resetviewButton)
        spectraButtonLayout.addWidget(self.savespectrumButton)
        spectraLayout.addLayout(spectraButtonLayout)
        self.compoundtab2.setLayout(spectraLayout)
        self.compoundTabs.addTab(self.compoundtab2, "Simulated Spectrum")

        tableLayout = QVBoxLayout()
        tableLayout.addWidget(self.peakTable)
        tablebuttonLayout = QHBoxLayout()
        tablebuttonLayout.addWidget(self.addButton)
        tablebuttonLayout.addWidget(self.editButton)
        tablebuttonLayout.addWidget(self.removeButton)
        tablebuttonLayout.addWidget(self.restorepeaklistButton)
        tablebuttonLayout.addWidget(self.savepeaksButton)
        tableLayout.addLayout(tablebuttonLayout)
        self.compoundtab3.setLayout(tableLayout)
        self.compoundTabs.addTab(self.compoundtab3, "Peaklist Table")

        winLayout.addWidget(self.compoundTabs)
        winLayout.addItem(QSpacerItem(0, 20, QSizePolicy.Maximum))
        winLayout.addWidget(self.closeButton)
        winLayout.setAlignment(self.closeButton, Qt.AlignCenter)

    def createConnections(self):
        self.editinfoButton.clicked.connect(self.editInfo)
        self.restoreinfoButton.clicked.connect(self.restoreInfo)
        self.savestructureButton.clicked.connect(self.saveStructure)

        self.showignoredregionsCheckBox.stateChanged.connect(self.handleIgnored)
        self.showignoredpeaksCheckBox.stateChanged.connect(self.handleIgnoredPeaks)
        self.resetviewButton.clicked.connect(self.resetSpectra)
        self.savespectrumButton.clicked.connect(self.saveSpectra)

        self.addButton.clicked.connect(self.addPeak)
        self.removeButton.clicked.connect(self.removePeak)
        self.editButton.clicked.connect(self.editPeak)
        self.restorepeaklistButton.clicked.connect(self.resetPeakList)
        self.savepeaksButton.clicked.connect(self.savePeakList)

        self.closeButton.clicked.connect(self.closeEvent)

    def editInfo(self):
        editinfo_win = InfoWindow(self.params, self.compound)
        if editinfo_win.exec_():
            self.modified = True
            self.updateInfo()

    def restoreInfo(self):
        self.compound.restoreOriginalDescriptors()
        self.modified = True
        self.updateInfo()

    def saveStructure(self):
        filename = "%s.png" % self.compound.id
        filepath = os.path.join(self.params.work_dir, filename)
        filestype = "static (*.png *.jpg *.svg)"
        fileObj = QFileDialog.getSaveFileName(self, "Save Structure Image", directory=filepath, filter=filestype)
        if fileObj[0]:
            self.compound.structure_image.save(fileObj[0])

    def handleIgnored(self):
        if self.showignoredregionsCheckBox.isChecked():
            self.show_ignored = True
            self.drawData()
        else:
            self.show_ignored = False
            self.drawData()

    def handleIgnoredPeaks(self):
        if self.showignoredpeaksCheckBox.isChecked():
            self.show_ignored_peaks = True
            self.drawData()
        else:
            self.show_ignored_peaks = False
            self.drawData()

    def resetSpectra(self):
        self.mpl_toolbar.home()
        self.drawData()

    def saveSpectra(self):
        filename = "%s.png" % self.compound.id
        filepath = os.path.join(self.params.work_dir, filename)
        filestype = "static (*.png *.jpg *.svg)"
        fileObj = QFileDialog.getSaveFileName(self, caption="Save Simulated Compound Spectrum", directory=filepath,
                                              filter=filestype)
        if fileObj[0]:
            self.fig.set_size_inches(12, 8)
            plt.savefig(fileObj[0], dpi=200)

    def addPeak(self):
        addpeak_win = PeakWindow(self.params, self.compound)
        if addpeak_win.exec_():
            self.compound.addPeak(tuple(addpeak_win.table_values))
            self.setTable()
            self.modified = True
            self.drawData()

    def editPeak(self):
        selected = self.peakTable.currentRow()
        # status = self.peakTable.item(selected, 0).text()
        chemshift = float(self.peakTable.item(selected, 1).text())
        intensity = float(self.peakTable.item(selected, 2).text())
        width = self.peakTable.item(selected, 3).text()
        if width != 'Default':
            curr_peak = (chemshift, intensity, float(width))
        else:
            curr_peak = (chemshift, intensity)
        editpeak_win = PeakWindow(self.params, self.compound, curr_peak)
        if editpeak_win.exec_():
            self.compound.editPeak(tuple(editpeak_win.table_values))
            self.setTable()
            self.modified = True
            self.drawData()

    def removePeak(self):
        try:
            selected = self.peakTable.currentRow()
            # status = self.peakTable.item(selected, 0).text()
            chemshift = float(self.peakTable.item(selected, 1).text())
            intensity = float(self.peakTable.item(selected, 2).text())
            width = self.peakTable.item(selected, 3).text()
            peak_list = self.compound.mix_peaklist + self.compound.ignored_peaklist
            if width != 'Default':
                curr_peak = (chemshift, intensity, float(width))
            else:
                curr_peak = (chemshift, intensity)
            min_diff = 9999999
            min_i = 9999999
            for i, peak in enumerate(peak_list):
                diff = abs(float(peak[1]) - float(curr_peak[1]))
                if diff < min_diff:
                    min_diff = diff
                    min_i = i
            matched_peak = peak_list[min_i]
            self.compound.removePeak(matched_peak)
            self.setTable()
            self.modified = True
            self.drawData()
        except Exception as e:
            # print(e)
            pass

    def resetPeakList(self):
        self.compound.resetPeakList()
        self.setTable()
        self.modified = True
        self.drawData()

    def savePeakList(self):
        filename = "%s_custom.csv" % self.compound.id
        filepath = os.path.join(self.params.peaklist_dir, filename)
        filestype = "static (*.csv)"
        fileObj = QFileDialog.getSaveFileName(self, caption="Save Custom Peak List", directory=filepath,
                                              filter=filestype)
        if fileObj[0]:
            filename = os.path.basename(fileObj[0])
            peak_list = self.compound.mix_peaklist + self.compound.ignored_peaklist
            with open(fileObj[0], 'w') as peaks_csv:
                writer = csv.writer(peaks_csv)
                header = ['ChemShift', 'Intensity', 'Width']
                writer.writerow(header)
                writer.writerows(peak_list)
            for i, row in enumerate(self.library.library_csv):
                if row[1] == self.compound.id:
                    self.library.library_csv[i][5] = filename
                    self.library.library_csv[i][6] = 'USER'

    def lorentzian(self, mu, hwhm, intensity):
        def f(x):
            numerator = hwhm ** 2
            denominator = pow((x - mu), 2) + (hwhm ** 2)
            total = intensity * (numerator / denominator)
            return(total)
        return(f)

    def drawPeakData(self, peaks, color="red", alpha=1.0):
        for peak in peaks:
            if len(peak) == 3:
                width = peak[2] * 3
                hwhm = peak[2] * self.params.peak_display_width
            else:
                width = self.params.peak_range * 3
                hwhm = self.params.peak_range * self.params.peak_display_width
            mean = peak[0]
            intensity = peak[1]
            shifts = (np.arange(mean-width, mean+width, 0.001))
            f = self.lorentzian(mean, hwhm, intensity)
            y = ([f(x) for x in shifts])
            self.ax.plot(shifts, y, color=color, linewidth=1, alpha=alpha)

    def drawIgnoredRegions(self, ignored_list):
        updated_ignored = list(set(ignored_list))
        for ignored in updated_ignored:
            ignored_width = abs(ignored[1] - ignored[0])
            ignored_center = (ignored[1] + ignored[0]) / 2
            self.ax.bar(ignored_center, 100, width=ignored_width, color='gray', align='center', edgecolor='gray',
                        linewidth=1, alpha=0.6, picker=True)
            self.ax.bar(ignored_center, -100, width=ignored_width, color='gray', align='center', edgecolor='gray',
                        linewidth=1, alpha=0.6, picker=True)


    def drawData(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection="My_Axes")
        ignored_regions = []
        pos_peaks = self.compound.mix_peaklist
        ignored_peaks = self.compound.ignored_peaklist
        ignored_regions += list(self.compound.ignored_regions.values())
        self.drawPeakData(pos_peaks)
        if self.show_ignored_peaks:
            self.drawPeakData(ignored_peaks, color='gray', alpha=0.8)
        if self.show_ignored:
            self.drawIgnoredRegions(ignored_regions)
        self.ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        self.ax.spines['bottom'].set_position('zero')
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.set_xlim(self.params.shift_range[self.params.nuclei])
        self.ax.set_ylim([0, 1])
        self.ax.set_xlabel('Chemical Shift (ppm)', fontweight='bold')
        self.ax.set_ylabel('Intensity (Normalized)', fontweight='bold')
        self.fig.tight_layout()
        self.canvas.draw()

    def clearTable(self):
        """Deletes all rows in the table."""
        while self.peakTable.rowCount() > 0:
            self.peakTable.removeRow(0)

    def setTable(self):
        self.peakTable.setSortingEnabled(False)
        self.clearTable()
        tablesize = len(self.compound.mix_peaklist) + len(self.compound.ignored_peaklist)
        self.peakTable.setRowCount(tablesize)
        for row, peak in enumerate(self.compound.mix_peaklist):
            self.peakTable.setRowHeight(row, 50)
            active = QTableWidgetItem("ACTIVE")
            active.setTextAlignment(Qt.AlignCenter)
            self.peakTable.setItem(row, 0, active)
            chemshift = QTableWidgetItem()
            chemshift.setTextAlignment(Qt.AlignCenter)
            chemshift.setData(Qt.DisplayRole, "%0.3f" % peak[0])
            self.peakTable.setItem(row, 1, chemshift)
            intensity = QTableWidgetItem()
            intensity.setTextAlignment(Qt.AlignCenter)
            intensity.setData(Qt.DisplayRole, "%0.3f" % peak[1])
            self.peakTable.setItem(row, 2, intensity)
            width = QTableWidgetItem()
            width.setTextAlignment(Qt.AlignCenter)
            if len(peak) == 3:
                width.setData(Qt.DisplayRole, "%0.3f" % peak[2])
            else:
                width.setText('Default')
            self.peakTable.setItem(row, 3, width)
        if len(self.compound.mix_peaklist) > 0:
            next_row = len(self.compound.mix_peaklist)
        else:
            next_row = 0
        for row, peak in enumerate(self.compound.ignored_peaklist, start=next_row):
            self.peakTable.setRowHeight(row, 40)
            active = QTableWidgetItem("IGNORED")
            active.setTextAlignment(Qt.AlignCenter)
            self.peakTable.setItem(row, 0, active)
            chemshift = QTableWidgetItem()
            chemshift.setTextAlignment(Qt.AlignCenter)
            chemshift.setData(Qt.DisplayRole, "%0.3f" % peak[0])
            self.peakTable.setItem(row, 1, chemshift)
            intensity = QTableWidgetItem()
            intensity.setTextAlignment(Qt.AlignCenter)
            intensity.setData(Qt.DisplayRole, "%0.3f" % peak[1])
            self.peakTable.setItem(row, 2, intensity)
            width = QTableWidgetItem()
            width.setTextAlignment(Qt.AlignCenter)
            if len(peak) == 3:
                width.setData(Qt.DisplayRole, "%0.3f" % peak[2])
            else:
                width.setText('Default')
            self.peakTable.setItem(row, 3, width)
        if len(self.compound.mix_peaklist)+len(self.compound.ignored_peaklist) > 0:
            next_row = len(self.compound.mix_peaklist)+len(self.compound.ignored_peaklist)
        else:
            next_row = 0
        for row, peak in enumerate(self.compound.removed_peaklist, start=next_row):
            self.peakTable.setRowHeight(row, 40)
            active = QTableWidgetItem("REMOVED")
            active.setTextAlignment(Qt.AlignCenter)
            self.peakTable.setItem(row, 0, active)
            chemshift = QTableWidgetItem()
            chemshift.setTextAlignment(Qt.AlignCenter)
            chemshift.setData(Qt.DisplayRole, float("%0.3f" % peak[0]))
            self.peakTable.setItem(row, 1, chemshift)
            intensity = QTableWidgetItem()
            intensity.setTextAlignment(Qt.AlignCenter)
            intensity.setData(Qt.DisplayRole, float("%0.3f" % peak[1]))
            self.peakTable.setItem(row, 2, intensity)
            if len(peak) == 3:
                width = QTableWidgetItem()
                width.setTextAlignment(Qt.AlignCenter)
                width.setData(Qt.DisplayRole, float("%0.3f" % peak[2]))
                self.peakTable.setItem(row, 3, width)
        self.peakTable.setSortingEnabled(True)
        self.peakTable.selectRow(0)

    def updateInfo(self):
        self.nameLabel.setText("<b>Name:</b> %s" % self.compound.name)
        self.groupLabel.setText("<b>Group:</b> %s" % self.compound.group)
        self.pubchemLabel.setText("<b>PubChem CID:</b> <a href='https://pubchem.ncbi.nlm.nih.gov/compound/%s'>%s</a>"
                                   % (self.compound.pubchem_id, self.compound.pubchem_id))
        self.pubchemLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.pubchemLabel.setOpenExternalLinks(True)
        self.keggLabel.setText("<b>KEGG ID:</b> <a href='http://www.genome.jp/dbget-bin/www_bget?cpd:%s'>%s</a>"
                                % (self.compound.kegg_id, self.compound.kegg_id))
        self.keggLabel.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.keggLabel.setOpenExternalLinks(True)

        if self.compound.smiles:
            self.smilesLabel.setText("<b>SMILES:</b> %s" % self.compound.smiles)
            try:
                self.compound.set2DStructure()
                molformula = ""
                for count, i in enumerate(self.compound.molformula):
                    try:
                        if count > 0:
                            if self.compound.molformula[count-1] == "-" or self.compound.molformula[count-1] == "+":
                                j = "<sup>%d</sup>" % int(i)
                            else:
                                j = "<sub>%d</sub>" % int(i)
                        else:
                            j = i
                    except:
                        if i == "-" or i == "+":
                            j = "<sup>%s</sup>" % i
                        else:
                            j = i
                    molformula += j
                self.molformulaLabel.setText("<b>Mol. Formula:</b> %s" % molformula)
                self.molwtLabel.setText("<b>Mol. Weight:</b> %0.3f" % self.compound.molwt)
                if self.compound.structure_image:
                    self.pixmap = QPixmap.fromImage(self.compound.structure_qt)
                    self.structure.setText("")
                    self.structure.setPixmap(self.pixmap)
                    self.structure.setAlignment(Qt.AlignCenter)
                else:
                    self.structure.setText("No Structure Available")
                    self.structure.setAlignment(Qt.AlignCenter)
            except:
                self.molformulaLabel.setText("<b>Mol. Formula:</b> Unknown")
                self.molwtLabel.setText("<b>Mol. Weight:</b> Unknown")
        else:
            self.smilesLabel.setText("<b>SMILES:</b> Unknown")
            self.molformulaLabel.setText("<b>Mol. Formula:</b> Unknown")
            self.molwtLabel.setText("<b>Mol. Weight:</b> Unknown")
            self.structure.setText("No Structure Available")
            self.structure.setAlignment(Qt.AlignCenter)

        for i, row in enumerate(self.library.library_csv):
                if row[1] == self.compound.id:
                    self.library.library_csv[i][2] = self.compound.name
                    self.library.library_csv[i][3] = self.compound.bmrb_id
                    self.library.library_csv[i][4] = self.compound.hmdb_id
                    self.library.library_csv[i][8] = self.compound.pubchem_id
                    self.library.library_csv[i][9] = self.compound.kegg_id
                    self.library.library_csv[i][10] = self.compound.smiles


    def zooming(self, event):
        cur_ylim = self.ax.get_ylim()
        cur_yrange = (cur_ylim[1] - cur_ylim[0])
        if event.button == 'up':
            scale_factor = self.scale
        elif event.button == 'down':
            scale_factor = 1/self.scale
        else:
            scale_factor = 1

        self.ax.set_ylim([0, (cur_yrange*scale_factor)])
        self.canvas.draw()

    def acceptChanges(self):
        pass

    def closeEvent(self, event=False):
        self.fig.clear()
        QDialog.accept(self)


class My_Axes(matplotlib.axes.Axes):
    name = "My_Axes"
    def drag_pan(self, button, key, x, y):
        matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y)


class PeakWindow(QDialog):
    def __init__(self, params_object, compound_object, table_values=[], parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.compound = compound_object
        self.peak_list = self.compound.mix_peaklist + self.compound.ignored_peaklist
        self.table_values = table_values
        if table_values:
            min_diff = 9999999
            min_i = 9999999
            for i, peak in enumerate(self.peak_list):
                diff = abs(float(peak[1]) - float(self.table_values[1]))
                if diff < min_diff:
                    min_diff = diff
                    min_i = i
            self.matched_peak = self.peak_list[min_i]
            self.peak_list.remove(self.matched_peak)
            self.setWindowTitle("Edit Peak")
        else:
            self.matched_peak = None
            self.setWindowTitle("Add New Peak")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        # self.activeLabel = QLabel("<b>Active</b>")
        # self.activeLabel.setToolTip("Tooltip")

        self.peakLabel = QLabel("<b>Chemical shift (ppm)</b>")
        self.peakLabel.setToolTip("Tooltip")
        self.peakSpinBox = QDoubleSpinBox()
        self.peakSpinBox.setRange(-5.000, 12.000)
        self.peakSpinBox.setSingleStep(0.100)
        self.peakSpinBox.setDecimals(3)

        self.intensityLabel = QLabel("<b>Intensity</b>")
        self.intensityLabel.setToolTip("Tooltip")
        self.intensitySpinBox = QDoubleSpinBox()
        self.intensitySpinBox.setRange(0.00001, 100)
        self.intensitySpinBox.setSingleStep(0.100)
        self.intensitySpinBox.setDecimals(3)

        self.widthLabel = QLabel("<b>Custom Overlap Range (ppm)</b>")
        self.widthLabel.setToolTip("Enables the use of a custom overlap range for this peak instead of the default.")
        self.widthCheckBox = QCheckBox("Use Custom Peak Width")
        self.widthCheckBox.setToolTip("Enables the use of a custom overlap range for this peak instead of the default.")
        self.widthSpinBox = QDoubleSpinBox()
        self.widthSpinBox.setRange(0.001, 5.000)
        self.widthSpinBox.setSingleStep(0.005)
        self.widthSpinBox.setDecimals(3)
        self.widthSpinBox.setEnabled(False)

        if self.table_values:
            self.peakSpinBox.setValue(float(self.table_values[0]))
            self.intensitySpinBox.setValue(float(self.table_values[1]))
            if len(self.table_values) >= 3:
                self.widthCheckBox.setChecked(True)
                self.widthSpinBox.setValue(float(self.table_values[2]))
                self.widthSpinBox.setEnabled(True)
            else:
                self.widthCheckBox.setChecked(False)
                self.widthSpinBox.setValue(self.params.peak_range)
                self.widthSpinBox.setEnabled(False)
        else:
            self.peakSpinBox.setValue(4.700)
            self.intensitySpinBox.setValue(1.000)
            self.widthSpinBox.setValue(self.params.peak_range)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.okButton = QPushButton("Accept")
        self.okButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")

    def layoutWidgets(self):
        layout = QGridLayout(self)
        layout.addWidget(self.peakLabel, 0, 0)
        layout.addWidget(self.intensityLabel, 0, 1)
        layout.addWidget(self.widthLabel, 0, 2, 1, 2)
        layout.addWidget(self.peakSpinBox, 1, 0)
        layout.addWidget(self.intensitySpinBox, 1, 1)
        layout.addWidget(self.widthCheckBox, 1, 2)
        layout.addWidget(self.widthSpinBox, 1, 3)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.okButton)
        layout.addLayout(buttonLayout, 2, 0, 1, 3)

    def createConnections(self):
        self.cancelButton.clicked.connect(self.reject)
        self.okButton.clicked.connect(self.acceptRegion)
        self.widthCheckBox.stateChanged.connect(self.customWidth)

    def customWidth(self):
        if self.widthCheckBox.isChecked():
            self.widthSpinBox.setEnabled(True)
        else:
            self.widthSpinBox.setEnabled(False)

    def acceptRegion(self):
        if self.checkTableValues():
            if self.matched_peak:
                if self.matched_peak in self.compound.mix_peaklist:
                    self.compound.mix_peaklist.remove(self.matched_peak)
                elif self.matched_peak in self.compound.ignored_peaklist:
                    self.compound.ignored_peaklist.remove(self.matched_peak)
                elif self.matched_peak in self.compound.removed_peaklist:
                    self.compound.removed_peaklist.remove(self.matched_peak)
            QDialog.accept(self)

    def checkTableValues(self):
        for peak in self.peak_list:
            if self.peakSpinBox.value() in peak:
                error = QMessageBox(self)
                error.setWindowTitle("Duplicate Peak!")
                error.setText("A peak at %0.3f already exists. Peaks must be unique."
                              % self.peakSpinBox.value())
                error.exec_()
                return(False)
        else:
            self.setTableValues()
            return(True)

    def setTableValues(self):
        self.table_values = []
        self.table_values.append(float(self.peakSpinBox.value()))
        self.table_values.append(float(self.intensitySpinBox.value()))
        if self.widthCheckBox.isChecked():
            self.table_values.append(float(self.widthSpinBox.value()))

class InfoWindow(QDialog):
    def __init__(self, params_object, compound_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.compound = compound_object
        self.setWindowTitle("Edit Compound Information")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.nameLabel = QLabel("<b>Name:</b>")
        self.nameEdit = QLineEdit(self.compound.name)
        # self.groupLabel = QLabel("<b>Group:</b>")
        # self.groupEdit = QLineEdit(self.compound.group)
        self.bmrbLabel = QLabel("<b>BMRB ID:</b>")
        self.bmrbEdit = QLineEdit(self.compound.bmrb_id)
        self.hmdbLabel = QLabel("<b>HMDB ID:</b>")
        self.hmdbEdit = QLineEdit(self.compound.hmdb_id)
        self.pubchemLabel = QLabel("<b>PubChem CID:</b>")
        self.pubchemEdit = QLineEdit(self.compound.pubchem_id)
        self.keggLabel = QLabel("<b>KEGG ID:</b>")
        self.keggEdit = QLineEdit(self.compound.kegg_id)
        self.smilesLabel = QLabel("<b>SMILES:</b>")
        self.smilesEdit = QLineEdit(self.compound.smiles)
        self.cancelButton = QPushButton("Cancel")
        self.acceptButton = QPushButton("Accept")


    def layoutWidgets(self):
        winLayout = QFormLayout(self)
        winLayout.addRow(self.nameLabel, self.nameEdit)
        # winLayout.addRow(self.groupLabel, self.groupEdit)
        winLayout.addRow(self.bmrbLabel, self.bmrbEdit)
        winLayout.addRow(self.hmdbLabel, self.hmdbEdit)
        winLayout.addRow(self.pubchemLabel, self.pubchemEdit)
        winLayout.addRow(self.keggLabel, self.keggEdit)
        winLayout.addRow(self.smilesLabel, self.smilesEdit)
        winLayout.addRow(self.cancelButton, self.acceptButton)

    def createConnections(self):
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.acceptChanges)

    def acceptChanges(self):
        if self.checkChanges():
            self.accept()
        else:
            # TODO: Add message for failure
            self.reject()

    def checkChanges(self):
        try:
            self.compound.editName(self.nameEdit.text())
            # self.compound.editGroup(self.groupEdit.text())
            self.compound.editBMRB(self.bmrbEdit.text())
            self.compound.editHMDB(self.hmdbEdit.text())
            self.compound.editPubChem(self.pubchemEdit.text())
            self.compound.editKEGG(self.keggEdit.text())
            self.compound.editSMILES(self.smilesEdit.text())
            return True
        except Exception as e:
            print("Failed", e)
            return False