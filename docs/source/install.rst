Installation
============

Obtaining NMRmix
----------------

NMRmix is available from the `NMRFAM website <http://pine.nmrfam.wisc.edu/download_packages.html>`_ as zipped python
source files.

An example compound library comprising of metabolites found in the `BMRB <http://www.bmrb.wisc.edu/metabolomics/>`_
can also be downloaded and directly imported into NMRmix.


NMRFAM Virtual Machine
^^^^^^^^^^^^^^^^^^^^^^

In an effort to minimize the effort involved with installing software, NMRFAM has created a Linux virtual machine which
includes most of the software developed at NMRFAM. A virtual machine is essentially like running another computer, which
may be a completely different operating system (*i.e.* Linux, Windows, etc.), on your computer. The NMRFAM Virtual
Machine can be run using a VM software, such as the `Oracle VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_.

Download the NMRFAM Virtual Machine `here <http://pine.nmrfam.wisc.edu/download_packages.html>`_.

.. warning::
    While the NMRFAM Virtual Machine is the easiest way to install all the various NMRFAM software, including NMRmix,
    running a virtual machine on your computer will have to share resources between your computer's operating system
    and the virtual machine's operating system. For that reason, you'll want to use a computer that has at least two CPUs
    or CPU cores and a significant amount of RAM (>4GB).




Dependencies
------------

NMRmix relies on the use of several packages to work. The following represent the minimum version of each required
dependency. Testing of NMRmix was done with these versions. There is no guarantee that a different version will
work.

**Software Dependencies**

* Python 2.7.11 or Python 3.5.1
* RDKit 2015.09.02
* Qt 5.1
* Cairo 1.14.6
* PyCairo 1.10.0
* Pango 1.38.1 [OPTIONAL]
* PyQt 5.5.1

**Python Packages**

* Numpy 1.10.4
* Matplotlib 1.5.1
* BeautifulSoup 4.4.1
* Pillow 3.1.1
* Unicodecsv 0.14.1 [ONLY NEEDED FOR PYTHON 2 BUILD]



Mac OS X Installation (Homebrew)
--------------------------------

The easiest approach to install NMRmix on Mac OS X would be to use the *install_mac.sh* script found in the NMRmix folder.
This script may take up to an hour or so to complete due to the installation of some of the necessary dependencies.

Execute this script by typing the following into the terminal from the NMRmix directory to install NMRmix using Python 3::

    ./install_mac_py3.sh

Or type the following to install using Python 2::

    ./install_mac_py2.sh


However, if you would like to manually work through the installation process that the script performs, follow the
instructions below. The installation of NMRmix on Mac OS X benefits from the use of a package manager (*i.e.* Homebrew, MacPorts,
Anaconda, etc.) to download and install the necessary packages. The instructions here will focus on the use of
`Homebrew <http://brew.sh>`_ to install the necessary packages, but the installation procedures should be fairly
similar on other package managers. If you have successfully installed NMRmix using another package manager, please
`email Jaime Stark <jstark@nmrfam.wisc.edu>`_ your instructions, and it will be added to the documentation.

The **install_mac.sh** installs the Homebrew package manager and uses it to install the dependencies necessary for
running NMRmix. At the end of the script, the script calls a python script (**setup_mac.py**) that copies the NMRmix
program to your Applications directory and then sets up a symbolic link that allows NMRmix to be started from the
terminal with a simple command.

.. warning::
    There may be problems installing NMRmix using this script or the method described below if you already use another
    package manager. If you have concerns about this issue, `email Jaime Stark <jstark@nmrfam.wisc.edu>`_ or try
    using the `NMRFAM Virtual Machine`_.


Installing Homebrew
^^^^^^^^^^^^^^^^^^^

Open a terminal and type the following command::

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

This will probably ask you to install the Xcode command line tools, if you don't already have Xcode installed. While
the  Xcode command line tools should be able to be installed at this point, the Homebrew installation may still fail. If
so, try installing the Xcode command line tools first by typing the following::

    xcode-select --install

If the installation of both the Xcode command line tools and Homebrew successfully completes, type the following
command to check for any problems::

    brew doctor

If there are any issues, you will want to refer to the `documentation for
Homebrew <https://github.com/Homebrew/homebrew/tree/master/share/doc/homebrew#readme>`_ to help troubleshoot.


Installing Packages
^^^^^^^^^^^^^^^^^^^

As you might have guessed, all commands using the Homebrew package manager start with **brew**.
For example to get information about installing Python 3, which is necessary for NMRmix, type the following command::

    brew info python3

This command will show a short overview of the Python package, description, dependencies, and installation arguments.

.. sidebar:: Why Install Python?

    Python 2.7 is already preinstalled by Apple in Mac OS X. However, this version is not frequently updated,
    and often utilizes outdated packages. The version installed by package managers like Homebrew are much easier to
    update and manage.

.. note:: Manual Installation

    Normally, you could install both of the Python 2 and Python 3 dependencies without much issue. However, this is not
    currently true for the RDKit package. It can only be install for either Python 2 or Python 3, not both. So for the
    purposes of NMRmix, you will need to decide whether to use the Python 2 or Python 3 version.

To install Python 3, type the following command::

    brew install python3

Or type the following to install Python 2::

    brew install python


This will begin by installing all the software dependencies for python first, and then it will install python. Each
package that is necessary for NMRMix can be installed in this way. Type the following commands into a terminal window
in this order to install all of the necessary packages, for the Python 3 build::

    brew install python3
    brew install fontconfig
    brew install py3cairo
    brew install pyqt5
    brew tap rdkit/rdkit
    brew install rdkit --with-pycairo --with-python3

Or type the following to install all the packages necessary, for the Python 2 build::

    brew install python
    brew install fontconfig
    brew install py2cairo
    brew install libsvg-cairo
    brew install gtk
    brew install pyqt5
    brew tap rdkit/rdkit
    brew install rdkit --with-pycairo


The installation may take a while (an hour or more), especially for the installation of **pyqt5** and their
dependencies.

Following the successful installation of these
packages, several python packages will also need to be installed. To install Python packages, the PIP package manager
will be used, which works similarly to Homebrew and was installed along with Python.
Type the following commands into the terminal for the Python 3 build::

    pip3 install numpy
    pip3 install matplotlib
    pip3 install cairocffi
    pip3 install beautifulsoup4
    pip3 install Pillow

Or type the following for the Python 2 build::

    pip install numpy
    pip install matplotlib
    pip install cairocffi
    pip install beautifulsoup4
    pip install Pillow
    pip install unicodecsv

These commands should install each python package and their dependencies.

Installing NMRmix
^^^^^^^^^^^^^^^^^
The NMRmix python script can be executed from the NMRmix folder. However, we can make NMRmix easier to execute from the
terminal with the following commands. First, we will make the NMRmix python script executable. In terminal, change the
directory to the folder containing the NMRmix program and then type the following command::

    chmod +x NMRmix/nmrmix/NMRmix.py

Next, copy the the NMRmix directory to the Applications directory with the following command::

    cp -r NMRmix /Applications

Finally, create a symlink that allows NMRmix to be executed easily within terminal using the following command::

    ln -s /Applications/NMRmix/nmrmix/NMRmix.py /usr/local/bin/nmrmix

To start NMRmix, type the following into the terminal::

    nmrmix

Linux Installation
------------------

The easiest approach to install NMRmix on Linux-based (Ubuntu, Debian, or Red Hat) systems would be to use the
*install_linux.py* script found in the NMRmix folder.

Execute this script by typing the following into the terminal from the NMRmix directory::

    python install_linux.py [INSTALLATION DIR]

where the path to the directory where you would like to install NMRmix replaces the [INSTALLATION DIR]. This script
will download the appropriate dependencies, copies the NMRmix program into the installation directory, and sets up a
symlink to allow NMRmix to be started from the terminal with a simple command::

    nmrmix

If you have any issues with this installation process, please `email Jaime Stark <jstark@nmrfam.wisc.edu>`_ or try
using the `NMRFAM Virtual Machine`_.


Windows Installation
--------------------

Coming Soon!