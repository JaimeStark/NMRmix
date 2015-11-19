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
        self.summary = []
        self.createMainFrame()
        self.createWidgets()
        self.createConnections()

    def createMainFrame(self):
        self.resultsTabs = QTabWidget()
        self.windowWidget = QWidget()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.windowWidget)
        self.fig = plt.gcf()
        self.fig.patch.set_facecolor('white')
        #self.fig.set_size_inches(12, 5)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(150)
        self.canvas.setMinimumWidth(150)
        self.mpl_toolbar = NavigationToolbar2(self.canvas, self)
        self.mpl_toolbar.hide()

    def createWidgets(self):
        winLayout = QVBoxLayout(self)
        widgetLayout = QVBoxLayout()

        statsLayout = QHBoxLayout()
        self.xLabel = QLabel("X-axis")
        self.xLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.xCombobox = QComboBox()
        self.xCombobox.addItems(['Steps', 'Temperature'])
        self.yLabel = QLabel("Y-axis")
        self.yLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.yCombobox = QComboBox()
        self.yCombobox.addItems(['Energy (Total)', 'Energy (Per Compound)', 'Energy Difference (Per Step)',
                                 'Peak Overlaps', 'Probabilities'])
        comboLayout = QHBoxLayout()
        comboLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
        comboLayout.addWidget(self.xLabel)
        comboLayout.addWidget(self.xCombobox)
        comboLayout.addItem(QSpacerItem(30,0, QSizePolicy.Maximum))
        comboLayout.addWidget(self.yLabel)
        comboLayout.addWidget(self.yCombobox)
        comboLayout.addItem(QSpacerItem(0,0, QSizePolicy.MinimumExpanding))
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
        self.numplots = len(self.mixtures.solvent_mixnum)
        self.curr_plot = 1
        for solvent in self.mixtures.solvent_mixnum:
            if self.refine:
                statlabel = "Refining"
            else:
                statlabel = "Optimizing"
            if not solvent:
                self.statsLabel[solvent] = QLabel("<b>%s Statistics</b>" % statlabel)
                self.summary.append('\n%s Statistics for All Mixtures' % statlabel)
            else:
                self.statsLabel[solvent] = QLabel("<b>%s Statistics for %s</b>" % (statlabel, solvent))
                self.summary.append('\n%s Statistics for %s Mixtures' % (statlabel, solvent))
            self.statsLabel[solvent].setAlignment(Qt.AlignCenter)
            self.calculateStats(solvent)
            solventLayout = QVBoxLayout()
            solventLayout.addWidget(self.statsLabel[solvent])
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
            statsLayout.addLayout(solventLayout)
            self.curr_plot += 1
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.saveButton = QPushButton("Save Results")
        self.closeButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.saveButton)
        widgetLayout.addWidget(self.canvas)
        widgetLayout.addLayout(comboLayout)
        widgetLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        widgetLayout.addLayout(statsLayout)
        widgetLayout.addItem(QSpacerItem(0, 15, QSizePolicy.Maximum))
        widgetLayout.addLayout(buttonLayout)
        self.windowWidget.setLayout(widgetLayout)
        winLayout.addWidget(self.scrollArea)
        self.fig.tight_layout(pad=4)
        self.canvas.draw()

    def createConnections(self):
        self.xCombobox.currentTextChanged.connect(self.updateStats)
        self.yCombobox.currentTextChanged.connect(self.updateStats)
        self.closeButton.clicked.connect(self.closeEvent)
        self.saveButton.clicked.connect(self.saveResults)

    def updateStats(self):
        self.fig.clear()
        self.curr_plot = 1
        for solvent in self.mixtures.solvent_mixnum:
            self.calculateStats(solvent)
            self.curr_plot += 1

    def calculateStats(self, solvent):
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
        subplot_num = "1%d%d" % (self.numplots, self.curr_plot)
        self.ax = self.fig.add_subplot(int(subplot_num))
        if not solvent:
            self.ax.set_title("%s of All Mixtures" % chart_title, fontweight='bold')
        else:
            self.ax.set_title("%s of %s Mixtures" % (chart_title, solvent), fontweight='bold')

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
                self.ax.set_xlabel("Optimization Step", fontweight='bold')
                self.ax.set_xlim([x[0], x[-1]])
            elif self.xCombobox.currentText() == 'Temperature':
                x = scores[iteration]['Temps']
                self.ax.set_xlabel("Optimization Temperature", fontweight='bold')
                self.ax.set_xlim([x[0], x[-1]])
            if self.yCombobox.currentText() == 'Energy (Total)':
                y = scores[iteration]['Scores']
                self.ax.set_ylabel("Total Mixtures Score", fontweight='bold')
            elif self.yCombobox.currentText() == 'Energy (Per Compound)':
                y = scores[iteration]['PerScores']
                self.ax.set_ylabel("Mixtures Score Per Compound", fontweight='bold')

            elif self.yCombobox.currentText() == 'Peak Overlaps':
                y = scores[iteration]['Overlaps']
                self.ax.set_ylabel("Total Peak Overlaps", fontweight='bold')

            elif self.yCombobox.currentText() == 'Energy Difference (Per Step)':
                y = scores[iteration]['DeltaScores']
                self.ax.set_ylabel("Total Mixtures Score Difference (Abs)", fontweight='bold')

            elif self.yCombobox.currentText() == 'Probabilities':
                y = scores[iteration]['Probabilities']
                if self.xCombobox.currentText() == 'Steps':
                    x = scores[iteration]['StepsProb']
                    self.ax.set_xlabel("Optimization Step", fontweight='bold')
                    self.ax.set_xlim([x[0], x[-1]])
                elif self.xCombobox.currentText() == 'Temperature':
                    x = scores[iteration]['TempsProb']
                    self.ax.set_xlabel("Optimization Temperature", fontweight='bold')
                    self.ax.set_xlim([x[0], x[-1]])
                self.ax.set_ylabel("Acceptance Probabilities", fontweight='bold')
            self.ax.plot(x, y, linewidth=2.0)
            self.canvas.draw()
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
        self.summary.append(self.totalmixturesLabel[solvent].text())
        self.totalcompLabel[solvent] = QLabel("Total Number of Compounds: %d" % len(self.mixtures.solvent_dict[solvent]))
        self.totalcompLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.totalcompLabel[solvent].text())
        self.totalpeaksLabel[solvent] = QLabel("Total Number of Peaks: %d" % num_peaks)
        self.totalpeaksLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.totalpeaksLabel[solvent].text())
        self.iterationsLabel[solvent] = QLabel("Number of Iterations: %d" % iterations)
        self.iterationsLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.iterationsLabel[solvent].text())
        self.startingLabel[solvent] = QLabel("Mean Starting Energy (Per Compound): %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                             (average_start, stdev_start,
                                              average_start / num_compounds, stdev_start / num_compounds))
        self.startingLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.startingLabel[solvent].text())
        self.deltascoresLabel[solvent] = QLabel("Mean Energy Difference Per Step (Min/Max): %0.1f ± %0.1f (%0.1f / %0.1f)" %
                                                (average_difference, stdev_difference, min_difference, max_difference))
        self.deltascoresLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.deltascoresLabel[solvent].text())
        # self.startingcompLabel[solvent] = QLabel("Average Starting Energy Per Compound: %0.1f ± %0.1f" %
        #                                          (average_start_compound, stdev_start_compound))
        # self.startingcompLabel[solvent].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.startingcompLabel[solvent].text())
        self.startingoverlapLabel[solvent] = QLabel("Mean Starting Overlaps: %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                                    (average_start_overlap, stdev_start_overlap,
                                                     average_start_overlap / num_compounds,
                                                     stdev_start_overlap / num_compounds))
        self.startingoverlapLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.startingoverlapLabel[solvent].text())
        self.finalLabel[solvent] = QLabel("Mean Final Energy (Per Compound): %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                          (average_final, stdev_final,
                                           average_final / num_compounds, stdev_final / num_compounds))
        self.finalLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.finalLabel[solvent].text())
        # self.finalcompLabel[solvent] = QLabel("Average Final Energy Per Compound: %0.1f ± %0.1f" %
        #                                       (average_final_compound, stdev_final_compound))
        # self.finalcompLabel[solvent].setAlignment(Qt.AlignCenter)
        # self.summary.append(self.finalcompLabel[solvent].text())
        self.finaloverlapLabel[solvent] = QLabel("Mean Final Overlaps: %0.1f ± %0.1f (%0.2f ± %0.2f)" %
                                                 (average_final_overlap, stdev_final_overlap,
                                                  average_final_overlap / num_compounds,
                                                  stdev_final_overlap / num_compounds))
        self.finaloverlapLabel[solvent].setAlignment(Qt.AlignCenter)
        self.summary.append(self.finaloverlapLabel[solvent].text())

    def saveResults(self):
        try:
            optimize_path = os.path.join(self.params.work_dir, self.mixtures.optimize_folder)
            if not os.path.isdir(optimize_path):
                os.mkdir(optimize_path)
            if self.refine:
                graphname = "refinement.png"
                graphpath = os.path.join(optimize_path, graphname)
                count = 1
                while os.path.exists(graphpath):
                    graphname = "refinement_%d.png" % count
                    graphpath = os.path.join(optimize_path, graphname)
                    count += 1
                summaryname = "refinement.txt"
                summarypath = os.path.join(optimize_path, summaryname)
                scoresname = "refinement.csv"
                scorespath = os.path.join(optimize_path, scoresname)
                paramsname = "refinement_params.txt"
                paramspath = os.path.join(optimize_path, paramsname)
                self.generateResults(summarypath, scorespath)
                self.generateParams(paramspath)
                output_msg = "Results saved to %s in working directory.<br><br>" \
                             "Refinement graphs: <font color='blue'>%s</font><br>" \
                             "Refinement summary stats: <font color='green'>%s</font><br>" \
                             "Refinement scores data: <font color='purple'>%s</font><br>" \
                             "Refinement parameters: <font color='orange'>%s</font>" % \
                             (self.mixtures.optimize_folder, graphname, summaryname, scoresname, paramsname)
            else:
                graphname = "optimization.png"
                graphpath = os.path.join(optimize_path, graphname)
                count = 1
                while os.path.exists(graphpath):
                    graphname = "optimization_%d.png" % count
                    graphpath = os.path.join(optimize_path, graphname)
                    count += 1
                summaryname = "optimization.txt"
                summarypath = os.path.join(optimize_path, summaryname)
                scoresname = "optimization.csv"
                scorespath = os.path.join(optimize_path, scoresname)
                paramsname = "optimization_params.txt"
                paramspath = os.path.join(optimize_path, paramsname)
                self.generateResults(summarypath, scorespath)
                self.generateParams(paramspath)
                output_msg = "Results saved to %s in working directory.<br><br>" \
                             "Optimization graphs: <font color='blue'>%s</font><br>" \
                             "Optimization summary stats: <font color='green'>%s</font><br>" \
                             "Optimization scores data: <font color='purple'>%s</font><br>" \
                             "Optimization parameters: <font color='orange'>%s</font>" % \
                             (self.mixtures.optimize_folder, graphname, summaryname, scoresname, paramsname)
            self.fig.set_size_inches(12, 8)
            plt.savefig(graphpath, dpi=200)
            # TODO: Save summary result
            # TODO: Save full scores
            QMessageBox.information(self, 'Results Saved', output_msg)
        except Exception as e:
            print(e)
            QMessageBox.critical(self, 'Results NOT Saved!',
                                 "Saving the results was unsuccessful. Please check folder permissions.")

    def generateResults(self, summary_path, scores_path):
        with codecs.open(summary_path, 'w', encoding='utf-8') as summary:
            for item in self.summary:
                summary.write("%s\n" % item)
        with open(scores_path, 'w') as scoresfile:
            writer = csv.writer(scoresfile)
            header = ['Solvent', 'Iteration', 'Step', 'Current Temp', 'Current Score', 'New Score',
                      'Current Overlap', 'New Overlap', 'Total Peaks', 'Max Score', 'Probability', 'Result']
            writer.writerow(header)
            for solvent in self.anneal_scores:
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
            params.write("Score Exponent: %d\n" % self.params.score_power)
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




