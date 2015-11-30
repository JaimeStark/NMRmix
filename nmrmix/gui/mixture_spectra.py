#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mixture_spectra.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar2

from gui import compound_info
    
class Window(QDialog):
    def __init__(self, params_object, library_object, compound_list, mixture_id, parent=None):
        QDialog.__init__(self, parent)
        matplotlib.projections.register_projection(My_Axes)
        self.library = library_object
        self.params = params_object
        self.compounds = list(compound_list)
        self.mixture_id = mixture_id
        self.show_list = list(compound_list)
        self.compound_colors = {0:'red', 1:'blue', 2:'green', 3:'orange', 4:'purple', 5:'teal', 6:'pink', 7:'gray',
                                8:'cyan', 9:'magenta', 10:'gold', 11:'brown', 12:'olive', 13:'yellow', 14:'maroon',
                                15: 'darkseagreen', 16:'darksalmon', 17:'turquoise', 18:'khaki', 19:'crimson'}
        self.scale = 1.05
        self.show_rois = True
        self.show_full_rois = False
        self.show_ignored = False
        self.show_ignored_peaks = False
        self.show_positive_overlap = False
        self.setWindowTitle("NMRmix: Simulated Spectra of Mixture %s" % self.mixture_id)
        self.createMainFrame()
        self.drawData()

    def createMainFrame(self):
        self.fig = plt.gcf()
        self.fig.patch.set_facecolor('white')
        self.fig.set_size_inches(12, 5)
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
        self.showroisCheckBox = QCheckBox("Show Unoverlapped ROIs")
        self.showroisCheckBox.setStyleSheet('QCheckBox{font-size: 12px;}')
        self.showroisCheckBox.setToolTip("Shows the regions of interest around every non-overlapped peak.\n"
                                         "Useful for visualizing the regions that should be monitored in this mixture.")
        self.showroisCheckBox.setChecked(True)
        self.showfullroisCheckBox = QCheckBox("Show Complete ROIs")
        self.showfullroisCheckBox.setStyleSheet('QCheckBox{font-size: 12px;}')
        self.showfullroisCheckBox.setToolTip("Shows the regions of interest around every peak regardless of whether\n"
                                             "it is overlapped or not. Useful for visualizing the magnitude of overlaps.")
        self.showignoredregionsCheckBox = QCheckBox("Show Ignored Regions")
        self.showignoredregionsCheckBox.setStyleSheet('QCheckBox{font-size: 12px;}')
        self.showignoredregionsCheckBox.setToolTip("Shows the ranges set by the solvent/buffer ignore regions, if any.")
        self.showignoredpeaksCheckBox = QCheckBox("Show Ignored Peaks")
        self.showignoredpeaksCheckBox.setStyleSheet('QCheckBox{font-size: 12px;}')
        self.showignoredpeaksCheckBox.setToolTip("Shows any compound peaks that are in the solvent/buffer ignore regions, if any.\n"
                                                 "These peaks are ignored and are not evaluated during mixing.")
        self.showpositiveoverlapCheckBox = QCheckBox("Show Overlaps as Positive")
        self.showpositiveoverlapCheckBox.setStyleSheet('QCheckBox{font-size: 12px;}')
        self.showpositiveoverlapCheckBox.setToolTip("By default, peaks that overlap are shown as negative peaks.\n"
                                                    "This option allows for these peaks to be shown as positive peaks.")
        self.resetButton = QPushButton("Reset")
        self.resetButton.setStyleSheet("QPushButton{color: orange; font-weight: bold;}")
        self.resetButton.setToolTip("Resets the spectral view to the default view.")
        self.saveButton = QPushButton("Save")
        self.saveButton.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        self.saveButton.setToolTip("Saves the image in the spectra window.")
        self.closeButton = QPushButton("Close")
        self.closeButton.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.closeButton.setToolTip("Closes this window.")
        vbox = QVBoxLayout(self)
        self.spectraLabel = QLabel("Simulated Spectra of Mixture %s" % self.mixture_id)
        self.spectraLabel.setStyleSheet('QLabel{color: red; font-weight: bold; qproperty-alignment: AlignCenter; '
                                        'font-size: 14px;}')
        self.spectraLabel.setToolTip("Shows the simulated spectra of the compounds in this mixture based solely on peaklists.\n"
                                     "Peaks are drawn based on a Lorentzian shape.")
        vbox.addWidget(self.spectraLabel)
        vbox.addWidget(self.canvas)
        ins = "Left-click+drag to pan x-axis / Right-click+drag to zoom x-axis / Scroll-wheel to change intensity scale"
        self.instructionLabel = QLabel(ins)
        self.instructionLabel.setStyleSheet('QLabel{qproperty-alignment: AlignCenter; font-size: 12px;}')
        vbox.addWidget(self.instructionLabel)
        gridbox = QGridLayout()
        self.compound_legend = {}
        for i, compound in enumerate(self.show_list):
            self.compound_legend[i] = QPushButtonRight(str(compound))
            self.compound_legend[i].setStyleSheet("QPushButton {background-color: %s; font-weight: bold;}" % self.compound_colors[i])
            self.compound_legend[i].leftClicked.connect(self.handleLegend)
            self.compound_legend[i].rightClicked.connect(self.handleCompoundButtonRight)
            self.compound_legend[i].setToolTip("Left-click to toggle the spectra for this compound.\n"
                                               "Right-click to show compound infomation.")

            row = int(i / 6)
            column = i % 6
            gridbox.addWidget(self.compound_legend[i], row, column)
        vbox.addLayout(gridbox)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.showroisCheckBox)
        hbox1.addWidget(self.showfullroisCheckBox)
        hbox1.addWidget(self.showignoredregionsCheckBox)
        hbox1.addWidget(self.showignoredpeaksCheckBox)
        hbox1.addWidget(self.showpositiveoverlapCheckBox)


        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.closeButton)
        hbox2.addWidget(self.resetButton)
        hbox2.addWidget(self.saveButton)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.showroisCheckBox.stateChanged.connect(self.handleROIs)
        self.showfullroisCheckBox.stateChanged.connect(self.handleFullROIs)
        self.showignoredregionsCheckBox.stateChanged.connect(self.handleIgnored)
        self.showignoredpeaksCheckBox.stateChanged.connect(self.handleIgnoredPeaks)
        self.showpositiveoverlapCheckBox.stateChanged.connect(self.handleOverlapPeaks)
        self.resetButton.clicked.connect(self.resetSpectra)
        self.saveButton.clicked.connect(self.saveSpectra)
        self.closeButton.clicked.connect(self.closeEvent)

        self.showroisCheckBox.isChecked()

    def handleLegend(self):
        button = self.sender()
        compound = str(button.text())
        i = self.compounds.index(compound)
        if compound in self.show_list:
            button.setStyleSheet("background-color: white; font-weight: normal;")
            self.show_list[i] = None
            self.drawData()
        else:
            button.setStyleSheet("background-color: %s; font-weight: bold;" % self.compound_colors[i])
            self.show_list[i] = compound
            self.drawData()

    def handleCompoundButtonRight(self):
        button = self.sender()
        compound = str(button.text())
        compound_obj = self.library.library[compound]
        compound_win = compound_info.Window(self.params, compound_obj, editable_peaklist=False)
        compound_win.exec_()

    def handleROIs(self):
        if self.showroisCheckBox.isChecked():
            self.show_rois = True
            self.drawData()
        else:
            self.show_rois = False
            self.drawData()

    def handleFullROIs(self):
        if self.showfullroisCheckBox.isChecked():
            self.show_full_rois = True
            self.drawData()
        else:
            self.show_full_rois = False
            self.drawData()

    def handleIgnored(self):
        if self.showignoredregionsCheckBox.isChecked():
            self.show_ignored = True
            self.drawData()
        else:
            self.show_ignored = False
            self.drawData()

    def handleIgnoredPeaks(self):
        if self.showignoredpeaksCheckBox.isChecked():
            self.show_ignored_peaks = True
            self.drawData()
        else:
            self.show_ignored_peaks = False
            self.drawData()

    def handleOverlapPeaks(self):
        if self.showpositiveoverlapCheckBox.isChecked():
            self.show_positive_overlap = True
            self.drawData()
        else:
            self.show_positive_overlap = False
            self.drawData()

    def resetSpectra(self):
        self.mpl_toolbar.home()
        self.drawData()

    def saveSpectra(self):
        filename = "%s.png" % self.mixture_id
        filepath = os.path.join(self.params.work_dir, filename)
        filestype = "static (*.png *.jpg *.svg)"
        fileObj = QFileDialog.getSaveFileName(self, caption="Save Simulated Mixture Spectrum", directory=filepath,
                                              filter=filestype)
        if fileObj[0]:
            self.fig.set_size_inches(12, 8)
            plt.savefig(fileObj[0], dpi=200)

    def lorentzian(self, mu, hwhm, intensity):
        def f(x):
            numerator = hwhm ** 2
            denominator = pow((x - mu), 2) + (hwhm ** 2)
            total = intensity * (numerator / denominator)
            return(total)
        return(f)

    def drawPeakData(self, peaks, i, alpha=1.0):
        for peak in peaks:
            if len(peak) == 3:
            #     hwhm = peak[2] / 10
                width = peak[2] * 3
            else:
                width = self.params.peak_range * 3
            #     hwhm = self.params.peak_range / 10
            hwhm = self.params.peak_display_width / 2
            mean = peak[0]
            intensity = peak[1]
            shifts = (np.arange(mean-width, mean+width, 0.001))
            f = self.lorentzian(mean, hwhm, intensity)
            y = ([f(x) for x in shifts])
            self.ax.plot(shifts, y, color=self.compound_colors[i], linewidth=1, alpha=alpha)

    def drawRoiData(self, rois, i):
        for roi in rois:
            roi_width = abs(roi[1] - roi[0])
            roi_center = (roi[1] + roi[0]) / 2
            self.ax.bar(roi_center, 100, width=roi_width, color=self.compound_colors[i], align='center',
                        edgecolor=self.compound_colors[i], linewidth=1, alpha=0.2, picker=True)

    def drawIgnoredRegions(self, ignored_list):
        updated_ignored = list(set(ignored_list))
        for ignored in updated_ignored:
            ignored_width = abs(ignored[1] - ignored[0])
            ignored_center = (ignored[1] + ignored[0]) / 2
            self.ax.bar(ignored_center, 100, width=ignored_width, color='gray', align='center', edgecolor='gray',
                        linewidth=1, alpha=0.6, picker=True)
            self.ax.bar(ignored_center, -100, width=ignored_width, color='gray', align='center', edgecolor='gray',
                        linewidth=1, alpha=0.6, picker=True)


    def drawData(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111, projection="My_Axes")
        ignored_regions = []
        for i, compound in enumerate(self.show_list):
            if not compound:
                continue
            pos_peaks = self.library.library[compound].no_overlap_list
            neg_peaks = self.library.library[compound].overlap_list
            rois = self.library.library[compound].no_overlap_rois
            full_rois = self.library.library[compound].full_rois
            ignored_regions += list(self.library.library[compound].ignored_regions.values())
            ignored_peaks = self.library.library[compound].ignored_peaklist
            if self.show_rois:
                self.drawRoiData(rois, i)
            if self.show_full_rois:
                self.drawRoiData(full_rois, i)
            self.drawPeakData(pos_peaks, i)
            if self.show_positive_overlap:
                if neg_peaks:
                    new_peaks = []
                    for peak in neg_peaks:
                        new_peaks.append(list(peak))
                        flipped = -peak[1]
                        new_peaks[-1][1] = flipped
                    self.drawPeakData(new_peaks, i, alpha=0.8)
            else:
                self.drawPeakData(neg_peaks, i, alpha=0.8)
            if self.show_ignored_peaks:
                self.drawPeakData(ignored_peaks, i, alpha=0.5)
        if self.show_ignored:
            self.drawIgnoredRegions(ignored_regions)
        self.ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        self.ax.spines['bottom'].set_position('zero')
        self.ax.get_xaxis().tick_bottom()
        self.ax.get_yaxis().tick_left()
        self.ax.spines['top'].set_visible(False)
        self.ax.set_xlim([10.5, -0.5])
        self.ax.set_ylim([-1, 1])
        self.ax.set_xlabel('Chemical Shift (ppm)', fontweight='bold')
        self.ax.xaxis.set_label_coords(0.5,0)
        self.ax.set_ylabel('Intensity (Normalized)', fontweight='bold')
        self.fig.tight_layout()
        self.canvas.draw()

    def zooming(self, event):
        cur_ylim = self.ax.get_ylim()
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*0.5
        if event.button == 'up':
            scale_factor = self.scale
        elif event.button == 'down':
            scale_factor = 1/self.scale
        else:
            scale_factor = 1

        self.ax.set_ylim([-(cur_yrange*scale_factor),
                          (cur_yrange*scale_factor)])
        self.canvas.draw()

    def closeEvent(self, event=False):
        self.fig.clear()
        QDialog.reject(self)

class My_Axes(matplotlib.axes.Axes):
    name = "My_Axes"
    def drag_pan(self, button, key, x, y):
        matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y)

class QPushButtonRight(QPushButton):
    rightClicked = pyqtSignal()
    leftClicked = pyqtSignal()

    def __init__(self, string):
        QPushButton.__init__(self, string)

    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit()