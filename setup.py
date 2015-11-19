import sys
from cx_Freeze import setup, Executable

application_title = "NMRmix"
main_python_file = "NMRmix.py"

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

includes = ["sip", "PyQt5", "rdkit"]
zipfiles = [('static/nmrfam_logo.png'),
            ('static/nmrmix_logo.png'),
            ('static/nmrmix.icns')
                ]
excludes = ['Tkinter', 'tkinter', 'PyQt4', 'PySide']
packages = ['core', 'gui', 'PIL', 'PIL.Image', 'PyQt5.QtGui', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'rdkit.Chem',
            'distutils', 'matplotlib.backends.backend_qt5agg', 'matplotlib.pyplot', 'future',
            'future.builtins', 'bs4', 'urllib', 'wand']

options = {
    'build_exe': {
        'includes': includes,
        'excludes': excludes,
        'packages': packages,
        'zip_includes': zipfiles
    }
}

executables = [
    Executable(main_python_file, base=base)
]

setup(name=application_title,
      version='0.90',
      url='http://nmrfam.wisc.edu',
      license='GNU General Public License (GPL v3)',
      author='Jaime Stark',
      author_email='jstark@nmrfam.wisc.edu',
      description='A tool for generating small molecule mixtures with minimal NMR 1H peak overlap',
      classifiers=["Programming Language :: Python",
                   "License :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Development Status :: 4 - Beta"
                   ],
      options=options,
      executables=executables
      )