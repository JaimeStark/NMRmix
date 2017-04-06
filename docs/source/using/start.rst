.. _starting-nmrmix:

Starting NMRmix
===============

Assuming that NMRmix was installed using the installer scripts, open a terminal window and type::

    nmrmix

If NMRmix was installed manually without the scripts, but all the necessary dependencies are present, then the
program can be started like any other python program. Open a terminal window, change the current directory to the
location of the NMRmix source files, and type::

    python NMRmix.py

The NMRFAM splash screen should pop up, and NMRmix should start. On the resulting NMRmix title screen, press
**Continue** to start using NMRmix.

Setting Default Parameters
--------------------------

The default user-defined parameters can be set and saved for future uses of NMRmix. The parameters are saved as a
simple text file (**parameters.txt**) that is located in a directory called **.nmrmix**,
which can be found under the user's home directory. This file and folder is only created if the default parameters are
changed and saved. If for any reason NMRmix is unable to create this directory/file,
saving the default parameters will not be possible. Instead, each parameter will need to be modified manually, if
necessary, for each execution of the NMRmix program.

To set the default preferences, click the *Set Default Preferences* button on the NMRmix title window. The Default
Preferences window should appear with four tabs: Directories/Scoring; Optimizing; Refining; and Display/Statistics.

Directories/Scoring Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Working Directory
    For a description of this parameter, see :ref:`setting-working-peaklist-directories`.

Local Peak List Directory
    For a description of this parameter, see :ref:`setting-working-peaklist-directories`.

Overlap Range
    For a description of this parameter, see

Score Scaling
    For a description of this parameter, see

Use Intensity Scoring
    For a description of this parameter, see

Autosave Results
    For a description of this parameter, see

Optimizing Parameters
^^^^^^^^^^^^^^^^^^^^^

Starting Mixture Number
    For a description of this parameter, see

Max Mixture Size
    For a description of this parameter, see

Extra Mixtures
    For a description of this parameter, see

Cooling Rate
    For a description of this parameter, see

Start Temp
    For a description of this parameter, see

Final Temp
    For a description of this parameter, see

Max Steps
    For a description of this parameter, see

Mix Rate
    For a description of this parameter, see

Iterations
    For a description of this parameter, see

Restrict by Group
    For a description of this parameter, see

Randomize Initial Mixture
    For a description of this parameter, see

Refining Parameters
^^^^^^^^^^^^^^^^^^^

Use Refinement
    For a description of this parameter, see

Cooling Rate
    For a description of this parameter, see

Start Temp
    For a description of this parameter, see

Final Temp
    For a description of this parameter, see

Max Steps
    For a description of this parameter, see

Mix Rate
    For a description of this parameter, see


.. _display-statistics parameters:

Display/Statistics Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Optimization Progress Bar Update (steps)
    During the optimization of the mixtures, a progress bar is used to show the number of annealing steps that have been
    completed. On most computers each step can happen fairly quickly. This parameter defines how often to draw an update
    to the progress bar. For example, the default is set to 50 steps, which indicates that the progress bar will update
    every 50 annealing steps. With some lower end computers, it may be useful to draw the updates less frequently
    (larger step size).

Simulated Peak Width Fraction (half-width at half-maximum)
    The simulated spectra in NMRmix draws each peak using a Lorentz distribution. While the resolution and line width
    of NMR peaks is often dependent upon magnet strength, the simulated spectra uses a default line width for drawing.
    This parameter only changes the cosmetic look of the simulated peaks and does NOT affect the optimization process.


.. _saving-default parameters:

Saving Default Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

Close
    This button closes the Default Preferences window without saving any of the changes made. This means that NMRmix will
    use the parameters that were loaded upon startup, whether these are the factory defaults or the parameters read from
    an existing parameters file.

Reset
    This button resets all of the parameters to the factory default parameters. While this updates all the default parameter
    values for this open instance of NMRmix, these values are not saved as the default values in the
    *.nmrmix/parameters.txt* file. To save these values, press the **Save** button.

Restore
    This button resets all of the parameters to the values found in the *.nmrmix/parameters.txt* file. This updates all
    the default parameter values for this open instance of NMRmix. Since these values are read directly from the
    *parameters.txt* file, there is no need to save unless changes are made.

Save
    This button will write the all of the parameters in the Default Parameters window to the *.nmrmix/parameters.txt*
    file. If the *.nmrmix* directory does not exist, NMRmix will create it and place the *parameters.txt* file within.
    A window will pop-up indicating whether the save was successful.

    If saving fails (likely due to permissions issues),
    these current parameters will be the defaults for the currently open instance of NMRmix. In this case, subsequent
    launches of NMRmix will not use the updated parameters as they were not saved.