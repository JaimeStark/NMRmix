# NMRmix

##Introduction

Ligand affinity screening by nuclear magnetic resonance (NMR) spectroscopy is a versatile tool that is routinely
used to support drug discovery and functional genomics research. The real power of NMR ligand affinity screens arises
from its ability to directly detect protein-ligand binding events under native or near-native sample conditions. The
most common NMR screening approaches (_i.e._ line-broadening, STD-NMR, and WaterLOGSY) are focused on detecting changes
in the one-dimensional (1D) <sup>1</sup>H spectrum of a ligand upon binding to a protein. Hundreds of compounds can be 
analyzed
in a day by coupling these benefits with an automated sample changer, software to optimize probe tuning and other
parameters, and rapid NMR data collection of with a cryogenic probe.

To improve the efficiency of NMR ligand affinity screens, compounds are usually evaluated in mixtures. Using mixtures
provides two significant benefits: (1) a larger number of compounds can be screened in a shorter amount of time; and
(2) the amount of protein required for the entire screen is reduced. However, there are also some drawbacks. As the
size of a mixture increases, the probability that a mixture might contain more than one compound competing for the
same binding site increases, thus weakening the NMR observable binding event for each compound. Also, compounds in
the same mixture may react or interact with each other, thus chemically changing the compounds or causing problems
with solubility or aggregation. Finally, the NMR signals from the multiple compounds may overlap leading to ambiguity
in analyzing the binding results and the necessity for rescreening with individual compounds. This last problem can
be overcome by creating mixtures without peak overlaps, but this task becomes challenging when one is working with a
screen composed of hundreds or thousands of compounds. However, a previous study showed that mixtures with minimal
peak overlap could be efficiently created by using a simulated annealing algorithm.

NMRmix is a freely available, open-source software solution for the generation of mixtures with minimal peak overlap.
NMRmix was written in [Python](https://www.python.org) and utilizes the [Qt5](http://www.qt.io) framework with 
[PyQt5](https://www.riverbankcomputing.com) bindings to build a graphical user
interface. NMRmix utilizes a combination of 1D <sup>1</sup>H peak lists for each compound and an overlap range to 
define whether
overlaps occur. The overlap scoring function considers the proportion of peaks in a compound that are overlapped as
well as the intensity of the peaks. The software has customizable parameters, downloadable peak list data from the
[BMRB](http://www.bmrb.wisc.edu/metabolomics/) or [HMDB](http://www.hmdb.ca), interactive simulated spectra views, 
graphs of statistics, and an easily useable interface.
Additionally, NMRmix outputs regions of interest (ROIs) in a readable format that can be used to automate the
analysis of NMR ligand affinity screening data.

For more instructions on the installation process, see [NMRmix Documentation](http://nmrmix.nmrfam.wisc.edu)

## References

* Jaime L. Stark, Hamid R. Eghbalnia, Woonghee Lee, William M. Westler, and John L. Markley. [NMRmix: a tool for the 
optimization of compound mixtures for 1D 1H NMR ligand affinity screens.](http://pubs.acs.org/doi/abs/10.1021/acs.jproteome.6b00121)
_Journal of Proteome Research_ (2016),15(4): 1360-1368.
* Xavier Arroyo, Michael Goldflam, Miguel Feliz, Ignasi Belda, and Ernest Giralt. [Computer-Aided Design of 
Fragment Mixtures for NMR-Based Screening](http://dx.plos.org/10.1371/journal.pone.0058571) _PLoS ONE_ (2013), 
8(3): e58571.