SCRIPT YOUNG PWN EVOLUTION 

Script for computing the evolution of an electron population (with a broken power law as injection spectrum) of a PWN inside a SNR.

The script is valid only if the radius of the PWN is smaller than the radius of the SNR.

To run the script:
- Install GAMERA (http://libgamera.github.io/GAMERA/docs/download_installation.html)
- in launch_evo_youngPWN.py modify the parameter of the PWN (description of parameter in the file)
- in evo_gelfand_model.py modify the location of the GAMERA library: sys.path.append('location/of/GAMERA/lib')
- run python launch_evo_youngPWN.py

As output:
- Electron SED (el_sed_***.txt)
- Photon SED (ph_sed_tot_***.txt, ph_sed_***.png)
- Photon SED from IC (ph_sed_IC_{CMB,NIR,FIR,SSC}_***.txt) and synchrotron (ph_sed_sync_***.txt)
- Array with the time evolution of the parameter of the PWN (evo_***.txt)


To run the script for multiple systems:
- Execute launch_multiple_evo.py: python launch_multiple_evo.py <SNR_file>
- Need as input the output of the code of the SNRs (in txt format)
- As output: Two files with all the information pre and post script execution and one file for each PWN computed with the relative photon spectrum (the numbers of the sources correspond to the numbers of the SNRs)
