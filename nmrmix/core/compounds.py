#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
compounds.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
from operator import itemgetter


from PIL import ImageQt

import numpy as np

from rdkit import Chem
from rdkit.Chem import Draw, rdMolDescriptors, rdDepictor
from rdkit.Chem.Draw import DrawingOptions

from core import readpeaks

if 'RDBASE' not in os.environ.keys():
    os.environ['RDBASE'] = os.getcwd()

# DrawingOptions.atomLabelFontSize=20
# DrawingOptions.atomLabelMinFontSize=18
# DrawingOptions.coordScale=1.0
# DrawingOptions.bgColor=(1,1,1)
# DrawingOptions.dotsPerAngstrom=1000
DrawingOptions.bondLineWidth=2
# DrawingOptions.useFraction=1.0


class Compound(object):
    """Requires the input of a list of rows from the library csv file."""
    def __init__(self, params_object, compound_list):
        self.params = params_object
        self.modified = False
        self.peaks_modified = False
        self.descriptors_modified = False
        # Sets whether to include the compound in the mixtures
        if str(compound_list[0]).upper().strip() == 'YES':
            self.active = True
        else:
            self.active = False
        self.id = str(compound_list[1]).strip()
        self.sortname = self.id
        self.name = compound_list[2].strip()
        self.bmrb_id = compound_list[3].lower().strip()
        self.hmdb_id = compound_list[4].lower().strip()
        self.user_file= compound_list[5].strip()
        self.format_choice = compound_list[6].upper().strip()
        group = compound_list[7].upper().strip()
        if group:
            self.group = group
        else:
            self.group = 'N/A'
        self.pubchem_id = str(compound_list[8]).strip()
        self.kegg_id = str(compound_list[9]).upper().strip()
        self.smiles = str(compound_list[10]).strip()
        self.structure_image = False
        self.structure_data = False

        self.original_data = {'id':self.id, 'name':self.name, 'bmrb':self.bmrb_id, 'hmdb':self.hmdb_id, 'file':self.user_file,
                              'format':self.format_choice, 'group':self.group, 'pubchem':self.pubchem_id,
                              'kegg':self.kegg_id, 'smiles':self.smiles}

        self.peak_range_list = []
        self.full_rois = []
        self.ignored_regions = {}
        self.no_overlap_list = []
        self.overlap_list = []
        self.overlap_list_pos = []
        self.no_overlap_rois = []
        self.overlap_rois = []

    def __repr__(self):
        compound = "%s: %s" % (self.id, self.name)
        return(compound)

    def __lt__(self, other):
        return(self.sortname, other.sortname)



    def importPeakList(self):
        """Based upon the contents of the column of database choice in the library file, read in a peak list.
        Calls the setPeakList method to store the peak lists."""
        format_options = ['USER', 'BMRB_ID', 'HMDB_ID', 'ACD', 'MNOVA', 'TOPSPIN', 'VNMR', 'NMRPIPE', 'NMRSTAR', 'HMDB']
        self.original_peaklist_path = os.path.join(self.params.peaklist_dir, '', self.user_file)
        if self.format_choice in format_options:
            if self.format_choice not in ['BMRB_ID', 'HMDB_ID']:
                peaklist = readpeaks.set_filetype(self.format_choice, self.original_peaklist_path)
                if peaklist:
                    self.setPeakList(peaklist)
                    return(True)
                else:
                    return(False)
            else:
                if self.format_choice == 'BMRB_ID':
                    peaklist = readpeaks.download_bmrb(self.bmrb_id, self.params.peaklist_dir)
                    if peaklist:
                        self.setPeakList(peaklist)
                        return(True)
                    else:
                        return(False)
                elif self.format_choice == 'HMDB_ID':
                    peaklist = readpeaks.download_hmdb(self.hmdb_id, self.params.peaklist_dir)
                    if peaklist:
                        self.setPeakList(peaklist)
                        return(True)
                    else:
                        return(False)
        else:
            # print("No t a valid format choice for %s" % self.id)
            return(False)

    def setPeakList(self, peaklist):
        """Stores the peaklist to the compound instance as a tuple. Also creates a mix_peaklist which is an
        editable version of the peaklist. The mix_peaklist is what is actually used during mixture generation.
        Initially, peaklist and mix_peaklist start out as identical."""
        max_length = 0
        peaklist.sort()
        for peaks in peaklist:
            if len(peaks) > max_length:
                max_length = len(peaks)
        if max_length == 1:
            tmp_peaklist = []
            for peak in peaklist:
                peaktuple = (peak, 1)
                tmp_peaklist.append(peaktuple)
            self.original_peaklist = list(tmp_peaklist)
        elif max_length == 2:
            tmp_peaklist = []
            for peak in peaklist:
                if len(peak) < 2:
                    continue
                else:
                    tmp_peaklist.append(peak)
            self.original_peaklist = list(tmp_peaklist)
        elif max_length == 3:
            tmp_peaklist = []
            for peak in peaklist:
                if not peak[0]:
                    continue
                elif not peak[1]:
                    continue
                tmp_peaklist.append(peak)
            self.original_peaklist = list(tmp_peaklist)
        self.peaklist = list(self.original_peaklist)
        self.mix_peaklist = list(self.peaklist)
        self.ignored_peaklist = []
        self.removed_peaklist = []
        self.normalizeIntensities()
        self.full_rois = self.generateROIs(self.mix_peaklist)
        # self.roi_list = self.generateROIs(self.mix_peaklist)

    def set2DStructure(self):
        if self.smiles:
            try:
                mol = Chem.MolFromSmiles(self.smiles)
                self.molwt = rdMolDescriptors.CalcExactMolWt(mol)
                self.molformula = rdMolDescriptors.CalcMolFormula(mol)
                rdDepictor.Compute2DCoords(mol)
                self.structure_image = Draw.MolToImage(mol, size=(400,200), kekulize=True, wedgeBonds=False)
                pixdata = self.structure_image.load()
                for y in range(self.structure_image.size[1]):
                    for x in range(self.structure_image.size[0]):
                        if pixdata[x, y] == (255, 255, 255, 255):
                            pixdata[x, y] = (255, 255, 255, 0)
                self.structure_qt = ImageQt.ImageQt(self.structure_image)
            except Exception as e:
                print(e)
                self.molwt = False
                self.molformula = False
                self.structure_image = False
                self.structure_data = False
        else:
            self.molwt = False
            self.molformula = False
            self.structure_image = False
            self.structure_data = False

    def calcStats(self):
        self.aromatic_peaks = 0
        self.aliphatic_peaks = 0
        peaklist = list(self.peaklist)
        peaklist.sort(key=itemgetter(1), reverse=True)
        max_intensity = float(peaklist[0][1])
        median_list = []
        intense_peak_list = []
        for peak in peaklist:
            median_list.append(peak[0])
            percentage = peak[1] / max_intensity
            if percentage > self.params.intense_peak_cutoff:
                intense_peak_list.append(peak[0])
            if peak[0] >= self.params.aromatic_cutoff:
                self.aromatic_peaks += 1
            else:
                self.aliphatic_peaks += 1
        self.aromatic_percent = self.aromatic_peaks / (self.aromatic_peaks + self.aliphatic_peaks) * 100
        if self.aromatic_peaks == self.aliphatic_peaks:
            self.peak_types = 'aliphatic/aromatic'
        elif (self.aromatic_peaks > self.aliphatic_peaks) and (self.aliphatic_peaks == 0):
            self.peak_types = 'all aromatic'
        elif (self.aromatic_peaks < self.aliphatic_peaks) and (self.aromatic_peaks == 0):
            self.peak_types = 'all aliphatic'
        elif self.aromatic_peaks > self.aliphatic_peaks:
            self.peak_types = 'more aromatic'
        elif self.aliphatic_peaks > self.aromatic_peaks:
            self.peak_types = 'more aliphatic'
        self.median_shift = np.median(median_list)
        return(median_list, intense_peak_list)

    def normalizeIntensities(self):
        """From an imported peaklist which contains intensities, normalize the intensities so that the highest
        peak equals 1. Note: It is possible to have negative intensities for a peak due to how the baseline is
        set. Currently, negative values are normalized to zero, which will only have an effect if intensities
        are used during the mixture determination. If these negative peaks are important, create a custom peaklist
        that removes the negative values."""
        if not self.mix_peaklist:
            peaklist = []
            ignoredlist = list(self.ignored_peaklist)
            removedlist = list(self.removed_peaklist)
            sumlist = list(self.ignored_peaklist) + list(self.removed_peaklist)
            sumlist.sort(key=itemgetter(1), reverse=True)
            max_intensity = float(sumlist[0][1])
        else:
            peaklist = list(self.mix_peaklist)
            ignoredlist = list(self.ignored_peaklist)
            removedlist = list(self.removed_peaklist)
            peaklist.sort(key=itemgetter(1), reverse=True)
            max_intensity = float(peaklist[0][1])

        # Sort peaklist by intensity (larger to smaller)
        if peaklist:
            tmp_peaklist = []
            for peak in peaklist:
                if float(peak[1]) < 0:  # For cases when peak intensity is negative.
                    new_intensity = 0
                else:
                    new_intensity = float(peak[1]) / max_intensity
                if len(peak) == 3:
                    new_peak = (peak[0], new_intensity, peak[2])
                else:
                    new_peak = (peak[0], new_intensity)
                tmp_peaklist.append(new_peak)
            # Rewrite mixing peaklist with normalized intensities.
            peaklist = sorted(list(tmp_peaklist))
            self.mix_peaklist = list(peaklist)


        if ignoredlist:
            tmp_peaklist = []
            for peak in ignoredlist:
                if float(peak[1]) < 0:
                    new_intensity = 0
                else:
                    new_intensity = float(peak[1]) / max_intensity
                if len(peak) == 3:
                    new_peak = (peak[0], new_intensity, peak[2])
                else:
                    new_peak = (peak[0], new_intensity)
                tmp_peaklist.append(new_peak)
            ignoredlist = sorted(list(tmp_peaklist))
            self.ignored_peaklist = list(ignoredlist)
        if removedlist:
            tmp_peaklist = []
            for peak in removedlist:
                if float(peak[1]) < 0:
                    new_intensity = 0
                else:
                    new_intensity = float(peak[1]) / max_intensity
                if len(peak) == 3:
                    new_peak = (peak[0], new_intensity, peak[2])
                else:
                    new_peak = (peak[0], new_intensity)
                tmp_peaklist.append(new_peak)
            removedlist = sorted(list(tmp_peaklist))
            self.removed_peaklist = list(removedlist)
        self.calculateIntensitySum()

    def denormalizeIntensity(self, peak, peaklist):
        peak_max = -9999999999
        for aPeak in peaklist:
            if aPeak[1] > peak_max:
                peak_max = aPeak[1]
        new_peak = peak[1] * peak_max
        return(new_peak)

    def calculateIntensitySum(self):
        self.intensity_sum = 0
        if self.mix_peaklist:
            for peak in self.mix_peaklist:
                self.intensity_sum += peak[1]

    def setIgnoredRegions(self, ignored_regions):
        self.ignored_regions = {}
        for name in ignored_regions:
            if (ignored_regions[name][2] == 'ALL') or (ignored_regions[name][2] == self.group):
                self.ignored_regions[name] = ignored_regions[name]

    def determineIgnoredPeaks(self, custom_peaks=[]):
        tmp_peaklist = list(self.mix_peaklist)
        tmp_peaklist.sort(key=itemgetter(1), reverse=True)
        try:
            max_intensity = tmp_peaklist[0][1]
        except Exception as e:
            return
        self.ignored_intense_count = 0
        for peak in tmp_peaklist:
            for name in self.ignored_regions:
                if (peak[0] >= self.ignored_regions[name][0]) and (peak[0] <= self.ignored_regions[name][1]):
                    self.ignorePeak(peak)
                    if peak[1] >= (self.params.intense_peak_cutoff * max_intensity):
                        self.ignored_intense_count += 1
                    break
        self.normalizeIntensities()
        self.full_rois = self.generateROIs(self.mix_peaklist)
        return

    def resetMixPeakList(self):
        self.mix_peaklist = list(self.peaklist)
        self.ignored_peaklist = []
        self.ignored_regions = {}
        # self.determineIgnoredPeaks()
        self.normalizeIntensities()

    def resetPeakList(self):
        self.setPeakList(self.original_peaklist)
        self.determineIgnoredPeaks()
        self.peaks_modified = False

    def ignorePeak(self, peak):
        """Removes a peak from the mix_peaklist and adds it to the ignored_peaklist."""
        self.mix_peaklist.remove(peak)
        self.ignored_peaklist.append(peak)

    def removePeak(self, peak):
        if peak in self.mix_peaklist:
            self.mix_peaklist.remove(peak)
        elif peak in self.ignored_peaklist:
            self.ignored_peaklist.remove(peak)
        self.removed_peaklist.append(peak)
        self.peaklist = self.mix_peaklist + self.ignored_peaklist
        self.resetMixPeakList()
        self.determineIgnoredPeaks()
        self.peaks_modified = True

    def editPeak(self, peak):
        self.peaklist = self.mix_peaklist + self.ignored_peaklist + [peak]
        self.resetMixPeakList()
        self.determineIgnoredPeaks()

    def addPeak(self, peak):
        self.peaklist = self.mix_peaklist + self.ignored_peaklist + [peak]
        self.resetMixPeakList()
        self.determineIgnoredPeaks()
        self.peaks_modified = True
        # self.added_peaklist.append(peak)

    def restoreOriginalDescriptors(self):
        self.id = self.original_data['id']
        self.sortname = self.original_data['id']
        self.name = self.original_data['name']
        self.bmrb_id = self.original_data['bmrb']
        self.hmdb_id = self.original_data['hmdb']
        self.user_file= self.original_data['file']
        self.format_choice = self.original_data['format']
        self.group = self.original_data['group']
        self.pubchem_id = self.original_data['pubchem']
        self.kegg_id = self.original_data['kegg']
        self.smiles = self.original_data['smiles']
        self.descriptors_modified = False

    def editName(self, name):
        try:
            self.name = str(name)
            self.descriptors_modified = True
        except:
            pass

    def editBMRB(self, bmrb):
        try:
            # TODO: Add BMRB check
            self.bmrb_id = str(bmrb)
            self.descriptors_modified = True
        except:
            pass


    def editHMDB(self, hmdb):
        try:
            # TODO: Add HMDB check
            self.hmdb_id = str(hmdb)
            self.descriptors_modified = True
        except:
            pass


    def editGroup(self, group):
        try:
            self.group = str(group)
            self.descriptors_modified = True
        except:
            pass

    def editPubChem(self, pubchem):
        try:
            # TODO: Add PubChem check
            self.pubchem_id = str(pubchem)
            self.descriptors_modified = True
        except:
            pass

    def editKEGG(self, kegg):
        try:
            # TODO: Add KEGG check
            self.kegg_id = str(kegg)
            self.descriptors_modified = True
        except:
            pass

    def editSMILES(self, smiles):
        try:
            # TODO: Add SMILES check
            self.smiles = str(smiles)
            self.descriptors_modified = True
        except:
            pass


    def updatefromBMRB(self):
        pass

    def updatefromHMDB(self):
        pass

    def updatefromPubChem(self):
        pass

    def updatefromKEGG(self):
        pass

    def generateROIs(self, peaklist):
        range_list = []
        for peak in peaklist:
            if len(peak) == 3:
                peak_low = peak[0] - (peak[2] / 2)
                peak_high = peak[0] + (peak[2] / 2)
            else:
                peak_low = peak[0] - (self.params.peak_range / 2)
                peak_high = peak[0] + (self.params.peak_range / 2)
            peak_roi = [peak_low, peak_high]
            range_list.append(peak_roi)

        sorted_list = sorted(range_list)
        merged_list = []
        for higher in sorted_list:
            if not merged_list:
                merged_list.append(higher)
            else:
                lower = merged_list[-1]
                if higher[0] <= lower[1]:
                    upper_bound = max(lower[1], higher[1])
                    merged_list[-1] = (lower[0], upper_bound)
                else:
                    merged_list.append(higher)
        return(list(merged_list))

    def generatePeakRanges(self):
        self.peak_range_list = []
        for peak in self.mix_peaklist:
            if len(peak) == 3:
                peak_low = peak[0] - (peak[2] / 2)
                peak_high = peak[0] + (peak[2] / 2)
            else:
                peak_low = peak[0] - (self.params.peak_range / 2)
                peak_high = peak[0] + (self.params.peak_range / 2)
            peak_center = peak[0]
            intensity = peak[1]
            self.peak_range_list.append((peak_center, peak_low, peak_high, intensity))