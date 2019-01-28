# prepare_data()
# make_experiment()
# collect_result()

import logging
import re
import shutil
import subprocess
import sys
from os import listdir

from saxs_experiment import LogPipe


def prepare_data(all_files, tmpdir, mydirvariable):
    datas_files = []
    files = listdir(tmpdir + '/dats/')
    for line in files:
        line = line.rstrip()
        if re.search('.dat$', line):
            datas_files.append(line)
    lines = []
    for file in datas_files:
        with open(f'{tmpdir}/dats/{file}', 'w') as f:
            f.writelines(lines[:0] + lines[2:])
            shutil.copy(file, f'{tmpdir}/method/')

    for file in all_files:  # not strict format for pdbs file
        shutil.copy(f'{mydirvariable}/{file}.pdb', f'{tmpdir}/pdbs/')
        shutil.copy(f'{mydirvariable}/{file}.dat', f'{tmpdir}/dats/')
        shutil.copy(f'{mydirvariable}/{file}.dat', f'{tmpdir}/method/')


def make_experiment(all_files, tmpdir, verbose, verbose_logfile, path, mydirvariable):
    # Run MES
    logpipe = LogPipe(logging.DEBUG)
    logpipe_err = LogPipe(logging.DEBUG)
    # add empty line to curve,modified.dat
    with open(f'{tmpdir}/method/curve.modified.dat', 'r+') as f:
        line = ''
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
    # remove second line from file.dat, program accepts just one line at the beginning

    with open(f'{tmpdir}/method/filelist', 'w') as file_mes:

        file_mes.write(f'curve.modified.dat \n')
        for file in all_files:
            file_mes.write(f'{file}.dat' + '\n')
            # remove second line from saxs file
            call = subprocess.run(['sed', '-i', '2d', f'{tmpdir}/method/' + f'{file}' + '.dat'])
            if call.returncode:
                print(f'ERROR: script failed in methods mes', file=sys.stderr)
                logging.error(f'Script failed in method mes.')
                sys.exit(1)

    if verbose_logfile:
        with open(f'{tmpdir}/method/result_mes', 'a') as file_mes:
            call = subprocess.run([path, f'{tmpdir}/method/filelist'],
                                  cwd=f'{tmpdir}/method/',
                                  stdout=file_mes, stderr=logpipe_err)
    else:
        with open(f'{tmpdir}/method/result_mes', 'a') as file_mes:
            call = subprocess.run([path, f'{tmpdir}/method/filelist'],
                                  cwd=f'{tmpdir}/method/',
                                  stdout=file_mes, stderr=subprocess.PIPE)

    if call.returncode:
        print(f'ERROR: mes failed', file=sys.stderr)
        logging.error(f'mes failed.')
        sys.exit(1)
    logpipe.close()
    logpipe_err.close()


def collect_results(tmpdir, all_files):
    result = []
    chi2 = 0
    weight_strucutre = []
    with open(f'{tmpdir}/method/result_mes') as file_mes:
        for line in file_mes:
            if line.startswith('  best xi'):
                chi2 = float(line.split(':')[1])
            if re.search('\d.dat', line):
                structure = line.split('.')[0].strip() + '.pdb'
                weight = float(line.split(' ')[5].rstrip())
                weight_strucutre.append((structure, weight))
        result.append((chi2, weight_strucutre))
    return result
