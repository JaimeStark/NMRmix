#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
parameters.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import codecs
import math

class Parameters(object):
    def __init__(self, app_directory):
        self.setDefaultParams()
        self.app_directory = app_directory
        self.param_dir = "~/.nmrmix"
        self.param_file = "~/.nmrmix/parameters.txt"
        if os.path.exists(os.path.expanduser(self.param_dir)):
            if os.path.isfile(os.path.expanduser(self.param_file)):
                self.readPreferences()


    def setDefaultParams(self):
        self.work_dir = os.path.expanduser("~/Desktop")
        self.peaklist_dir = os.path.expanduser("~/Desktop")
        self.library_path = os.path.expanduser("~/Desktop/library.csv")
        self.autosave = True
        self.use_intensity = False
        self.extra_mixtures = 0
        self.peak_range = 0.025
        self.use_group = False
        self.max_steps = 1000
        self.refine_max_steps = 1000
        self.start_temp = 10000
        self.refine_start_temp = 50
        self.final_temp = 25
        self.refine_final_temp = 25
        self.alpha_temp = math.exp((math.log(self.final_temp/self.start_temp))/self.max_steps)
        self.refine_alpha_temp = math.exp((math.log(self.refine_final_temp/self.refine_start_temp))/self.refine_max_steps)
        self.cooling = 'exponential'
        self.refine_cooling = 'exponential'
        self.mix_rate = 2
        self.refine_mix_rate = 2
        self.mix_size = 5
        self.start_num = 1001
        self.blind_regions = []
        self.aromatic_cutoff = 4.700
        self.intense_peak_cutoff = 0.900
        self.score_scale = 10000
        self.iterations = 1
        self.randomize_initial = True
        self.use_refine = False
        self.group_specific_ignored_region = False
        self.print_step_size = 50
        self.peak_display_width = 0.06


    def setLibraryPath(self, library_path):
        """Sets the path to the csv file containing th compound library. See
        documentation for format of csv file."""
        if os.path.isfile(library_path):
            self.library_path = library_path

    def setWorkingDirectory(self, work_dir):
        """Sets the directory to which any generated files will be placed."""
        if os.path.isdir(work_dir):
            self.work_dir = work_dir

    def setPeakListDirectory(self, peaklist_dir):
        """Sets the directory where the user-created peaklists for each compound
        can be found."""
        if os.path.isdir(peaklist_dir):
            self.peaklist_dir = peaklist_dir

    def useAutosave(self):
        """Turns on the use of autosave after optimization is accepted."""
        self.autosave = True

    def noAutosave(self):
        """Turns off the use of autosave after optimization is accepted."""
        self.autosave = False

    def useIntensity(self):
        """Turns on the use of peak intensity for peak overlap scoring."""
        self.use_intensity = True

    def noIntensity(self):
        """Turns off the use of peak intensity for peak overlap scoring."""
        self.use_intensity = False

    def useGroup(self):
        """Turns on the generation of mixtures so that each mixture only
        contains compounds dissolved in the same group."""
        self.use_group = True

    def noGroup(self):
        """Turns off the generation of mixtures so that each mixture only
        contains compounds dissolved in the same group."""
        self.use_group = False

    def setPeakRange(self, peak_range):
        """Sets the range width (in ppm) of a peak that is used to
        determine whether peaks are overlapped."""
        try:
            self.peak_range = float(peak_range)
        except:
            pass

    def setMaxSteps(self, max_steps):
        """Sets the max number of simulated annealing steps to perform."""
        try:
            self.max_steps = int(max_steps)
        except:
            pass

    def setRefineMaxSteps(self, max_steps):
        """Sets the max number of simulated annealing steps to perform."""
        try:
            self.refine_max_steps = int(max_steps)
        except:
            pass

    def setStartingTemp(self, start_temp):
        """Sets the starting temperature for the simulated annealing."""
        try:
            if float(start_temp) > 0:
                self.start_temp = float(start_temp)
        except:
            pass

    def setRefineStartingTemp(self, start_temp):
        """Sets the starting temperature for the simulated annealing."""
        try:
            if float(start_temp) > 0:
                self.refine_start_temp = float(start_temp)
        except:
            pass

    def setFinalTemp(self, final_temp):
        """Sets the final temperature for the simulated annealing."""
        try:
            if float(final_temp) > 0:
                self.final_temp = float(final_temp)
        except:
            pass

    def setRefineFinalTemp(self, final_temp):
        """Sets the final temperature for the simulated annealing."""
        try:
            if float(final_temp) > 0:
                self.refine_final_temp = float(final_temp)
        except:
            pass

    def setAlphaTemp(self):
        """Sets the final temperature for the simulated annealing."""
        try:
            self.alpha_temp = math.exp((math.log(self.final_temp/self.start_temp))/self.max_steps)
        except:
            pass

    def setRefineAlphaTemp(self):
        """Sets the final temperature for the simulated annealing."""
        try:
            self.refine_alpha_temp = math.exp((math.log(self.refine_final_temp/self.refine_start_temp))/self.refine_max_steps)
        except:
            pass

    def useLinearCooling(self):
        self.cooling = 'linear'

    def useRefineLinearCooling(self):
        self.refine_cooling = 'linear'

    def useExponentialCooling(self):
        self.cooling = 'exponential'

    def useRefineExponentialCooling(self):
        self.refine_cooling = 'exponential'

    def setMixRate(self, mix_rate):
        """Sets the number of mixtures to mix during each temperature step of
        the simulated annealing process."""
        try:
            self.mix_rate = int(mix_rate)
        except:
            pass

    def setRefineMixRate(self, mix_rate):
        """Sets the number of mixtures to mix during each temperature step of
        the simulated annealing process."""
        try:
            self.refine_mix_rate = int(mix_rate)
        except:
            pass

    def setMixSize(self, mix_size):
        """Sets the max number of compounds to be placed in each mixture."""
        try:
            self.mix_size = int(mix_size)
        except:
            pass

    def setStartingMixtureNum(self, start_num):
        """Sets the number of the first mixture and increments by one for each
        new mixture."""
        try:
            self.start_num = int(start_num)
        except Exception as e:
            pass

    def setExtraMixtures(self, extra_mixtures):
        try:
            self.extra_mixtures = int(extra_mixtures)
        except:
            pass

    def setBlindRegions(self, blind_regions):
        """Using a list of number pairs, sets the blind regions in the NMR
        spectra."""
        for region in blind_regions:
            try:
                a = float(region[0])
                b = float(region[1])
                if a < b:
                    blind_range = (a, b)
                    self.blind_regions.append(blind_range)
                elif a > b:
                    blind_range = (b, a)
                    self.blind_regions.append(blind_range)
                else:
                    continue
            except:
                pass

    def setAromaticCutoff(self, cutoff):
        try:
            self.aromatic_cutoff = float(cutoff)
        except:
            pass

    def setIntensePeakCutoff(self, cutoff):
        try:
            if float(cutoff) > 1:
                self.intense_peak_cutoff = 1
            elif float(cutoff) < 0:
                self.intense_peak_cutoff = 0
            else:
                self.intense_peak_cutoff = float(cutoff)
        except:
            pass


    def setScoreScale(self, scale):
        try:
            if int(scale) >= 1:
                self.score_scale = int(scale)
        except:
            pass

    def setNumIterations(self, iterations):
        try:
            if int(iterations) > 0:
                self.iterations = int(iterations)
        except:
            pass

    def setPrintStepSize(self, step_size):
        """Sets how often the optimization progress bar updates"""
        try:
            if float(step_size) > 0:
                self.print_step_size = float(step_size)
        except:
            pass

    def setPeakDrawWidth(self, peak_width):
        """Sets how often the optimization progress bar updates"""
        try:
            if float(peak_width) > 0 and float(peak_width) <= 1.0:
                self.peak_display_width = float(peak_width)
        except:
            pass

    def initWindowSize(self, size):
        self.size = size

    def exportScoringParams(self, results_path):
        path = os.path.join(results_path, 'params_scoring.log')
        try:
            with codecs.open(path, 'w', encoding='utf-8') as scoreparams:
                peak_range = "DefaultPeak Overlap Range: %0.3f" % self.peak_range
                scoreparams.write(peak_range+'\n')
                score_scale = "Score Scaling Factor: %d" % self.score_scale
                scoreparams.write(score_scale+'\n')
                use_intensity = "Intensity Scoring: %s" % str(self.use_intensity)
                scoreparams.write(use_intensity+'\n')
        except:
            pass

    def resetPreferences(self):
        self.setDefaultParams()
        self.writePreferences()

    def readPreferences(self):
        try:
            param_path = os.path.expanduser(self.param_file)
            if os.path.isfile(param_path):
                with codecs.open(param_path, 'r', encoding='utf-8') as param_file:
                    for line in param_file:
                        line_list = line.split('=')
                        parameter = line_list[0].strip()
                        param_value = line_list[1].strip()
                        if parameter == "Working Directory":
                            self.setWorkingDirectory(param_value)
                        elif parameter == "Peaklist Directory":
                            self.setPeakListDirectory(param_value)
                        elif parameter == "Library File Path":
                            self.setLibraryPath(param_value)
                        elif parameter == "Use Autosave":
                            if param_value.lower() == "true":
                                self.useAutosave()
                            else:
                                self.noAutosave()
                        elif parameter == "Use Peak Intensity":
                            if param_value.lower() == "true":
                                self.useIntensity()
                            else:
                                self.noIntensity()
                        elif parameter == "Extra Mixtures":
                            self.setExtraMixtures(param_value)
                        elif parameter == "Overlap Range":
                            self.setPeakRange(param_value)
                        elif parameter == "Use Group":
                            if param_value.lower() == "true":
                                self.useGroup()
                            else:
                                self.noGroup()
                        elif parameter == "Max Optimizing Steps":
                            self.setMaxSteps(param_value)
                        elif parameter == "Max Refining Steps":
                            self.setRefineMaxSteps(param_value)
                        elif parameter == "Optimizing Start Temp":
                            self.setStartingTemp(param_value)
                        elif parameter == "Refining Start Temp":
                            self.setRefineStartingTemp(param_value)
                        elif parameter == "Optimizing Final Temp":
                            self.setFinalTemp(param_value)
                        elif parameter == "Refining Start Temp":
                            self.setRefineFinalTemp(param_value)
                        elif parameter == "Optimizing Cooling Rate":
                            if param_value.lower() == 'linear':
                                self.useLinearCooling()
                            else:
                                self.useExponentialCooling()
                        elif parameter == "Refining Cooling Rate":
                            if param_value.lower() == 'linear':
                                self.useRefineLinearCooling()
                            else:
                                self.useRefineExponentialCooling()
                        elif parameter == "Optimizing Mix Rate":
                            self.setMixRate(param_value)
                        elif parameter == "Refining Mix Rate":
                            self.setRefineMixRate(param_value)
                        elif parameter == "Max Mixture Size":
                            self.setMixSize(param_value)
                        elif parameter == "Mixture Start Number":
                            self.setStartingMixtureNum(param_value)
                        elif parameter == "Aromatic/Aliphatic Cutoff":
                            self.setAromaticCutoff(param_value)
                        elif parameter == "Intense Peak Cutoff":
                            self.setIntensePeakCutoff(param_value)
                        elif parameter == "Score Scale":
                            self.setScoreScale(param_value)
                        elif parameter == "Iterations":
                            self.setNumIterations(param_value)
                        elif parameter == "Randomize Initial Mixture State":
                            if param_value.lower() == "true":
                                self.randomize_initial = True
                            else:
                                self.randomize_initial = False
                        elif parameter == "Use Refinement":
                            if param_value.lower() == "true":
                                self.use_refine = True
                            else:
                                self.use_refine = False
                        elif parameter == "Step Size Print":
                            try:
                                self.print_step_size = int(param_value)
                            except:
                                pass
                        elif parameter == "Peak Display Width":
                            try:
                                self.peak_display_width = float(param_value)
                            except:
                                pass
        except Exception as e:
            # print("Failed to read preferences")
            # print(e)
            pass

    def writePreferences(self):
        try:
            if not os.path.exists(os.path.expanduser(self.param_dir)):
                os.mkdir(os.path.expanduser(self.param_dir))
            param_path = os.path.expanduser(self.param_file)
            with codecs.open(param_path, 'w', encoding='utf-8') as param_file:
                param_file.write("Working Directory" + " = " + str(self.work_dir) + "\n")
                param_file.write("Peaklist Directory" + " = " + str(self.peaklist_dir) + "\n")
                param_file.write("Library File Path" + " = " + str(self.library_path) + "\n")
                param_file.write("Use Autosave" + " = " + str(self.autosave) + "\n")
                param_file.write("Use Peak Intensity" + " = " + str(self.use_intensity) + "\n")
                param_file.write("Extra Mixtures" + " = " + str(self.extra_mixtures) + "\n")
                param_file.write("Overlap Range" + " = " + str(self.peak_range) + "\n")
                param_file.write("Use Group" + " = " + str(self.use_group) + "\n")
                param_file.write("Max Optimizing Steps" + " = " + str(self.max_steps) + "\n")
                param_file.write("Max Refining Steps" + " = " + str(self.refine_max_steps) + "\n")
                param_file.write("Optimizing Start Temp" + " = " + str(self.start_temp) + "\n")
                param_file.write("Refining Start Temp" + " = " + str(self.refine_start_temp) + "\n")
                param_file.write("Optimizing Final Temp" + " = " + str(self.final_temp) + "\n")
                param_file.write("Refining Final Temp" + " = " + str(self.refine_final_temp) + "\n")
                param_file.write("Optimizing Cooling Rate" + " = " + str(self.cooling) + "\n")
                param_file.write("Refining Cooling Rate" + " = " + str(self.refine_cooling) + "\n")
                param_file.write("Optimizing Mix Rate" + " = " + str(self.mix_rate) + "\n")
                param_file.write("Refining Mix Rate" + " = " + str(self.refine_mix_rate) + "\n")
                param_file.write("Max Mixture Size" + " = " + str(self.mix_size) + "\n")
                param_file.write("Mixture Start Number" + " = " + str(self.start_num) + "\n")
                # param_file.write("Ignored Regions" + " = " + self.blind_regions + "\n")
                param_file.write("Aromatic/Aliphatic Cutoff" + " = " + str(self.aromatic_cutoff) + "\n")
                param_file.write("Intense Peak Cutoff" + " = " + str(self.intense_peak_cutoff) + "\n")
                param_file.write("Score Scale" + " = " + str(self.score_scale) + "\n")
                param_file.write("Iterations" + " = " + str(self.iterations) + "\n")
                param_file.write("Randomize Initial Mixture State" + " = " + str(self.randomize_initial) + "\n")
                param_file.write("Use Refinement" + " = " + str(self.use_refine) + "\n")
                param_file.write("Step Size Print" + " = " + str(self.print_step_size) + "\n")
                param_file.write("Peak Display Width" + " = " + str(self.peak_display_width) + "\n")
        except Exception as e:
            # print("Failed to write preferences")
            # print(e)
            pass

    
