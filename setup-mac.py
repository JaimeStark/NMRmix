import os, sys
from copy import copy

import collections
from setuptools import setup, find_packages
#from nmrmix.NMRmix import __VERSION__

__VERSION__ = open('nmrmix/VERSION', 'rU').read()
#source_path = os.path.join(os.getcwd(), 'nmrmix')
#sys.path.insert(0, source_path)

APP = ['nmrmix/NMRmix.py']

OPTIONS=dict(
    argv_emulation=True,
    includes = ['sip', 'cairo', 'pango', 'pangocairo', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'rdkit',
                'matplotlib',
                ],

    excludes = ['PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL', 'PyQt5.QtScript',
                'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtWebKit', 'PyQt5.QtXml', 'PyQt5.phonon',
                'PyQt5.QtBluetooth', 'PyQt5.QtHelp', 'PyQt5.QtMultimediaWidgets', 'PyQt5.QtWebChannel',
                'PyQt5.QtWebEngineWidgets', 'PyQt5.QtPositioning', 'PyQt5.QtQml', 'PyQt5.QtQuick',
                'PyQt5.QtQuickWidgets', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtWebKitWidgets',
                'PyQt5.QtMultimedia', 'PyQt5.QtSvg', 'PyQt5.QtSql', 'PyQt5.QtXmlPatterns', 'PyQt5.QtScriptTools',
                'PyQt5.QtDeclarative', 'PyQt5.QtWebSockets',
                'Tkinter', 'cx_Freeze', 'mpl-data', 'PyQt4', 'PySide', 'nose'
                ],

    resources = ['nmrmix/static',
                 ],

    plist=dict(CFBundleName = 'NMRmix',
               CFBundleShortVersionString = __VERSION__,
               CFBundleGetInfoString = 'NMRmix %s' % __VERSION__,
               CFBundleExecutable = 'NMRmix',
               CFBundleIdentifier = 'org.nmrfam.nmrmix',
               ),

    iconfile='nmrmix/static/nmrmix.icns',

    # qt_plugins needed?
    qt_plugins=['platforms/libqcocoa.dylib', 'imageformats/*', 'printsupport/libcocoaprintersupport.dylib', 'accessible',
                ],

)

setup(
    name='NMRmix',
    version=__VERSION__,
    url='http://nmrfam.wisc.edu',
    license='GNU General Public License (GPL v3)',
    author='Jaime Stark',
    author_email='jstark@nmrfam.wisc.edu',
    description='A tool for generating small molecule mixtures with minimal NMR 1H peak overlap',
    packages = find_packages(),
    include_package_data = True,
    #data_files = DATA_FILES,
    app = ['nmrmix/NMRmix.py'],
    options={
        'py2app': OPTIONS,
            },
    setup_requires=['py2app']
)
