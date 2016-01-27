#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimize.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import math
import random
import time
import datetime
import copy

from nmrmix.gui import optimize_view


class Window(QDialog):
    def __init__(self, params_object, library_object, mixture_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.mixtures = mixture_object
        self.mixtures.directory = []
        self.setWindowTitle("NMRmix: Optimizing Mixtures")
        self.createWidgets()
        self.createConnections()
        self.optimizeMixtures()

    def createWidgets(self):
        self.progressLabels1 = {}
        self.progressLabels3 = {}
        self.progressLabels2 = {}
        self.progressBars = {}
        vbox = QVBoxLayout(self)
        for solvent in self.mixtures.solvent_mixnum:
            if solvent == "":
                solvent_name = "N/A"
            else:
                solvent_name = solvent
            self.progressLabels1[solvent] = QLabel("Solvent <font color='red'>%s</font>" % str(solvent_name))
            self.progressLabels1[solvent].setStyleSheet("QLabel {font-weight: bold;}")
            self.progressLabels1[solvent].setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.progressLabels2[solvent] = QLabel("Iteration: <font color='blue'>1/%d</font>" % self.params.iterations)
            self.progressLabels2[solvent].setStyleSheet("QLabel {font-weight: bold;}")
            self.progressLabels2[solvent].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.progressLabels3[solvent] = QLabel("Optimizing")
            self.progressLabels3[solvent].setStyleSheet("QLabel {font-weight: bold; color: green;}")
            self.progressLabels3[solvent].setAlignment(Qt.AlignCenter)
            self.progressBars[solvent] = QProgressBar()
            self.setForegroundColor(self.progressBars[solvent], QColor("red"))
            self.progressBars[solvent].setMinimum(0)
            self.progressBars[solvent].setMaximum(self.params.max_steps)
            value = 0
            self.progressBars[solvent].setValue(value)
            self.progressBars[solvent].setFormat('%d / %d' % (value, self.params.max_steps))
            hbox1 = QHBoxLayout()
            hbox1.addWidget(self.progressLabels1[solvent])
            hbox1.addItem(QSpacerItem(30, 0, QSizePolicy.Maximum))
            hbox1.addWidget(self.progressLabels3[solvent])
            hbox1.addItem(QSpacerItem(30, 0, QSizePolicy.Maximum))
            hbox1.addWidget(self.progressLabels2[solvent])
            vbox.addLayout(hbox1)
            vbox.addWidget(self.progressBars[solvent])

        vbox.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        self.durationLabel = QLabel()
        self.durationLabel.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.durationLabel)

        vbox.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))

        hbox3 = QHBoxLayout()
        self.optimizeResults = QPushButton("Optimization Stats")
        self.optimizeResults.setDisabled(True)
        self.refineResults = QPushButton("Refinement Stats")
        self.refineResults.setDisabled(True)
        hbox3.addWidget(self.optimizeResults)
        hbox3.addWidget(self.refineResults)
        vbox.addLayout(hbox3)

        vbox.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))

        hbox2 = QHBoxLayout()
        self.stopButton = QPushButton("Stop Optimizing")
        self.stopButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.stopButton.setDefault(True)
        hbox2.addWidget(self.stopButton)
        self.okButton = QPushButton("Accept Results")
        self.okButton.setStyleSheet("QPushButton{color: gray; font-weight: bold;}")
        self.okButton.setDisabled(True)
        hbox2.addWidget(self.okButton)
        vbox.addLayout(hbox2)

    def createConnections(self):
        self.okButton.clicked.connect(self.acceptMixtures)
        self.stopButton.clicked.connect(self.stopOptimization)
        self.optimizeResults.clicked.connect(lambda: self.viewScorePlots(refine=False))
        self.refineResults.clicked.connect(lambda: self.viewScorePlots(refine=True))

    def optimizeMixtures(self):
        solvents = list(self.mixtures.solvent_mixnum.keys())
        self.solvent_count = len(solvents)
        self.finished_threads = 0
        self.mixtures.calculateTotalScore(self.mixtures.mixtures)
        self.mixtures.anneal_results = {}
        self.mixtures.curr_mixtures = copy.deepcopy(self.mixtures.mixtures)
        for locked in self.mixtures.mixtures_lock:
            del self.mixtures.curr_mixtures[locked]
        self.thread_pool = {}
        self.mixtures.anneal_scores = {}
        self.start_time = time.time()
        self.mixtures.optimize_time = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y%m%d_%H%M%S')
        self.mixtures.optimize_folder =  self.mixtures.optimize_time + "_Optimize"
        for solvent in solvents:
            mixnum_list = list(self.mixtures.solvent_mixnum[solvent])
            self.thread_pool[solvent] = AnnealThread(self.params, self.library, self.mixtures, solvent, mixnum_list)
            self.thread_pool[solvent].newIteration.connect(self.updateLabels)
            self.thread_pool[solvent].newStep.connect(self.updateProgressBars)
            self.thread_pool[solvent].startRefining.connect(self.updateLabels)
            self.thread_pool[solvent].doneThread.connect(self.updateOkButton)
            self.thread_pool[solvent].start()

    def updateLabels(self, text, solvent, i):
        self.progressLabels3[solvent].setText("%s" % (text))
        self.progressLabels2[solvent].setText("Iteration: <font color='blue'>%d/%d</font>"
                                                   % (i+1, self.params.iterations))

    def updateProgressBars(self, solvent, i, score, refining=False):
        if refining:
            max_steps = self.params.refine_max_steps
        else:
            max_steps = self.params.max_steps
        value = i
        self.progressBars[solvent].setValue(value)
        self.progressBars[solvent].setMaximum(max_steps)
        self.progressBars[solvent].setFormat('%d / %d  (%0.1f)' % (value, max_steps, score))

    def updateOkButton(self):
        self.finished_threads += 1
        if self.finished_threads == self.solvent_count:
            self.finish_time = time.time()
            m, s = divmod(self.finish_time - self.start_time, 60)
            h, m = divmod(m, 60)
            self.mixtures.optimize_duration = "%d hrs, %02d mins, %02d secs" % (h, m, s)
            self.durationLabel.setText("Optimization Time: %s" % self.mixtures.optimize_duration)
            self.okButton.setDisabled(False)
            self.okButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
            self.optimizeResults.setDisabled(False)
            self.optimizeResults.setDefault(True)
            self.stopButton.setText("Cancel Changes")
            self.stopButton.setDefault(False)
            if self.params.use_refine:
                self.refineResults.setDisabled(False)

    def viewScorePlots(self, refine):
        scoreplot_win = optimize_view.Window(self.params, self.mixtures, refine=refine)
        scoreplot_win.exec_()

    def setForegroundColor(self, widget, color):
        palette=widget.palette()
        palette.setColor(QPalette.Highlight, color)
        widget.setPalette(palette)

    def stopOptimization(self):
        for solvent in self.mixtures.solvent_mixnum:
            self.thread_pool[solvent].stop()
        QDialog.reject(self)

    def acceptMixtures(self):
        self.mixtures.mixtures.update(self.mixtures.curr_mixtures)
        QDialog.accept(self)

class AnnealThread(QThread):
    newIteration = pyqtSignal(str, str, int)
    newStep = pyqtSignal(str, int, float, bool)
    startRefining = pyqtSignal(str, str, int)
    doneThread = pyqtSignal()

    def __init__(self, params_object, library_object, mixtures_object, solvent, mixnum_list, parent=None):
        QThread.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.mixtures = mixtures_object
        self.solvent = solvent
        self.mixnum_list = list(mixnum_list)
        self.mixtures.anneal_scores[self.solvent] = {}
        self.mixtures.refine_scores[self.solvent] = {}
        self.exiting = False

    def stop(self):
        self.exiting = True
        self.wait()
        self.exit()

    def run(self):
        time.sleep(0.5)
        i = 0
        while not self.exiting and i < self.params.iterations:
            self.newIteration.emit("Optimizing", self.solvent, i)
            if self.params.randomize_initial:
                init_mixtures = self.randomizeMixtures()
            else:
                init_mixtures = {}
                for mixnum in self.mixnum_list:
                    init_mixtures[mixnum] = list(self.mixtures.mixtures[mixnum])
            curr_score, mixtures, scores = self.annealMixtures(init_mixtures)
            if self.params.use_refine:
                self.startRefining.emit("Refining", self.solvent, i)
                curr_score, mixtures, refine_scores = self.annealMixtures(mixtures, refining=True)
                self.mixtures.refine_scores[self.solvent][i] = list(refine_scores)
            self.mixtures.anneal_scores[self.solvent][i] = list(scores)
            if i == 0:
                self.mixtures.curr_mixtures.update(mixtures)
                previous_score = curr_score
            else:
                if curr_score <= previous_score:
                    self.mixtures.curr_mixtures.update(mixtures)
            i += 1
        self.doneThread.emit()

    def randomizeMixtures(self):
        compound_list = []
        mixtures = {}
        for mixnum in self.mixnum_list:
            compounds = list(self.mixtures.mixtures[mixnum])
            for compound in compounds:
                compound_list.append(compound)
        random.shuffle(compound_list)
        for mixnum in self.mixnum_list:
            mixtures[mixnum] = []
            for mix_size in range(self.params.mix_size):
                if len(compound_list) != 0:
                    compound = compound_list.pop()
                    mixtures[mixnum].append(compound)
            mixtures[mixnum].sort()
        return(mixtures)


    def annealMixtures(self, mixtures_dict, refining=False):
        mixtures = copy.deepcopy(mixtures_dict)
        if refining:
            cooling = self.params.refine_cooling
            max_steps = self.params.refine_max_steps
            mix_rate = self.params.mix_rate
        else:
            cooling = self.params.cooling
            max_steps = self.params.max_steps
            mix_rate = self.params.refine_mix_rate
        scores = []
        max_score = mix_rate * self.params.score_scale
        #delta_scores = []
        curr_score, curr_overlap = self.mixtures.calculateTotalScore(mixtures)
        unlocked_list = list(mixtures.keys())
        for mixture in self.mixtures.mixtures_lock:
            if mixture in unlocked_list:
                unlocked_list.remove(mixture)
        num_peaks = 0
        for mixture in mixtures:
            for compound in mixtures[mixture]:
                num_peaks += self.mixtures.compound_scores[compound][2]
        step = 1
        if cooling == 'exponential':
            cooling_schedule = self.mixtures.exponentialCooling(refining)
        else:
            cooling_schedule = self.mixtures.linearCooling(refining)
        for current_temp in cooling_schedule:
            if (step % self.params.print_step_size) == 0:
                self.newStep.emit(self.solvent, step, curr_score, refining)
            if len(unlocked_list) >= 2:
                new_mixtures, diff_score, diff_overlaps  = self.mixtures.mixMixtures(mixtures, unlocked_list, refining=refining)
            else:
                break
                # new_mixtures = mixtures
            # new_score, new_overlap = self.mixtures.calculateTotalScore(new_mixtures)

            new_score = curr_score + diff_score
            # print(new_score, curr_score, diff_score)
            new_overlap = curr_overlap + diff_overlaps
            # delta_max = score_diff
            # delta_scores.append(score_diff)
            # if step == 1:
                # delta_median = score_diff
                # delta_max = score_diff
            # else:
            #     delta_median = self.mixtures.medianDeltaScore(delta_scores)

            if new_score <= 0.0001:
                score_step = (step, current_temp, curr_score, new_score, curr_overlap, new_overlap,
                              num_peaks, max_score, 1, 'PASSED')
                scores.append(score_step)
                mixtures.update(new_mixtures)
                curr_score = new_score
                curr_overlap = new_overlap
                self.newStep.emit(self.solvent, step, abs(curr_score), refining)
                break
            elif new_score <= curr_score:
                score_step = (step, current_temp, curr_score, new_score, curr_overlap, new_overlap,
                              num_peaks, max_score, 1, 'PASSED')
                scores.append(score_step)
                mixtures.update(new_mixtures)
                curr_score = new_score
                curr_overlap = new_overlap
            else:
                if current_temp > 0.0:
                    score_diff = new_score - curr_score
                    probability = math.exp(((-score_diff / max_score) / current_temp) * 25000)
                    if random.random() < probability:
                        score_step = (step, current_temp, curr_score, new_score, curr_overlap, new_overlap,
                                      num_peaks, max_score, probability, 'PASSED')
                        scores.append(score_step)
                        mixtures.update(new_mixtures)
                        curr_score = new_score
                        curr_overlap = new_overlap
                    else:
                        score_step = (step, current_temp, curr_score, new_score, curr_overlap, new_overlap,
                                      num_peaks, max_score, probability, 'FAILED')
                        scores.append(score_step)
                else:
                    score_step = (step, current_temp, curr_score, new_score, curr_overlap, new_overlap,
                                      num_peaks, max_score, 0, 'FAILED')
                    scores.append(score_step)
                # print(score_step)
                # if score_diff > delta_max:
                #     delta_max = score_diff
                # test_score, test_overlap = self.mixtures.calculateTotalScore(mixtures)
                # print(test_score, curr_score, test_overlap, curr_overlap)
            step += 1
            if step > max_steps:
                self.newStep.emit(self.solvent, step-1, curr_score, refining)
                break
            if self.exiting:
                self.newStep.emit(self.solvent, step, curr_score, refining)
                break
        return(curr_score, mixtures, scores)