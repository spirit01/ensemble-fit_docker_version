#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import random
import re
import shutil
import sys
import tempfile
from argparse import ArgumentParser
from os import listdir
import numpy as np
from adderror import adderror
import logging
from time import localtime, strftime
from comparison import compare_ensembles
import threading
import pkgutil
import importlib
import pathlib
import configparser


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LogPipe(threading.Thread):

    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)

class Run:
    def __init__(self, all_files, selected_files, weights, run, method):
        # experiment
        self.all_files = all_files
        self.selected_files = selected_files
        self.weights = weights
        self.method = method
        self.run = run
        # results from experiment
        self.results = []

    def print_result(self, args):
        if args.verbose == 3 or args.verbose == 2:
            print(f'{Colors.OKBLUE} \n Selected structure:\n {Colors.ENDC}')
            for structure, weight in list(zip(self.selected_files, self.weights)):
                print(f'structure: {structure} weight: {weight:.3f} \n')
        if args.verbose == 3 or args.verbose == 2:
            print(f'{Colors.OKBLUE} \n Results:\n {Colors.ENDC}')
            for sumrmsd, chi2, data in self.results:
                print(f'RMSD: {sumrmsd:.3f} Chi2: {chi2:.3f}\n')
                for structure, weight in data:
                    print(f'structure: {structure} weight: {weight:.3f} \n')
        for sumrmsd, chi2, data in self.results:
            logging.info(f'###result_RMSD: {sumrmsd:5.3f} \n###result_CHI2: {chi2:5.3f}')
            for structure, weight in data:
                logging.info(f'#result_structure: {structure}| result_weight: {weight}')
    def get_best_result(self):
        if self.results == []:
            return 0
        else:
            print(self.results)
            return min(rmsd for rmsd, _, _ in self.results)

class SpecialFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG : logging._STYLES['{'][0]("DEBUG: {message}"),
           logging.ERROR : logging._STYLES['{'][0]("{module} : {lineno}: {message}"),
           logging.INFO : logging._STYLES['{'][0]("{message}"),
           'DEFAULT' : logging._STYLES['{'][0](" {message}")}

    def format(self, record):
        # Ugly. Should be better
        self._style = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)



def set_argument():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="mydirvariable",
                        help="Choose dir", metavar="DIR", required=True)

    parser.add_argument("-n", metavar='N', type=int,
                        dest="n_files",
                        help="Number of selected structure",
                        required=True)

    parser.add_argument("-k", metavar='K', type=int,
                        dest="k_options",
                        help="Number of possibility structure, must be less then selected files",
                        required=True)

    parser.add_argument("-r", metavar='R', type=int,
                        dest="repeat", help="Number of repetitions",
                        default=1)
    parser.add_argument("--verbose", type = int,
                        help="increase output verbosity, possible value 0, 1, 2, 3",
                        default=0)

    parser.add_argument("--verbose_logfile", help="increase output verbosity",
                       action="store_true")


    parser.add_argument("--tolerance", type=float, dest="tolerance",
                        help="pessimist (0) or optimist (0 < x <1) result",
                        default=0)

    parser.add_argument("--preserve", help="preserve temporary directory",
                        action="store_true")

    parser.add_argument("--method", help="choose method",
                        choices=get_saxs_methods(), required=True)

    parser.add_argument("--output", help="choose directory to save output",
                        metavar = "DIR", dest="output", required=True)


    parser.add_argument("--experimentdata", help="choose file for adderror",
                        metavar = "DIR", dest="experimentdata",required=True)

    return parser.parse_args()


def find_pdb_file(mydirvariable):
    pdb_files = []
    files = listdir(mydirvariable)
    for line in files:
        line = line.rstrip()
        if re.search('.pdb$', line):
            pdb_files.append(line)

    return pdb_files


def test_argument(args, list_pdb_file):
    if len(list_pdb_file) < args.n_files:
        print(f'{Colors.WARNING} Number of pdb files is ONLY {Colors.END} {len(list_pdb_file)} \n')
        logging.error(f'Number of pdb files is ONLY {len(list_pdb_file)}')
        sys.exit(1)
    if args.k_options > args.n_files:
        print(f'{Colors.WARNING} Number of selected structure is ONLY {Colors.ENDC} {args.n_files} \n')
        logging.error(f'Number of selected structure is ONLY { args.n_files}')
        sys.exit(1)
    if args.tolerance > 1:
        print('Tolerance should be less then 1.')
        logging.error('Tolerance should be less then 1.')
        sys.exit(1)


def print_parameters_verbose(args, list_pdb_file, all_files):
    print(f'{Colors.OKBLUE} Parameters \n {Colors.ENDC}')
    print(f'Working directory: {os.getcwd()} \n')
    print(f'Tolerance: {args.tolerance} \n')
    print(f'Total number of available pdb files in the directory: {len(list_pdb_file)} \n')
    print(f'List of the all used files ({len(all_files)}):\n')
    for i in range(len(all_files)):
        if (i + 1) % 7 == 0:
            print(all_files[i])
        else:
            print(all_files[i], '\t', end='')
    print('\n')
    print('-------------------------------------------')

def prepare_directory(tmpdir):
    pathlib.Path(f'{tmpdir}/pdbs').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{tmpdir}/dats').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{tmpdir}/method').mkdir(parents=True, exist_ok=True)
    pathlib.Path(f'{tmpdir}/results').mkdir(parents=True, exist_ok=True)
    # prepare 'file'.dat and copy to /dats/


def make_curve_for_experiment(files_and_weights, tmpdir, experimentdata, mydirvariable):
    files = [filename for filename, weight in files_and_weights]
    qs = np.linspace(0, 0.5, 501)
    curves = {}
    for filename in files:
        with open(mydirvariable + filename.split('.')[0] + '.dat') as file:
            data = []
            for line in file:
                if line.startswith('#'):
                    continue
                data.append(line.split()[1])
            curves[filename] = np.array(data, dtype=float)

    result_curve = np.zeros(501, dtype=float)

    for filename, weight in files_and_weights:
        result_curve += curves[filename] * weight

    with open(f'{tmpdir}/method/curve', 'w') as file:
        for q, y in zip(qs, result_curve):
            file.write(f'{q:5.3f} {y} 0\n')

    adderror(experimentdata, f'{tmpdir}/method/curve')


def process_result(tolerance, result_chi_structure_weights, run, mydirvariable):
    minimum = min(chi2 for chi2, _ in result_chi_structure_weights)
    maximum = minimum * (1 + tolerance)

    all_results = []
    for chi2, names_and_weights in result_chi_structure_weights:
        result_files = [file for file, _ in names_and_weights]
        result_weights = [weight for _, weight in names_and_weights]
        if float(chi2) <= maximum:
            os.chdir(mydirvariable)
            weighted_rmsd = compare_ensembles([mydirvariable + x + '.pdb' for x in run.selected_files], result_files, run.weights, result_weights)
            all_results.append((weighted_rmsd, chi2, names_and_weights))
    run.results = all_results
    return run


def final_statistic(runs, verbose):
    if verbose == 2 or verbose == 1 or verbose == 3:
        print('====================================================')
        print('====================================================')
        print(f'{Colors.HEADER}\nFINAL STATISTICS \n {Colors.ENDC}')
    rmsd = [result.get_best_result() for result in runs]
    if verbose == 2 or verbose == 1 or verbose == 3:
        print(f'Number of runs: {len(runs)}')
    logging.info(f'*****All RMSDs| runs {len(runs)}:')
    for number in rmsd:
        logging.info(f'|{number:5.3f}|')

    indices = [i for i, x in enumerate(rmsd) if x == min(rmsd)]
    if verbose == 2 or verbose == 1 or verbose == 3:
        #TODO opravit *indices
        print('Best RMSD {:5.3f}, run {}'.format(min(rmsd), *indices))
        print(f'RMSD = {np.mean(rmsd):.3f} ± {np.std(rmsd):.3f}')
    logging.info('Best RMSD {:5.3f}, run {}'.format(min(rmsd), *indices))
    logging.info(f'*****FINAL RMSD and STD| {np.mean(rmsd):5.3f}|{np.std(rmsd):5.3f}')

def run_method(args, path, method):
    all_runs = []
    for i in range(args.repeat):
        tmpdir = tempfile.mkdtemp()
        logging.info(f'Task {i}')
        logging.info(f'#Working directory: {tmpdir}')
        list_pdb_file = find_pdb_file(args.mydirvariable)
        if args.verbose ==  3 or args.verbose == 2:
            print('====================================================')
            print(f'{Colors.OKGREEN} RUN {i+1}/{args.repeat} \n {Colors.ENDC} \n')
        all_files = [x.split('.')[0] for x in random.sample(list_pdb_file, args.n_files)]
        # copy to pds
        selected_files = random.sample(all_files, args.k_options)
        # copy to dats
        sample = np.random.dirichlet(np.ones(args.k_options), size=1)[0]
        weights = np.round(np.random.multinomial(1000, sample) / 1000, 3)
        files_and_weights = list(zip(selected_files,weights))
        logging.info(f'#Selected_files \n')
        for file1, weight1 in files_and_weights:
            logging.info(f'#structure {file1} | weight {weight1:5.3f}')
        # copy to methods
        prepare_directory(tmpdir)
        if args.verbose == 3:
            print(f'{Colors.OKBLUE}\nCreated temporary directory \n {Colors.ENDC} {tmpdir}\n')
            print(f'{Colors.OKBLUE} Method {Colors.ENDC}\n {method} \n')
        m = importlib.import_module(f'methods_saxs.{method}')
        m.prepare_data(all_files, tmpdir, args.mydirvariable)
        logging.info(f'\n==========================\n')
        make_curve_for_experiment(files_and_weights, tmpdir, args.experimentdata, args.mydirvariable)
        if args.verbose == 3:
            print_parameters_verbose(args, list_pdb_file, all_files)
        run = Run(all_files, selected_files, weights, i + 1, method)
        m.make_experiment(all_files, tmpdir, args.verbose, args.verbose_logfile, path, args.mydirvariable)
        result_chi_structure_weights = m.collect_results(tmpdir, all_files)
        run = process_result(args.tolerance, result_chi_structure_weights, run, args.mydirvariable)

        all_runs.append(run)

        if not args.preserve:
            shutil.rmtree(tmpdir)

        run.print_result(args)
        logging.info(f'\n=============================\n')

    final_statistic(all_runs, args.verbose)
def check_binary():
    if os.path.exists(f'{os.getcwd()}/config.ini'):
        return True
    else:
        print('Config file does not exist!')
    return False

def get_saxs_methods():
    return list(m.name for m in pkgutil.iter_modules([config['SOURCE_METHODS']['path']]))

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(f'{os.getcwd()}/config.ini')

    if not check_binary():
        sys.exit(1)
    methods = get_saxs_methods()
    random.seed(1)
    np.random.seed(1)
    args = set_argument()
    os.chdir(args.mydirvariable)
    test_argument(args, find_pdb_file(args.mydirvariable))
    hdlr = logging.FileHandler(
        f'{args.output}/result_{args.method}_n{args.n_files}_k{args.k_options}_{strftime("%Y-%m-%d__%H-%M-%S", localtime())}.log')
    hdlr.setFormatter(SpecialFormatter())
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)
    logging.info(f'***Output from ensemble*** {strftime("%Y-%m-%d__%H-%M-%S", localtime())} \n')
    logging.info(f'Assignment for experiment')
    logging.info(f'#Method: {args.method}')
    logging.info(f'#Repeats: {args.repeat}')
    logging.info(f'#All_files: {args.n_files}')
    logging.info(f'\n=============================\n')
    logging.info(f'An assignment for each iteration\n')
    logging.info(f'----------------------------------\n')
    if args.verbose == 3 or args.verbose == 2 or args.verbose == 1:
        print(f' \n EXPERIMENT  {strftime("%Y-%m-%d__%H-%M-%S", localtime())}')

    if int(config[args.method]['value']) == -1:
        print('Wrong parametrs in config.int')
        sys.exit(1)

    if int(config[args.method]['value']) == 0:
        path = args.method
    else:
        path = config[args.method]['path']
    run_method(args, path, args.method)
