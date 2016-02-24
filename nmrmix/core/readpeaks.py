#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
readpeaks.py
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import os
import codecs
import sys
if sys.version > '3':
    import csv
    from urllib.request import urlretrieve, urlopen
else:
    import unicodecsv as csv
    from urllib import urlretrieve, urlopen
from bs4 import BeautifulSoup

def set_filetype(filetype, filepath):
    if filetype == 'ACD':
        peaklist = read_acd(filepath)
    elif filetype == 'MNOVA':
        peaklist = read_mnova(filepath)
    elif filetype == 'TOPSPIN':
        peaklist = read_topspin(filepath)
    elif filetype == 'VNMR':
        peaklist = read_vnmrj(filepath)
    elif filetype == 'NMRSTAR':
        peaklist = read_nmrstar(filepath)
    elif filetype == 'HMDB':
        peaklist = read_hmdb(filepath)
    elif filetype == 'USER':
        peaklist = read_user(filepath)
    return(peaklist)


def read_acd(filepath):
    """Reads in an ACD-generated peaklist in text format."""
    try:
        with codecs.open(filepath, 'rU', encoding='utf-8') as peaklist_file:
            rownum = 0
            peaklist = []
            for i, readline in enumerate(peaklist_file):
                if i == 0:
                    continue
                elif rownum == 1:
                    header = readline
                else:
                    linelist = readline.split()
                    if '\x00' in linelist:
                        continue
                    else:
                        peak = (float(linelist[1]), float(linelist[3]))
                        peaklist.append(peak)
                rownum += 1
            return(peaklist)
    except:
        peaklist = []
        return(peaklist)

def read_mnova(filepath):
    """Reads in a Mnova-generated peaklist."""
    try:
        with codecs.open(filepath, 'rU', encoding='utf-8') as peaklist_file:
            rownum = 0
            peaklist = []
            for readline in peaklist_file:
                linelist = readline.split()
                if not linelist:
                    continue
                elif len(linelist) < 6:
                    header = readline
                else:
                    peak = (float(linelist[0]), float(linelist[1]))
                    peaklist.append(peak)
            rownum += 1
        return(peaklist)
    except:
        peaklist = []
        return(peaklist)

def read_topspin(filepath):
    """Reads in a Bruker Topspin-generated csv peaklist."""
    try:
        with open(filepath, 'rU') as csv_file:
            reader = csv.reader(csv_file)
            peaklist = []
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                else:
                    peak = (float(row[4]), float(row[6]))
                peaklist.append(tuple(peak))
        return(peaklist)
    except:
        peaklist = []
        return(peaklist)


def read_vnmrj(filepath):
    """Reads in a Varian VnmrJ-generated peaklist."""
    try:
        with codecs.open(filepath, 'rU', encoding='utf-8') as peaklist_file:
            rownum = 0
            peaklist = []
            for readline in peaklist_file:
                linelist = readline.split()
                if not linelist:
                    continue
                elif (linelist[0] == 'index'):
                    header = readline
                else:
                    peak = (float(linelist[1]), float(linelist[2]))
                    peaklist.append(peak)
            rownum += 1
        return(peaklist)
    except:
        peaklist = []
        return(peaklist)


def read_user(filepath):
    """Reads in a user-created peaklist. See documentation for the format of
    this file."""
    try:
        with open(filepath, 'rU') as csv_file:
            reader = csv.reader(csv_file, encoding='utf-8')
            peaklist = []
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                else:
                    if row[1]:
                        try:
                            if row[2]:
                                peak = (float(row[0]), (float(row[1])), float(row[2]))
                            else:
                                peak = (float(row[0]), (float(row[1])))
                        except:
                            peak = (float(row[0]), (float(row[1])))
                    else:
                        try:
                            if row[2]:
                                peak = (float(row[0]), 1.0, float(row[2]))
                            else:
                                peak = (float(row[0]), 1.0)
                        except:
                            peak = (float(row[0]), 1.0)
                    peaklist.append(tuple(peak))
        return(peaklist)
    except Exception as e:
        print(e)
        peaklist = []
        return(peaklist)

def download_bmrb(bmrb_id, directory_path):
    bmrb_file = bmrb_id + ".str"
    bmrb_path = os.path.join(directory_path, bmrb_file)
    if os.path.exists(bmrb_path):
        peaklist = read_nmrstar(bmrb_path)
    else:
        bmrb_url = 'http://www.bmrb.wisc.edu/ftp/pub/bmrb/metabolomics/NMR_STAR_experimental_entries/' + bmrb_file
        try:
            urlretrieve(bmrb_url, bmrb_path)
            peaklist = read_nmrstar(bmrb_path)
        except:
            peaklist = []
    return(peaklist)

def read_nmrstar(filepath):
    """Reads in a BMRB-STAR file to extract the peaklist."""
    try:
        with codecs.open(filepath, 'rU', encoding='utf-8') as star_file:
            height_flag = False
            shift_flag = False
            proton_flag = False
            peaklist = []
            height_list = []
            shift_list = []
            for row in star_file:
                if not row.strip():
                    continue
                elif row.strip() == "save_":
                    proton_flag = False
                elif row.strip() == "save_spectral_peak_1H":
                    proton_flag = True
                elif proton_flag and row.strip() == "stop_":
                    height_flag = False
                    shift_flag = False
                elif proton_flag and row.strip() == "_Spectral_transition_general_char.Spectral_peak_list_ID":
                    height_flag = True
                elif proton_flag and row.strip() == "_Spectral_transition_char.Spectral_peak_list_ID":
                    shift_flag = True
                elif height_flag:
                    row_list = row.split()
                    height_list.append(row_list[1])
                elif shift_flag:
                    row_list = row.split()
                    shift_list.append(row_list[2])
        for i, peak in enumerate(shift_list):
            apeak = (float(peak), float(height_list[i]))
            peaklist.append(apeak)
        return(peaklist)
    except:
        peaklist = []
        return(peaklist)

def download_hmdb(hmdb_id, directory_path):
    hmdb_file = hmdb_id + ".txt"
    hmdb_path = os.path.join(directory_path, hmdb_file)
    if os.path.exists(hmdb_path):
        peaklist = read_hmdb(hmdb_path)
    else:
        try:
            url = "http://www.hmdb.ca/metabolites/" + hmdb_id
            html = urlopen(url).read()
            soup = BeautifulSoup(html)
            link = soup.find('a', href=True, text='1H NMR Spectrum')
            url2 = "http://www.hmdb.ca" + str(link['href'])
            html2 = urlopen(url2).read()
            soup2 = BeautifulSoup(html2)
            link2 = soup2.find_all('td')
            for i, a in enumerate(link2):
                if str(a) == '<td>List of chemical shift values for the spectrum</td>':
                    link3_pos = i + 1
            html3 = str(link2[link3_pos])
            soup3 = BeautifulSoup(html3)
            link3 = soup3.find('a', href=True)
            urlretrieve(str(link3['href']), hmdb_path)
            peaklist = read_hmdb(hmdb_path)
        except Exception as e:
            #print(e)
            peaklist = []
    return(peaklist)

def read_hmdb(filepath):
    """Reads in a HMDB assignment file to extract the peaklist."""
    try:
        with codecs.open(filepath, 'rU', encoding='utf-8') as hmdb_file:
            peaks_flag = False
            peaklist = []
            for row in hmdb_file:
                if "peaks" in row.lower():
                    peaks_flag = True
                    continue
                if "multiplets" in row.lower():
                    peaks_flag = False
                    continue
                if "assignments" in row.lower():
                    peaks_flag = False
                    continue
                if not row:
                    continue
                if peaks_flag:
                    row_list = row.split()
                    if not row_list:
                        continue
                    elif row_list[1] == '(ppm)':
                        continue
                    else:
                        apeak = (float(row_list[1]), float(row_list[3]))
                        peaklist.append(apeak)
        return(peaklist)
    except:
        peaklist = []
        return(peaklist)