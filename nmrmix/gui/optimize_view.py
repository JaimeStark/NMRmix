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
    import unicodecsv as csv

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
        #self.createMainFrame()
        self.createWidgets()
        self.createConnections()

    #def createMainFrame(self):
        #self.resultsTabs = QTabWidget()
        #self.windowWidget = QWidget()
        # self.scrollArea = QScrollArea()
        # self.scrollArea.setWidgetResizable(True)
        # self.scrollArea.setWidget(self.windowWidget)
        # self.fig = plt.gcf()
        # self.fig.patch.set_facecolor('white')
        # #self.fig.set_size_inches(12, 5)
        # self.canvas = FigureCanvas(self.fig)
        # self.canvas.setMinimumHeight(150)
        # self.canvas.setMinimumWidth(150)
        # self.mpl_toolbar = NavigationToolbar2(self.canvas, self)
        # self.mpl_toolbar.hide()

    def createWidgets(self):
        winLayout = QVBoxLayout(self)
        winLayout.setAlignment(Qt.AlignCenter)
        self.resultsTabs = QTabWidget()
        self.resultsTabs.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.resultsTabs.setStyleSheet('QTabBar {font-weight: bold;}'
                                     'QTabBar::tab {color: black;}'
                                     'QTabBar::tab:selected {color: red;}')
        #widgetLayout = QVBoxLayout()


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
        # self.startingcompLabel = {}
        self.startingoverlapLabel = {}
        self.deltascoresLabel = {}
        self.finalLabel = {}
        # self.finalcompLabel = {}
        self.finaloverlapLabel = {}
        self.solventTab = {}

        # solventLayout = {}
        # self.numplots = len(self.mixtures.solvent_mixnum)
        #self.curr_plot = 1
        for i, solvent in enumerate(self.mixtures.solvent_mixnum):
            self.summary[solvent] = []
            self.solventTab[solvent] = QWidget()
            self.solventTab[solvent].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
            if self.refine:
                statlabel = "Refining"
            else:
                statlabel = "Optimizing"
            if not solvent:
                self.statsLabel[solvent] = QLabel("<b>%s Statistics</b>" % statlabel)
                self.summary[solvent].append('\n%s Statistics for All Mixtures' % statlabel)
            else:
                self.statsLabel[solvent] = QLabel("<b>%s Statistics for %s</b>" % (statlabel, solvent))
                self.summary[solvent].append('\n%s Statistics for %s Mixtures' % (statlabel, solvent))
            self.statsLabel[solvent].setAlignment(Qt.AlignCenter)
            self.fig[solvent] = plt.figure(i)
            self.fig[solvent].patch.set_facecolor('white')
            self.canvas[solvent] = FigureCanvas(self.fig[solvent])
            self.canvas[solvent].setMinimumHeight(150)
            self.canvas[solvent].setMinimumWidth(150)
            self.calculateStats(i, solvent)
            self.mpl_toolbar[solvent] = NavigationToolbar2(self.canvas[solvent], self)
            self.mpl_toolbar[solvent].hide()
            solventLayout = QVBoxLayout()
            #solventLayout.addWidget(self.statsLabel[solvent])
            solventLayout.addWidget(self.canvas[solvent], Qt.AlignCenter)
            #solventLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
            solventLayout.addWidget(self.totalcompLabel[solvent])
            solventLayout.addWidget(self.totalpeaksLabel[solvent])
            solventLayout.addWidget(self.iterationsLabel[solvent])
            solventLayout.addWidget(self.startingLabel[solvent])
            solventLayout.addWidget(self.finalLabel[solvent])
            solventLayout.addWidget(self.deltascoresLabel[solvent])
            # solventLayout.addWidget(self.startingcompLabel[solvent])
            # solventLayout.addWidget(self.finalcompLabel[solvent])
            solventLayout.addWidget(self.startingoverlapLabel[solvent])
            solventLayout.addWidget(self.finaloverlapLabel[solvent])
            # TODO: Add best score and overlap
            self.solventTab[solvent].setLayout(solventLayout)
            if not solvent:
                self.resultsTabs.addTab(self.solventTab[solvent], "ALL")
            else:
                self.resultsTabs.addTab(self.solventTab[solvent], solvent)
            self.fig[solvent].tight_layout(pad=4)
            self.canvas[solvent].draw()
            #statsLayout.addLayout(solventLayout)
            #self.curr_plot += 1
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
        #widgetLayout.addWidget(self.canvas[solvent])
        #widgetLayout.addLayout(comboLayout)
        winLayout.addWidget(self.resultsTabs)
        winLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        winLayout.addLayout(comboLayout)
        # winLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        # winLayout.addWidget(self.fullResultsCheckbox)
        winLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        winLayout.addLayout(buttonLayout)
        #self.windowWidget.setLayout(winLayout)
        # for solvent in self.mixtures.solvent_mixnum:
        #     self.fig[solvent].tight_layout(pad=4)
        #     self.canvas[solvent].draw()

    def createConnections(self):
        self.xCombobox.currentTextChanged.connect(self.updateStats)
        self.yCombobox.currentTextChanged.connect(self.updateStats)
        self.closeButton.clicked.connect(self.closeEvent)
        self.saveFigButton.clicked.connect(lambda: self.saveResults(figures_only=True))
        self.saveButton.clicked.connect(self.saveResults)

    def updateStats(self):
        #self.curr_plot = 1
        for i, solvent in enumerate(self.mixtures.solvent_mixnum):
            self.fig[solvent].clear()
            self.calculateStats(i, solvent)
            # self.curr_plot += 1

    def calculateStats(self, solvent_key, solvent):
        scores = {}
        best_iteration_score = 99999999999
        iterations = len(self.mixtures.anneal_scores[solvent])
        num_compounds = len(self.mixtures.solvent_dict[solvent])
        starting_energy = []
        final_energy = []
        starting_overlaps = []
        final_overlaps = []
        delta_scores = []
        if self.refine:
            chart_title = "Refinement"
        else:
            chart_title = "Optimization"
        #subplot_num = "1%d%d" % (self.numplots, self.curr_plot)
        plt.figure(solvent_key)
        if not solvent:
            plt.title("%s of All Mixtures" % chart_title, fontweight='bold')
        else:
            plt.title("%s of %s Mixtures" % (chart_title, solvent), fontweight='bold')

        for iteration in self.mixtures.anneal_scores[solvent]:
            scores[iteration] = {}
            iteration_list = list(self.anneal_scores[solvent][iteration])
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

            # elif self.yCombobox.currentText() == 'Probabilities':
            #     y = scores[iteration]['Probabilities']
            #     if self.xCombobox.currentText() == 'Steps':
            #         x = scores[iteration]['StepsProb']
            #         plt.xlabel("Optimization Step", fontweight='bold')
            #         plt.xlim([x[0], x[-1]])
            #     elif self.xCombobox.currentText() == 'Temperature':
            #         x = scores[iteration]['TempsProb']
            #         plt.xlabel("Optimization Temperature", fontweight='bold')
            #         plt.xlim([x[0], x[-1]])
            #     plt.ylabel("Acceptance Probabilities", fontweight='bold')
            plt.plot(x, y, linewidth=2.0)
            self.canvas[solvent].draw()
        average_start = np.mean(starting_energy)
        average_final = np.mean(final_energy)
        average_difference = np.mean(delta_scores)
        max_difference = max(delta_scores)
        min_difference = min(delta_scores)
        average_start_overlap = np.mean(starting_overlaps)
        average_final_overlap = np.mean(final_overlaps)
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

        self.totalmixturesLabel[solvent] = QLabel("Total Number of Mixtures: %d" % len(self.mixtures.solvent_mixnum[solvent]))
        self.totalmixturesLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.totalmixturesLabel[solvent].text())
        self.totalcompLabel[solvent] = QLabel("Total Number of Compounds: %d" % len(self.mixtures.solvent_dict[solvent]))
        self.totalcompLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.totalcompLabel[solvent].text())
        self.totalpeaksLabel[solvent] = QLabel("Total Number of Peaks: %d" % num_peaks)
        self.totalpeaksLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.totalpeaksLabel[solvent].text())
        self.iterationsLabel[solvent] = QLabel("Number of Iterations: %d" % iterations)
        self.iterationsLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.iterationsLabel[solvent].text())
        self.startingLabel[solvent] = QLabel("Mean Starting Energy (Per Compound): %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                             (average_start, stdev_start,
                                              average_start / num_compounds, stdev_start / num_compounds))
        self.startingLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.startingLabel[solvent].text())
        self.deltascoresLabel[solvent] = QLabel("Mean Energy Difference Per Step (Min/Max): %0.1f ± %0.1f (%0.1f / %0.1f)" %
                                                (average_difference, stdev_difference, min_difference, max_difference))
        self.deltascoresLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.deltascoresLabel[solvent].text())
        # self.startingcompLabel[solvent] = QLabel("Average Starting Energy Per Compound: %0.1f ± %0.1f" %
        #                                          (average_start_compound, stdev_start_compound))
        # self.startingcompLabel[solvent].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.startingcompLabel[solvent].text())
        self.startingoverlapLabel[solvent] = QLabel("Mean Starting Overlaps: %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                                    (average_start_overlap, stdev_start_overlap,
                                                     average_start_overlap / num_compounds,
                                                     stdev_start_overlap / num_compounds))
        self.startingoverlapLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.startingoverlapLabel[solvent].text())
        self.finalLabel[solvent] = QLabel("Mean Final Energy (Per Compound): %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                          (average_final, stdev_final,
                                           average_final / num_compounds, stdev_final / num_compounds))
        self.finalLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.finalLabel[solvent].text())
        # self.finalcompLabel[solvent] = QLabel("Average Final Energy Per Compound: %0.1f ± %0.1f" %
        #                                       (average_final_compound, stdev_final_compound))
        # self.finalcompLabel[solvent].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.finalcompLabel[solvent].text())
        self.finaloverlapLabel[solvent] = QLabel("Mean Final Overlaps: %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                                 (average_final_overlap, stdev_final_overlap,
                                                  average_final_overlap / num_compounds,
                                                  stdev_final_overlap / num_compounds))
        self.finaloverlapLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary[solvent].append(self.finaloverlapLabel[solvent].text())

    def saveResults(self, figures_only=False):
        try:
            optimize_path = os.path.join(self.params.work_dir, self.mixtures.optimize_folder)
            if not os.path.isdir(optimize_path):
                os.mkdir(optimize_path)
            if self.refine:
                for solvent in self.mixtures.solvent_mixnum:
                    if not solvent:
                        solvent_name = "_ALL"
                    else:
                        solvent_name = "_" + solvent
                    graphname = "refinement%s.png" % (solvent_name)
                    graphpath = os.path.join(optimize_path, graphname)
                    count = 1
                    while os.path.exists(graphpath):
                        graphname = "refinement%s%d.png" % (solvent_name, count)
                        graphpath = os.path.join(optimize_path, graphname)
                        count += 1
                    self.fig[solvent].set_size_inches(12, 8)
                    plt.savefig(graphpath, dpi=200)
                    if not figures_only:
                        summaryname = "refinement%s.txt" % (solvent_name)
                        summarypath = os.path.join(optimize_path, summaryname)
                        scoresname = "refinement%s.csv" % (solvent_name)
                        scorespath = os.path.join(optimize_path, scoresname)
                        self.generateResults(summarypath, scorespath, solvent)
                if not figures_only:
                    paramsname = "refinement_params.txt"
                    paramspath = os.path.join(optimize_path, paramsname)
                    self.generateParams(paramspath)
            else:
                for solvent in self.mixtures.solvent_mixnum:
                    if not solvent:
                        solvent_name = "_ALL"
                    else:
                        solvent_name = "_" + solvent
                    graphname = "optimization%s.png" % (solvent_name)
                    graphpath = os.path.join(optimize_path, graphname)
                    count = 1
                    while os.path.exists(graphpath):
                        graphname = "optimization%s%d.png" % (solvent_name, count)
                        graphpath = os.path.join(optimize_path, graphname)
                        count += 1
                    self.fig[solvent].set_size_inches(12, 8)
                    plt.savefig(graphpath, dpi=200)
                    if not figures_only:
                        summaryname = "optimization%s.txt" % (solvent_name)
                        summarypath = os.path.join(optimize_path, summaryname)
                        scoresname = "optimization%s.csv" % (solvent_name)
                        scorespath = os.path.join(optimize_path, scoresname)
                        self.generateResults(summarypath, scorespath, solvent)
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


    def generateResults(self, summary_path, scores_path, solvent):
        with codecs.open(summary_path, 'w', encoding='utf-8') as summary:
            for item in self.summary[solvent]:
                summary.write("%s\n" % item)
        if self.fullResultsCheckbox.isChecked():
            with open(scores_path, 'wb') as scoresfile:
                writer = csv.writer(scoresfile)
                header = ['Solvent', 'Iteration', 'Step', 'Current Temp', 'Current Score', 'New Score',
                          'Current Overlap', 'New Overlap', 'Total Peaks', 'Max Score', 'Probability', 'Result']
                writer.writerow(header)
                for i in self.anneal_scores[solvent]:
                    for step in self.anneal_scores[solvent][i]:
                        scores = list(step)
                        scores.insert(0, i+1)
                        scores.insert(0, solvent)
                        writer.writerow(scores)

    def generateParams(self, params_path):
        with codecs.open(params_path, 'w', encoding='utf-8') as params:
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




