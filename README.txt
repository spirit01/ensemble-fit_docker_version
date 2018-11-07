.. -*- coding: utf-8 -*-

===========================================
Ensemble-fit
===========================================

:Date: $Date: 2016-09-25 21:40:17 +0000 (Fri, 26 Feb 2016) $
:Copyright: This document has been placed in the public domain.

.. contents::
.. sectnum::

This manual is for testing script, which compare ensemble and several other methods: EOM, MultiFoxs a MES. More information about methods:
 :EOM: https://www.embl-hamburg.de/biosaxs/manuals/eom.html
 :MultiFoxs: https://modbase.compbio.ucsf.edu/multifoxs/help.cgi?type=about
 :MES: http://bl1231.als.lbl.gov/saxs_protocols/mes.php

The following sections briefly describe the testing script and detail the steps required to run the program.

Dockerfile
==========
Program **ensemble-fit** and testing script are available in docker image **ensemble**. Manual for running image ensemble is below:

Download all IMP 2.9.0. libraries for Fedora 28 from https://integrativemodeling.org/download-linux.html

- wget https://integrativemodeling.org/2.9.0/download/IMP-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-python3-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-mpich-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-devel-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/


Program **GAJOE** can donwload only with permision and create an account. If you want to use GAJOE in you analysis download ATSAS

 - Download ATSAS from https://www.embl-hamburg.de/biosaxs/download.html in version 2.8.4. for openSUSE-42
 - wget ATSAS-2.8.4-1.SUSE-42.x86_64.rpm to {your_path}/ensemble-fit_docker_version/dependences/

**Verify that you have a docker running and create docker image:**

- sudo docker build -t ensamble .

**run docker image:**

- sudo docker run --rm -ti ensamble bash

Examples
========
Script for SAXS curve is in make_saxs_curves directory and has several options
 - -d directory with pdb files
 - --finaldir final directory
 - --makecurve choose method for SAXS curve (foxs, crysol)


Makes SAXS curve with software Fox in ensemble image. For pdb's file in examples_I makes saxs curve as file.dat. Results are saved in directory /home/Ensemble-test/foxs_curves.

 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/foxs_curves --makecurve foxs


 Makes SAXS curve with software Crysol in ensemble image. These curves have more options, SAXS curves are saved in file+00.int in /home/ensemble-test/crysol_curves directory.

 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/crysol_curves --makecurve crysol

Testing scripts works with pdb's files and saxs curves. All files must be in the same directory, if you want to prepare your own datas.

It is available to run just one method or several method in the same time.

Mixing foxs_curves
------------------

Curves are mixing and with srcipts adderror. Adderror scripts use experimental data for better mistakes.

Run ONE methods
----------------
saxs_experiment runs just one method, it is necessary to turn on this method in config.ini.

- -d directory with pdbs and foxs files
- -n pool with pdb files
- -k selection from pool with n files
- -r number of repetition, each repetition has different pool.
- --tolerance is number between 0 and 1.
- --experimentdata file with experimental dats for adderror
- --output directory with results, it MUST exists before
- --preserve don't delete tmp directory
- --verbose 0, 1, 2 or 3
- ---verbose_logfile
- -method choose method for testing, method must be ON in config.ini


 Example below makes pool from 10 strucutres a choose 4 of them to makes a mix curve. This process is repeated three times. Experimental file for adderror is in /home/ensemble-test/experimental_data/exp.dat. Outpud is saved in results. This directory have had to exist before running script.

- /home/ensemble-test/src/saxs_experiment -d /home/ensemble-test/foxs_curves/ -n 10 -k 5 -r 3 --experimentdata /home/ensemble-test/experimental_data/exp.dat --output /home/ensemble-test/results/ --preserve --verbose 3 --tolerance 1

Run several methods
-------------------
run_script_ensemble can runs all method and compares results, results are collected in a logs files


Ensemble
========

What is Ensemble?
-----------------


EOM & GAJOE
===========

What is EOM and GAJOE?
----------------------

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

Examples
========
Run all experimetns:

In /home/ensemble-test/src/ run all method from cinfig.ini:
./run_script_ensemble -d ../foxs_curves/ -n 10 -k 5 -r 3 --tolerance 0 --verbose 3 --preserve --experimentdata ../experimental_data/exp.dat --output ../results/

Run just one method, for example ensemble-fit. You must turn on ensemble-fit method in config.ini.

./saxs_experiment.py -d ../foxs_curves/ -n 10 -k 5 -r 3 --tolerance 0 --verbose 3 --preserve --experimentdata ../experimental_data/exp.dat --output ../results/ --method ensemble
