.. -*- coding: utf-8 -*-

===========================================
Ensemble-fit
===========================================

:Date: $Date: 2016-09-25 21:40:17 +0000 (Fri, 26 Feb 2016) $
:Revision: $Revision: 7934 $
:Web site: http://docutils.sourceforge.net/
:Copyright: This document has been placed in the public domain.

.. contents::
.. sectnum::


This manual is for testing script, which compare ensemble and several other methods: EOM, MultiFoxs a MES.
The following sections briefly describe the testing script and detail the steps required to run the program. File input and output are explained.



.. _master copy: http://docutils.sourceforge.net/FAQ.html
.. _let us know:
.. _Docutils-users: docs/user/mailing-lists.html#docutils-users


Dockerfile
==========
Program **ensemble-fit** and testing script are available in docker image.

Download all IMP 2.9.0. libraries for Fedora 28 from https://integrativemodeling.org/download-linux.html with

- wget https://integrativemodeling.org/2.9.0/download/IMP-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-python3-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-mpich-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/

- wget https://integrativemodeling.org/2.9.0/download/IMP-devel-2.9.0-1.fc28.x86_64.rpm -P {your_path}/ensemble-fit_docker_version/dependences/IMP/


Program **GAJOE** can donwload only with permision and create an account. If you want to use GAJOE in you analysis download

 - ATSAS from https://www.embl-hamburg.de/biosaxs/download.html in version 2.8.4. for openSUSE-42
 - ATSAS-2.8.4-1.SUSE-42.x86_64.rpm to {your_path}/ensemble-fit_docker_version/dependences/

**Verify that you have a docker running and create docker image:**

- sudo docker build -t ensamble .

and **run docker image:**

- sudo docker run --rm -ti ensamble bash

Examples
========
Script for SAXS curve is in make_saxs_curves with several switch
 - -d directory with pdb files
 - --finaldir final directory
 - --makecurve choose method for SAXS curve (foxs, crysol)

Makes SAXS curve with software Fox in ensemble image:
 - /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/foxs_curves --makecurve foxs

 Makes SAXS curve with software Crysol in ensemble image:
 - RUN /home/ensemble-test/src/make_saxs_curves.py -d /home/ensemble-test/examples_I/  --finaldir /home/ensemble-test/foxs_curves --makecurve crysol

Script for testing method:

saxs_experiment runs ONE method with several options.

- /home/ensemble-test/src/saxs_experiment -d /home/ensemble-test/foxs_curves/ -n 10 -k 5 -r 3 --experimentdata /home/ensemble-test/experimental_data/exp.dat --output /home/ensemble-test/results/ --preserve --verbose 3 --tolerance 1

 - -d directory with pdbs and foxs files
 - -n set with pdb files
 - -k selection with n set
 - -r number of repetition
 - --tolerance
 - --experimentdata file with experimental dats
 - --output directory with results, it MUST exists before
 - --preserve
 - --verbose
 - ---verbose_logfile
 - -method choose method for testing, method must be ON in config.ini

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
