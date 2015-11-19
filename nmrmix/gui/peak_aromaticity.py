#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
peak_count.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy as np
import os

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2

class Window(QDialog):
    def __init__(self, params_object, library_object, solvent, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.solvent = solvent
        matplotlib.projections.register_projection(My_Axes)
        self.region_colors = {0:'gray', 1:'red', 2:'green', 3:'orange', 4:'teal', 5:'pink',
                              6:'cyan', 7:'magenta', 8:'gold'}
        if self.solvent == 'ALL':
            self.plural_solvent = "s"
        else:
            self.plural_solvent = ""
        self.setWindowTitle("NMRmix: Peak Aromaticity Histogram for %s Solvent%s" % (self.solvent, self.plural_solvent))
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.scale = 1.05
        self.mean = np.mean(self.library.stats[solvent]['Aromaticity'])
        self.stdev = np.std(self.library.stats[solvent]['Aromaticity'])
        self.median = np.median(self.library.stats[solvent]['Aromaticity'])
        self.createMainFrame()

    def createMainFrame(self):
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
        # self.mpl_toolbar.pan()
        self.canvas.mpl_connect('scroll_event', self.zooming)
        ins = "Left-click+drag to pan x-axis / Right-click+drag to zoom x-axis"
        self.instructionLabel = QLabel(ins)
        self.instructionLabel.setStyleSheet('QLabel{qproperty-alignment: AlignCenter; font-size: 12px;}')
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.closeButton.clicked.connect(self.closeEvent)
        self.saveButton = QPushButton("Save")
        self.saveButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        self.saveButton.clicked.connect(self.saveResults)
        self.resetButton = QPushButton("Reset")
        self.resetButton.setStyleSheet("QPushButton{color: blue; font-weight: bold;}")
        self.resetButton.clicked.connect(self.resetGraph)
        self.calculateHistogram()
        winLayout = QVBoxLayout(self)
        winLayout.addWidget(self.canvas)
        winLayout.addWidget(self.instructionLabel)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.resetButton)
        buttonLayout.addWidget(self.saveButton)
        winLayout.addLayout(buttonLayout)
        self.fig.tight_layout(pad=3)
        self.canvas.draw()

    def calculateHistogram(self):
        self.ax = self.fig.add_subplot(111, projection="My_Axes")
        self.ax.set_title("Peak Aromaticity Histogram for %s Solvent%s" % (self.solvent, self.plural_solvent),
                          fontweight='bold')
        self.ax.set_xlabel("Percentage of Aromatic Peaks (aromatic >= %0.3f ppm)" % self.params.aromatic_cutoff, fontweight='bold')
        self.ax.set_ylabel("Number of Compounds", fontweight='bold')
        data = list(self.library.stats[self.solvent]['Aromaticity'])
        self.ax.hist(data, bins=range(0, 110, 10), color='red', alpha=0.75, rwidth=0.9)
        self.ax.xaxis.set_ticks_position('none')
        self.ax.yaxis.set_ticks_position('none')
        self.ax.annotate("Mean: %.1f %%" % (self.mean), xy=(0.70, 0.82), xycoords='figure fraction',
                         horizontalalignment='left')
        self.ax.annotate("Median: %.0f %%" % (self.median), xy=(0.70, 0.79), xycoords='figure fraction',
                         horizontalalignment='left')

    def resetGraph(self):
        self.mpl_toolbar.home()

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

    def saveResults(self):
        filename = "peakaromaticity.png"
        filepath = os.path.join(self.params.work_dir, filename)
        filestype = "static (*.png *.jpg *.svg)"
        fileObj = QFileDialog.getSaveFileName(self, caption="Save Peak Stats Plot", directory=filepath, filter=filestype)
        if fileObj[0]:
            self.fig.set_size_inches(12, 8)
            plt.savefig(fileObj[0], dpi=200)

    def closeEvent(self, event=False):
        self.fig.clear()
        QDialog.reject(self)

class My_Axes(matplotlib.axes.Axes):
    name = "My_Axes"
    def drag_pan(self, button, key, x, y):
        matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y)