import os, sys
from copy import copy

import collections
from setuptools import setup, find_packages

__version__ = open('VERSION', 'rU').read()
sys.path.insert(0, 'nmrmix')

mainscript = 'NMRmix.py'

build_py2app=dict(
    argv_emulation=True,
    includes = [
        'sip',
        'cairo',
        'pango',
        'pangocairo',
        'PyQt5',
        'rdkit',
        'matplotlib',
    ],
    excludes = [
        'Tkinter',
        'PyQt5.QtDesigner',
        'PyQt5.QtNetwork',
        'PyQt5.QtOpenGL',
        'PyQt5.QtScript',
        'PyQt5.QtSql',
        'PyQt5.QtTest',
        'PyQt5.QtWebKit',
        'PyQt5.QtXml',
        'PyQt5.phonon',
    ],
    resources = [
        'nmrmix/static',
        'VERSION',
        'README.md',
    ],
    plist=dict(
        CFBundleName = 'NMRmix',
        CFBundleShortVersionString = __version__,
        CFBundleGetInfoString = 'NMRmix %s' % __version__,
        CFBundleExecutable = 'NMRmix',
        CFBundleIdentifier = 'org.nmrfam.nmrmix',
    ),
    iconfile='nmrmix/static/icon.icns',
    # qt_plugins needed?
    qt_plugins=[
        'platforms/libqcocoa.dylib',
        'imageformats',
        'printsupport/libcocoaprintersupport.dylib',
        'accessible',
    ],
)

setup(
    name='NMRmix',
    version=__version__,
    url='http://nmrfam.wisc.edu',
    license='GNU General Public License (GPL v3)',
    author='Jaime Stark',
    author_email='jstark@nmrfam.wisc.edu',
    description='A tool for generating small molecule mixtures with minimal NMR 1H peak overlap',
    packages = find_packages(),
    include_package_data = True,
    app = ['NMRmix.py'],
    options={
        'py2app': build_py2app,
            },
    setup_requires=['py2app']
)
