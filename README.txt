.. -*- coding: utf-8 -*-

===========================================
Ensemble
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

-d ../test_directory/ -n 10 -k 5 -r 3 --tolerance 0 --verbose 3 --preserve --experimentdata ../data/exp.dat --output ../output
