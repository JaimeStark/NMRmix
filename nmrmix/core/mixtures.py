#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mixtures.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import random
import codecs
import math
import numpy as np
import sys
if sys.version > '3':
    import csv
else:
    try:
        import unicodecsv as csv
    except:
        from core import unicodecsv as csv
import copy

class Mixtures(object):
    """An object to represent the entire set of mixtures being evaluated."""
    def __init__(self, params_object, library_object):
        self.params = params_object
        self.library = library_object
        self.mixtures = {}
        self.group_dict = {}
        self.group_mixnum = {}
        self.mixture_scores = {}
        self.mixture_overlaps = {}
        self.compound_scores = {}
        self.total_score = 0
        self.total_overlaps = 0
        self.anneal_scores = {}
        self.anneal_overlaps = {}
        self.refine_scores = {}
        self.refine_overlaps = {}
        self.mixtures_lock = []


    def generateGroupLists(self):
        """Generates a dictionary where the keys are the different groups, and the values is a list of
        compound IDs that have those groups."""
        self.group_dict = {}
        self.group_mixnum = {}
        if self.params.use_group:
            for compound in self.library.library:
                compound_object = self.library.library[compound]
                if compound_object.group in self.group_dict:
                    self.group_dict[compound_object.group].append(compound_object.id)
                else:
                    self.group_dict[compound_object.group] = []
                    self.group_dict[compound_object.group].append(compound_object.id)
        else:
            self.group_dict[""] = []
            for compound in self.library.library:
                compound_object = self.library.library[compound]
                self.group_dict[""].append(compound_object.id)

    def generateInitialMixtures(self):
        self.mixtures = {}
        self.mixtures.update(self.mixtures_lock)
        start_num = self.params.start_num
        for group in self.group_dict:
            self.group_mixnum[group] = []
            library_list = list(self.group_dict[group])
            random.shuffle(library_list)
            num_compounds = len(library_list)
            # Prevents setting mixture size to greater than the size of the library.
            if num_compounds <= self.params.mix_size:
                num_mixtures = 2
            else:
                num_mixtures = int(math.ceil(num_compounds / self.params.mix_size))
                if num_mixtures < self.params.extra_mixtures:
                    num_mixtures += num_mixtures
                else:
                    num_mixtures += self.params.extra_mixtures
            adjust_value = 0
            mix_num = start_num + adjust_value
            for i in range(num_mixtures):
                mix_num = start_num + i + adjust_value
                while mix_num in self.mixtures:
                    adjust_value += 1
                    mix_num = start_num + i + adjust_value
                self.mixtures[mix_num] = []
                for j in range(self.params.mix_size):
                    if len(library_list) != 0:
                        compound = library_list.pop()
                        self.mixtures[mix_num].append(compound)
                # Reorganizes the elements in the mixture alphabetically
                self.mixtures[mix_num].sort()
                self.group_mixnum[group].append(mix_num)
            start_num = mix_num + 1
        self.num_mixtures = len(self.mixtures)
        self.resetScores()
        self.total_score, self.total_overlaps = self.calculateTotalScore(self.mixtures)

    def resetScores(self):
        self.mixture_scores = {}
        self.compound_scores = {}
        self.mixture_overlaps = {}
        self.total_score = 0
        self.total_overlaps = 0

    def calculateTotalScore(self, mixtures_dict):
        score = 0
        overlaps = 0
        for mixture in mixtures_dict:
            addscore, addoverlaps = self.calculateMixtureScore(mixtures_dict[mixture])
            score += addscore
            overlaps += addoverlaps
        return(score, overlaps)


    def calculateMixtureScore(self, mixture_list, temp_score = False):
        temp_list = sorted(list(set(mixture_list)))
        if tuple(temp_list) in self.mixture_scores:
            score = self.mixture_scores[tuple(temp_list)]
            overlaps = self.mixture_overlaps[tuple(temp_list)]
        else:
            score = 0
            overlaps = 0
            for compound in temp_list:
                comp_list = list(temp_list)
                comp_list.remove(compound)
                if temp_score:
                    addscore, addoverlaps = self.calculateCompoundScore(compound, comp_list, temp_score=True)
                else:
                    addscore, addoverlaps = self.calculateCompoundScore(compound, comp_list, temp_score=False)
                score += addscore
                overlaps += addoverlaps
            self.mixture_scores[tuple(temp_list)] = score
            self.mixture_overlaps[tuple(temp_list)] = overlaps
        return(score, overlaps)

    def calculateCompoundScore(self, compound1, mixture_list, temp_score = False):
        compound_object = self.library.library[compound1]
        if not temp_score:
            compound_object.generatePeakRanges()
        peak_listA = list(compound_object.peak_range_list)
        peak_listB = []
        for compound2 in mixture_list:
            if not temp_score:
                self.library.library[compound2].generatePeakRanges()
            peak_listB += list(self.library.library[compound2].peak_range_list)
        num_peaks = len(peak_listA)
        peak_overlap_score = 0.0
        peak_overlap_count = 0
        peak_overlap_list = []

        for peakB in peak_listB:
            new_list = list(peak_listA)
            for peakA in peak_listA:
                if (peakA[2] > peakB[1]) and (peakA[1] < peakB[2]):
                    peak_overlap_count += 1
                    if self.params.use_intensity:
                        intensity_sum = compound_object.intensity_sum
                        peak_overlap_score += float(peakA[3]) / intensity_sum
                    else:
                        peak_overlap_score += 1.0
                    overlap_peak = (peakA[0], -peakA[3], peakA[2]-peakA[1])
                    peak_overlap_list.append(overlap_peak)
                    new_list.remove(peakA)
            peak_listA = list(new_list)
        if self.params.use_intensity:
            compound_score = peak_overlap_score * self.params.score_scale
        else:
            compound_score = (peak_overlap_score / num_peaks) * self.params.score_scale
        if not temp_score:
            compound_object.no_overlap_list = [(item[0], item[3], item[2]-item[1]) for item in peak_listA]
            compound_object.no_overlap_rois = compound_object.generateROIs(compound_object.no_overlap_list)
            compound_object.overlap_list = list(peak_overlap_list)
            self.compound_scores[compound1] = (compound_score, peak_overlap_count, num_peaks)

        return(compound_score, peak_overlap_count)

    def calcPeakStats(self):
        self.peak_overlap_count = 0
        self.num_peaks = 0
        for compound in self.compound_scores:
            self.peak_overlap_count += int(self.compound_scores[compound][1])
            self.num_peaks += int(self.compound_scores[compound][2])

    def linearCooling(self, refining=False):
        if refining:
            start_temp = self.params.refine_start_temp
            final_temp = self.params.refine_final_temp
            max_steps = self.params.refine_max_steps
        else:
            start_temp = self.params.start_temp
            final_temp = self.params.final_temp
            max_steps = self.params.max_steps
        tempsteps = (start_temp - final_temp) / max_steps
        temp = start_temp
        while True:
            yield temp
            temp -= tempsteps

    def exponentialCooling(self, refining=False):
        if refining:
            self.params.setRefineAlphaTemp()
            start_temp = self.params.refine_start_temp
            alpha_temp = self.params.refine_alpha_temp
        else:
            self.params.setAlphaTemp()
            start_temp = self.params.start_temp
            alpha_temp = self.params.alpha_temp

        temp = start_temp
        while True:
            yield temp
            temp *= alpha_temp

    def medianDeltaScore(self, delta_scores):
        if not delta_scores:
            delta_median = 1
        else:
            delta_median = np.median(delta_scores)
        if delta_median < (0.001 * self.params.score_scale):
            delta_median = (0.001 * self.params.score_scale)
        return(delta_median)

    def meanDeltaScore(self, delta_scores):
        if not delta_scores:
            delta_mean = 1
        else:
            delta_mean = np.mean(delta_scores)
        if delta_mean < (0.001 * self.params.score_scale):
            delta_mean = (0.001 * self.params.score_scale)
        return(delta_mean)

    def mixMixtures(self, mixtures_dict, mixture_list, refining=False):
        new_mixtures = {}
        if refining:
            ideal_mix_rate = self.params.refine_mix_rate
        else:
            ideal_mix_rate = self.params.mix_rate
        if len(mixtures_dict) < ideal_mix_rate:
            mix_rate = len(mixtures_dict)
        else:
            mix_rate = ideal_mix_rate
        mixed_mixtures = random.sample(mixture_list, mix_rate)
        swap_list = []
        for mix_num in mixed_mixtures:
            new_mixtures[mix_num] = list(mixtures_dict[mix_num])
            if len(new_mixtures[mix_num]) < self.params.mix_size:
                intpick = random.randint(1, self.params.mix_size)
                if intpick > len(new_mixtures[mix_num]):
                    pick = "Blank"
                else:
                    pick = new_mixtures[mix_num][intpick-1]
                    new_mixtures[mix_num].remove(pick)
            else:
                pick = random.choice(new_mixtures[mix_num])
                new_mixtures[mix_num].remove(pick)
            swap_list.append(pick)
        diff_score = 0.0
        diff_overlaps = 0.0
        for i,mix_num in enumerate(mixed_mixtures):
            if i+1 == mix_rate:
                pick = swap_list[0]
            else:
                pick = swap_list[i+1]
            if pick == "Blank":
                pass
            else:
                new_mixtures[mix_num].append(pick)
            new_mixtures[mix_num].sort()
            old_score, old_overlaps = self.calculateMixtureScore(mixtures_dict[mix_num], temp_score=True)
            new_score, new_overlaps = self.calculateMixtureScore(new_mixtures[mix_num], temp_score=True)
            diff_score = diff_score + (new_score - old_score)
            diff_overlaps = diff_overlaps + (new_overlaps - old_overlaps)
        return(new_mixtures, diff_score, diff_overlaps)

    def optimizeMixtures(self):
        """Only used in command line version. Not threaded."""
        groups = list(self.group_dict)
        self.calculateTotalScore(self.mixtures)
        self.anneal_scores = {}
        for group in groups:
            iter = {}
            for i in range(self.params.iterations):
                mixnum_list = list(self.group_mixnum[group])
                curr_score, mixtures, scores = self.annealMixtures(mixnum_list)
                iter[i] = [curr_score, mixtures, scores]
                if i == 0:
                    self.mixtures.update(mixtures)
                    previous_score = curr_score
                else:
                    if curr_score <= previous_score:
                        self.mixtures.update(mixtures)
        self.calculateTotalScore(self.mixtures)


    def annealMixtures(self, mixnum_list):
        mixtures = {}
        for mixnum in mixnum_list:
            mixtures[mixnum] = self.mixtures[mixnum]
        scores = []
        delta_scores = []
        curr_score = self.calculateTotalScore(mixtures)
        step = 1
        if self.params.cooling == 'exponential':
            cooling_schedule = self.exponentialCooling()
        else:
            cooling_schedule = self.linearCooling()
        for current_temp in cooling_schedule:
            if step > self.params.max_steps:
                break
            new_mixtures = dict(self.mixMixtures(mixtures))
            new_score = self.calculateTotalScore(new_mixtures)
            score_diff = abs(new_score - curr_score)
            delta_scores.append(score_diff)
            if step == 1:
                delta_median = score_diff
            else:
                delta_median = self.medianDeltaScore(delta_scores)
            if new_score == 0:
                score_step = (step, current_temp, curr_score, new_score, delta_median, 1, 'PASSED')
                scores.append(score_step)
                mixtures = dict(new_mixtures)
                curr_score = new_score
                break
            elif new_score <= curr_score:
                score_step = (step, current_temp, curr_score, new_score, delta_median, 1, 'PASSED')
                scores.append(score_step)
                mixtures = dict(new_mixtures)
                curr_score = new_score
            else:
                probability = math.exp(-(score_diff)/(delta_median * current_temp))
                if random.random() < probability:
                    score_step = (step, current_temp, curr_score, new_score, delta_median, probability, 'PASSED')
                    scores.append(score_step)
                    mixtures = dict(new_mixtures)
                    curr_score = new_score
                else:
                    score_step = (step, current_temp, curr_score, new_score, delta_median, probability, 'FAILED')
                    scores.append(score_step)
            step += 1
        return(curr_score, mixtures, scores)

    def exportMixturesCSV(self, results_directory):
        path = os.path.join(results_directory, "mixtures.csv")
        with open(path, 'w') as mixture_csv:
            writer = csv.writer(mixture_csv)
            header = ['Mixture Number', 'Mixture Score', 'Mixture Group']
            max_length = 0
            for mixture in sorted(self.mixtures.keys()):
                if len(self.mixtures[mixture]) > max_length:
                    max_length = len(self.mixtures[mixture])
            for i in range(max_length):
                new_text = "Compound %d" % (i+1)
                header.append(new_text)
            writer.writerow(header)
            for mixture in sorted(self.mixtures.keys()):
                mixture_results = []
                mixture_results.append(str(mixture))
                mixture_group = []
                mixture_score = "%0.1f" % self.mixture_scores[tuple(self.mixtures[mixture])]
                mixture_results.append(mixture_score)
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                if len(mixture_group) >= 2:
                    group = 'Mixed'
                else:
                    if not mixture_group or len(mixture_group) == 0:
                        group = ''
                    else:
                        group = mixture_group[0]
                mixture_results.append(group)
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                    mixture_results.append(compound)
                writer.writerow(mixture_results)

    def exportRoiCSV(self, results_directory):
        path = os.path.join(results_directory, "roi_no_overlap.csv")
        with open(path, 'w') as mixture_csv:
            writer = csv.writer(mixture_csv)
            for mixture in sorted(self.mixtures.keys()):
                mixture_group = []
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                if len(mixture_group) >= 2:
                    group = 'Mixed'
                else:
                    if not mixture_group or len(mixture_group) == 0:
                        group = ''
                    else:
                        group = mixture_group[0]
                for compound in self.mixtures[mixture]:
                    compound_name = self.library.library[compound].name
                    for i, roi in enumerate(self.library.library[compound].no_overlap_rois):
                        roi_list = [mixture, compound, compound_name, i+1, roi[0], roi[1], group]
                        writer.writerow(roi_list)

    def exportFullRoiCSV(self, results_directory):
        path = os.path.join(results_directory, "roi_w_overlaps.csv")
        with open(path, 'w') as mixture_csv:
            writer = csv.writer(mixture_csv)
            for mixture in sorted(self.mixtures.keys()):
                mixture_group = []
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                if len(mixture_group) >= 2:
                    group = 'Mixed'
                else:
                    if not mixture_group or len(mixture_group) == 0:
                        group = ''
                    else:
                        group = mixture_group[0]
                for compound in self.mixtures[mixture]:
                    compound_name = self.library.library[compound].name
                    for i, roi in enumerate(self.library.library[compound].full_rois):
                        roi_list = [mixture, compound, compound_name, i+1, roi[0], roi[1], group]
                        writer.writerow(roi_list)

    def exportPeakListCSV(self, results_directory):
        path = os.path.join(results_directory, "peaks_mixtures.csv")
        with open(path, 'w') as peaks_csv:
            writer = csv.writer(peaks_csv)
            for mixture in sorted(self.mixtures.keys()):
                mixture_group = []
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                if len(mixture_group) >= 2:
                    group = 'Mixed'
                else:
                    if not mixture_group or len(mixture_group) == 0:
                        group = ''
                    else:
                        group = mixture_group[0]
                for compound in self.mixtures[mixture]:
                    compound_name = self.library.library[compound].name
                    for i, peak in enumerate(self.library.library[compound].mix_peaklist):
                        if len(peak) == 3:
                            peak_range = peak[2]
                        else:
                            peak_range = self.params.peak_range
                        peak_list = [mixture, compound, compound_name, i+1, peak[0], peak[1], peak_range, group]
                        writer.writerow(peak_list)
                    for j, peak in enumerate(self.library.library[compound].ignored_peaklist, i+1):
                        if len(peak) == 3:
                            peak_range = peak[2]
                        else:
                            peak_range = self.params.peak_range
                        peak_list = [mixture, compound, compound_name, j+1, peak[0], peak[1], peak_range, group]
                        writer.writerow(peak_list)

    def exportSimpleMixturesTXT(self, results_directory):
        path = os.path.join(results_directory, "mixtures.txt")
        with codecs.open(path, 'w', encoding='utf-8') as mixture_text:
            mixture_text.write("Total # of Compounds: %d\n" % len(self.library.library))
            mixture_text.write("Total # of Mixtures: %d\n" % len(self.mixtures))
            mixture_text.write("Total # of Peaks: %d\n" % self.num_peaks)
            mixture_text.write("Total # of Overlaps: %d\n" % self.peak_overlap_count)
            mixture_text.write("Total Score: %0.1f\n" % self.total_score)
            mixture_text.write("# of Overlaps / Compound: %0.1f\n" % (self.peak_overlap_count / len(self.library.library)))
            mixture_text.write("Score / Compound: %0.1f\n\n" % (self.total_score / len(self.library.library)))
            for mixture in sorted(self.mixtures.keys()):
                mixture_results = []
                mixture_group = []
                mixture_results.append(str(mixture))
                for compound in self.mixtures[mixture]:
                    if self.library.library[compound].group not in mixture_group:
                        mixture_group.append(self.library.library[compound].group)
                if len(mixture_group) >= 2:
                    group = 'Mixed'
                else:
                    if not mixture_group or len(mixture_group) == 0:
                        group = 'N/A'
                    else:
                        group = mixture_group[0]
                mixture_results.append("%.1f" % self.mixture_scores[tuple(self.mixtures[mixture])])
                mixture_results.append("%s" % group)
                compound_list = list(self.mixtures[mixture])
                while len(compound_list) < self.params.mix_size:
                    compound_list.append('Blank')
                mixture_results = mixture_results + compound_list
                string = ' | '.join(mixture_results) + "\n"
                mixture_text.write(string)

    def exportScores(self, results_directory):
        path = os.path.join(results_directory, "scores.csv")
        with open(path, 'w') as scores_csv:
            writer = csv.writer(scores_csv)
            header = ["Compound ID", "Compound Peaks", "Compound Overlaps", "Compound Score",
                      "Mixture Number", "Mixture Score"]
            writer.writerow(header)
            for mixture in sorted(self.mixtures.keys()):
                for compound in self.mixtures[mixture]:
                    scores = []
                    scores.append(compound)
                    scores.append(self.compound_scores[compound][2])
                    scores.append(self.compound_scores[compound][1])
                    scores.append("%.1f" % self.compound_scores[compound][0])
                    scores.append(mixture)
                    scores.append("%.1f" % self.mixture_scores[tuple(self.mixtures[mixture])])
                    writer.writerow(scores)

    def exportStats(self):
        # TODO: Library Stats
        # TODO: Mixture Stats
        pass