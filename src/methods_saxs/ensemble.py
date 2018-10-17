# prepare_data()
# make_experiment()
# collect_result()

import shutil
import subprocess
import sys
import logging
from saxs_experiment import LogPipe
import pathlib
from saxs_experiment import Colors


def prepare_data(all_files, tmpdir, mydirvariable):
    pathlib.Path(f'{tmpdir}/pdbs/ensembles').mkdir(parents=True, exist_ok=True)

    for i, file in enumerate(all_files, start=1):
        shutil.copy(f'{mydirvariable}/{file}.pdb', f'{tmpdir}/pdbs/ensembles/{i:02d}.pdb')
def make_experiment(all_files, tmpdir, verbose, verbose_logfile, path, mydirvariable):
    # RUN ensemble
    command = f'{path} -L -p {tmpdir}/pdbs/ensembles/ -n {len(all_files)} -m {tmpdir}/method/curve.modified.dat'
    if verbose == 3:
        print(f'{Colors.OKBLUE} Command for ensemble fit \n {Colors.ENDC, comman} \n')
    if verbose_logfile:
        logpipe = LogPipe(logging.DEBUG)
        logpipe_err = LogPipe(logging.ERROR)
        logging.info(f'Command for ensemble fit \n {command}')
        call = subprocess.run([f'{path}', '-L', '-p', f'{tmpdir}/pdbs/ensembles/', '-n', f'{len(all_files)}',
                               '-m', f'{tmpdir}/method/curve.modified.dat'],
                              cwd=f'{tmpdir}/results/', stdout=logpipe, stderr=logpipe_err)
        logpipe.close()
        logpipe_err.close()
    else:
        call = subprocess.run(
            [f'{path}', '-L', '-p', f'{tmpdir}/pdbs/ensembles/', '-n', f'{len(all_files)}', '-m',
             f'{tmpdir}/method/curve.modified.dat'],
            cwd=f'{tmpdir}/results/', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if call.returncode:
        print(f'ERROR: ensemble failed', file=sys.stderr)
        logging.error(f'Ensemble failed.')

        sys.exit(1)


def collect_results(tmpdir, all_files):
    # Process with result from ensemble
    result_chi_and_weights_ensemble = []
    # 5000
    # 1.08e+01,0.952,2.558,4.352610,0.000,0.300,0.000,0.000,0.000,0.000,0.000,0.092,0.000,0.908
    # 1.08e+01,0.950,2.558,4.752610,0.000,0.100,0.000,0.000,0.000,0.000,0.000,0.092,0.000,0.908
    with open(f'{tmpdir}/results/result', 'r') as f:
        next(f)

        for line in f:
            line = line.rstrip()
            value_of_chi2 = float(line.split(',')[3])
            values_of_index_result = [float(value) for value in line.split(',')[4:]]
            result_chi_and_weights_ensemble.append((value_of_chi2, values_of_index_result))
    ensemble_results = []
    structure = []
    for chi2, weights in result_chi_and_weights_ensemble:
        for i, weight in enumerate(weights):
            if weight >= 0.001:
                structure.append((f'{all_files[i]}.pdb', weight))
        ensemble_results.append((chi2, structure))
    return ensemble_results

    # ((chi2, [('mod10.pdb', 0.3), ('mod15.pdb', 0.7)]),(chi2(strucutre, weight),(strucutre, weight)))
