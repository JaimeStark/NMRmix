#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
library_import.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys

from core import library
from gui import peak_info, peak_import


class MainWindow(QWidget):
    def __init__(self, params_object, parent=None):
        QWidget.__init__(self)
        self.params = params_object
        self.library = library.Library(self.params)
        self.setWindowTitle("NMRmix: Library Import")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        """Sets up the widgets and widget parameters for this window."""
        # Default Directories Widgets and Parameters
        self.dirwidget = QWidget()
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
        self.nucleiLabel = QLabel("<b>Nuclei</b>")
        self.nucleiComboBox = QComboBox()
        self.nucleiComboBox.addItems(["1H", "19F", "13C"])
        self.nucleiComboBox.setMinimumWidth(30)

        # Table Widget and Parameters
        self.tblwidget = QWidget()
        self.table = QTableWidget(0, 11, self)
        self.combolist = ['BMRB_ID', 'HMDB_ID','TOPSPIN', 'VNMR', 'MNOVA', 'ACD', 'NMRSTAR', 'HMDB', 'USER']
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.AscendingOrder)
        self.header = self.table.horizontalHeader()
        self.header.setStretchLastSection(True)
        self.headerlabels = ['Active', 'Identifier', 'Compound Name', 'BMRB ID', 'HMDB ID', 'Peaklist File',
                             'Peaklist Format', 'Group', 'PubChem CID', 'KEGG ID', 'SMILES']
        self.table.setHorizontalHeaderLabels(self.headerlabels)
        self.header.setStyleSheet("QHeaderView {font-weight: bold;}")

        self.table.setColumnWidth(0, 65)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 125)
        self.table.setColumnWidth(7, 70)
        self.table.setColumnWidth(8, 115)
        self.table.setColumnWidth(9, 80)
        self.table.setColumnWidth(10, 80)


        self.table.verticalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.table.horizontalHeaderItem(0).setToolTip('Checked items will be used to generate mixures.\n'
                                                      'Unchecked items will not be included in mixtures.')
        self.table.horizontalHeaderItem(1).setToolTip('A unique identifier for the compound.\nShould be kept short.\n'
                                                      'Example: 000001 or P1A1\nREQUIRED')
        self.table.horizontalHeaderItem(2).setToolTip('The name of the compound.\nREQUIRED')
        self.table.horizontalHeaderItem(3).setToolTip('The BMRB ID for the compound.\n'
                                                      'Used to download peak lists from the BMRB website.\n'
                                                      'Example: bmse000001\nOPTIONAL')
        self.table.horizontalHeaderItem(4).setToolTip('THE HMDB ID for the compound.\n'
                                                      'Used to download peak lists from the HMDB website.\n'
                                                      'Example: hmdb00001\n'
                                                      'OPTIONAL')
        self.table.horizontalHeaderItem(5).setToolTip('The filename of the local peak list for this compound.\n'
                                                      'REQUIRED if no BMRB or HMDB IDs')
        self.table.horizontalHeaderItem(6).setToolTip('Selects the format of the peak list file.\n'
                                                      'Set to the appropriate format used for peak list files.\n'
                                                      'Set to BMRB ID or HMDB ID to download from those sites.\n'
                                                      'See documentation for format of USER files.')
        self.table.horizontalHeaderItem(7).setToolTip('Sets the compound to belong to a group.\n'
                                                      'Typically, the dissolving solvent is used here.\n'
                                                       'OPTIONAL')
        self.table.horizontalHeaderItem(8).setToolTip('The Pubchem Chemical ID for the compound.\n'
                                                      'OPTIONAL')
        self.table.horizontalHeaderItem(9).setToolTip('The KEGG Compound ID for the compound.\n'
                                                      'OPTIONAL')
        self.table.horizontalHeaderItem(10).setToolTip('The SMILES string for the compound.\n'
                                                      'OPTIONAL')

        self.table.selectRow(0)

        # Table Buttons and Parameters
        self.tblbtnwidget = QWidget()
        self.tblbtnAdd = QPushButton("Add Compound")
        self.tblbtnAdd.setToolTip('Add a new empty row at the end to manually enter a new compound.\n'
                                  'Remember, the Identifier must be unique.')
        self.tblbtnAdd.setStyleSheet("QPushButton{color: blue;}")
        self.tblbtnRemove = QPushButton("Delete Compound")
        self.tblbtnRemove.setToolTip('Remove the selected row from the table.')
        self.tblbtnRemove.setStyleSheet("QPushButton{color: orange;}")
        self.tblbtnClear = QPushButton("Delete All")
        self.tblbtnClear.setToolTip('Removes all items from the table.')
        self.tblbtnClear.setStyleSheet("QPushButton{color: red;}")
        self.tblbtnImport = QPushButton("Open Library")
        self.tblbtnImport.setToolTip('Opens a dialog to select a library CSV file to import and populate the table.\n'
                                   'Automatically deletes all previous items in the table.')
        self.tblbtnImport.setStyleSheet("QPushButton{color: purple;}")
        self.btnwidget = QWidget()

        # Import Button and Parameters
        self.quitBtn = QPushButton("Quit NMRmix")
        self.quitBtn.setToolTip("Quits the NMRmix program.")
        self.quitBtn.setStyleSheet("QPushButton{font-size:20px; color: red; font-weight: bold;}")
        self.quitBtn.setFixedHeight(50)
        self.quitBtn.setFixedWidth(350)
        self.importBtn = QPushButton("Continue To Import Peak Lists")
        self.importBtn.setToolTip('Begins importing the peak lists for all ACTIVE compounds in the table.\n'
                                  'A new window will show the progress.')
        self.importBtn.setStyleSheet("QPushButton{font-size:20px; color: green; font-weight: bold;}")
        self.importBtn.setFixedHeight(50)
        self.importBtn.setFixedWidth(350)

    def layoutWidgets(self):
        """Sets up the layout information for this window."""
        winlayout = QVBoxLayout(self)
        winlayout.addWidget(self.dirwidget)
        winlayout.addWidget(self.tblwidget)
        winlayout.addWidget(self.btnwidget)
        dirlayout = QGridLayout(self.dirwidget)
        dirlayout.setSpacing(10)
        dirlayout.addWidget(self.wdirLabel, 0, 0)
        dirlayout.addWidget(self.wdirLine, 1, 0)
        dirlayout.addWidget(self.wdirButton, 1, 1)
        dirlayout.addItem(QSpacerItem(30, 0, QSizePolicy.Maximum), 1, 2)
        dirlayout.addWidget(self.pdirLabel, 0, 3)
        dirlayout.addWidget(self.pdirLine, 1, 3)
        dirlayout.addWidget(self.pdirButton, 1, 4)
        dirlayout.addItem(QSpacerItem(30, 0, QSizePolicy.Maximum), 1, 5)
        dirlayout.addWidget(self.nucleiLabel, 0, 6)
        dirlayout.addWidget(self.nucleiComboBox, 1, 6)
        tblLayout = QVBoxLayout(self.tblwidget)
        tblbtnLayout = QHBoxLayout(self.tblbtnwidget)
        tblbtnLayout.addWidget(self.tblbtnImport)
        tblbtnLayout.addWidget(self.tblbtnAdd)
        tblbtnLayout.addWidget(self.tblbtnRemove)
        tblbtnLayout.addWidget(self.tblbtnClear)
        tblLayout.addWidget(self.table)
        tblLayout.addWidget(self.tblbtnwidget)
        btnlayout = QHBoxLayout(self.btnwidget)

        btnlayout.addWidget(self.quitBtn)
        btnlayout.addItem(QSpacerItem(15, 50, QSizePolicy.Maximum, QSizePolicy.Maximum))
        btnlayout.addWidget(self.importBtn)

    def createConnections(self):
        """Sets up the signals and slots connections for this window."""
        self.wdirButton.clicked.connect(self.setWorkingDir)
        self.pdirButton.clicked.connect(self.setPeakListDir)
        self.tblbtnImport.clicked.connect(self.importLibraryFile)
        self.tblbtnAdd.clicked.connect(self.addTableRow)
        self.tblbtnRemove.clicked.connect(self.removeTableRow)
        self.tblbtnClear.clicked.connect(self.clearTable)
        self.importBtn.clicked.connect(self.importPeakLists)
        self.quitBtn.clicked.connect(self.close)
        self.nucleiComboBox.currentTextChanged.connect(self.updateNuclei)

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

    def updateNuclei(self):
        nuclei = self.nucleiComboBox.currentText()
        self.params.setNuclei(nuclei)
        print(self.params.nuclei)

    def importLibraryFile(self):
        """Opens a file dialog to select the library.csv file to import, and then populates the table widget with
        the data."""
        dir = self.params.work_dir
        fileObj = QFileDialog.getOpenFileName(self, "Open Compound Library CSV", directory=dir,
                                                        filter="CSV Files: (*.csv)")
        if fileObj[0]:
            self.params.setLibraryPath(fileObj[0])
            success, message = self.library.readLibraryFile()
            if not success:
                QMessageBox.critical(self, "Import Error!", message, QMessageBox.Ok)
                self.library.library_csv = []
                self.library.library_header = []
            else:
                self.populateTable(self.library.library_csv)

    def addTableRow(self, data=[]):
        """Adds an new empty row at the end of the table, and selects it."""
        self.table.sortByColumn(0, Qt.AscendingOrder)
        self.table.setSortingEnabled(False)
        rows = self.table.rowCount()
        columns = 11
        self.table.insertRow(rows)
        rows = self.table.rowCount()
        self.setTable(rows, columns, single_row=True)
        self.table.scrollToItem(self.table.item(rows-1, 1))
        self.table.selectRow(rows-1)
        self.table.setSortingEnabled(True)

    def removeTableRow(self):
        """Deletes the selected row from the table."""
        selected = self.table.currentRow()
        self.table.removeRow(selected)

    def clearTable(self):
        """Deletes all rows in the table."""
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

    def setTable(self, rows, columns, data=[], single_row=False):
        """Generates the structure of the table, which includes a checkbox widget in column 0 and a combobox in
        column 6. If importing data from a csv, it will populate all the elements of the table with the appropriate
        data."""
        self.table.setSortingEnabled(False)
        if single_row:
            start_row = rows-1
        else:
            start_row = 0
        for column in range(columns):
            for row in range(start_row, rows):
                if column == 0:
                    self.table.setRowHeight(row, 40)
                    compnum = row + 1
                    rowitem = QTableWidgetItem(str(compnum))
                    rowitem.setTextAlignment(Qt.AlignCenter)
                    self.table.setVerticalHeaderItem(row, rowitem)
                    cellwid = QWidget()
                    layout = QHBoxLayout(cellwid)
                    item = QCheckBox()
                    if not data:
                        item.setCheckState(Qt.Checked)
                    elif data[row][column] == 'YES':
                        item.setCheckState(Qt.Checked)
                    else:
                        item.setCheckState(Qt.Unchecked)
                    layout.addStretch()
                    layout.addWidget(item)
                    layout.addStretch()
                    self.table.setCellWidget(row, column, cellwid)
                elif column == 6:
                    item = ComboBoxNoWheel()
                    item.setEditable(True)
                    item.lineEdit().setReadOnly(True)
                    item.lineEdit().setAlignment(Qt.AlignCenter)
                    item.addItems(self.combolist)
                    if not data:
                        item.setCurrentIndex(self.combolist.index('USER'))
                    elif data[row][column] in self.combolist:
                        item.setCurrentIndex(self.combolist.index(data[row][column]))
                    else:
                        item.setCurrentIndex(self.combolist.index('USER'))
                    self.table.setCellWidget(row, column, item)
                else:
                    if not data:
                        item = QTableWidgetItem()
                    else:
                        item = QTableWidgetItem(data[row][column])
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)

    def populateTable(self, data):
        """Clears the table widget contents, then pulls in the data from the imported library.csv file.
        Calls the setTable method to populate the cells in the table."""
        self.table.setSortingEnabled(False)
        self.clearTable()
        rows = len(self.library.library_csv)
        columns = 11
        self.table.setRowCount(rows)
        self.table.setColumnCount(columns)
        self.setTable(rows, columns, data)
        self.table.selectRow(0)
        self.table.setSortingEnabled(True)

    def importPeakLists(self):
        """Checks for the occurrence of at least one compound that has an identifier and compound name. If that
        condition is satisfied, opens the Peak List Import window."""
        # importtime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
        self.generateLibraryFromTable()
        if not self.library.library_csv:
            error_msg = "You can't import a library with no compounds!\n" \
                        "Compounds must have identifiers, names, and at least one peaklist source."
            QMessageBox.critical(self, "Import Error!", error_msg, QMessageBox.Ok)
        else:
            peakimport_win = peak_import.Window(self.params, self.library)
            peakimport_win.accepted.connect(self.toLibraryPeakInfo)
            size = QApplication.desktop().availableGeometry()
            peakimport_win.resize(int(self.params.size.width() * 0.3), int(self.params.size.height() * 0.7))
            peakimport_win.exec_()

    def generateLibraryFromTable(self):
        """Updates the library_csv object to contain all the current items in the table. These elements will be
        used during the peak list import."""
        temp_csv = []
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        for row in range(rows):
            col_list = []
            for column in range(columns):
                if column is 0:
                    is_checked = self.table.cellWidget(row, column).findChild(QCheckBox).isChecked()
                    if is_checked:
                        item = "YES"
                    else:
                        item = 'NO'
                elif column is 6:
                    item = str(self.table.cellWidget(row, column).currentText())
                else:
                    item = self.table.item(row,column).text()
                col_list.append(item)
            if not col_list[1]:
                continue
            if not col_list[2]:
                continue
            temp_csv.append(col_list)
        self.library.library_csv = list(temp_csv)

    def toLibraryPeakInfo(self):
        self.hide()
        self.peakinfo_win = peak_info.Window(self.params, self.library)
        self.peakinfo_win.resize(int(self.params.size.width() * 0.85), int(self.params.size.height() * 0.7))
        self.peakinfo_win.show()
        self.peakinfo_win.rejected.connect(self.show)

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

class ComboBoxNoWheel(QComboBox):
    def wheelEvent(self, event):
        event.ignore()