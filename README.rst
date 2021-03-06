.. -*- coding: utf-8 -*-

===========================================
Ensemble-fit
===========================================

:Copyright: This document has been placed in the public domain.

.. contents::
.. sectnum::

<<<<<<< HEAD

Manual describes testing script for comparing several methods for analysis od SAXS curves: Ensemble-fit, EOM, MultiFoxs a MES. Detail information about each method is desribed on the following websites:
=======
This manual is for testing script, which compares ensemble and several other methods: EOM, MultiFoxs a MES. More information about each method is on the following websites:
>>>>>>> e2c9f617fb60efb45668e2fbf39bef85f7ce5e49
 :EOM: https://www.embl-hamburg.de/biosaxs/manuals/eom.html
 :MultiFoxs: https://modbase.compbio.ucsf.edu/multifoxs/help.cgi?type=about
 :MES: http://bl1231.als.lbl.gov/saxs_protocols/mes.php
 :GAJOE: https://www.embl-hamburg.de/biosaxs/manuals/eom.html
<<<<<<< HEAD
 :Ensemble-fit: (reference to paper)

The following sections briefly describe the testing script and the detailel steps required to run the testing script and geting results. Testing methods is divided into two part. At first, script ***make_saxs_curves*** creates SAXS curves from pdb files in a propriate format to {name_of_your_directory}. Second, script performes analysis on these curves and pdb files. Results are written to log file.

For testing environment is available image on docker hub to easy manipulation.

Making curves from PDB files
==========
***make_saxs_curves*** prepares file.dat from your pdb files to {your_name_of_dictionary}.

 -d directory with pdb files
 --finaldir new directory for saving SAXS curves
 --makecurve choose method for SAXS curve - foxs or crysol
 --verbose_logfile gives your detail information about transformation

EXAMPLE for foxs:
  ./make_saxs_curves.py ../data/examples_I --makecurve crysol --finaldir ../examples_I_crysol

Make SAXS curve with software Crysol in ensemble image. These curves have more options, SAXS curves are saved in file+00.int in /home/ensemble-test/crysol_curves directory.

EXAMPLE for crysol:
    ./make_saxs_curves.py ../data/examples_I --makecurve foxs --finaldir ../examples_I_foxs

Parametrs of testing scripts
========
=======

The following sections briefly describe the testing script and the detailel steps required to run the testing script. Testing is divided into two part. At first, script make_curves creates SAXS curves from pdb files in a propriate format. The second script performes analysis on these curves and pdb files. You have to upload zour own PDB files or use predefined ones in directory examples_I and examples_II.


Making curves from PDB files
==========




Parametrs of testing scripts
========
Script for SAXS curve is in **make_saxs_curves** directory and has a several options
 - -d directory with pdb files
 - --finaldir final directory, it can not exist yet.
 - --makecurve choose method for SAXS curve - foxs or crysol

Using the Fox software you can create SAXS curve in ensemble image. For pdb's file in examples_I the script outputs saxs curve as file.dat. Results are saved in directory /home/Ensemble-test/foxs_curves. 

 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/foxs_curves --makecurve foxs

>>>>>>> e2c9f617fb60efb45668e2fbf39bef85f7ce5e49

Testing scripts works with pdb's files and saxs curves. All files ({}.pdb and {}.dat) must be in the same directory. It is possible to use your own data, but you have keep the same data format as script ***make_saxs_curves***.

<<<<<<< HEAD
Runing methods have several options. It possible to use them individualy or combined. If you run them combined you get also a comparsion for each method. The result of individual method is saved in format result_{method}_{n}_{k}_{date}.log. Results for more than one method is saved in final_result_{n}_{k}_date.log file. The verbosity of output is defined by verbose_logfile parametrs. Verbosity of std_out is  in range 0 to 2.
=======
 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/crysol_curves --makecurve crysol

Testing scripts works with pdb's files and saxs curves. All files ({}.pdb and {}.dat) must be in the same directory. It is possible to use your own data, but you have keep the data format.

Runing method have several options. It possible to use them individualy or combined. If you run them combined you get also a comparsion for each method. The result of individual method is saved in format result_{method}_{n}_{k}_{date}.log. Results for more than one method is saved in final_result_{n}_{k}_date.log file. The verbosity of output is defined by verbose_logfile parametrs. Verbosity of std_out is  in range 0 to 2.
>>>>>>> e2c9f617fb60efb45668e2fbf39bef85f7ce5e49

Mixing foxs_curves
------------------
Curves are mixed and modified with adderror scripts. Adderror scripts use experimental data for better mistakes. More information about used algorithm is in an article .... .

Configuration files
-------------------
File config.ini contains information required to run the method. Value -1 ***turn off*** method. 0 means, that source files for method are located in ***PATH*** and it is not necessary to explicitely write the position. Value 1 means run method which is not in PATH. There you have to specify the complete path to the method source files.

Run ONE methods
----------------
Script ***saxs_experiment*** runs just one method, it is necessary to turn on this method in config.ini.

- -d directory with pdbs and foxs files
- -n set with pdb files
- -k selection from set with n files
- -r number of repetition, each repetition has different pool.
- --tolerance is number between 0 and 1.
- --experimentdata file with experimental dats for adderror
- --output directory with results, it MUST exists before
- --preserve don't delete tmp directory
- --verbose 0, 1, 2 or 3
- --verbose_logfile
- -method choose method for testing, method must be ON in config.ini


 Example below makes set of 10 structures and chooses 4 of them to make a mix curve. This process is repeated three times. Experimental file for adderror is in /home/ensemble-test/experimental_data/exp.dat. Output is saved in results. This directory has to exist before running script.

- /home/ensemble-test/src/saxs_experiment -d /home/ensemble-test/foxs_curves/ -n 10 -k 5 -r 3 --experimentdata /home/ensemble-test/experimental_data/exp.dat --output /home/ensemble-test/results/ --preserve --verbose 3 --tolerance 1

Run several methods
-------------------
run_script_ensemble can run all methods and compares results, results are collected in a logs files


Technical Parametrs
-------------------
Testing script uses python3-3.6.6-1

Parametrs for script
--------------------
 -d or --dir is directory with pdb files
 --output is name for directory with results

 -n is number of selected files from all pdb files in directory
 -k is numbe of selected files in pool from n
 -r is repetition
 --tolerance
 --preserve
 --method
 --experimentdata
 --verbose has 3
 --verbose_logfile
 
Docker image for ensemble-fit
==========
Program **ensemble-fit** , testing script and data are available in a docker image **ensemble** on DockerHub. Manual for running image ensemble is below.


Program **GAJOE** can be donwloaded only with permision and an account on website. If you want to use GAJOE in your analysis, download ATSAS in version 2.8.4. for openSUSE-42. Otherwise set value = -1 for GAJOE in confing.ini. GAJOE is not part of basic ensemble and it is neccessary to build new image from ensemble with this extenstion.

 - Download ATSAS from https://www.embl-hamburg.de/biosaxs/download.html
 - wget ATSAS-2.8.4-1.SUSE-42.x86_64.rpm to {your_path}/ensemble-fit_docker_version/dependences/


<<<<<<< HEAD
Docker image for ensemble-fit
==========
Program **ensemble-fit** , testing script and data are available in a docker image **ensemble** on DockerHub. Manual for running image ensemble is below.


Program **GAJOE** can be donwloaded only with permision and an account on website. If you want to use GAJOE in your analysis, download ATSAS in version 2.8.4. for openSUSE-42. Otherwise set value = -1 for GAJOE in confing.ini. GAJOE is not part of basic ensemble and it is neccessary to build new image from ensemble with this extenstion.

 - Download ATSAS from https://www.embl-hamburg.de/biosaxs/download.html
 - wget ATSAS-2.8.4-1.SUSE-42.x86_64.rpm to {your_path}/ensemble-fit_docker_version/dependences/


=======
>>>>>>> e2c9f617fb60efb45668e2fbf39bef85f7ce5e49

Program ensemble-fit is saved in directory /home/ensemble-fit/. Testing script is in ensemble-test directory. In /home/weights/ is program MES. MultiFoxs is part of IMP libraries.
Examples
========
**Verify that you have a docker running and create docker image:**
(You can use sudo or docker group).

Image without GAJOE is saved on DockerHub, thus it is fast and easy to use it.


Image with GAJOE must be build on your own

- sudo docker build -t ensamble_gajoe .

**run docker image:**

Image has default setting and anticipated testing with parametrs:
 - n = 10, k = 5, r = 3, experimentdata = /home/data/experimental_data/exp.dat, output = /home/ensemble-test/results/, preserve, verbose = 3 and tolerance = 1
 - docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensembleRun all experimetns:

In /home/ensemble-test/src/ run all method from cinfig.ini:
./run_script_ensemble -d ../foxs_curves/ -n 10 -k 5 -r 3 --tolerance 0 --verbose 3 --preserve --experimentdata ../experimental_data/exp.dat --output ../results/

.Run just one method, for example ensemble-fit. You must turn on ensemble-fit method in config.ini.

./saxs_experiment.py -d ../foxs_curves/ -n 10 -k 5 -r 3 --tolerance 0 --verbose 3 --preserve --experimentdata ../experimental_data/exp.dat --output ../results/ --method ensemble
--------------------


Run with pre-defined setting. There is automatical run_script_ensemble with pre-defined parametrs. It runs the container, makes experiments a exits.
 docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble

Run automatically run_script with your setting, make experiments and exit.
docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble -d /home/data/foxs_curves/ -n 10 -k 5 -r 5 --experimentdata /home/data/experimental_data/exp.dat --output /home/ensemble-test/results/ --verbose 3

Run interactive terminal in container.
docker run -ti --entrypoint=/bin/bash -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble
