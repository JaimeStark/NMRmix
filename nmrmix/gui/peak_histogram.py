#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
peak_histogram.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy as np
import math
import os

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2

class Window(QDialog):
    def __init__(self, params_object, library_object, group, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.group = group
        matplotlib.projections.register_projection(My_Axes)
        self.region_colors = {0:'gray', 1:'red', 2:'green', 3:'orange', 4:'teal', 5:'pink',
                              6:'cyan', 7:'magenta', 8:'gold'}
        if self.group == 'ALL':
            self.plural_group = "s"
        else:
            self.plural_group = ""
        self.setWindowTitle("NMRmix: Peaks Histogram for %s Group%s" % (self.group, self.plural_group))
        self.scale = 1.05
        self.setAttribute(Qt.WA_DeleteOnClose, True)
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
        self.mpl_toolbar.pan()
        self.canvas.mpl_connect('scroll_event', self.zooming)
        ins = "Left-click+drag to pan x-axis / Right-click+drag to zoom x-axis"
        self.instructionLabel = QLabel(ins)
        self.instructionLabel.setStyleSheet('QLabel{qproperty-alignment: AlignCenter; font-size: 12px;}')

        self.showignoredregionsCheckBox = QCheckBox("Show Ignored Regions")
        self.showignoredregionsCheckBox.setChecked(True)
        self.showignoredregionsCheckBox.setToolTip("Tooltip") # TODO: Tooltip
        self.showignoredregionsCheckBox.stateChanged.connect(self.handleIgnored)
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.closeButton.clicked.connect(self.closeEvent)
        self.saveButton = QPushButton("Save")
        self.saveButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        self.saveButton.clicked.connect(self.saveResults)
        self.resetButton = QPushButton("Reset")
        self.resetButton.setStyleSheet("QPushButton{color: blue; font-weight: bold;}")
        self.resetButton.clicked.connect(self.resetGraph)
        self.calculateAllHistogram()
        self.calculateIntenseHistogram()
        self.drawIgnoredRegions()
        winLayout = QVBoxLayout(self)
        winLayout.addWidget(self.canvas)
        winLayout.addWidget(self.instructionLabel)
        winLayout.addWidget(self.showignoredregionsCheckBox)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.resetButton)
        buttonLayout.addWidget(self.saveButton)
        winLayout.addLayout(buttonLayout)
        winLayout.setAlignment(self.showignoredregionsCheckBox, Qt.AlignCenter)
        self.fig.tight_layout(pad=3)
        self.canvas.draw()

    def calculateAllHistogram(self):
        self.ax1 = self.fig.add_subplot(211, projection="My_Axes")
        self.ax1.set_title("Peaks Histogram for %s Group%s" % (self.group, self.plural_group), fontweight='bold')
        self.ax1.set_xlabel("Chemical Shift (ppm)", fontweight='bold')
        self.ax1.set_ylabel("Number of Peaks", fontweight='bold')
        data = list(self.library.stats[self.group]['Peaklist'])
        y, binEdges = np.histogram(data, bins=np.arange(-1, 12, 0.02))
        bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
        self.ax1.set_xlim(self.params.shift_range[self.params.nuclei])
        self.upper_ylim_all = max(y)+(math.ceil(max(y)*0.05))
        self.ax1.set_ylim([0, self.upper_ylim_all])
        self.ax1.plot(bincenters, y, '-', color='blue')

    def calculateIntenseHistogram(self):
        self.ax2 = self.fig.add_subplot(212, sharex=self.ax1, projection="My_Axes")
        self.ax2.set_title("Intense Peaks Histogram for %s Group%s" % (self.group, self.plural_group),
                           fontweight='bold')
        self.ax2.set_xlabel("Chemical Shift (ppm)", fontweight='bold')
        self.ax2.set_ylabel("Number of Peaks", fontweight='bold')
        data = list(self.library.stats[self.group]['Intense Peaklist'])
        y, binEdges = np.histogram(data, bins=np.arange(-1, 12, 0.02))
        bincenters = 0.5 * (binEdges[1:] + binEdges[:-1])
        self.ax2.set_xlim([12, -1])
        self.upper_ylim_intense = max(y)+(math.ceil(max(y)*0.05))
        self.ax2.set_ylim([0, self.upper_ylim_intense])
        self.ax2.plot(bincenters, y, '-', color='purple')

    def resetGraph(self):
        self.mpl_toolbar.home()

    def drawIgnoredRegions(self):
        groups = ['ALL']
        if self.group != 'ALL':
            groups.append(self.group)
        for region in self.library.ignored_regions:
            group = self.library.ignored_regions[region][2]
            if self.group == 'ALL':
                if group not in groups:
                    groups.append(group)
        for region in self.library.ignored_regions:
            lower_bound = self.library.ignored_regions[region][0]
            upper_bound = self.library.ignored_regions[region][1]
            group = self.library.ignored_regions[region][2]
            if group in groups:
                color = self.region_colors[groups.index(group)]
                bar_width = abs(upper_bound - lower_bound)
                bar_center = (lower_bound + upper_bound) / 2
                self.ax1.bar(bar_center, self.upper_ylim_all, width=bar_width, color=color, align='center', edgecolor=color,
                             linewidth=1, alpha=0.4)
                self.ax2.bar(bar_center, self.upper_ylim_intense, width=bar_width, color=color, align='center',
                             edgecolor=color, linewidth=1, alpha=0.4)
            else:
                continue

    def handleIgnored(self):
        if self.showignoredregionsCheckBox.isChecked():
            self.fig.clear()
            self.calculateAllHistogram()
            self.calculateIntenseHistogram()
            self.drawIgnoredRegions()
            self.canvas.draw()
        else:
            self.fig.clear()
            self.calculateAllHistogram()
            self.calculateIntenseHistogram()
            self.canvas.draw()

    def zooming(self, event):
        cur_ylim1 = self.ax1.get_ylim()
        cur_ylim2 = self.ax2.get_ylim()
        cur_yrange1 = (cur_ylim1[1] - cur_ylim1[0])
        cur_yrange2 = (cur_ylim2[1] - cur_ylim2[0])
        if event.button == 'up':
            scale_factor = self.scale
        elif event.button == 'down':
            scale_factor = 1/self.scale
        else:
            scale_factor = 1

        self.ax1.set_ylim([0, (cur_yrange1*scale_factor)])
        self.ax2.set_ylim([0, (cur_yrange2*scale_factor)])
        self.canvas.draw()

    def saveResults(self):
        filename = "peakstats.png"
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