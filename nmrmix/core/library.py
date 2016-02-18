#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
library.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import codecs
import sys
if sys.version > '3':
    import csv
else:
    import unicodecsv as csv
import numpy as np
import copy

from core import compounds

class Library(object):
    """DOCSTRING"""
    def __init__(self, params_object):
        self.params = params_object
        self.library = {}
        self.inactive_library = {}
        self.ignored_library = {}
        self.original_library = {}
        self.groups = []
        self.import_log = []

    def __repr__(self):
        return(self.library.keys)

    def readLibraryFile(self):
        try:
            with open(self.params.library_path, 'rU') as csv_file:
                reader = csv.reader(csv_file)
                self.library_csv = []
                self.library_header = []
                for rowcounter, row in enumerate(reader):
                    if len(row) != 11:
                        message = "There should be 11 columns. The imported file has %d" % len(row)
                        return(False, message)
                    if rowcounter == 0:
                        # Assumes that a header resides in the first row of the csv file.
                        self.library_header.append(row)
                    else:
                        if row[0].upper() != "YES":
                            if row[0].upper() != "NO":
                                message = "Library csv format does not appear correct."
                                return(False, message)
                        if row[1] in self.library_csv:
                            message = "%s is a duplicate" % row[1]
                            return(False, message)
                        else:
                            self.library_csv.append(row)
                return(True, "")
        except IOError:
            message = "Filepath %s does not exist." % self.params.library_path
            return(False, message)

    def exportLibraryCSV(self, results_path):
        path = os.path.join(results_path, 'library.csv')
        try:
            with open(path, 'wb') as newcsv:
                writer = csv.writer(newcsv)
                writer.writerows(self.library_header)
                writer.writerows(self.library_csv)
        except:
            print('CSV export failed')

    def exportImportLog(self, results_path):
        path = os.path.join(results_path, 'peakimport.log')
        try:
            with codecs.open(path, 'w', encoding='utf-8') as newlog:
                for line in self.import_log:
                    newlog.write(line+'\n')
        except:
            print("Log export failed")

    def exportPeaklistCSV(self, results_path):
        path = os.path.join(results_path, 'peaks_all.csv')
        status = ['ACTIVE', 'IGNORED', 'REMOVED']
        try:
            with open(path, 'wb') as newcsv:
                writer = csv.writer(newcsv)
                compound_list = list(self.library.keys())
                writer.writerow(['Compound ID', 'Peak Number', 'PPM', 'Intensity', 'Width', 'Status'])
                for compound in compound_list:
                    compound_obj = self.library[compound]
                    for i in range(0,3):
                        if i == 0:
                            peaklist = compound_obj.mix_peaklist
                        elif i == 1:
                            peaklist = compound_obj.ignored_peaklist
                        elif i == 2:
                            peaklist = compound_obj.removed_peaklist
                        for j, peak in enumerate(peaklist):
                            if len(peak) > 2:
                                peakrow = [compound_obj.id, j+1, peak[0], peak[1], peak[2], status[i]]
                            else:
                                peakrow = [compound_obj.id, j+1, peak[0], peak[1], self.params.peak_range, status[i]]
                            writer.writerow(peakrow)
                compound_list = list(self.ignored_library.keys())
                for compound in compound_list:
                    compound_obj = self.ignored_library[compound]
                    for i in range(0,3):
                        if i == 0:
                            peaklist = compound_obj.mix_peaklist
                        elif i == 1:
                            peaklist = compound_obj.ignored_peaklist
                        elif i == 2:
                            peaklist = compound_obj.removed_peaklist
                        for j, peak in enumerate(peaklist):
                            if len(peak) > 2:
                                peakrow = [compound_obj.id, j+1, peak[0], peak[1], peak[2], status[i]]
                            else:
                                peakrow = [compound_obj.id, j+1, peak[0], peak[1], self.params.peak_range, status[i]]
                            writer.writerow(peakrow)
        except Exception as e:
            print("Peaklist export failed")
            print(e)

    def exportLibraryStats(self, results_path):
        path = os.path.join(results_path, 'library_stats.csv')
        try:
            with open(path, 'wb') as newcsv:
                writer = csv.writer(newcsv)
                num_groups = len(self.groups)
                header_list = ["", 'All Groups']
                header_list.extend(self.groups)
                writer.writerow(header_list)
                stats_list = ['Total Compounds', 'Total Peaks', 'Peaks per Compound (Mean)',
                           'Peaks per Compound (Median)', 'Most/Least Peaks per Compound',
                           '# Aromatic Compounds', '# Aliphatic Compounds',
                           '# Compounds with Ignored Peaks (Total Peaks)',
                           '# Compounds with Ignored Intense Peaks (Total Peaks)',
                           '# Compounds with All Peaks Ignored']
        except Exception as e:
            print("Library stats export failed")

    def importPeakLists(self):
        self.import_log = []
        for i, row in enumerate(self.library_csv):
            try:
                compound = compounds.Compound(self.params, row)
                if compound.active:
                    compound.importPeakList()
                    compound.normalizeIntensities()
                    self.addLibraryCompound(i, compound)
                else:
                    self.addLibraryCompound(i, compound)
            except Exception as e:
                # print(e)
                pass

    def importIgnoreRegions(self, filepath):
        message_log = []
        ignore_regions = []
        ignore_regions_header = []
        try:
            with open(filepath, 'rU') as csv_file:
                reader = csv.reader(csv_file)
                for rowcounter, row in enumerate(reader):
                    if len(row) != 4:
                        message_log.append("There should be 4 columns. The imported file has %d" % len(row))
                        break
                    if "" in row[0:3]:
                        message_log.append("Skipped row %d due to missing name or limits" % (rowcounter+1))
                        continue
                    if row[0]  == "Name":
                        # Assumes that a header resides in the first row of the csv file.
                        ignore_regions_header.append(row)
                    else:
                        name = row[0]
                        lower = row[1]
                        upper = row[2]
                        group = row[3]
                        if row[1] > row[2]:
                            message_log.append("PPM limits for %s were reversed" % row[0])
                            lower = row[2]
                            upper = row[1]
                        elif row[1] == row[2]:
                            message_log.append("No range of limits for %s. Region skipped." % row[0])
                            continue
                        if group not in self.groups:
                            if group != "ALL":
                                message_log.append("Group specificity for %s not recognized. Set to ALL" % row[0])
                                group = 'ALL'
                        for region in ignore_regions:
                            if row[0] in region:
                                message_log.append("%s is a duplicate" % row[0])
                                row[0] = ""
                        if row[0] == '':
                            continue
                        ignore_regions.append([name, lower, upper, group])
                if not ignore_regions:
                    message_log.append("No valid ignore regions recognized in file.")
                return(ignore_regions, message_log)
        except IOError:
            message_log.append("Filepath %s does not exist." % self.params.library_path)
            return(ignore_regions, message_log)

    def exportIgnoreRegions(self, results_directory):
            path = os.path.join(results_directory, "ignored.csv")
            with open(path, 'wb') as ignore_csv:
                writer = csv.writer(ignore_csv)
                header = ['Name', 'Lower', 'Upper', 'Group']
                writer.writerow(header)
                for name in self.ignored_regions:
                    region = self.ignored_regions[name]
                    region_list = [name, region[0], region[1], region[2]]
                    writer.writerow(region_list)

            path = os.path.join(results_directory, 'ignored_compounds.csv')
            with open(path, 'wb') as ignored_compounds_csv:
                writer = csv.writer(ignored_compounds_csv)
                header = ['Compound ID', 'Compound Name', 'Compound Group']
                writer.writerow(header)
                if self.ignored_library:
                    for compound in self.ignored_library:
                        row = [self.ignored_library[compound].id, self.ignored_library[compound].name,
                               self.ignored_library[compound].group]
                        writer.writerow(row)

    def addLibraryCompound(self, index_count, compound_object):
        """Adds the compound object to the library dictionary with a key that is the same as the compound id."""
        if compound_object.id in self.library:
            log_message = "%s at index %d is a duplicate and was not imported." % (compound_object.id, index_count)
            self.importlog.append(log_message)
        else:
            if compound_object.active:
                self.library[compound_object.id] = compound_object
                if compound_object.group not in self.groups:
                    self.groups.append(compound_object.group)
            else:
                self.inactive_library[compound_object.id] = compound_object

    def removeLibraryCompound(self, compound_object):
        self.inactive_library[compound_object.id] = compound_object
        del self.library[compound_object.id]

    def backupOriginalLibraryCompound(self, compound_object):
        self.original_library[compound_object.id] = compound_object

    def restoreOriginalLibraryCompound(self, compound_object):
        self.library[compound_object.id] = self.original_library[compound_object.id]
        del self.original_library[compound_object.id]

    def calcStats(self, ignored_regions={}):
        self.stats = {}
        self.stats["ALL"] = {}
        ignored_peak_count = {}
        ignored_intense_count = {}
        peak_types = {}
        self.stats["ALL"]['Compound List'] = []
        self.stats["ALL"]['Peaklist'] = []
        self.stats["ALL"]['Intense Peaklist'] = []
        self.stats["ALL"]['Peak Count'] = []
        self.stats["ALL"]['Aromaticity'] = []
        self.stats["ALL"]['Ignored Peak Compounds'] = []
        self.stats["ALL"]['Ignored Intense Peak Compounds'] = []
        self.stats["ALL"]['Ignored Compounds'] = []
        ignored_peak_count["ALL"] = []
        ignored_intense_count["ALL"] = []
        peak_types["ALL"] = {'aliphatic/aromatic': 0, 'all aromatic': 0, 'all aliphatic': 0, 'more aromatic': 0,
                             'more aliphatic': 0}
        for group in self.groups:
            self.stats[group] = {}
            self.stats[group]['Compound List'] = []
            self.stats[group]['Peaklist'] = []
            self.stats[group]['Intense Peaklist'] = []
            self.stats[group]['Peak Count'] = []
            self.stats[group]['Aromaticity'] = []
            self.stats[group]['Ignored Peak Compounds'] = []
            self.stats[group]['Ignored Intense Peak Compounds'] = []
            self.stats[group]['Ignored Compounds'] = []
            ignored_peak_count[group] = []
            ignored_intense_count[group] = []
            peak_types[group] = {'aliphatic/aromatic': 0, 'all aromatic': 0, 'all aliphatic': 0, 'more aromatic': 0,
                                   'more aliphatic': 0}
        self.ignored_regions = dict(ignored_regions)
        self.library.update(self.ignored_library)
        self.ignored_library = {}

        compound_list = list(self.library.keys())
        for compound in compound_list:
            # Resets the mix_peaklist and ignored_peaklist
            compound_obj = self.library[compound]
            compound_obj.resetMixPeakList()
            peaklist_hist, intense_peaklist_hist = compound_obj.calcStats()
            self.stats['ALL']['Compound List'].append(compound)
            self.stats[compound_obj.group]['Compound List'].append(compound)
            self.stats['ALL']['Peaklist'] += peaklist_hist
            self.stats['ALL']['Intense Peaklist'] += intense_peaklist_hist
            self.stats[compound_obj.group]['Peaklist'] += peaklist_hist
            self.stats[compound_obj.group]['Intense Peaklist'] += intense_peaklist_hist
            peaklist = list(compound_obj.peaklist)
            num_peaks = len(peaklist)
            self.stats['ALL']['Peak Count'].append(num_peaks)
            self.stats[compound_obj.group]['Peak Count'].append(num_peaks)
            self.stats["ALL"]['Aromaticity'].append(compound_obj.aromatic_percent)
            self.stats[compound_obj.group]['Aromaticity'].append(compound_obj.aromatic_percent)
            peak_types["ALL"][compound_obj.peak_types] += 1
            peak_types[compound_obj.group][compound_obj.peak_types] += 1
            if self.ignored_regions:
                compound_obj.determineIgnoredPeaks(self.ignored_regions)
                # Add the changed peaks back here?
                if len(compound_obj.ignored_peaklist) != 0:
                    self.stats['ALL']['Ignored Peak Compounds'].append(compound_obj.id)
                    self.stats[compound_obj.group]['Ignored Peak Compounds'].append(compound_obj.id)
                    ignored_peak_count["ALL"].append(len(compound_obj.ignored_peaklist))
                    ignored_peak_count[compound_obj.group].append(len(compound_obj.ignored_peaklist))
                if compound_obj.ignored_intense_count != 0:
                    self.stats['ALL']['Ignored Intense Peak Compounds'].append(compound_obj.id)
                    self.stats[compound_obj.group]['Ignored Intense Peak Compounds'].append(compound_obj.id)
                    ignored_intense_count["ALL"].append(compound_obj.ignored_intense_count)
                    ignored_intense_count[compound_obj.group].append(compound_obj.ignored_intense_count)
                if len(compound_obj.mix_peaklist) == 0:
                    self.stats['ALL']['Ignored Compounds'].append(compound_obj.id)
                    self.stats[compound_obj.group]['Ignored Compounds'].append(compound_obj.id)
                    a = copy.deepcopy(self.library[compound_obj.id])
                    self.ignored_library[compound_obj.id] = a
                    del self.library[compound_obj.id]
        # Total Number of Compounds
        self.stats["ALL"][0] = "%d" % len(self.stats["ALL"]["Peak Count"])
        # Total Number of Peaks
        self.stats["ALL"][1] = "%d" % np.sum(self.stats["ALL"]["Peak Count"])
        # Number of Peaks per Compound (Mean)
        self.stats["ALL"][2] = "%.1f ± %.1f" % (np.mean(self.stats["ALL"]["Peak Count"]),
                                                np.std(self.stats["ALL"]["Peak Count"]))
        # Number of Peaks per Compound (Median)
        self.stats["ALL"][3] = "%.1f" % np.median(self.stats["ALL"]["Peak Count"])
        # Number of Compounds with Ignored Peaks (Total Peaks)
        self.stats["ALL"][7] = "%d (%d)" % (len(ignored_peak_count["ALL"]), np.sum(ignored_peak_count["ALL"]))
        # Number of Compounds with Ignored Intense Peaks (Total Peaks)
        self.stats["ALL"][8] = "%d (%d)" % (len(ignored_intense_count["ALL"]), np.sum(ignored_intense_count["ALL"]))
        # Number of Compoundswith All Peaks Ignored
        self.stats["ALL"][9] = "%d" % len(self.stats['ALL']['Ignored Compounds'])
        # Number of Compounds (Aliphatic and Aromatic)
        self.stats["ALL"][5] = "%d" % (peak_types["ALL"]['all aromatic'] + peak_types["ALL"]['more aromatic'])
        self.stats["ALL"][6] = "%d" % (peak_types["ALL"]['all aliphatic'] + peak_types["ALL"]['more aliphatic'])
        # Most/Least Number of Peaks per Compound
        self.stats["ALL"][4] = "%d / %d" % (max(self.stats['ALL']["Peak Count"]), min(self.stats['ALL']["Peak Count"]))
        for group in self.groups:
            # Total Number of Compounds
            self.stats[group][0] = "%d" % len(self.stats[group]["Peak Count"])
            # Total Number of Peaks
            self.stats[group][1] = "%d" % np.sum(self.stats[group]["Peak Count"])
            # Number of Peaks per Compound (Mean)
            self.stats[group][2] = "%.1f ± %.1f" % (np.mean(self.stats[group]["Peak Count"]),
                                                      np.std(self.stats[group]["Peak Count"]))
            # Number of Peaks per Compound (Median)
            self.stats[group][3] = "%.1f" % np.median(self.stats[group]["Peak Count"])
            # Number of Compounds with Ignored Peaks (Total Peaks)
            self.stats[group][7] = "%d (%d)" % (len(ignored_peak_count[group]), np.sum(ignored_peak_count[group]))
            # Number of Compounds with Ignored Intense Peaks (Total Peaks)
            self.stats[group][8] = "%d (%d)" % (len(ignored_intense_count[group]), np.sum(ignored_intense_count[group]))
            # Number of Compounds with All Peaks Ignored
            self.stats[group][9] = "%d" % len(self.stats[group]['Ignored Compounds'])
            # Number of Compounds (Aliphatic / Aromatic)
            self.stats[group][5] = "%d" % (peak_types[group]['all aromatic'] + peak_types[group]['more aromatic'])
            self.stats[group][6] = "%d" % (peak_types[group]['all aliphatic'] + peak_types[group]['more aliphatic'])
            # Most/Least Number of Peaks per Compound
            self.stats[group][4] = "%d / %d" % (max(self.stats[group]["Peak Count"]), min(self.stats[group]["Peak Count"]))