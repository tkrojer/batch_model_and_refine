import os
import csv


def make_sample_directory(projectDir, sampleID):
    os.chdir(projectDir)
    if not os.path.isdir(sampleID):
        print('{0!s}: making sample directory'.format(sampleID))
        os.mkdir(sampleID)
    else:
        print('{0!s}: sample directory exists'.format(sampleID))


def make_subdirectory(projectDir, sampleID, subdirectory):
    os.chdir(os.path.join(projectDir, sampleID))
    if not os.path.isdir(subdirectory):
        print('{0!s}: making subirectory for ligand files with name {1!s}'.format(sampleID, subdirectory))
        os.mkdir(subdirectory)
    else:
        print('{0!s}: subirectory for ligand files with name {1!s} exists'.format(sampleID, subdirectory))


def modules_to_load(restraints_program):
    if restraints_program == 'acedrg':
        module = 'module load gopresto CCP4'
    elif restraints_program == 'grade':
        module = 'module load gopresto BUSTER'
    elif restraints_program == 'elbow':
        module = 'module load gopresto Phenix'
    return module


def maxiv_header(restraints_program):
    header = (
        '#!/bin/bash\n'
        '#SBATCH --time=10:00:00\n'
        '#SBATCH --job-name={0!s}\n'.format(restraints_program) +
        '#SBATCH --cpus-per-task=1\n'
    )
    return header


def restraints_program_cmd(restraints_program, ligandID, smiles):
    if restraints_program == 'acedrg':
        cmd = 'acedrg --res LIG -i "{0!s}" -o {1!s}'.format(smiles, ligandID)
    elif restraints_program == 'grade':
        cmd = ''
    elif restraints_program == 'elbow':
        cmd = ''
    return cmd


def prepare_script_for_maxiv(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles):
    os.chdir(os.path.join(projectDir, sampleID, subdirectory))
    cmd = maxiv_header()
    cmd += maxiv_header(restraints_program)
    cmd += 'cd {0!s}\n'.format(os.path.join(projectDir, sampleID, subdirectory))
    cmd += restraints_program_cmd(restraints_program, ligandID, smiles)
    f = open('{0!s}.sh'.format(restraints_program), 'w')
    f.write(cmd)
    f.close()


def submit_maxiv_script(restraints_program, projectDir, sampleID, subdirectory):
    os.chdir(os.path.join(projectDir, sampleID, subdirectory))
    print('{0!s}: submitting {1!s} to cluster'.format(sampleID, restraints_program))
    os.system('sbatch {0!s}.sh'.format(restraints_program))


def run_program_on_maxiv_cluster(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles):
    prepare_script_for_maxiv(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles)
    submit_maxiv_script(restraints_program, projectDir, sampleID, subdirectory)


def run_program_on_local_machine(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles):
    cmd = restraints_program_cmd(restraints_program, ligandID, smiles)
    os.chdir(os.path.join(projectDir, sampleID, subdirectory))
    os.system(cmd)

def make_ligand_restraints(projectDir, ligandCsv, restraints_program, overwrite, subdirectory, maxiv):
    dialect = csv.Sniffer().sniff(open(ligandCsv).readline(), [',', ';'])
    csvFile = csv.reader(open(ligandCsv), dialect)

    for row in csvFile:
        sampleID = row[0].replace(' ', '')
        ligandID = row[1].replace(' ', '')
        smiles = row[2].replace(' ', '')
        make_sample_directory(projectDir, sampleID)
        if subdirectory:
            make_subdirectory(projectDir, sampleID, subdirectory)
        if maxiv:
            run_program_on_maxiv_cluster(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles)
        else:
            run_program_on_local_machine(restraints_program, projectDir, sampleID, subdirectory, ligandID, smiles)


def usage():
    usage = (
        '\n'
        'usage:\n'
        'ccp4-python make_ligand_restraints.py -p <project_dir> -l <ligand_csv> -r <restraints_program>\n'
        '\n'
        'additional command line options:\n'
        '--project-directory, -p\n'
        '    project directory\n'
        '--ligand-csv, -l\n'
        '    ligand csv file formatted as "sample_ID","ligand_ID","smiles"\n'
        '--restraints-program, -l\n'
        '    program for restraints generation: grade, acedrg, elbow\n'
        '--subdirectory, -s\n'
        '    subdirectory name where compound restraints are stored, e.g. "-s compound"\n'
        '--maxiv, -m\n'
        '    flag to running script on MAXIV offline cluster"\n'
        '--overwrite, -o\n'
        '    flag to overwrite existing files\n'
    )
    print(usage)

def check_csv(ligandCsv):
    print('-> checking csv file: {0!s}'.format(ligandCsv))
    passed = True
    try:
        dialect = csv.Sniffer().sniff(open(ligandCsv).readline(), [',', ';'])
    except FileNotFoundError:
        print('ERROR: csv file does not exists')
        passed = False
    except UnicodeDecodeError:
        print('ERROR: that does not look like a csv file')
        passed = False
    if passed:
        print('OK: csv file exists')
    return passed


def check_csv_content(ligandCsv, passed):
    print('-> checking contents of csv file: {0!s}'.format(ligandCsv))
    passed = True
    dialect = csv.Sniffer().sniff(open(ligandCsv).readline(), [',', ';'])
    csvFile = csv.reader(open(ligandCsv), dialect)
    line_number = -1
    for line_number, row in enumerate(csvFile):
        warning = False
        if len(row) < 3:
            print('ERROR: missing value in row: {0!s}'.format(row))
            passed = False
        else:
            sampleID = row[0]
            ligandID = row[1]
            smiles = row[2]
            if ' ' in sampleID:
                print('WARNING: there is a space character in sampleID field -> {0!s}'.format(sampleID))
                warning = True
            if ' ' in ligandID:
                print('WARNING: there is a space character in ligandID field -> {0!s}'.format(ligandID))
                warning = True
            if ' ' in smiles:
                print('WARNING: there is a space character in smiles field -> {0!s}'.format(smiles))
                warning = True
            if warning:
                print('WARNING: all space characters will be removed!')
    print('INFO: found {0!s} lines in {1!s}'.format(line_number+1, ligandCsv))
    return passed


def check_if_project_directory_exists(projectDir, passed):
    print('-> checking project directory: {0!s}'.format(projectDir))
    passed = True
    if os.path.isdir(projectDir):
        print('OK: project directory exists')
    else:
        print('ERROR: project directory does not exisit')
        passed = False
    return passed


def check_restraints_program_option(restraints_program, passed):
    print('-> checking restraints program option: {0!s}'.format(restraints_program))
    supported_options = ['acedrg', 'grade', 'elbow']
    if restraints_program in supported_options:
        print('OK: option exists')
    else:
        print('ERROR: option does not exist')
        passed = False
    return passed


def run_checks(projectDir, ligandCsv, restraints_program):
    print('>>> checking input file and command line options')
    passed = check_csv(ligandCsv)
    if passed:
        check_csv_content(ligandCsv, passed)
    passed = check_if_project_directory_exists(projectDir, passed)
    passed = check_restraints_program_option(restraints_program, passed)
    return passed


def main(argv):
    projectDir = None
    subdirectory = ''
    ligandCsv = None
    restraints_program = None
    maxiv = False
    overwrite = False

    try:
        opts, args = getopt.getopt(argv,"p:l:r:s:ho",["project-directory=", "ligand-csv=", "subdirectory=",
                                                         "restraints-program=", "overwrite", "maxiv"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-p", "--project-directory"):
            projectDir = arg
        elif opt in ("-s", "--subdirectory"):
            subdirectory = arg
        elif opt in ("-l", "--ligand-csv"):
            ligandCsv = arg
        elif opt in ("-r", "--restraints-program"):
            restraints_program = arg
        elif opt in ("-m", "--maxiv"):
            overwrite = True
        elif opt in ("-p", "--overwrite"):
            overwrite = True

    checks_passed = run_checks(projectDir, ligandCsv, restraints_program)

    if checks_passed:
        make_ligand_restraints(projectDir, ligandCsv, restraints_program, overwrite, subdirectory, maxiv)
    else:
        print('something is wrong, please check comments above and use -h option for more information')

if __name__ == '__main__':
    main(sys.argv[1:])
