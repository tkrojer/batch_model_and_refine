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
from tabulate import tabulate


def analyse_process_directory(sample_folder, pdbDir):
    table = []
    header = ['run', 'process', 'resolution', 'spacegroup', 'reference_pdb', 'delta(UCvolume)']
    pipelines = ['autoproc', 'staraniso', 'dials']
    for runs in sorted(glob.glob(os.path.join(sample_folder, '*'))):
        run = runs.split('/')[len(runs.split('/'))-1]
        for process_pipeline in pipelines:
            pipeline, mtz_extension, log_extension, cif_extension = get_pipeline_path(process_pipeline)
            for mtzfile in sorted(glob.glob(os.path.join(runs, pipeline))):
                mtz = mtz_info(mtzfile)
                pdb, diff, pdb_name = find_pdb_input_file(pdbDir, mtzfile)
                table.append([run, process_pipeline, round(float(mtz['resolution_high']), 2), mtz['space_group'], pdb_name, diff])
    print(tabulate(table, headers=header))
    print("\n")


def print_summary():
    print('\n')
    print('Number of samples: ')
    print()


def create_sample_folder_in_project_dir(projectDir, sample, analyseOnly):
    if not analyseOnly:
        os.chdir(projectDir)
        if not os.path.isdir(sample):
            os.mkdir(sample)

def get_pipeline_path(process_pipeline):


    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/Data_2_autoPROC_TRUNCATE_all.cif
    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/HDF5_1/truncate-unique.mtz
    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/HDF5_1/aimless.log

    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/Data_1_autoPROC_STARANISO_all.cif
    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/HDF5_1/staraniso_alldata-unique.mtz
    # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/autoPROC/cn83_20211114-175135/AutoPROCv1_0_anom/HDF5_1/staraniso_alldata.log

    if process_pipeline == 'autoproc':
        pipeline = os.path.join('autoPROC', 'cn*', 'AutoPROCv1_*', 'HDF5_1', 'truncate-unique.mtz')
        mtz_extension = 'HDF5_1/truncate-unique.mtz'
        log_extension = 'HDF5_1/aimless.log'
        cif_extension = 'Data_2_autoPROC_TRUNCATE_all.cif'
    elif process_pipeline == 'staraniso':
        pipeline = os.path.join('autoPROC', 'cn*', 'AutoPROCv1_*', 'HDF5_1', 'staraniso_alldata-unique.mtz')
        mtz_extension = 'HDF5_1/staraniso_alldata-unique.mtz'
        log_extension = 'HDF5_1/staraniso_alldata.log'
        cif_extension = 'Data_1_autoPROC_STARANISO_all.cif'
    elif process_pipeline == 'dials':
        # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/xia2DIALS/cn68_20211114-175326/Xia2DIALSv1_0_anom/DataFiles/xia2.mmcif.bz2
        # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/xia2DIALS/cn68_20211114-175326/Xia2DIALSv1_0_anom/DataFiles/AUTOMATIC_DEFAULT_free.mtz
        # /data/visitors/biomax/20200054/20211113/process/hsDHS/hsDHS-x0139/xds_hsDHS-x0139_2_1/xia2DIALS/cn68_20211114-175326/Xia2DIALSv1_0_anom/LogFiles/AUTOMATIC_DEFAULT_SCALE.log
        pipeline = os.path.join('xia2DIALS', 'cn*', 'Xia2DIALSv1_*', 'DataFiles', 'AUTOMATIC_DEFAULT_free.mtz')
#        print(pipeline)
        mtz_extension = 'DataFiles/AUTOMATIC_DEFAULT_free.mtz'
        log_extension = 'LogFiles/AUTOMATIC_DEFAULT_SCALE.log'
        cif_extension = 'DataFiles/xia2.mmcif.bz2'
    return pipeline, mtz_extension, log_extension, cif_extension

def find_autoproc_results(sample_folder, process_pipeline):
    bestmtz = None
    bestlog = None
    bestcif = None
    pipeline, mtz_extension, log_extension, cif_extension = get_pipeline_path(process_pipeline)
    try:
        resoList = []
#        print('mtzfile', os.path.join(sample_folder, '*', pipeline))
        for mtzfile in glob.glob(os.path.join(sample_folder, '*', pipeline)):
            if os.path.isfile(mtzfile.replace(mtz_extension, log_extension)):
                logfile = mtzfile.replace(mtz_extension, log_extension)
            if os.path.isfile(mtzfile.replace(mtz_extension, cif_extension)):
                ciffile = mtzfile.replace(mtz_extension, cif_extension)
            else:
                logfile = None
#            mtz = gemmi.read_mtz_file(mtzfile)
            mtz = mtz_info(mtzfile)
#            print('>>>>>>>>>', mtz['unitcell'])
            resoList.append([mtzfile, float(mtz['resolution_high']), logfile, ciffile])
        if resoList:
            bestmtz = min(resoList, key=lambda x: x[1])[0]
            bestlog = min(resoList, key=lambda x: x[1])[2]
            bestcif = min(resoList, key=lambda x: x[1])[3]
    except UnboundLocalError:
        pass
    return bestmtz, bestlog, bestcif


def link_files_to_project_folder(projectDir, sample, mtz, log, cif):
    os.chdir(os.path.join(projectDir, sample))
    if not os.path.isfile('process.mtz'):
        os.system('ln -s {0!s} process.mtz'.format(mtz))
    if not os.path.isfile('process.log'):
        os.system('ln -s {0!s} process.log'.format(log))
    if not os.path.isfile('process.cif'):
        os.system('ln -s {0!s} process.cif'.format(cif))


def mtz_point_group_uc_volume(mtzfile):
    mtz = gemmi.read_mtz_file(mtzfile)
    unitcell = mtz.cell
    unitcell_volume = unitcell.volume
    sym = mtz.spacegroup
    point_group = sym.point_group_hm()
    return point_group, unitcell_volume

def mtz_info(mtzfile):
    mtzDict = {}
    mtz = gemmi.read_mtz_file(mtzfile)
    mtzDict['unitcell'] = mtz.cell
    mtzDict['unitcell_volume'] = mtz.cell.volume
    mtzDict['point_group'] = mtz.spacegroup.point_group_hm()
    mtzDict['resolution_high'] = mtz.resolution_high()
    mtzDict['space_group'] = mtz.spacegroup.hm
    return mtzDict


def pdb_point_group_uc_volume(pdbfile):
    structure = gemmi.read_pdb(pdbfile)
    unitcell = structure.cell
    unitcell_volume = unitcell.volume
#    structure.spacegroup_hm
    sym = gemmi.find_spacegroup_by_name(structure.spacegroup_hm)
    point_group = sym.point_group_hm()
    return point_group, unitcell_volume


def find_pdb_input_file(pdbDir, mtz):
    pdb = None
    pdb_name = None
    mtz_point_group, mtz_unitcell_volume = mtz_point_group_uc_volume(mtz)
    for pdbfile in glob.glob(os.path.join(pdbDir, '*.pdb')):
        pdb_point_group, pdb_unitcell_volume = pdb_point_group_uc_volume(pdbfile)
        diff = abs(mtz_unitcell_volume - pdb_unitcell_volume) / pdb_unitcell_volume
        if mtz_point_group == pdb_point_group and diff < 0.1:
            pdb = pdbfile
            pdb_name = pdb.split('/')[len(pdb.split('/'))-1]
    return pdb, diff, pdb_name


def prepare_init_refine_script(projectDir, sample, pdb, refine_pipeline):
    os.chdir(os.path.join(projectDir, sample))
    cmd = (
            '#!/bin/bash\n'
            '#SBATCH --time=10:00:00\n'
            '#SBATCH --job-name={0!s}\n'.format(refine_pipeline) +
            '#SBATCH --cpus-per-task=1\n'
    )

    if refine_pipeline == 'dimple':
        cmd += (
                'module load gopresto CCP4/7.1.016-SHELX-ARP-8.0-1-PReSTO\n'
                'cd {0!s}\n'.format(os.path.join(projectDir, sample)) +
                'dimple process.mtz {0!s} dimple'.format(pdb)
        )

    elif refine_pipeline == 'pipedream':
        cmd += (
        		'module load gopresto BUSTER\n'
        		'cd {0!s}\n'.format(os.path.join(projectDir, sample)) +
        		'pipedream -hklin process.mtz -xyzin {0!s} -d pipedream -nofreeref -nolmr'.format(pdb)
        )

    f = open('{0!s}.sh'.format(refine_pipeline), 'w')
    f.write(cmd)
    f.close()

def submit_init_refine_script(projectDir, sample, refine_pipeline):
    os.chdir(os.path.join(projectDir, sample))
    print('submitting {0!s} job for {1!s}'.format(refine_pipeline, sample))
    os.system('sbatch {0!s}.sh'.format(refine_pipeline))


def run_initial_refinement(processDir, projectDir, pdbDir, process_pipeline, refine_pipeline, analyseOnly):
    for n, sample_folder in enumerate(sorted(glob.glob(os.path.join(processDir, '*')))):
        sample = sample_folder.split('/')[len(sample_folder.split('/'))-1]
        print('sample: ' + sample + '\n')
        if analyseOnly:
            analyse_process_directory(sample_folder, pdbDir)
        else:
#            create_sample_folder_in_project_dir(projectDir, sample, analyseOnly)
            mtz, log, cif = find_autoproc_results(sample_folder, process_pipeline)
            if mtz:
                create_sample_folder_in_project_dir(projectDir, sample, analyseOnly)
                link_files_to_project_folder(projectDir, sample, mtz, log, cif)
                pdb, diff, pdb_name = find_pdb_input_file(pdbDir, mtz)
                prepare_init_refine_script(projectDir, sample, pdb, refine_pipeline)
                submit_init_refine_script(projectDir, sample, refine_pipeline)



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
        '--analyse, -y\n'
        '    flag to analyse process directory, without file operations\n'
    )
    print(usage)



def main(argv):
    processDir = None
    projectDir = None
    pdbDir = None
    process_pipeline = None
    refine_pipeline = None
    overwrite = False
    analyseOnly = False

    try:
        opts, args = getopt.getopt(argv,"i:o:p:a:r:hy",["input=", "output=", "pdbdir=",
                                                         "autoproc=", "refine=", "analyse"])
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
        elif opt in ("-y", "--analyse"):
            analyseOnly = True


#    try:
    run_initial_refinement(processDir, projectDir, pdbDir, process_pipeline, refine_pipeline, analyseOnly)
#    except TypeError:
#        print('kkkkkk')
#        usage()

if __name__ == '__main__':
    main(sys.argv[1:])
