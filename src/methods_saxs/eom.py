# prepare_data()
# make_experiment()
# collect_result()
import re
import shutil
import subprocess
import sys
import fortranformat as ff
import logging
from saxs_experiment import LogPipe

def prepare_data(all_files, tmpdir, method, verbose_logfile):
    for file in all_files:  # not strict format for pdbs file
        shutil.copy(file, f'{tmpdir}/pdbs/')
        shutil.copy(file + '.dat', f'{tmpdir}/dats/')
def make_experiment(all_files, tmpdir, verbose, verbose_logfile, method):
    # Angular axis m01000.sax             Datafile m21000.sub         21-Jun-2001
    # .0162755E+00 0.644075E+03 0.293106E+02
    with open(tmpdir + '/method/curve_gajoe.dat', 'w') as file_gajoe:
        file_gajoe.write(' Angular axis m01000.sax             Datafile m21000.sub         21-Jun-2001\n')
        lineformat = ff.FortranRecordWriter('(1E12.6)')
        with open(tmpdir + '/method/curve.modified.dat') as file1:
            for line in file1:
                if not line.strip():
                    break
                data1 = float(line.split()[0])
                data2 = float(line.split()[1])
                data3 = float(line.split()[2])
                a = lineformat.write([data1])
                x = a[1:]
                b = lineformat.write([data2])
                c = lineformat.write([data3])
                file_gajoe.write(f' {x} {b} {c}\n')
    # S values    num_lines
    # 0.000000E+00
    # ------
    #  Curve no.     1
    # 0.309279E+08
    num_lines = sum(1 for line in open(all_files[0] + ".dat")) - 2
    with open(tmpdir + '/method/juneom.eom', 'w') as file1:
        file1.write(f'    S values   {num_lines} \n')
        with open(all_files[0] + ".dat") as file2:
            for line in file2:
                if line.startswith('#'):
                    continue
                data = float(line.split()[0])
                lineformat = ff.FortranRecordWriter('(1E14.6)')
                b = lineformat.write([data])
                file1.write(f'{b}\n')
        for i, filename in enumerate(all_files, start=1):
            with open(filename + ".dat") as file2:
                file1.write(f'Curve no.     {i} \n')
                for line in file2:
                    if line.startswith('#'):
                        continue
                    data1 = float(line.split()[1])
                    lineformat = ff.FortranRecordWriter('(1E14.6)')
                    b = lineformat.write([data1])
                    file1.write(f'{b}\n')
    if verbose_logfile:
        logpipe = LogPipe(logging.DEBUG)
        logpipe_err = LogPipe(logging.ERROR)
        p1 = subprocess.Popen(['yes'], stdout=subprocess.PIPE)
        call = subprocess.Popen(['gajoe', f'{tmpdir}/method/curve_gajoe.dat', f'-i={tmpdir}/method/juneom.eom',
                                 '-t=5'], cwd=f'{tmpdir}/results/', stdin=p1.stdout,
                                stdout=logpipe, stderr=logpipe_err)
        call.communicate()
        logpipe.close()
        logpipe_err.close()
    else:
        p1 = subprocess.Popen(['yes'], stdout=subprocess.PIPE)
        call = subprocess.Popen(['gajoe', f'{tmpdir}/method/curve_gajoe.dat', f'-i={tmpdir}/method/juneom.eom',
                                 '-t=5'], cwd=f'{tmpdir}/results/', stdin=p1.stdout,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        call.communicate()
    if call.returncode:
        print(f'ERROR: GAJOE failed', file=sys.stderr)
        logging.error(f'GAJOE failed.')
        sys.exit(1)


def collect_results(tmpdir, all_files):
    # process results from gajoe (/GAOO1/curve_1/
    chi2 = None
    structure_weight = []
    m = re.compile('^\s*\d+\)')
    with open(tmpdir + '/results/GA001/curve_1/logFile_001_1.log') as file_gajoe:
        for line in file_gajoe:
            if '-- Chi^2 : ' in line:
                chi2 = float(line.split(':')[1])
                # curve                   weight
                # 00002ethod/juneom.pd ~0.253.00
                # 00003ethod/juneom.pd ~0.172.00
            p = m.search(line)
            if p:
                index = int(line.split()[1][:5]) - 1
                weight = float((line.split()[4][1:6]).strip('*'))
                structure_weight.append((all_files[index], weight))
    return [(chi2, structure_weight)]
    # ([chi2,[(structure, weight), (structure,weight), (structure, weight),... ], [chi2,(),...])
