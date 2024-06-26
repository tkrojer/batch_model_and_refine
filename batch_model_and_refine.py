# plugin for COOT for batch data processing
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

import os
import glob
import sys

import gtk
import coot
import __main__

import time

import json


def defaults():
    defaults = {
        'glob_string':          '*',
        'pdb':                  'refine.pdb',
        'mtz':                  'refine.pdb',
        'mtz_free':             'free.mtz',
        'ligand_cif':           'ligand_files/*.cif',
        'windows_refmac_path': 'C:\\'
    }
    return defaults


def project_data():
    project_information = {
        'settings': {
            'project_directory':    '',
            'glob_string':          '*',
            'pdb':                  'refine.pdb',
            'mtz':                  'refine.mtz',
            'mtz_free':             'free.mtz',
            'ligand_cif':           'ligand_files/*.cif'
            },
        'datasets': []
    }
    return project_information


def dataset_information():
    # append datasets list
    dataset = {
        'sample_ID':    '',
        'pdb':          '',
        'mtz':          '',
        'status':       '',
        'mtz_free':     '',
        'ligand_cif':   '',
        'refinement_program':   '',
        'refinement_params':    '',
        'tag':          ''
    }
    return dataset


def status_categories():
    status_categories = [
        '-1 - Analysed & Rejected'
        '0 - All Datasets',
        '1 - Analysis Pending',
        '2 - In Refinement',
        '3 - Deposition ready'
    ]
    return status_categories


def refmac_refinement_params():
    refmac_refinement_params = {
        'TLSADD':           '',
        'NCYCLES':          '',
        'MATRIX_WEIGHT':    '',
        'BREF':             '',
        'TLS':              '',
        'NCS':              '',
        'TWIN':             ''
    }
    return refmac_refinement_params


def buster_refinement_params():
    buster_refinement_params = {
        'anisotropic_Bfactor':      '',
        'update_water':             '',
        'refine_ligand_occupancy':  '',
        'ignore_sanity_check':      ''
    }
    return buster_refinement_params

class data_paths(object):
    """ settings window
    """


    def __init__(self, settingsDict):
        self.settingsDict = settingsDict
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.settings = defaults()

    def start_gui(self):
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_title("Data Paths")
        self.window.set_default_size(600, 300)
        self.vbox = gtk.VBox()

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        hbox.add(gtk.Label('subfolder search'))
        self.glob_string = gtk.Entry()
        self.glob_string.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.glob_string.connect("key-release-event", self.on_key_release_glob_string)
        self.glob_string.set_text(self.settingsDict['glob_string'])
        hbox.add(self.glob_string)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        hbox.add(gtk.Label('PDB file name'))
        self.input_pdb_entry = gtk.Entry()
        self.input_pdb_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.input_pdb_entry.connect("key-release-event", self.on_key_release_input_pdb)
        self.input_pdb_entry.set_text(self.settingsDict['pdb'])
        hbox.add(self.input_pdb_entry)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        hbox.add(gtk.Label('MTZ free file name'))
        self.input_mtz_free_entry = gtk.Entry()
        self.input_mtz_free_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.input_mtz_free_entry.connect("key-release-event", self.on_key_release_input_mtz_free)
        self.input_mtz_free_entry.set_text(self.settingsDict['mtz_free'])
        hbox.add(self.input_mtz_free_entry)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        hbox.add(gtk.Label('MTZ auto file name'))
        self.input_mtz_auto_entry = gtk.Entry()
        self.input_mtz_auto_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.input_mtz_auto_entry.connect("key-release-event", self.on_key_release_input_mtz_auto)
        self.input_mtz_auto_entry.set_text(self.settingsDict['mtz'])
        hbox.add(self.input_mtz_auto_entry)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        hbox.add(gtk.Label('CIF file name'))
        self.input_cif_entry = gtk.Entry()
        self.input_cif_entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        self.input_cif_entry.connect("key-release-event", self.on_key_release_input_cif)
        self.input_cif_entry.set_text(self.settingsDict['ligand_cif'])
        hbox.add(self.input_cif_entry)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        revert_to_defaults_button = gtk.Button(label="Revert to defaults")
        revert_to_defaults_button.connect("clicked", self.revert_to_defaults)
        self.vbox.add(revert_to_defaults_button)

        ok_button = gtk.Button(label="OK")
        ok_button.connect("clicked", self.ok)
        self.vbox.add(ok_button)

        self.window.add(self.vbox)
        self.window.show_all()
        return self.settingsDict

    def on_key_release_glob_string(self, widget, event):
        self.settingsDict['glob_string'] = widget.get_text()

    def on_key_release_input_pdb(self, widget, event):
        self.settingsDict['pdb'] = widget.get_text()

    def on_key_release_input_mtz_free(self, widget, event):
        self.settingsDict['mtz_free'] = widget.get_text()

    def on_key_release_input_mtz_auto(self, widget, event):
        self.settingsDict['mtz'] = widget.get_text()

    def on_key_release_input_cif(self, widget, event):
        self.settingsDict['ligand_cif'] = widget.get_text()

    def load_template(self):
        print('hallo')

    def save_template(self):
        print('hallo')

    def revert_to_defaults(self, widgets):
        self.input_pdb_entry.set_text(defaults()['pdb'])
        self.input_mtz_auto_entry.set_text(defaults()['mtz'])
        self.input_mtz_free_entry.set_text(defaults()['mtz_free'])
        self.input_cif_entry.set_text(defaults()['ligand_cif'])

    def ok(self, widget):
        self.window.destroy()


class pdbtools(object):
    """ reads refinement statistics from PDB header
        Note: class should be replaced by GEMMI once it is available in WinCOOT
    """

    def __init__(self, pdb, l):
        self.pdb = pdb
        self.l = l
        print('here')
        if os.path.isfile(self.pdb):
            print('all good')
        else:
            print('bummer')

    def spacegroup(self):
        spacegroup = ''
        for line in open(self.pdb):
            if line.startswith('CRYST1'):
                spacegroup = line[55:65]
                break
        return spacegroup

    def r_free(self):
        r_free = ''
        for line in open(self.pdb):
            if line.startswith('REMARK   3   FREE R VALUE                     :'):
                r_free = line.split()[6]
                break
        return r_free

    def r_work(self):
        r_work = ''
        for line in open(self.pdb):
            if line.startswith('REMARK   3   R VALUE     (WORKING + TEST SET) :'):
                r_work = line.split()[9]
                break
        return r_work

    def resolution_high(self):
        resolution_high = ''
#        for line in open(self.pdb):
        print('--> self.pdb', self.pdb)
        if os.path.isfile(self.pdb):
            print('still all good')
        else:
            print('nooooooooooo')
        print('list', self.l)
#        for line in open(self.pdb):
        for line in open(os.sep.join(self.l)):
            if line.startswith('REMARK   3   RESOLUTION RANGE HIGH (ANGSTROMS) :'):
                resolution_high = line.split()[7]
                break
        return resolution_high

    def rmsd_bonds(self):
        rmsd_bonds = ''
        for line in open(self.pdb):
            if line.startswith('REMARK   3   BOND LENGTHS REFINED ATOMS        (A):'):
                rmsd_bonds = line.split()[9]
                break
        return rmsd_bonds

    def rmsd_angles(self):
        rmsd_angles = ''
        for line in open(self.pdb):
            if line.startswith('REMARK   3   BOND ANGLES REFINED ATOMS   (DEGREES):'):
                rmsd_angles = line.split()[9]
                break
        return rmsd_angles


class command_line_scripts(object):

    def __init__(self):
        print("hallo")

#    def create_refinement_in_progress_file(self, projectDir, xtal):
#        os.chdir(os.path.join(projectDir, xtal))
#        f = open('refinement_in_progress', 'w')
#        f.write('')
#        f.close()


    def prepare_refmac_windows_script(self, nextCycle, mtz_free, ligand_cif, project_data, xtal):
        os.chdir(os.path.join(project_data, xtal, "scripts"))

        params = (
            'ncyc 5\n'
            'end\n'
        )
        f = open('params_{0!s}.inp'.format(nextCycle), 'w')
        f.write(params)
        f.close()

        libin = ''
        if ligand_cif:
            libin = "libin " + ligand_cif

        cmd = (
        "@echo off\n"
        "call C:\CCP4-7\7.1\ccp4.setup\n"
        "refmac5"
        " hklin ..\{0!s} hklout ..\Refine_{1!s}\\refine.mtz ".format(mtz_free, nextCycle) +
        " xyzin ..\saved_models\input_model_for_cycle_{0!s} xyzout ..\Refine_{1!s}\\refine.pdb ".format(nextCycle, nextCycle) +
        libin +
        "< params_{0!s}.inp\n".format(nextCycle) +
        "chdir ..\n"
        "copy Refine_{0!s}\rrefine.pdb .\n".format(nextCycle) +
        "copy Refine_{0!s}\rrefine.mtz .\n".format(nextCycle) +
        "del refinement_in_progress"
        )

        print('writing refmac_{0!s}.sh in {1!s}'.format(nextCycle, os.path.join(project_data, xtal, "scripts")))
        f = open('refmac_{0!s}.bat'.format(nextCycle), 'w')
        f.write(cmd)
        f.close()


    def prepare_refmac_unix_script(self, nextCycle, mtz_free, ligand_cif, project_data, xtal):
        os.chdir(os.path.join(project_data, xtal, "scripts"))

        libin = ''
        if ligand_cif:
            libin = "libin " + ligand_cif
        else:
            libin = ''

        cmd = (
            '#!'+os.getenv('SHELL')+'\n'
            'refmac5 '
            ' hklin ../{0!s}'.format(mtz_free) +
            ' hklout ../Refine_{0!s}/refine.mtz'.format(nextCycle) +
            ' xyzin ../saved_models/input_model_for_cycle_{0!s}.pdb '.format(nextCycle) +
            ' xyzout ../Refine_{0!s}/refine.pdb '.format(nextCycle) +
            libin +
            ' << EOF > refmac.log\n'
            'make -\n'
            '    hydrogen ALL -\n'
            '    hout NO -\n'
            '    peptide NO -\n'
            '    cispeptide YES -\n'
            '    ssbridge YES -\n'
            '    symmetry YES -\n'
            '    sugar YES -\n'
            '    connectivity NO -\n'
            '    link NO\n'
            'refi -\n'
            '    type REST -\n'
            '    resi MLKF -\n'
            '    meth CGMAT -\n'
            'scal -\n'
            '    type SIMP -\n'
            '    LSSC -\n'
            '    ANISO -\n'
            '    EXPE\n'
            'solvent YES\n'
            'monitor MEDIUM -\n'
            '    torsion 10.0 -\n'
            '    distance 10.0 -\n'
            '    angle 10.0 -\n'
            '    plane 10.0 -\n'
            '    chiral 10.0 -\n'
            '    bfactor 10.0 -\n'
            '    bsphere 10.0 -\n'
            '    rbond 10.0 -\n'
            '    ncsr 10.0\n'
            'labin  FP=F SIGFP=SIGF FREE=FreeR_flag\n'
            'labout  FC=FC FWT=FWT PHIC=PHIC PHWT=PHWT DELFWT=DELFWT PHDELWT=PHDELWT FOM=FOM\n'
            'DNAME '+self.xtalID+'\n'
            'END\n'
            'EOF\n\n'
            'cd {0!s}/{1!s} \n\n'.format(project_data, xtal) +
            'ln -s ./Refine_{0!s}/refine.pdb .\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine.mtz .\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine.mmcif .\n'.format(nextCycle)
        )

        print('writing refmac_{0!s}.sh in {1!s}'.format(nextCycle, os.path.join(project_data, xtal, "scripts")))
        f = open('refmac_{0!s}.sh'.format(nextCycle), 'w')
        f.write(cmd)
        f.close()


    def prepare_buster_maxiv_script(self, nextCycle, ligand_cif, projectDir, xtal):
#        cif_name = ligand_cif.split('/')[len(ligand_cif.split('/'))-1]
        cif_name = "." + ligand_cif.replace(os.path.join(projectDir, xtal), '')
        os.chdir(os.path.join(projectDir, xtal, "scripts"))
        cmd = (
            '#!/bin/bash\n'
            '#SBATCH --time=10:00:00\n'
            '#SBATCH --job-name=buster\n'
            '#SBATCH --cpus-per-task=1\n'
            'module load gopresto BUSTER\n'
            'cd {0!s}\n'.format(os.path.join(projectDir, xtal).replace('/Volumes/offline-staff', '/data/staff')) +
            'touch refinement_in_progress\n'
            'refine' 
            ' -p saved_models/input_model_for_cycle_{0!s}.pdb'.format(nextCycle) +
            ' -m free.mtz'
            ' -d Refine_{0!s}'.format(nextCycle) +
            ' -l {0!s}\n'.format(cif_name) +
            'ln -s ./Refine_{0!s}/refine.pdb .\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine.mtz .\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/BUSTER_model.cif refine.cif\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/BUSTER_refln.cif refine_sf.cif\n'.format(nextCycle) +
            '/data/staff/biomax/tobias/software/MAXIV_tools/pdb_validate_cif.sh -m refine.cif -s refine_sf.cif -o refine_{0!s}\n'.format(nextCycle) +
            '/data/staff/biomax/tobias/software/MAXIV_tools/table_one.sh -m refine.cif -c process.cif -x xray-report-refine_{0!s}.xml\n'.format(nextCycle) +
            '/bin/rm refinement_in_progress\n'

        )
        print('writing buster_{0!s}.sh in {1!s}'.format(nextCycle, os.path.join(projectDir, xtal, "scripts")))
        f = open('buster_{0!s}.sh'.format(nextCycle), 'w')
        f.write(cmd)
        f.close()

        print('submitting job...')
        print('ssh offline-fe1 "cd {0!s}; sbatch buster_{1!s}.sh"'.format(os.path.join(projectDir, xtal, "scripts").replace('/Volumes/offline-staff', '/data/staff'), nextCycle))
        os.system('ssh offline-fe1 "cd {0!s}; sbatch buster_{1!s}.sh"'.format(os.path.join(projectDir, xtal, "scripts").replace('/Volumes/offline-staff', '/data/staff'), nextCycle))


#    def prepare_giant_quick_refine_script(self):
#        cmd = "giant.quick_refine input.pdb=MID2-x0054-ensemble-model.pdb mtz=free.mtz cif=VT00188.cif params=multi-state-restraints.refmac.params"

    def prepare_phenix_maxiv_script(self, nextCycle, ligand_cif, projectDir, xtal):
        cif_name = "." + ligand_cif.replace(os.path.join(projectDir, xtal), '')
        if not os.path.isdir(os.path.join(projectDir, xtal, "Refine_{0!s}".format(nextCycle))):
            os.mkdir(os.path.join(projectDir, xtal, "Refine_{0!s}".format(nextCycle)))
        os.chdir(os.path.join(projectDir, xtal, "scripts"))
        cmd = (
            '#!/bin/bash\n'
            '#SBATCH --time=10:00:00\n'
            '#SBATCH --job-name=phenix.refine\n'
            'source /data/staff/biomax/tobias/software/phenix-1.20.1-4487/phenix_env.sh\n'
            'cd {0!s}\n'.format(os.path.join(projectDir, xtal).replace('/Volumes/offline-staff', '/data/staff')) +
            'touch refinement_in_progress\n'
            'cd Refine_{0!s}\n'.format(nextCycle) +
            'phenix.refine ../saved_models/input_model_for_cycle_{0!s}.pdb'.format(nextCycle) +
            ' ../free.mtz'
            ' ../{0!s}'.format(cif_name) +
            ' output.prefix="refine"'
            ' refinement.input.xray_data.labels="F,SIGF"'
            ' refinement.input.xray_data.r_free_flags.label="FreeR_flag"'
            ' refinement.input.xray_data.r_free_flags.test_flag_value=0\n'
            'phenix.mtz_as_cif refine_001.mtz\n'
            'cd {0!s}\n'.format(os.path.join(projectDir, xtal).replace('/Volumes/offline-staff', '/data/staff')) +
            'ln -s ./Refine_{0!s}/refine_001.pdb refine.pdb\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine_001.mtz refine.mtz\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine_001.cif refine.cif\n'.format(nextCycle) +
            'ln -s ./Refine_{0!s}/refine_001.reflections.cif refine_sf.cif\n'.format(nextCycle) +
            '/data/staff/biomax/tobias/software/MAXIV_tools/pdb_validate_cif.sh -m refine.cif -s refine_sf.cif -o refine_{0!s}\n'.format(nextCycle) +
            '/data/staff/biomax/tobias/software/MAXIV_tools/table_one.sh -m refine.cif -c process.cif -x xray-report-refine_{0!s}.xml\n'.format(nextCycle) +
            '/bin/rm refinement_in_progress\n'

        )
        print('writing phenix_{0!s}.sh in {1!s}'.format(nextCycle, os.path.join(projectDir, xtal, "scripts")))
        f = open('phenix_{0!s}.sh'.format(nextCycle), 'w')
        f.write(cmd)
        f.close()

        print('submitting job...')
        print('ssh offline-fe1 "cd {0!s}; sbatch phenix_{1!s}.sh"'.format(os.path.join(projectDir, xtal, "scripts").replace('/Volumes/offline-staff', '/data/staff'), nextCycle))
        os.system('ssh offline-fe1 "cd {0!s}; sbatch phenix_{1!s}.sh"'.format(os.path.join(projectDir, xtal, "scripts").replace('/Volumes/offline-staff', '/data/staff'), nextCycle))


    def run_refmac_unix_script(self, nextCycle, project_data, xtal):
        os.chdir(os.path.join(project_data, xtal, "scripts"))
        os.system('chmod +x refmac_{0!s}.sh'.format(nextCycle))
        os.system('./refmac_{0!s}.sh &'.format(nextCycle))


class main_window(object):
    """ main window of the plugin
    """

    def __init__(self):

        self.index = -1
#        self.Todo = []
        self.mol_dict = {
            'pdb': None,
            'mtz': None,
            'cif': None
            }

        self.project_data = project_data()
        self.projectDir = self.project_data['settings']['project_directory']

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.vbox = gtk.VBox()  # this is the main container

        self.index_label = gtk.Label('')
        self.index_total_label = gtk.Label('')
        self.pdb_label = gtk.Label('')
        self.mtz_label = gtk.Label('')
        self.mtz_free_label = gtk.Label('')
        self.ligand_cif_label = gtk.Label('')

        self.xtal_label = gtk.Label('')
        self.resolution_label = gtk.Label('')
        self.r_work_label = gtk.Label('')
        self.r_free_label = gtk.Label('')
        self.space_group_label = gtk.Label('')


    def start_gui(self):
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_default_size(400, 600)
        self.window.set_title("Batch model & refine")

        frame = gtk.Frame(label='Settings')
        hbox = gtk.HBox()

        load_project_button = gtk.Button(label="load project")
        load_project_button.connect("clicked", self.load_project)
        hbox.add(load_project_button)
        save_project_button = gtk.Button(label="save project")
        save_project_button.connect("clicked", self.save_project)
        hbox.add(save_project_button)
        change_settings_button = gtk.Button(label="change settings")
        change_settings_button.connect("clicked", self.change_settings)
        hbox.add(change_settings_button)
        frame.add(hbox)
        self.vbox.pack_start(frame)

#        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='Datasets')
        vbox = gtk.VBox()
        select_project_directory_button = gtk.Button(label="select project directory")
        select_project_directory_button.connect("clicked", self.select_project_directory)
        vbox.add(select_project_directory_button)
        read_datasets_button = gtk.Button(label="read datasets")
        read_datasets_button.connect("clicked", self.read_datasets)
        vbox.add(read_datasets_button)
        frame.add(vbox)
        self.vbox.pack_start(frame)

        outer_frame = gtk.Frame()
        hbox = gtk.HBox()
        table = gtk.Table(5, 4, False)

        frame = gtk.Frame()
        frame.add(gtk.Label('Current'))
        table.attach(frame, 0, 1, 0, 1)
        frame = gtk.Frame()
        frame.add(self.index_label)
        table.attach(frame, 1, 2, 0, 1)

        frame = gtk.Frame()
        frame.add(gtk.Label('Total'))
        table.attach(frame, 2, 3, 0, 1)
        frame = gtk.Frame()
        frame.add(self.index_total_label)
        table.attach(frame, 3, 4, 0, 1)

#        frame = gtk.Frame()
#        frame.add(gtk.Label('PDB'))
#        table.attach(frame, 0, 1, 1, 2)
#        frame = gtk.Frame()
#        frame.add(self.index_label)
#        table.attach(frame, 1, 2, 1, 2)

#        frame = gtk.Frame()
#        frame.add(gtk.Label('MTZ'))
#        table.attach(frame, 2, 3, 1, 2)
#        frame = gtk.Frame()
#        frame.add(self.index_total_label)
#        table.attach(frame, 3, 4, 1, 2)

#        frame = gtk.Frame()
#        frame.add(gtk.Label('MTZ free'))
#        table.attach(frame, 0, 1, 2, 3)
#        frame = gtk.Frame()
#        frame.add(self.index_label)
#        table.attach(frame, 1, 2, 2, 3)

#        frame = gtk.Frame()
#        frame.add(gtk.Label('CIF'))
#        table.attach(frame, 2, 3, 2, 3)
#        frame = gtk.Frame()
#        frame.add(self.index_total_label)
#        table.attach(frame, 3, 4, 2, 3)

        outer_frame.add(table)
        hbox.add(outer_frame)
        self.vbox.add(hbox)

#        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='Navigator')
        vbox = gtk.VBox()
        PREVbutton = gtk.Button(label="<<<")
        NEXTbutton = gtk.Button(label=">>>")
        PREVbutton.connect("clicked", self.backward)
        NEXTbutton.connect("clicked", self.forward)
        hbox = gtk.HBox()
        hbox.pack_start(PREVbutton)
        hbox.pack_start(NEXTbutton)
        vbox.add(hbox)
        self.crystal_progressbar = gtk.ProgressBar()
        vbox.add(self.crystal_progressbar)
        frame.add(vbox)
        self.vbox.add(frame)

        outer_frame = gtk.Frame()
        hbox = gtk.HBox()

        table = gtk.Table(4, 2, False)

        frame = gtk.Frame()
        frame.add(gtk.Label('Crystal'))
        table.attach(frame, 0, 1, 0, 1)
        frame = gtk.Frame()
        frame.add(self.xtal_label)
        table.attach(frame, 1, 2, 0, 1)

        frame = gtk.Frame()
        frame.add(gtk.Label('ligand CIF'))
        table.attach(frame, 0, 1, 1, 2)
        frame = gtk.Frame()
        frame.add(self.ligand_cif_label)
        table.attach(frame, 1, 2, 1, 2)

        frame = gtk.Frame()
        frame.add(gtk.Label('Space group'))
        table.attach(frame, 0, 1, 2, 3)
        frame = gtk.Frame()
        frame.add(self.space_group_label)
        table.attach(frame, 1, 2, 2, 3)

        frame = gtk.Frame()
        frame.add(gtk.Label('Resolution'))
        table.attach(frame, 0, 1, 3, 4)
        frame = gtk.Frame()
        frame.add(self.resolution_label)
        table.attach(frame, 1, 2, 3, 4)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rwork'))
        table.attach(frame, 0, 1, 4, 5)
        frame = gtk.Frame()
        frame.add(self.r_work_label)
        table.attach(frame, 1, 2, 4, 5)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rfree'))
        table.attach(frame, 0, 1, 5, 6)
        frame = gtk.Frame()
        frame.add(self.r_free_label)
        table.attach(frame, 1, 2, 5, 6)

        outer_frame.add(table)
        hbox.add(outer_frame)
        self.vbox.add(hbox)

#        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='Tags')
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        self.cb_tag = gtk.combo_box_new_text()
#        self.cb_tag.connect("changed", self.select_tag)
        hbox.add(self.cb_tag)
        set_tag_button = gtk.Button(label="set tag")
#        set_tag_button.connect("clicked", self.set_tag)
        hbox.add(set_tag_button)
        vbox.add(hbox)
        select_by_tag_button = gtk.Button(label="select samples by tag")
#        select_by_tag_button.connect("clicked", self.select_by_tag)
        vbox.add(select_by_tag_button)
        frame.add(vbox)
        self.vbox.add(frame)

#        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='Ligand Modeling')
        hbox = gtk.HBox()
        merge_ligand_button = gtk.Button(label="Merge Ligand")
        place_ligand_here_button = gtk.Button(label="Place Ligand here")
#        merge_ligand_button.set_sensitive(False)
        hbox.add(place_ligand_here_button)
        place_ligand_here_button.connect("clicked", self.place_ligand_here)
#        place_ligand_here_button.set_sensitive(False)
        hbox.add(merge_ligand_button)
        merge_ligand_button.connect("clicked", self.merge_ligand_into_protein)
        frame.add(hbox)
        self.vbox.pack_start(frame)

#        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='')
        hbox = gtk.HBox()
        self.show_outliers_button = gtk.Button(label="Show Outliers")
        hbox.add(self.show_outliers_button)
        self.show_outliers_button.connect("clicked", self.show_outliers)
        #        self.save_current_model_button.set_sensitive(False)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Save')
        hbox = gtk.HBox()
        self.save_current_model_button = gtk.Button(label="Save Model")
        hbox.add(self.save_current_model_button)
        self.save_current_model_button.connect("clicked", self.save_current_model)
#        self.save_current_model_button.set_sensitive(False)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        self.vbox.add(gtk.Label("\n"))

        frame = gtk.Frame(label='Refinement')
        vbox = gtk.VBox()
        refinement_parameters_button = gtk.Button(label="Refinement parameters")
        refinement_parameters_button.connect("clicked", self.refinement_parameters_button)
        refinement_parameters_button.set_sensitive(False)
        vbox.add(refinement_parameters_button)
        refine_button = gtk.Button(label="Refine")
        refine_button.connect("clicked", self.refine)
#        refine_button.set_sensitive(False)
        vbox.add(refine_button)
        frame.add(vbox)
        self.vbox.pack_start(frame)

        self.vbox.add(gtk.Label("\n"))

        cancel_button = gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.cancel)
        self.vbox.add(cancel_button)

        self.window.add(self.vbox)
        self.window.show_all()


    def select_project_directory(self, widget):
        dlg = gtk.FileChooserDialog("Open..", None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dlg.run()
#        response = dlg.run()
        self.projectDir = dlg.get_filename()
        self.project_data['settings']['project_directory'] = self.projectDir
        dlg.destroy()

    def load_project(self, widget):
        dlg = gtk.FileChooserDialog("Load..", None, gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dlg.run()
#        response = dlg.run()
        tmp = dlg.get_filename()
        print(tmp)
        dlg.destroy()

    def save_project(self, widget):
        dlg = gtk.FileChooserDialog("Save..", None, gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dlg.run()
        json_file = dlg.get_filename().split('.')[0] + '.json'
        with open(json_file, 'w') as fp:
            json.dump(self.project_data, fp)
        dlg.destroy()


    def change_settings(self, widget):
        self.project_data['settings'] = data_paths(self.project_data['settings']).start_gui()

    def read_datasets(self, widget):
        globString = self.project_data['settings']['glob_string']
        pdbName = self.project_data['settings']['pdb']
        mtzName = self.project_data['settings']['mtz']
        cifName = self.project_data['settings']['ligand_cif']
        self.crystal_progressbar.set_fraction(0)
        n = 0
        n_folders = len(glob.glob(os.path.join(self.projectDir, globString, pdbName)))
        for pdbFile in sorted(glob.glob(os.path.join(self.projectDir, globString, pdbName))):
            if not os.path.isfile(pdbFile):
                # in case of broken sym links
                continue
#            if os.name == 'nt':
#                sample_ID = pdbFile.split('\\')[len(self.projectDir.split('\\'))]
##                sample_ID = pdbFile.split('\\')[len(pdbFile.split('\\'))]
#            else:
#                sample_ID = pdbFile.split('/')[len(self.projectDir.split('/'))]
##                sample_ID = pdbFile.split('/')[len(pdbFile.split('/'))]
            sample_ID = pdbFile.split(os.sep)[len(self.projectDir.split(os.sep))]
            print('checking folder: {0!s}'.format(sample_ID))
            newSample = True
            for d in self.project_data['datasets']:
                if sample_ID == d['sample_ID']:
                    print('sample exists')
                    datasetDict = d
                    newSample = False
                    break
            if newSample:
                datasetDict = dataset_information()
                datasetDict['sample_ID'] = sample_ID
#            datasetDict['pdb'] = repr(pdbFile)
            datasetDict['pdb'] = pdbFile.split(os.sep)
#            print('pdb', datasetDict['pdb'])
#            print('repr(pdb)', repr(datasetDict['pdb']))
            for mtzFile in sorted(glob.glob(os.path.join(self.projectDir, sample_ID, mtzName))):
                print('INFO: found mtz file: {0!s}'.format(mtzFile))
                datasetDict['mtz'] = mtzFile.split(os.sep)
#            if os.path.isfile(pdbFile.replace(pdbName, mtzName)):
#                print('INFO: found mtz file: {0!s}'.format(pdbFile.replace(pdbName, mtzName)))
#                datasetDict['mtz'] = pdbFile.replace(pdbName, mtzName).split(os.sep)
#            else:
#                print('ERROR: cannot find mtz file: {0!s}'.format(pdbFile.replace(pdbName, mtzName)))
            foundCIF = False
#            print("cifNamr", cifName)
#            print("glob",os.path.join(self.projectDir, sample_ID, cifName))
            for cifFile in glob.glob(os.path.join(self.projectDir, sample_ID, cifName)):
                if os.path.isfile(cifFile.replace('.cif', '.pdb')):
                    datasetDict['ligand_cif'] = cifFile.split(os.sep)
                    print("found ligand cif and corresponding pdb file: {0!s}".format(cifFile))
                    foundCIF = True
                    break
            if not foundCIF:
                print('WARNING: did not find ligand cif file for {0!s}'.format(sample_ID))
            self.project_data['datasets'].append((datasetDict))
#            print('datasetDict', datasetDict)
            n += 1
            self.crystal_progressbar.set_fraction(float(n)/float(n_folders))
        print('INFO: PDB, MTZ, CIF file in project_data:')
        print(self.project_data)
        print('INFO: done...')
        self.crystal_progressbar.set_fraction(0)
        self.index_label.set_label(str(self.index))
        self.index_total_label.set_label(str(len(self.project_data['datasets'])))

    def update_labels(self):
#        pdb = pdbtools(self.pdb)
        pdb = pdbtools(self.pdb, self.project_data['datasets'][self.index]['pdb'])
        self.xtal_label.set_label(self.xtal)
        self.resolution_label.set_label(pdb.resolution_high())
        self.r_free_label.set_label(pdb.r_free())
        self.r_work_label.set_label(pdb.r_work())
        self.space_group_label.set_label(pdb.spacegroup())
        print('ligand_cif', self.ligand_cif)
#        if os.name == 'nt':
#            cif = self.ligand_cif.split('\\')[len(self.ligand_cif.split('\\'))-1].replace('.cif', '')
#        else:
#            cif = self.ligand_cif.split('/')[len(self.ligand_cif.split('/')) - 1].replace('.cif', '')
        cif = self.ligand_cif.split(os.sep)[len(self.ligand_cif.split(os.sep))-1].replace('.cif', '')
        self.ligand_cif_label.set_label(cif)

    def update_params(self):
        self.xtal = self.project_data['datasets'][self.index]['sample_ID']
        print('#####>>>> {0!s}'.format(self.project_data['datasets'][self.index]['pdb']))
        self.pdb = os.sep.join(self.project_data['datasets'][self.index]['pdb'])
        print('join >>>> {0!s}'.format(self.pdb))
        if os.path.isfile(self.pdb):
            print('found it')
        else:
            print('on')
        self.mtz = os.sep.join(self.project_data['datasets'][self.index]['mtz'])
        self.ligand_cif = os.sep.join(self.project_data['datasets'][self.index]['ligand_cif'])

    def RefreshData(self):

        if len(__main__.molecule_number_list()) > 0:
            for item in __main__.molecule_number_list():
                coot.close_molecule(item)

        self.mol_dict = {
            'pdb': None,
            'mtz': None,
            'mtz_free': None,
            'ligand_cif': None
            }

        if self.index < 0:
            self.index = 0
        if self.index > len(self.project_data['datasets']) - 1:
            self.index = len(self.project_data['datasets']) - 1

        self.crystal_progressbar.set_fraction(float(self.index+1)/float(len(self.project_data['datasets'])))

        self.index_label.set_label(str(self.index+1))

        self.update_params()

        self.update_labels()

        coot.set_nomenclature_errors_on_read("ignore")
#        print('self.pdb {0!s}'.format(self.pdb))
#        print('realpath(self.pdb {0!s})'.format(os.path.realpath(self.pdb)))
#        if os.path.islink(self.pdb):
#            print('this is a link')
#        else:
#            print('not sure what it is')
#        x = os.readlink(self.pdb)
#        print('x {0!s}'.format(x))
        imol = coot.handle_read_draw_molecule_with_recentre(self.pdb, 0)
        self.mol_dict['pdb'] = imol
        imol = coot.auto_read_make_and_draw_maps(self.mtz)
        self.mol_dict['mtz'] = imol

        if os.path.isfile(self.ligand_cif.replace('.cif', '.pdb')):
#            print('HHH', self.ligand_cif)
#            print('ggg', self.ligand_cif.replace(os.path.join(self.projectDir, self.xtal), ''))
            coot.read_cif_dictionary(self.ligand_cif)
            imol = coot.handle_read_draw_molecule_with_recentre(self.ligand_cif.replace('.cif', '.pdb'), 0)
            self.mol_dict['ligand_cif'] = imol
            coot.seqnum_from_serial_number(imol, "X", 0)
            coot.set_b_factor_residue_range(imol, "X", 1, 1, 20.00)


        coot.set_colour_map_rotation_on_read_pdb(0)
        coot.set_colour_map_rotation_for_map(0)

    def place_ligand_here(self, widget):
        print('===> moving ligand to pointer')
        print('LIGAND: ', self.mol_dict['ligand_cif'])
        __main__.move_molecule_here(self.mol_dict['ligand_cif'])

    def merge_ligand_into_protein(self, widget):
        print('===> merge ligand into protein structure')
        # merge_molecules(list(imols), imol) e.g. merge_molecules([1],0)
        coot.merge_molecules_py([self.mol_dict['ligand_cif']], self.mol_dict['pdb'])
        print('===> deleting ligand molecule')
        coot.close_molecule(self.mol_dict['ligand_cif'])

    def get_next_model_number(self):
        modelList = [0]
        for m in sorted(glob.glob(os.path.join(self.projectDir, self.xtal, 'saved_models', 'model_*'))):
            n = m[m.rfind('/') + 1:].split('_')[1].replace('.pdb', '')
            modelList.append(int(n))
        nextModel = str(max(modelList) + 1)
        return nextModel

    def save_current_model(self, widget):
        self.create_saved_models_folder_if_not_exists()
        nextModel = self.get_next_model_number()
        self.save_model_to_saved_models_folder("model_{0!s}.pdb".format(nextModel))

    def backward(self, widget):
        self.index -= 1
        self.RefreshData()

    def forward(self, widget):
        self.index += 1
        self.RefreshData()

    def cancel(self, widget):
        self.window.destroy()

    def create_saved_models_folder_if_not_exists(self):
        if not os.path.isdir(os.path.join(self.projectDir, self.xtal, 'saved_models')):
            print('creating saved_models folder in {0!s}'.format(os.path.join(self.projectDir, self.xtal)))
            os.mkdir(os.path.join(self.projectDir, self.xtal, 'saved_models'))

    def save_model_to_saved_models_folder(self, fileName):
        print("saving model as {0!s}".format(os.path.join(self.projectDir, self.xtal, 'saved_models', fileName)))
        coot.write_pdb_file(self.mol_dict['pdb'], os.path.join(self.projectDir, self.xtal, 'saved_models', fileName))

    def create_scripts_folder_if_not_exists(self):
        if not os.path.isdir(os.path.join(self.projectDir, self.xtal, 'scripts')):
            print('creating scripts folder in {0!s}'.format(os.path.join(self.projectDir, self.xtal)))
            os.mkdir(os.path.join(self.projectDir, self.xtal, 'scripts'))

    def get_next_refinement_cycle(self):
        cycleList = [0]
        for c in sorted(glob.glob(os.path.join(self.projectDir, self.xtal, 'Refine_*'))):
            n = c[c.rfind('/') + 1:].split('_')[1]
            cycleList.append(int(n))
        nextCycle = str(max(cycleList) + 1)
        return nextCycle

    def refinement_parameters_button(self, widget):
        print('hallo')

    def prepare_refinement_batch_script(self, nextCycle):
        print('preparing refinement script...')
        print('chcking if {0!s} exists'.format(os.path.join(self.projectDir, self.xtal, "REFINE_AS_ENSEMBLE")))

        #        if os.name == 'nt':
#            command_line_scripts.prepare_refmac_windows_script(nextCycle, self.mtz_free, self.ligand_cif, self.project_data, self.xtal)
#        else:
#            command_line_scripts.prepare_refmac_unix_script(nextCycle, self.mtz_free, self.ligand_cif, self.project_data, self.xtal)
        if os.path.isfile(os.path.join(self.projectDir, self.xtal, "REFINE_AS_ENSEMBLE")):
            print('running phenix because found {0!s}'.format(os.path.join(self.projectDir, self.xtal, "REFINE_AS_ENSEMBLE")))
            command_line_scripts().prepare_phenix_maxiv_script(nextCycle, self.ligand_cif, self.projectDir, self.xtal)
        else:
            print('no ensemble refinement; running buster...')
            command_line_scripts().prepare_buster_maxiv_script(nextCycle, self.ligand_cif, self.projectDir, self.xtal)

    def remove_files_from_previous_cycle(self):
        os.chdir(os.path.join(self.projectDir, self.xtal))
        if os.path.isfile('refine.pdb'):
            os.remove('refine.pdb')
        if os.path.isfile('refine.mtz'):
            os.remove('refine.mtz')
        if os.path.isfile('refine.cif'):
            os.remove('refine.cif')
        if os.path.isfile('refine_sf.cif'):
            os.remove('refine_sf.cif')

    def run_refinement_batch_script(self, nextCycle):
        print("hallo")
        if os.name == 'nt':
            print('does not work; patience...')
        else:
            command_line_scripts.run_refmac_unix_script(nextCycle, self.project_data, self.xtal)

    def refine(self, widget):
        self.create_saved_models_folder_if_not_exists()
        self.create_scripts_folder_if_not_exists()

#        if not os.path.isfile('refinement_in_progress'):
#            command_line_scripts().create_refinement_in_progress_file(self.projectDir, self.xtal)
#        else:
#            print('ERROR: refinement in progress; please try again later')

#        if os.path.isfile('refinement_in_progress'):
#            print('ERROR: refinement in progress; please try again later')
#            return None

        self.remove_files_from_previous_cycle()
        nextCycle = self.get_next_refinement_cycle()
        pdbin = "input_model_for_cycle_{0!s}.pdb".format(nextCycle)
        self.save_model_to_saved_models_folder(pdbin)

        self.prepare_refinement_batch_script(nextCycle)

#        self.run_refinement_batch_script(nextCycle)

        self.index += 1
        self.RefreshData()


    def show_outliers(self, widget):
        coot.clear_all_views()
        if os.path.isfile(os.path.join(self.projectDir, self.xtal, 'refine.scm')):
            coot.run_script(os.path.join(self.projectDir, self.xtal, 'refine.scm'))
            views_panel_gui()

if __name__ == '__main__':
    main_window().start_gui()

