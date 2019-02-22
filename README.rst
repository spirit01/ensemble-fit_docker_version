.. -*- coding: utf-8 -*-

===========================================
Ensemble-fit
===========================================

:Copyright: This document has been placed in the public domain.

.. contents::
.. sectnum::

This manual is for testing script, which compare ensemble and several other methods: EOM, MultiFoxs a MES. More information about each methods is on the website:
 :EOM: https://www.embl-hamburg.de/biosaxs/manuals/eom.html
 :MultiFoxs: https://modbase.compbio.ucsf.edu/multifoxs/help.cgi?type=about
 :MES: http://bl1231.als.lbl.gov/saxs_protocols/mes.php
 :GAJOE: https://www.embl-hamburg.de/biosaxs/manuals/eom.html

The following sections briefly describe the testing script and the detail steps required to run the testing script. Testing id divided to two part. At first, script make_curves creates SAXS curves from pdb files in a propriate format. The second, running analysis on this curves and pdb files. PDB files yould be upload or use predefined directory examples_I or examples_II.


Making curves from PDB files
==========




Parametrs of testing scripts
========
Script for SAXS curve is in **make_saxs_curves** directory and has a several options
 - -d directory with pdb files
 - --finaldir final directory, it can not exist yet.
 - --makecurve choose method for SAXS curve - foxs or crysol

Make SAXS curve with software Fox in ensemble image. For pdb's file in examples_I makes saxs curve as file.dat. Results are saved in directory /home/Ensemble-test/foxs_curves.

 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/foxs_curves --makecurve foxs


 Make SAXS curve with software Crysol in ensemble image. These curves have more options, SAXS curves are saved in file+00.int in /home/ensemble-test/crysol_curves directory.

 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/crysol_curves --makecurve crysol

Testing scripts works with pdb's files and saxs curves. All files ({}.pdb and {}.dat) must be in the same directory. It is possible to use your own data, but you have keep the data format.

Runing method have several options. It possible to used them individualy or together. If you run it together you get also a comparsion for each method. The result of individual method is saved in format result_{method}_{n}_{k}_{date}.log. Results for more than one method is saved in final_result_{n}_{k}_date.log file. The verbosity of output is defined by verbose_logfile parametrs. Verbosity of std_out is  in range 0 to 2.

Mixing foxs_curves
------------------
Curves are mixing and with srcipts adderror. Adderror scripts use experimental data for better mistakes. More information about algorithm is in an article .... .

Configuration files
-------------------
File config.ini contains information to run the method. Value -1 ***turn off*** method. 0 means, that method is in ***PATH*** and it is not necessary to explicite write the position. Value 1 run method which is not in PATH. There you have to use the all path to method.

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


 Example below makes set from 10 structures and choose 4 of them to makes a mix curve. This process is repeated three times. Experimental file for adderror is in /home/ensemble-test/experimental_data/exp.dat. Outpud is saved in results. This directory have had to exist before running script.

- /home/ensemble-test/src/saxs_experiment -d /home/ensemble-test/foxs_curves/ -n 10 -k 5 -r 3 --experimentdata /home/ensemble-test/experimental_data/exp.dat --output /home/ensemble-test/results/ --preserve --verbose 3 --tolerance 1

Run several methods
-------------------
run_script_ensemble can runs all method and compares results, results are collected in a logs files


Technical Parametrs
-------------------
Testing script use python3-3.6.6-1

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
Program **ensemble-fit** , testing script and data are available in docker image **ensemble** on DockerHub. Manual for running image ensemble is below.


Program **GAJOE** can donwload only with permision and an account on website. If you want to use GAJOE in your analysis, download ATSAS in version 2.8.4. for openSUSE-42. Otherwise set value = -1 for GAJOE in confing.ini. GAJOE is not part of basic ensemble and it is neccessary to build new image from ensemble with this extenstion.

 - Download ATSAS from https://www.embl-hamburg.de/biosaxs/download.html
 - wget ATSAS-2.8.4-1.SUSE-42.x86_64.rpm to {your_path}/ensemble-fit_docker_version/dependences/



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


Run with pre-defined setting. There is automatical run_script_ensemble with pre-defined parametrs. It runs container, make experiments a exit.
 docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble

Run automatically run_script with your setting, make experiment and exit.
docker run -it -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble -d /home/data/foxs_curves/ -n 10 -k 5 -r 5 --experimentdata /home/data/experimental_data/exp.dat --output /home/ensemble-test/results/ --verbose 3

Run interactive terminal in container.
docker run -ti --entrypoint=/bin/bash -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/data:/home/data -v /home/petrahrozkova/Dokumenty/ensemble-fit_docker_version/src:/home/ensemble-test ensemble
