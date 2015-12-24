#!/usr/bin/env python3
# encoding: utf-8
"""
compounds_list.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nmrmix.gui import compound_info

class Window(QDialog):
    def __init__(self, params_object, library_object, compound_list, list_title, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.compound_list = compound_list
        self.title = list_title
        self.setWindowTitle("NMRmix: %s" % self.title)
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.titleLabel = QLabel("%s" % self.title)
        self.titleLabel.setStyleSheet("QLabel{font-weight: bold; color: red; qproperty-alignment: AlignCenter;}")
        self.compoundtable = QTableWidget(len(self.compound_list), 6, self)
        self.compoundtable.setSelectionMode(QAbstractItemView.NoSelection)
        self.compoundtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.compoundtable.setFocusPolicy(Qt.NoFocus)

        # self.compoundtable.verticalHeader().setDefaultSectionSize(40)
        self.compoundtable.setColumnWidth(0, 140)
        self.header = ['Identifier','Compound Name', 'Solvent', '# Peaks', '% Aromaticity', 'Info']
        self.compoundtable.setHorizontalHeaderLabels(self.header)
        self.compoundtable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.compoundtable.horizontalHeader().setStretchLastSection(True)
        self.compoundtable.setColumnWidth(0, 90)
        self.compoundtable.setColumnWidth(1, 200)
        self.compoundtable.setColumnWidth(2, 75)
        self.compoundtable.setColumnWidth(3, 75)
        self.compoundtable.setColumnWidth(4, 115)
        self.compoundtable.setColumnWidth(5, 60)
        self.compoundtable.verticalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.compoundtable.horizontalHeaderItem(0).setToolTip('Tooltip')
        self.compoundtable.horizontalHeaderItem(1).setToolTip('Tooltip')
        self.compoundtable.horizontalHeaderItem(2).setToolTip('Tooltip')
        self.compoundtable.horizontalHeaderItem(3).setToolTip('Tooltip')
        self.compoundtable.horizontalHeaderItem(4).setToolTip('Tooltip')
        self.compoundtable.horizontalHeaderItem(5).setToolTip('Tooltip')
        for i, compound in enumerate(self.compound_list):
            try:
                compound_obj = self.library.library[compound]
            except:
                compound_obj = self.library.ignored_library[compound]
            id = QTableWidgetItem(compound)
            id.setTextAlignment(Qt.AlignCenter)
            self.compoundtable.setItem(i, 0, id)
            name = QTableWidgetItem(compound_obj.name)
            name.setTextAlignment(Qt.AlignCenter)
            self.compoundtable.setItem(i, 1, name)
            solvent = QTableWidgetItem(compound_obj.solvent)
            solvent.setTextAlignment(Qt.AlignCenter)
            self.compoundtable.setItem(i, 2, solvent)
            # print(len(self.library.library[compound].peaklist), self.library.library[compound].aromatic_percent)
            numpeaks = QTableWidgetItem()
            numpeaks.setTextAlignment(Qt.AlignCenter)
            numpeaks.setData(Qt.DisplayRole, int(len(compound_obj.peaklist)))
            self.compoundtable.setItem(i, 3, numpeaks)
            aromatic_percent = "%0.1f" % (compound_obj.aromatic_percent)
            aromaticity = QTableWidgetItem()
            aromaticity.setTextAlignment(Qt.AlignCenter)
            aromaticity.setData(Qt.DisplayRole, float(aromatic_percent))
            self.compoundtable.setItem(i, 4, aromaticity)
            view_info = QPushButton("Info")
            view_info.setStyleSheet('QPushButton {color: blue;}')
            self.compoundtable.setCellWidget(i, 5, view_info)
            view_info.clicked.connect(self.handleInfo)
        self.compoundtable.setSortingEnabled(True)
        self.compoundtable.sortByColumn(0, Qt.AscendingOrder)
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.closeButton.setFixedWidth(200)

    def layoutWidgets(self):
        winLayout = QVBoxLayout(self)
        winLayout.addWidget(self.titleLabel)
        winLayout.addWidget(self.compoundtable)
        winLayout.addItem(QSpacerItem(0,20))
        winLayout.addWidget(self.closeButton)
        winLayout.setAlignment(self.closeButton, Qt.AlignCenter)

    def createConnections(self):
        self.closeButton.clicked.connect(self.accept)

    def handleInfo(self):
        button = self.sender()
        index = self.compoundtable.indexAt(button.pos())
        if index.isValid():
            compound = self.compoundtable.item(index.row(), 0).text()
            try:
                if compound in self.library.library:
                    compound_obj = self.library.library[compound]
                if compound in self.library.ignored_library:
                    compound_obj = self.library.ignored_library[compound]
                compound_win = compound_info.Window(self.params, compound_obj, editable_peaklist=True)
                compound_win.exec_()
            except Exception as e:
                #print(e)
                pass

    
