#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import tempfile
import os
import sys
import shutil
import logging
import subprocess
import threading
import glob
from multiprocessing import Pool
import configparser

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
                        help="Choose dir with pdb files", metavar="DIR", required=True)

    parser.add_argument("--finaldir", help="choose dir to making saxs curve")

    parser.add_argument("--makecurve", help="choose method to make a curve",
                        choices=['foxs', 'crysol'], required=True)

    parser.add_argument("--verbose_logfile", help="increase output verbosity",
                        action="store_true")

    return parser.parse_args()

def run_method(method, config):
    if shutil.which(method):
        print(f'Selected method: {shutil.which(method)}')
        path = method
    else:
        print(f'{method} will run from configurations file {os.getcwd()} config.ini')
        if os.path.exists(os.getcwd() + '/config.ini'):
            path = config[method]['path']
        else: print(f'Config file does not exist!, the {method} can not run.')
        sys.exit(1)
    if method=='foxs':
        make_foxs(glob.glob(os.path.join(os.getcwd(), '*')), path)
    if method == 'crysol':
        make_crysol(glob.glob(os.path.join(os.getcwd(), '*')), path)


def check_directory_pdb_files(mydirvariable, final_directory):
    if not os.path.exists(mydirvariable):
        print('Directory with pdb files does not exist')
        sys.exit(1)

    all_files = os.listdir(mydirvariable)
    for file in all_files:
        pass
        shutil.copy(f'{os.path.abspath(mydirvariable)}/{file}', final_directory)

def make_foxs(all_files, path):
    for file in all_files:
        """
        if verbose_logfile:
            logpipe = LogPipe(logging.DEBUG)
            # fox sends stdout to stderr by default
            logpipe_err = LogPipe(logging.DEBUG)
            return_value = subprocess.run(['foxs', f'{file}'], stdout=logpipe,
                                          stderr=logpipe_err)
            logpipe.close()
            logpipe_err.close()
        else:
        """
        return_value = subprocess.run([path, file], stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        if return_value.returncode:
            print(f'ERROR: Foxs failed.', file=sys.stderr)
            logging.error(f'Foxs failed.')
            sys.exit(1)
    [os.rename(f, f.replace('.pdb.dat', '.dat')) for f in glob.glob(os.path.join(os.getcwd(), '*'))] #if not f.startswith('.')]


#TODO
def make_crysol(all_files, path):
    #take an abinito's curve
    for file in all_files:
        """
        if verbose_logfile:
            logpipe = LogPipe(logging.DEBUG)
            # fox sends stdout to stderr by default
            logpipe_err = LogPipe(logging.DEBUG)
            return_value = subprocess.run(['crysol', f'{file}'], stdout=logpipe,
                                          stderr=logpipe_err)
            logpipe.close()
            logpipe_err.close()
        else:
        """
        return_value = subprocess.run([path, f'{file}'], stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)

        if return_value.returncode:
            print(f'ERROR: CRYSOL failed.', file=sys.stderr)
            logging.error(f'CRYSOL failed.')
            sys.exit(1)
    #crysol makes several curves, script takes  theoretical intensity in solution
    #The first line is a title. Five columns contain: (1) experimental scattering vector in inverse angstroms,
    # (2) theoretical intensity in solution, (3) in vacuo, (4) the solvent scattering
    # and (5) the border layer scattering.
    #crysol transforms mod01.pdb to mod01000.int
        print(file)
        new_name = file.split('.')[0] + '00.int'
        print(new_name)
        with open(new_name) as new_file, open(file.split('.')[0] + '.dat','w') as final_file:
            #final_file.write('# SAXS profile')
            for line in new_file:
                #if line.startswith(' Dif/ '):
                #    final_file.write(line)
                #    final_file.write('#    q    intensity    error')
                if line.startswith('  '):
                    final_file.write(line.split('  ')[1] + '\t')
                    final_file.write(line.split('  ')[2] + '\t')
                    final_file.write(line.split('  ')[5])
                else:
                    final_file.write('#' + line.rstrip() + '\n')
                    final_file.write('#    q    intensity    error' + '\n')
    #sys.exit(1)


def main():
    config = configparser.ConfigParser()
    config.read(os.getcwd() + '/config.ini')
    tmpdir = tempfile.mkdtemp()
    args = set_argument()
    print('Source directory is:', os.path.abspath(args.mydirvariable))
    if args.finaldir:
        if not os.path.exists(args.finaldir):
            os.makedirs(args.finaldir)
        else:
            print('Directory already exist')
            sys.exit(1)
        check_directory_pdb_files(args.mydirvariable, args.finaldir)
        print(f'Directory with saxs curve is: {args.finaldir}')
        os.chdir(args.finaldir)
    else:
        check_directory_pdb_files(args.mydirvariable, tmpdir)
        print('Directory with saxs curve is:', tmpdir)
        os.chdir(tmpdir)
    #function_partial = partial(make_foxs, args.verbose_logfile)
   # with  Pool(os.cpu_count()) as pool:
   #      if args.makecurve=='foxs':
   #          pool.map(make_foxs, glob.glob(os.path.join(os.getcwd(), '*')))
   #      if args.makecurve=='crysol':
   #         pool.map(make_crysol, glob.glob(os.path.join(os.getcwd(), '*')))
    run_method(args.makecurve, config)
    #if args.makecurve=='foxs':
    #    if check_binary(args.makecurve, config):
    #        make_foxs(glob.glob(os.path.join(os.getcwd(), '*')))
    #if args.makecurve == 'crysol':
    #    if check_binary(args.makecurve, config):
    #        make_crysol(glob.glob(os.path.join(os.getcwd(), '*')))
if __name__ == '__main__':
    main()