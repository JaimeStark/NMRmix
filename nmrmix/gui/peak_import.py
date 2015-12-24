#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
peak_import.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time

from nmrmix.core import compounds


class Window(QDialog):
    def __init__(self, params_object, library_object, parent=None):
        QDialog.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.setWindowTitle("NMRmix: Peak List Import")
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()

    def createWidgets(self):
        """Sets up widgets and widget parameters for this window."""
        self.logLabel = QLabel("<center><b>Peak List Import Log</b></center>")
        self.logOutput = QTextEdit()
        self.logOutput.setReadOnly(True)
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(len(self.library.library_csv))
        self.progressbar.setValue(0)
        self.setForegroundColor(self.progressbar, QColor("red"))
        self.buttonStart = QPushButton("Start Import")
        self.buttonStart.setStyleSheet('QPushButton {color: green;}')
        self.buttonStart.setToolTip("Starts the import of the peak lists.\n"
                                    "While import is occuring, the button can be pressed again to stop import.")
        self.buttonAccept = QPushButton("Continue")
        self.buttonAccept.setToolTip('Accepts the imported peak lists and continues to peak list statistics.')
        self.buttonAccept.setDisabled(True)
        self.buttonReject = QPushButton("Cancel")
        self.buttonReject.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.buttonReject.setToolTip('Rejects the imported peak lists and returns to library import table.')
        self.btnwidget = QWidget()

    def layoutWidgets(self):
        """Sets up widget layouts for this window."""
        layout = QVBoxLayout(self)
        layout.addWidget(self.logLabel)
        layout.addWidget(self.logOutput)
        layout.addWidget(self.progressbar)
        layout.addWidget(self.buttonStart)
        btnlayout = QHBoxLayout(self.btnwidget)
        btnlayout.addWidget(self.buttonReject)
        btnlayout.addWidget(self.buttonAccept)
        layout.addWidget(self.btnwidget)

    def createConnections(self):
        """Sets up signals and slots connections for this window."""
        self.buttonStart.clicked.connect(self.startstopImport)
        self.buttonReject.clicked.connect(self.reject)
        self.buttonAccept.clicked.connect(self.accept)

    def reject(self):
        self.library.library = {}
        self.library.inactive_library = {}
        QDialog.reject(self)

    def startstopImport(self):
        if self.buttonStart.text() == "Start Import":
            self.buttonReject.setStyleSheet("")
            self.buttonReject.setDisabled(True)
            self.import_stopped = False
            self.importPeakLists()
        else:
            self.thread.stop()
            self.progressbar.setValue(0)
            self.library.library = {}
            self.library.inactive_library = {}
            self.library.import_log = []
            self.library.failed_import = []
            self.buttonStart.setText("Start Import")
            self.buttonReject.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
            self.buttonReject.setDisabled(False)
            self.import_stopped = True
            self.logOutput.clear()

    def importPeakLists(self):
        self.importlog = []
        self.failed = []
        self.thread = PeakImportThread(self.params, self.library)
        self.thread.newCompound.connect(self.updateProgressBar)
        self.thread.updatedLog.connect(self.updateLog)
        self.thread.doneImport.connect(self.finishedImport)
        self.thread.start()
        self.buttonStart.setText('Stop Import')

    def updateLog(self, logtext):
        if not self.import_stopped:
            self.logOutput.append(logtext)

    def updateProgressBar(self):
        value = int(self.progressbar.value())
        self.progressbar.setValue(value+1)

    def finishedImport(self):
        self.buttonAccept.setDisabled(False)
        self.buttonAccept.setStyleSheet("QPushButton{color: green; font-weight: bold;}")
        self.buttonStart.setText('Finished Import')
        self.buttonStart.setDisabled(True)
        self.buttonStart.setStyleSheet('QPushButton {color: black;}')
        self.buttonReject.setStyleSheet("QPushButton{color: red; font-weight: bold;}")
        self.buttonReject.setDisabled(False)


    def setForegroundColor(self, widget, color):
        palette=widget.palette()
        palette.setColor(QPalette.Highlight, color)
        widget.setPalette(palette)

class PeakImportThread(QThread):
    updatedLog = pyqtSignal(str)
    newCompound = pyqtSignal()
    doneImport = pyqtSignal()

    def __init__(self, params_object, library_object, parent=None):
        QThread.__init__(self, parent)
        self.params = params_object
        self.library = library_object
        self.exiting = False

    def stop(self):
        self.exiting = True
        self.wait()
        self.exit()

    def run(self):
        time.sleep(0.5)
        self.library.import_log = []
        self.library.failed_import = []
        failed_num = 0
        i = 0
        while not self.exiting and i < len(self.library.library_csv):
            row = self.library.library_csv[i]
            try:
                compound = compounds.Compound(self.params, row)
                if compound.active:
                    success = compound.importPeakList()
                    if success:
                        self.library.addLibraryCompound(i, compound)
                        #compound.set2DStructure()
                        logtext = "%s peaklist import from %s succeeded" % (row[1], row[6])
                        self.updatedLog.emit(logtext)
                        self.library.import_log.append(logtext)
                    else:
                        logtext = "<font color='red'>%s peaklist import from %s failed</font>" % (row[1], row[6])
                        self.library.failed_import.append(self.library.library_csv[i][1])
                        self.library.library_csv[i][0] = "NO"
                        self.updatedLog.emit(logtext)
                        self.library.import_log.append(logtext)
                        failed_num += 1
                else:
                    self.library.addLibraryCompound(i, compound)
                    compound.set2DStructure()
                    logtext = "<font color='orange'>%s peaklist import from %s ignored</font>" % (row[1], row[6])
                    self.updatedLog.emit(logtext)
                    self.library.import_log.append(logtext)
            except Exception as e:
                print(e)
                logtext = "<font color='red'>%s peaklist import from %s failed</font>" % (row[1], row[6])
                self.library.failed_import.append(self.library.library_csv[i][1])
                self.updatedLog.emit(logtext)
                self.library.import_log.append(logtext)
                failed_num += 1
            i += 1
            self.newCompound.emit()
        if not self.exiting:
            succeeded_num = len(self.library.library)
            ignored_num = len(self.library.inactive_library)
            self.library.import_log.append("Number of Compounds Imported: %d" % succeeded_num)
            self.library.import_log.append("Number of Inactive Compounds: %d" % ignored_num)
            self.library.import_log.append("Number of Compounds Failing Import: %d" % failed_num)
            logtext = "<b>Number of Compounds Imported: <font color='blue'>%d</font></b>" % succeeded_num
            self.updatedLog.emit(logtext)
            logtext = "<b>Number of Inactive Compounds: <font color='orange'>%d</font></b>" % ignored_num
            self.updatedLog.emit(logtext)
            logtext = "<b>Number of Compounds Failing Import: <font color='red'>%d</font></b>" % failed_num
            self.updatedLog.emit(logtext)
            for fail in self.library.failed_import:
                logtext = "<font color='red'>Failed: %s</font>" % fail
                self.updatedLog.emit(logtext)
                self.library.import_log.append("Failed: %s" % fail)
            self.doneImport.emit()

