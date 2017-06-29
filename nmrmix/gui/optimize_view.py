#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
optimize_view.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import os
import numpy as np
import codecs
import sys
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
    def __init__(self, params_object, mixtures_object, refine=False, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.mixtures = mixtures_object
        self.refine = refine
        if self.refine:
            self.setWindowTitle("NMRmix: View Refining Score Plots")
            self.anneal_scores = self.mixtures.refine_scores
        else:
            self.setWindowTitle("NMRmix: View Optimizing Score Plots")
            self.anneal_scores = self.mixtures.anneal_scores
        self.summary = {}
        self.createWidgets()
        self.createConnections()

    def createWidgets(self):
        winLayout = QVBoxLayout(self)
        winLayout.setAlignment(Qt.AlignCenter)
        self.resultsTabs = QTabWidget()
        self.resultsTabs.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.resultsTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')

        self.xLabel = QLabel("X-axis")
        self.xLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xCombobox = QComboBox()
        self.xCombobox.addItems(['Steps', 'Temperature'])
        self.yLabel = QLabel("Y-axis")
        self.yLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.yCombobox = QComboBox()
        self.yCombobox.addItems(['Energy (Total)', 'Energy (Per Compound)', 'Energy Difference (Per Step)',
                                 'Peak Overlaps'])
        self.fullResultsCheckbox = QCheckBox("Save Full Results")
        self.fullResultsCheckbox.setToolTip("When enabled, a csv file is saved containing the results of\n"
                                            "every step of the optimization, which can result in very large\n"
                                            "files and take a significant amount of time to generate.")
        self.fullResultsCheckbox.setChecked(True)

        comboLayout = QHBoxLayout()
        comboLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
        comboLayout.addWidget(self.xLabel)
        comboLayout.addWidget(self.xCombobox)
        comboLayout.addItem(QSpacerItem(30,0, QSizePolicy.Maximum))
        comboLayout.addWidget(self.yLabel)
        comboLayout.addWidget(self.yCombobox)
        comboLayout.addItem(QSpacerItem(30,0, QSizePolicy.MinimumExpanding))
        comboLayout.addWidget(self.fullResultsCheckbox)
        comboLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))

        self.canvas = {}
        self.fig = {}
        self.mpl_toolbar = {}
        self.statsLabel = {}
        self.iterationsLabel = {}
        self.totalmixturesLabel = {}
        self.totalcompLabel = {}
        self.totalpeaksLabel = {}
        self.startingLabel = {}
        self.startingoverlapLabel = {}
        self.deltascoresLabel = {}
        self.finalLabel = {}
        self.finaloverlapLabel = {}
        self.groupTab = {}

        for i, group in enumerate(self.mixtures.group_mixnum):
            self.summary[group] = []
            self.groupTab[group] = QWidget()
            self.groupTab[group].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
            if self.refine:
                statlabel = "Refining"
            else:
                statlabel = "Optimizing"
            if not group:
                self.statsLabel[group] = QLabel("<b>%s Statistics</b>" % statlabel)
                self.summary[group].append('\n%s Statistics for All Mixtures' % statlabel)
            else:
                self.statsLabel[group] = QLabel("<b>%s Statistics for %s</b>" % (statlabel, group))
                self.summary[group].append('\n%s Statistics for %s Mixtures' % (statlabel, group))
            self.statsLabel[group].setAlignment(Qt.AlignCenter)
            self.fig[group] = plt.figure(i)
            self.fig[group].patch.set_facecolor('white')
            self.canvas[group] = FigureCanvas(self.fig[group])
            self.canvas[group].setMinimumHeight(150)
            self.canvas[group].setMinimumWidth(150)
            self.calculateStats(i, group)
            self.mpl_toolbar[group] = NavigationToolbar2(self.canvas[group], self)
            self.mpl_toolbar[group].hide()
            groupLayout = QVBoxLayout()
            groupLayout.addWidget(self.canvas[group], Qt.AlignCenter)
            groupLayout.addWidget(self.totalcompLabel[group])
            groupLayout.addWidget(self.totalpeaksLabel[group])
            groupLayout.addWidget(self.iterationsLabel[group])
            groupLayout.addWidget(self.startingLabel[group])
            groupLayout.addWidget(self.finalLabel[group])
            groupLayout.addWidget(self.deltascoresLabel[group])
            groupLayout.addWidget(self.startingoverlapLabel[group])
            groupLayout.addWidget(self.finaloverlapLabel[group])
            # TODO: Add best score and overlap
            self.groupTab[group].setLayout(groupLayout)
            if not group:
                self.resultsTabs.addTab(self.groupTab[group], "ALL")
            else:
                self.resultsTabs.addTab(self.groupTab[group], group)
            self.fig[group].tight_layout(pad=4)
            self.canvas[group].draw()
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.saveFigButton = QPushButton("Save Figure")
        self.saveFigButton.setStyleSheet("QPushButton{color: blue; font-weight: bold}")
        self.saveButton = QPushButton("Save Results")
        self.saveButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.saveFigButton)
        buttonLayout.addWidget(self.saveButton)
        winLayout.addWidget(self.resultsTabs)
        winLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        winLayout.addLayout(comboLayout)
        winLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        winLayout.addLayout(buttonLayout)

    def createConnections(self):
        self.xCombobox.currentTextChanged.connect(self.updateStats)
        self.yCombobox.currentTextChanged.connect(self.updateStats)
        self.closeButton.clicked.connect(self.closeEvent)
        self.saveFigButton.clicked.connect(lambda: self.saveResults(figures_only=True))
        self.saveButton.clicked.connect(self.saveResults)

    def updateStats(self):
        for i, group in enumerate(self.mixtures.group_mixnum):
            self.fig[group].clear()
            self.calculateStats(i, group)

    def calculateStats(self, group_key, group):
        scores = {}
        best_iteration_score = 99999999999
        iterations = len(self.mixtures.anneal_scores[group])
        num_compounds = len(self.mixtures.group_dict[group])
        starting_energy = []
        final_energy = []
        starting_overlaps = []
        final_overlaps = []
        delta_scores = []
        if self.refine:
            chart_title = "Refinement"
        else:
            chart_title = "Optimization"
        plt.figure(group_key)
        if not group:
            plt.title("%s of All Mixtures" % chart_title, fontweight='bold')
        else:
            plt.title("%s of %s Mixtures" % (chart_title, group), fontweight='bold')

        for iteration in self.mixtures.anneal_scores[group]:
            scores[iteration] = {}
            iteration_list = list(self.anneal_scores[group][iteration])
            scores[iteration]['Steps'] = []
            scores[iteration]['StepsProb'] = []
            scores[iteration]['Temps'] = []
            scores[iteration]['TempsProb'] = []
            scores[iteration]['Scores'] = []
            scores[iteration]['DeltaScores'] = []
            scores[iteration]['PerScores'] = []
            scores[iteration]['Probabilities'] = []
            scores[iteration]['Overlaps'] = []
            for i in iteration_list:
                num_peaks = i[6]
                scores[iteration]['Steps'].append(i[0])
                scores[iteration]['Temps'].append(i[1])
                scores[iteration]['DeltaScores'].append(abs(i[2]-i[3]))
                delta_scores.append(abs(i[2]-i[3]))

                if i[9] == 'FAILED':
                    scores[iteration]['Scores'].append(i[2])
                    scores[iteration]['PerScores'].append(i[2] / num_compounds)
                    scores[iteration]['Overlaps'].append(i[4])
                else:
                    scores[iteration]['Scores'].append(i[3])
                    scores[iteration]['PerScores'].append(i[3] / num_compounds)
                    scores[iteration]['Overlaps'].append(i[5])
                if i[8] < 1:
                    scores[iteration]['StepsProb'].append(i[0])
                    scores[iteration]['TempsProb'].append(i[1])
                    scores[iteration]['Probabilities'].append(i[8])

            final_energy.append(scores[iteration]['Scores'][-1])
            final_overlaps.append(scores[iteration]['Overlaps'][-1])
            starting_energy.append(scores[iteration]['Scores'][0])
            starting_overlaps.append(scores[iteration]['Overlaps'][0])
            if scores[iteration]['Scores'][-1] < best_iteration_score:
                best_iteration = iteration
            if self.xCombobox.currentText() == 'Steps':
                x = scores[iteration]['Steps']
                plt.xlabel("Optimization Step", fontweight='bold')
                if x[0] == x[-1]:
                    plt.xlim(x[0], x[-1]+1)
                else:
                    plt.xlim([x[0], x[-1]])
            elif self.xCombobox.currentText() == 'Temperature':
                x = scores[iteration]['Temps']
                plt.xlabel("Optimization Temperature", fontweight='bold')
                if x[0] == x[-1]:
                    plt.xlim(x[0], x[-1]-1)
                else:
                    plt.xlim([x[0], x[-1]])
            if self.yCombobox.currentText() == 'Energy (Total)':
                y = scores[iteration]['Scores']
                plt.ylabel("Total Mixtures Score", fontweight='bold')
            elif self.yCombobox.currentText() == 'Energy (Per Compound)':
                y = scores[iteration]['PerScores']
                plt.ylabel("Mixtures Score Per Compound", fontweight='bold')

            elif self.yCombobox.currentText() == 'Peak Overlaps':
                y = scores[iteration]['Overlaps']
                plt.ylabel("Total Peak Overlaps", fontweight='bold')

            elif self.yCombobox.currentText() == 'Energy Difference (Per Step)':
                y = scores[iteration]['DeltaScores']
                plt.ylabel("Total Mixtures Score Difference (Abs)", fontweight='bold')
            plt.plot(x, y, linewidth=2.0)
            self.canvas[group].draw()
        average_start = np.mean(starting_energy)
        average_final = np.mean(final_energy)
        min_start = np.min(starting_energy)
        max_start = np.max(starting_energy)
        min_final = np.min(final_energy)
        max_final = np.max(final_energy)
        average_difference = np.mean(delta_scores)
        max_difference = max(delta_scores)
        min_difference = min(delta_scores)
        average_start_overlap = np.mean(starting_overlaps)
        average_final_overlap = np.mean(final_overlaps)
        min_start_overlap = np.min(starting_overlaps)
        max_start_overlap = np.max(starting_overlaps)
        min_final_overlap = np.min(final_overlaps)
        max_final_overlap = np.max(final_overlaps)
        if iterations < 2:
            stdev_start = 0.0
            stdev_final = 0.0
            stdev_difference = 0.0
            stdev_start_overlap = 0.0
            stdev_final_overlap = 0.0
        else:
            stdev_start = np.std(starting_energy)
            stdev_final = np.std(final_energy)
            stdev_difference = np.std(delta_scores)
            stdev_start_overlap = np.std(starting_overlaps)
            stdev_final_overlap = np.std(final_overlaps)

        self.totalmixturesLabel[group] = QLabel("Total Number of Mixtures: %d" % len(self.mixtures.group_mixnum[group]))
        self.totalmixturesLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.totalmixturesLabel[group].text())
        self.totalcompLabel[group] = QLabel("Total Number of Compounds: %d" % len(self.mixtures.group_dict[group]))
        self.totalcompLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.totalcompLabel[group].text())
        self.totalpeaksLabel[group] = QLabel("Total Number of Peaks: %d" % num_peaks)
        self.totalpeaksLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.totalpeaksLabel[group].text())
        self.iterationsLabel[group] = QLabel("Number of Iterations: %d" % iterations)
        self.iterationsLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.iterationsLabel[group].text())
        self.startingLabel[group] = QLabel("Mean Starting Energy (Min/Max): %0.1f ± %0.1f (%0.1f / %0.1f)" %
                                             (average_start, stdev_start, min_start, max_start))
        self.startingLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.startingLabel[group].text())
        self.deltascoresLabel[group] = QLabel("Mean Energy Difference Per Step (Min/Max): %0.1f ± %0.1f (%0.1f / %0.1f)" %
                                                (average_difference, stdev_difference, min_difference, max_difference))
        self.deltascoresLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.deltascoresLabel[group].text())
        # self.startingcompLabel[group] = QLabel("Average Starting Energy Per Compound: %0.1f ± %0.1f" %
        #                                          (average_start_compound, stdev_start_compound))
        # self.startingcompLabel[group].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.startingcompLabel[group].text())
        self.startingoverlapLabel[group] = QLabel("Mean Starting Overlaps (Min/Max): %0.1f ± %0.1f (%d / %d)" %
                                                    (average_start_overlap, stdev_start_overlap, min_start_overlap,
                                                     max_start_overlap))
        self.startingoverlapLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.startingoverlapLabel[group].text())
        self.finalLabel[group] = QLabel("Mean Final Energy (Min/Max): %0.1f ± %0.1f (%0.1f / %0.1f)" %
                                          (average_final, stdev_final, min_final, max_final))
        self.finalLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.finalLabel[group].text())
        # self.finalcompLabel[group] = QLabel("Average Final Energy Per Compound: %0.1f ± %0.1f" %
        #                                       (average_final_compound, stdev_final_compound))
        # self.finalcompLabel[group].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.finalcompLabel[group].text())
        self.finaloverlapLabel[group] = QLabel("Mean Final Overlaps (Min/Max): %0.1f ± %0.1f (%d / %d)" %
                                                 (average_final_overlap, stdev_final_overlap, min_final_overlap,
                                                  max_final_overlap))
        self.finaloverlapLabel[group].setAlignment(Qt.AlignCenter)
        self.summary[group].append(self.finaloverlapLabel[group].text())

    def saveResults(self, figures_only=False):
        try:
            optimize_path = os.path.join(self.params.work_dir, self.mixtures.optimize_folder)
            if not os.path.isdir(optimize_path):
                os.mkdir(optimize_path)
            if self.refine:
                for group in self.mixtures.group_mixnum:
                    if not group:
                        group_name = "_ALL"
                    else:
                        group_name = "_" + group
                    graphname = "refinement%s.png" % (group_name)
                    graphpath = os.path.join(optimize_path, graphname)
                    count = 1
                    while os.path.exists(graphpath):
                        graphname = "refinement%s%d.png" % (group_name, count)
                        graphpath = os.path.join(optimize_path, graphname)
                        count += 1
                    self.fig[group].set_size_inches(12, 8)
                    plt.savefig(graphpath, dpi=200)
                    if not figures_only:
                        summaryname = "refinement%s.txt" % (group_name)
                        summarypath = os.path.join(optimize_path, summaryname)
                        scoresname = "refinement%s.csv" % (group_name)
                        scorespath = os.path.join(optimize_path, scoresname)
                        self.generateResults(summarypath, scorespath, group)
                if not figures_only:
                    paramsname = "refinement_params.txt"
                    paramspath = os.path.join(optimize_path, paramsname)
                    self.generateParams(paramspath)
            else:
                for group in self.mixtures.group_mixnum:
                    if not group:
                        group_name = "_ALL"
                    else:
                        group_name = "_" + group
                    graphname = "optimization%s.png" % (group_name)
                    graphpath = os.path.join(optimize_path, graphname)
                    count = 1
                    while os.path.exists(graphpath):
                        graphname = "optimization%s%d.png" % (group_name, count)
                        graphpath = os.path.join(optimize_path, graphname)
                        count += 1
                    self.fig[group].set_size_inches(12, 8)
                    plt.savefig(graphpath, dpi=200)
                    if not figures_only:
                        summaryname = "optimization%s.txt" % (group_name)
                        summarypath = os.path.join(optimize_path, summaryname)
                        scoresname = "optimization%s.csv" % (group_name)
                        scorespath = os.path.join(optimize_path, scoresname)
                        self.generateResults(summarypath, scorespath, group)
                if not figures_only:
                    paramsname = "optimization_params.txt"
                    paramspath = os.path.join(optimize_path, paramsname)
                    self.generateParams(paramspath)
            if not figures_only:
                output_msg = "Optimization results output to: <font color='blue'>%s</font>" % (optimize_path)
                QMessageBox.information(self, 'Results Saved', output_msg)
            else:
                output_msg = "Optimization figures output to: <font color='blue'>%s</font>" % (optimize_path)
                QMessageBox.information(self, 'Results Saved', output_msg)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, 'Results NOT Saved!',
                                 "<font color='red'>Saving the results was unsuccessful. Please check folder permissions.</font>")


    def generateResults(self, summary_path, scores_path, group):
        with codecs.open(summary_path, 'w', encoding='utf-8') as summary:
            for item in self.summary[group]:
                summary.write("%s\n" % item)
        if self.fullResultsCheckbox.isChecked():
            with open(scores_path, 'w') as scoresfile:
                writer = csv.writer(scoresfile)
                header = ['Group', 'Iteration', 'Step', 'Current Temp', 'Current Score', 'New Score',
                          'Current Overlap', 'New Overlap', 'Total Peaks', 'Max Score', 'Probability', 'Result']
                writer.writerow(header)
                for i in self.anneal_scores[group]:
                    for step in self.anneal_scores[group][i]:
                        scores = list(step)
                        scores.insert(0, i+1)
                        scores.insert(0, group)
                        writer.writerow(scores)

    def generateParams(self, params_path):
        with codecs.open(params_path, 'w', encoding='utf-8') as params:
            params.write("Optimization Time: %s\n" % self.mixtures.optimize_duration)
            params.write("Max Mixture Size: %d\n" % self.params.mix_size)
            params.write("Iterations: %d\n" % self.params.iterations)
            params.write("Default Overlap Range: %0.3f\n" % self.params.peak_range)
            if self.params.use_intensity:
                params.write("Using Peak Intensity: True\n")
            else:
                params.write("Using Peak Intensity: False\n")
            params.write("Score Scale: %d\n" % self.params.score_scale)

            if self.refine:
                params.write("Start Temperature: %0.2f\n" % self.params.refine_start_temp)
                params.write("Final Temperature: %0.2f\n" % self.params.refine_final_temp)
                if self.params.refine_cooling == 'exponential':
                    params.write("Cooling Rate: Exponential\n")
                else:
                    params.write("Cooling Rate: Linear\n")
                params.write("Max Temperature Steps: %d\n" % self.params.refine_max_steps)
                params.write("Mix Rate: %d\n" % self.params.refine_mix_rate)
            else:
                if self.params.randomize_initial:
                    params.write("Random Initial Mixture: True\n")
                else:
                    params.write("Random Initial Mixture: False\n")
                params.write("Start Temperature: %0.2f\n" % self.params.start_temp)
                params.write("Final Temperature: %0.2f\n" % self.params.final_temp)
                if self.params.cooling == 'exponential':
                    params.write("Cooling Rate: Exponential\n")
                else:
                    params.write("Cooling Rate: Linear\n")
                params.write("Max Temperature Steps: %d\n" % self.params.max_steps)
                params.write("Mix Rate: %d\n" % self.params.mix_rate)

    def closeEvent(self, event=False):
        self.fig.clear()
        QDialog.accept(self)




