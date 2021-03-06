#!/usr/bin/python
from __future__ import print_function
import os, sys

logo = """
NMRmix

Created by Jaime Stark on 2/12/14
Copyright (C) 2014
National Magnetic Resonance Facility At Madison (NMRFAM)
University of Wisconsin - Madison

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to
redistribute it under certain conditions.
See 'LICENSE' for details.

DESCRIPTION
NMRmix is a tool for generating optimal mixtures
for 1D NMR protein-ligand screening efforts,
such as line-broadening screens and STD experiments.
This tool utilizes the peak lists for each compound
in the library and generates mixtures that minimize
peak overlap using a simulated annealing approach.

REFERENCE
J.L. Stark, H. Eghbalnia, W. Lee, W.M. Westler, and J.L. Markley (2016). Journal of Proteome Research, 15(4):1360-1368.
"""

current_file = os.path.realpath(__file__)
current_path = os.path.dirname(current_file)
print("Current Path", current_path, current_file)

# copy first
install_dir = sys.argv[1].rstrip('/')
install_dir = os.path.realpath(install_dir)
if sys.argv[1].upper().find('NMRMIX') == -1:
    install_dir = os.path.join(install_dir, 'NMRmix')

if os.path.exists(os.path.join(install_dir, 'nmrmix/NMRmix.py')):
    # remove first
    cmd = "rm -rf %s" % install_dir
    print(cmd)
    os.system(cmd)

if current_path != install_dir:
    cmd = "cp -rf %s %s" % (current_path, install_dir)
    print(cmd)
    os.system(cmd)

# install libraries
bin_file = os.path.join(install_dir, "nmrmix/NMRmix.py")

link_path = '/usr/local/bin/nmrmix'
real_path = bin_file

cmd = 'chmod +x %s' % real_path
print(cmd)
os.system(cmd)

# symlink...
print('Creating sym links...')

if os.path.islink(link_path):
    cmd = 'rm -rf ' + link_path
    print(cmd)
    os.system('rm -rf ' + link_path)
cmd = 'ln -s %s %s' % (real_path, link_path)
print(link_path)
print(cmd)
os.system(cmd)

print('\n\nTo start NMRmix, please type the following into a terminal window:\n')
print('  nmrmix \n')
