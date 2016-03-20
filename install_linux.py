#!/usr/bin/python

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
J.L. Stark, H. Eghbalnia, W. Lee, W.M. Westler, and J.L. Markley (2016). In preparation.

USAGE
python install-linux.py [INSTALLATION DIR]
"""

ubuntu = "apt-get -y install pyqt5-dev-tools python-qt5 python-scipy python-matplotlib python-imaging python-rdkit python-bs4 python-unicodecsv"

redhat1_1 = "yum-config-manager --add-repo https://copr.fedoraproject.org/coprs/giallu/rdkit/repo/epel-6/giallu-rdkit-epel-6.repo"
redhat1_2 = "yum-config-manager --add-repo https://copr.fedoraproject.org/coprs/giallu/rdkit/repo/epel-7/giallu-rdkit-epel-7.repo"
redhat2 = "yum -y install PyQt5 PyQt5-devel scipy python-matplotlib python-imaging python-rdkit python-beautifulsoup4 "

print logo

import os, sys, getpass, platform

current_file = os.path.realpath(__file__)
current_path = os.path.dirname(current_file)

redhat_ver = ''

if len(sys.argv) < 2:
  print "[INSTALLATION DIR] not set."
  print "Exiting..."
  sys.exit()

user = getpass.getuser()
if user != 'root':
  print "Root privilege required."
  print "Exiting..."  
  sys.exit()
  
if (os.path.exists('/etc/redhat-release')) or (os.path.exists('/etc/fedora-release')):
  print "Redhat, Fedora or CentOS found."
  target_os = 'redhat'
  if platform.dist()[1].find('6.') != -1:
    redhat_ver = '6'
  elif platform.dist()[1].find('7.') != -1:
    redhat_ver = '7'    
  else:
    print "Unsupported operating system."
    print "Please install required libraries."
    print "Note that we test this distribution on Ubuntu and CentOS (6 and 7)."
    print "Exiting..."
elif (os.path.exists('/etc/lsb-release')) or (os.path.exists('/etc/debian-release')):
  print "Ubuntu or Debian found."
  target_os = 'ubuntu'
else:  
  print "Unsupported operating system."
  print "Please install required libraries."
  print "Note that we test this distribution on Ubuntu and CentOS (6 and 7)."
  print "Exiting..."
  
# copy first
install_dir = sys.argv[1].rstrip('/')
install_dir = os.path.realpath(install_dir)
if (sys.argv[1].upper().find('NMRMIX') == -1):
  install_dir = os.path.join(install_dir, 'NMRmix')
  
if os.path.exists( os.path.join(install_dir, 'nmrmix/NMRmix.py') ):
  # remove first
  cmd = "\\rm -rf %s" % install_dir
  print cmd
  os.system(cmd)
    
if current_path != install_dir:
  cmd = "\\cp -rf %s %s" % (current_path, install_dir)
  print cmd
  os.system(cmd)

# install libraries
bin_file = os.path.join(install_dir, "nmrmix/NMRmix.py")
if target_os == 'redhat':
  if redhat_ver == '6':
    print(redhat1_1)  
    os.system(redhat1_1)
  elif redhat_ver == '7': 
    print(redhat1_2)
    os.system(redhat1_2)    
  print(redhat2)
  os.system(redhat2)  
elif target_os == 'ubuntu':
  print(ubuntu)
  os.system(ubuntu)
    
# symlink...
print 'Creating sym links...'

link_path = '/usr/local/bin/nmrmix'
real_path = bin_file

cmd = 'chmod +x %s' % (real_path)
print cmd
os.system(cmd)

if os.path.exists(link_path):
  os.system('\\rm -rf ' + link_path)
cmd = 'ln -s %s %s' % (real_path, link_path)
print cmd
os.system(cmd)

if os.path.exists(link_path + '.py'):
  os.system('\\rm -rf ' + link_path + '.py')
cmd = 'ln -s %s %s.py' % (real_path, link_path)
print cmd
os.system(cmd)

print '\n\nPlease type nmrmix like the following to execute this program.\n'
print '\n  $ nmrmix \n' 