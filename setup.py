import sys
from cx_Freeze import setup, Executable

TITLE = "NMRmix"
APP = "nmrmix/NMRmix.py"

VERSION = open('nmrmix/VERSION', 'rU').read()

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

includes = ['sip', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui', 'rdkit',
            'matplotlib', 'bs4',
            ]

include_files = ['nmrmix/VERSION', 'nmrmix/static/nmrfam_logo.png', 'nmrmix/static/nmrmix_logo.png']

# zipfiles = [('nmrmix/static/nmrfam_logo.png'),
#             ('nmrmix/static/nmrmix_logo.png'),
#             ('nmrmix/static/nmrmix.icns'),
#             ]

excludes = ['PyQt5.QtDesigner', 'PyQt5.QtNetwork', 'PyQt5.QtOpenGL', 'PyQt5.QtScript',
            'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtWebKit', 'PyQt5.QtXml', 'PyQt5.phonon',
            'PyQt5.QtBluetooth', 'PyQt5.QtHelp', 'PyQt5.QtMultimediaWidgets', 'PyQt5.QtWebChannel',
            'PyQt5.QtWebEngineWidgets', 'PyQt5.QtPositioning', 'PyQt5.QtQml', 'PyQt5.QtQuick',
            'PyQt5.QtQuickWidgets', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtWebKitWidgets',
            'PyQt5.QtMultimedia', 'PyQt5.QtSvg', 'PyQt5.QtSql', 'PyQt5.QtXmlPatterns', 'PyQt5.QtScriptTools',
            'PyQt5.QtDeclarative', 'PyQt5.QtWebSockets',
            'Tkinter', 'py2app',
            ]

packages = ['nmrmix.core', 'nmrmix.gui']

icon = "nmrmix/static/nmrmix.icns"

options = {'build_exe': {'includes': includes,
                         'include_files': include_files,
                         'excludes': excludes,
                         'packages': packages,
                         'icon': icon,
                         # 'zip_includes': zipfiles
    }
}

executables = [
    Executable(APP, base=base)
]

setup(name=TITLE,
      version=VERSION,
      url='http://nmrfam.wisc.edu',
      license='GNU General Public License (GPL v3)',
      author='Jaime Stark',
      author_email='jstark@nmrfam.wisc.edu',
      description='A tool for generating small molecule mixtures with minimal NMR 1H peak overlap',
      # packages = find_packages(),
      # include_package_data = True,
      #data_files = DATA_FILES,
      # app = ['nmrmix/NMRmix.py'],
      options=options,
      executables=executables,
      )