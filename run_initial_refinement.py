# Copyright (c) 2022, Tobias Krojer, MAX IV Laboratory
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import getopt
import glob
import sys
import os
import gemmi


def create_sample_folder_in_project_dir(projectDir, sample):
    os.chdir(projectDir)
    if not os.path.isdir(sample):
        os.mkdir(sample)


def find_autoproc_results(sample_folder, process_pipeline):
    bestmtz = None
    bestlog = None
    if process_pipeline == 'autoproc':
        pipeline = os.path.join('autoPROC', 'results', '*_anom_truncate.mtz')
        log = '-unique.table1'
    try:
        resoList = []
        for mtzfile in glob.glob(os.path.join(sample_folder, '*', pipeline)):
            if os.path.isfile(mtzfile.replace('.mtz', log)):
                logfile = mtzfile.replace('.mtz', log)
            else:
                logfile = None
            mtz = gemmi.read_mtz_file(mtzfile)
            resoList.append([mtzfile, float(mtz.resolution_high()), logfile])
        if resoList:
            bestmtz = min(resoList, key=lambda x: x[1])[0]
            bestlog = min(resoList, key=lambda x: x[1])[2]
    except UnboundLocalError:
        pass
    return bestmtz, bestlog


def link_files_to_project_folder(processDir, sample, mtz, log):
    os.chdir(processDir, sample)
    if not os.path.isfile('process.mtz'):
        print('ln -s {0!s} process.mtz'.format(mtz))
    if not os.path.isfile('process.log'):
        print('ln -s {0!s} process.log'.format(log))


def mtz_point_group_uc_volume(mtzfile):
    mtz = gemmi.read_mtz_file(mtzfile)
    unitcell = mtz.cell
    unitcell_volume = unitcell.volume
    sym = mtz.spacegroup
    point_group = sym.point_group_hm()
    return point_group, unitcell_volume


def pdb_point_group_uc_volume(pdbfile):
    structure = gemmi.read_pdb(pdbfile)
    unitcell_volume = unitcell.volume
    structure.spacegroup_hm
    sym = gemmi.find_spacegroup_by_name(structure.spacegroup_hm)
    point_group = sym.point_group_hm()
    return point_group, unitcell_volume


def find_pdb_input_file(pdbDir, mtz):
    pdb = None
    mtz_point_group, mtz_unitcell_volume = mtz_point_group_uc_volume(mtz)
    for pdbfile in glob.glob(os.path.join(pdbDir, '*.pdb')):
        pdb_point_group, pdb_unitcell_volume = pdb_point_group_uc_volume(pdbfile)
        diff = abs(mtz_unitcell_volume - pdb_unitcell_volume) / pdb_unitcell_volume
        if mtz_point_group == pdb_point_group and diff < 0.1:
            pdb = pdbfile
    return pdb


def prepare_init_refine_script(processDir, sample, pdb, refine_pipeline):
    os.chdir(os.path.join(processDir, sample))
    cmd = (
            '#!/bin/bash\n'
            '#SBATCH --time=10:00:00\n'
            '#SBATCH --job-name={0!s}\n'.format(refine_pipeline) +
            '#SBATCH --cpus-per-task=1\n'
    )

    if refine_pipeline == 'dimple':
        cmd += (
                'module load gopresto CCP4/7.1.016-SHELX-ARP-8.0-1-PReSTO\n'
                'cd {0!s}\n'.format(os.path.join(processDir, sample)) +
                'dimple process.mtz {0!s} dimple'.format(pdb)
        )

    print(cmd)
#    f = open('{0!s}.sh'.format(refine_pipeline), 'w')
#    f.write(cmd)
#    f.close()

def submit_init_refine_script(processDir, sample, refine_pipeline):
    os.chdir(os.path.join(processDir, sample))
    print('submitting {0!s} job for {1!s}'.format(refine_pipeline, sample))
    print('sbatch {0!s}.sh'.format(refine_pipeline))


def run_initial_refinement(processDir, projectDir, pdbDir, process_pipeline, refine_pipeline):
    for sample_folder in sorted(glob.glob(os.path.join(processDir, '*'))):
        sample = sample_folder.split('/')[len(sample_folder.split('/'))-1]
        print(sample)
        create_sample_folder_in_project_dir(projectDir, sample)
        mtz, log = find_autoproc_results(sample_folder, process_pipeline)
        link_files_to_project_folder(processDir, sample, mtz, log)
        pdb = find_pdb_input_file(pdbDir, mtz)
        prepare_init_refine_script(processDir, sample, pdb, refine_pipeline)
        submit_init_refine_script(processDir, sample, refine_pipeline)



def usage():
    usage = (
        '\n'
        'usage:\n'
        'ccp4-python run_initial_refinement.py -i <process_dir> -o <project_dir>\n'
        '\n'
        'additional command line options:\n'
        '--input, -i\n'
        '    process directory\n'
        '--output, -o\n'
        '    project directory\n'
        '--pdbdir, -p\n'
        '    directory with pdb files\n'
        '    note: pdb files not to have valid CRYST1 card'
        '--autoproc, -a\n'
        '    auto-processing pipeline (e.g. autooproc)\n'
        '--refine, -r\n'
        '    initial refinement pipeline (e.g. dimple)\n'
        '--overwrite, -o\n'
        '    flag to overwrite files\n'
    )
    print(usage)



def main(argv):
    processDir = None
    projectDir = None
    pdbDir = None
    process_pipeline = None
    refine_pipeline = None
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"i:o:p:a:r:h",["input=", "output=", "pdbdir=",
                                                         "autoproc=", "refine=",])
    except getopt.GetoptError:
        print('foehfuie')
#        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            processDir = arg
        elif opt in ("-o", "--output"):
            projectDir = arg
        elif opt in ("-p", "--pdbdir"):
            pdbDir = arg
        elif opt in ("-a", "--autoproc"):
            process_pipeline = arg
        elif opt in ("-r", "--refine"):
            refine_pipeline = arg


#    try:
    run_initial_refinement(processDir, projectDir, pdbDir, process_pipeline, refine_pipeline)
#    except TypeError:
#        print('kkkkkk')
#        usage()

if __name__ == '__main__':
    main(sys.argv[1:])
