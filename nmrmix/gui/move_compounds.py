#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
move_compounds.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import copy
import numpy as np

class Window(QDialog):
    def __init__(self, params_object, library_object, mixtures_object, compound_id, mixture_id, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.mixtures = mixtures_object
        self.curr_compound = str(compound_id)
        self.mixture1 = str(mixture_id)
        self.mixture_list = []
        self.movedmixtures = copy.deepcopy(self.mixtures.mixtures)
        for mixnum in self.movedmixtures:
            self.mixture_list.append(str(mixnum))
        self.initial_scores = {}
        self.total_score_change = {}
        self.mixture_list.sort()
        self.setWindowTitle("NMRmix: Moving Compounds")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        self.mixture1Label = QLabel("Mixture")
        self.mixture1ComboBox = QComboBox()
        self.mixture1ComboBox.addItems(self.mixture_list)
        self.mixture1ComboBox.setCurrentIndex(self.mixture_list.index(self.mixture1))
        self.mixture1ComboBox.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.mixture1ComboBox.setMaxVisibleItems(10)
        self.mixture1List = QListWidget()
        self.mixture1List.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mixture1Score = QLabel("")
        self.mixture1ScoreChange = QLabel("")
        self.setMixture(1, self.mixture1)


        self.mixture2Label = QLabel("Mixture")
        self.mixture2ComboBox = QComboBox()
        self.mixture2ComboBox.addItems(self.mixture_list)
        self.mixture2ComboBox.setCurrentIndex(0)
        self.mixture2ComboBox.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.mixture2ComboBox.setMaxVisibleItems(10)
        self.mixture2 = self.mixture2ComboBox.currentText()

        self.mixture2List = QListWidget()
        self.mixture2List.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mixture2Score = QLabel("")
        self.mixture2ScoreChange = QLabel("")
        self.setMixture(2, self.mixture2)

        self.totalScoreLabel1 = QLabel("<b> Total Score Change </b>")
        self.totalScoreLabel1.setAlignment(Qt.AlignCenter)
        self.totalScoreLabel2 = QLabel("0.0")
        self.totalScoreLabel2.setAlignment(Qt.AlignCenter)

        self.toMixture2Button = QPushButton("-->")
        self.toMixture1Button = QPushButton("<--")

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.acceptButton = QPushButton("Accept")
        self.acceptButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")

    def layoutWidgets(self):
        winLayout = QGridLayout(self)
        winLayout.addWidget(self.mixture1Label, 0, 0)
        winLayout.addWidget(self.mixture2Label, 0, 3)
        winLayout.addWidget(self.mixture1ComboBox, 0, 1)
        winLayout.addWidget(self.mixture2ComboBox, 0, 4)
        winLayout.addWidget(self.mixture1List, 1, 0, 1, 2)
        transferLayout = QVBoxLayout()
        transferLayout.addWidget(self.toMixture2Button)
        transferLayout.addWidget(self.toMixture1Button)
        winLayout.addLayout(transferLayout, 1, 2)
        winLayout.addWidget(self.mixture2List, 1, 3, 1, 2)
        winLayout.addWidget(self.mixture1Score, 2, 0, 1, 2)
        winLayout.addWidget(self.mixture2Score, 2, 3, 1, 2)
        winLayout.addWidget(self.mixture1ScoreChange, 3, 0, 1, 2)
        winLayout.addWidget(self.mixture2ScoreChange, 3, 3, 1, 2)
        winLayout.addWidget(self.totalScoreLabel1, 4, 2)
        winLayout.addWidget(self.totalScoreLabel2, 5, 2)
        winLayout.addWidget(self.cancelButton, 6, 0, 1, 2)
        winLayout.addWidget(self.acceptButton, 6, 3, 1, 2)

    def createConnections(self):
        self.mixture1ComboBox.currentIndexChanged.connect(lambda: self.setMixture(1))
        self.mixture2ComboBox.currentIndexChanged.connect(lambda: self.setMixture(2))
        self.toMixture2Button.clicked.connect(self.moveToMixture2)
        self.toMixture1Button.clicked.connect(self.moveToMixture1)
        self.cancelButton.clicked.connect(self.reject)
        self.acceptButton.clicked.connect(self.acceptChanges)

    def scoreCompounds(self, mixture_list, listbox):
        curr_listbox = listbox
        curr_listbox.clear()
        mixture_score, overlap_score = self.mixtures.calculateMixtureScore(mixture_list)
        for compound in mixture_list:
            item = QListWidgetItem(listbox)
            item.setText(compound)
            temp_list = list(mixture_list)
            temp_list.remove(compound)
            compound_score, overlap = self.mixtures.calculateCompoundScore(compound, temp_list, temp_score = True)
            score_ratio = compound_score / self.params.score_scale
            curr_listbox.addItem(item)
            if score_ratio >= 0.75:
                item.setForeground(QColor('red'))
            elif score_ratio >= 0.50:
                item.setForeground(QColor('orange'))
            elif score_ratio >= 0.25:
                item.setForeground(QColor('purple'))
            elif score_ratio > 0.00:
                item.setForeground(QColor('blue'))
            else:
                item.setForeground(QColor('green'))
        return(mixture_score)

    def setMixture(self, listnum, mixnum=""):
        combobox = self.sender()
        if listnum == 1:
            self.mixture1List.clear()
            if not mixnum:
                self.mixture1 = combobox.currentText()
            else:
                self.mixture1 = mixnum
            curr_mixture_score = self.scoreCompounds(self.movedmixtures[int(self.mixture1)], self.mixture1List)
            if self.mixture1 not in self.initial_scores:
                self.initial_scores[self.mixture1] = curr_mixture_score
            score_change = curr_mixture_score - self.initial_scores[self.mixture1]
            self.total_score_change[self.mixture1] = score_change
            self.mixture1Score.setText("Score: %0.1f" % curr_mixture_score)
            if score_change < 0:
                self.mixture1ScoreChange.setStyleSheet("QLabel { color : green; }")
                score_change_text = "%0.1f" % score_change
            elif score_change > 0:
                self.mixture1ScoreChange.setStyleSheet("QLabel { color : red; }")
                score_change_text = "+%0.1f" % score_change
            else:
                self.mixture1ScoreChange.setStyleSheet("QLabel { color : black; }")
                score_change_text = "%0.1f" % score_change
            self.mixture1ScoreChange.setText("Change: %s" % score_change_text)
        elif listnum == 2:
            self.mixture2List.clear()
            if not mixnum:
                self.mixture2 = combobox.currentText()
            else:
                self.mixture2 = mixnum
            curr_mixture_score = self.scoreCompounds(self.movedmixtures[int(self.mixture2)], self.mixture2List)
            if self.mixture2 not in self.initial_scores:
                self.initial_scores[self.mixture2] = curr_mixture_score
            score_change = curr_mixture_score - self.initial_scores[self.mixture2]
            self.total_score_change[self.mixture2] = score_change
            self.mixture2Score.setText("Score: %0.1f" % curr_mixture_score)
            if score_change < 0:
                self.mixture2ScoreChange.setStyleSheet("QLabel { color : green; }")
                score_change_text = "%0.1f" % score_change
            elif score_change > 0:
                self.mixture2ScoreChange.setStyleSheet("QLabel { color : red; }")
                score_change_text = "+%0.1f" % score_change
            else:
                self.mixture2ScoreChange.setStyleSheet("QLabel { color : black; }")
                score_change_text = "%0.1f" % score_change
            self.mixture2ScoreChange.setText("Change: %s" % score_change_text)

    def moveToMixture2(self):
        if self.mixture1List.currentItem():
            moved_compound = self.mixture1List.currentItem().text()
            mixture_list1 = self.movedmixtures[int(self.mixture1)]
            mixture_list1.remove(moved_compound)
            mixture_list2 = self.movedmixtures[int(self.mixture2)]
            mixture_list2.append(moved_compound)
            self.setMixture(1, self.mixture1)
            self.setMixture(2, self.mixture2)
            mixture_list1.sort()
            mixture_list2.sort()
            total_score_change = np.sum(list(self.total_score_change.values()))
            if total_score_change < 0:
                self.totalScoreLabel2.setText("%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : green; }")
            elif total_score_change > 0:
                self.totalScoreLabel2.setText("+%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : red; }")
            else:
                self.totalScoreLabel2.setText("%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : black; }")
        # TODO: Check for violating mixing parameters like group or mixture size



    def moveToMixture1(self):
        if self.mixture2List.currentItem():
            moved_compound = self.mixture2List.currentItem().text()
            mixture_list2 = self.movedmixtures[int(self.mixture2)]
            mixture_list2.remove(moved_compound)
            mixture_list1 = self.movedmixtures[int(self.mixture1)]
            mixture_list1.append(moved_compound)
            self.setMixture(2, self.mixture2)
            self.setMixture(1, self.mixture1)
            mixture_list1.sort()
            mixture_list2.sort()
            total_score_change = np.sum(list(self.total_score_change.values()))
            if total_score_change < 0:
                self.totalScoreLabel2.setText("%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : green; }")
            elif total_score_change > 0:
                self.totalScoreLabel2.setText("+%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : red; }")
            else:
                self.totalScoreLabel2.setText("%0.1f" % total_score_change)
                self.totalScoreLabel2.setStyleSheet("QLabel { color : black; }")

    def acceptChanges(self):
        self.mixtures.mixtures.update(self.movedmixtures)
        for mixture in self.movedmixtures:
            if not self.movedmixtures[mixture]:
                del self.mixtures.mixtures[mixture]
        QDialog.accept(self)

