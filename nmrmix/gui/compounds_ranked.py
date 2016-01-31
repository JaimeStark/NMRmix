#!/usr/bin/env python3
# encoding: utf-8
"""
compounds_ranked.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from gui import compound_info

class Window(QDialog):
    def __init__(self, params_object, library_object, mixtures_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.mixtures = mixtures_object
        self.setWindowTitle("NMRmix: Score Ranked Compounds")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.titleLabel = QLabel("Score Ranked Compounds")
        self.titleLabel.setStyleSheet("QLabel{font-weight: bold; color: red; qproperty-alignment: AlignCenter;}")
        self.compoundtable = QTableWidget(len(self.library.library), 6, self)
        self.compoundtable.setSelectionMode(QAbstractItemView.NoSelection)
        self.compoundtable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.compoundtable.setFocusPolicy(Qt.NoFocus)

        # self.compoundtable.verticalHeader().setDefaultSectionSize(40)
        self.compoundtable.setColumnWidth(0, 140)
        self.header = ['Identifier','Compound Name', '# Peaks', '# Overlaps', 'Overlap Score', 'Info']
        self.compoundtable.setHorizontalHeaderLabels(self.header)
        self.compoundtable.horizontalHeader().setStyleSheet("QHeaderView {font-weight: bold;}")
        self.compoundtable.horizontalHeader().setStretchLastSection(True)
        self.compoundtable.sortByColumn(4, Qt.DescendingOrder)
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
        for i, compound in enumerate(self.library.library):
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
            numpeaks = QTableWidgetItem()
            numpeaks.setTextAlignment(Qt.AlignCenter)
            numpeaks.setData(Qt.DisplayRole, int(self.mixtures.compound_scores[compound][2]))
            self.compoundtable.setItem(i, 2, numpeaks)
            numoverlaps = QTableWidgetItem()
            numoverlaps.setTextAlignment(Qt.AlignCenter)
            numoverlaps.setData(Qt.DisplayRole, int(self.mixtures.compound_scores[compound][1]))
            self.compoundtable.setItem(i, 3, numoverlaps)
            compound_score = "%0.1f" % self.mixtures.compound_scores[compound][0]
            score = QTableWidgetItem()
            score.setTextAlignment(Qt.AlignCenter)
            score.setData(Qt.DisplayRole, float(compound_score))
            self.compoundtable.setItem(i, 4, score)
            view_info = QPushButton("Info")
            view_info.setStyleSheet('QPushButton {color: blue;}')
            self.compoundtable.setCellWidget(i, 5, view_info)
            view_info.clicked.connect(self.handleInfo)
        self.compoundtable.setSortingEnabled(True)
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
            compound_obj = self.library.library[compound]
            compound_win = compound_info.Window(self.params, compound_obj)
            compound_win.exec_()

