#    plugin for COOT for batch data processing
#    Copyright (C) 2021  Tobias Krojer, MAX IV Laboratory
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        'glob_string':    '*',
        'pdb':  'refine.pdb',
        'mtz': 'refine.pdb',
        'mtz_free': 'free.mtz',
        'ligand_cif': 'ligand.cif'
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
            'ligand_cif':           'ligand.cif'
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
        'refinement_params':    ''
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

    def __init__(self, settingsDict):
        self.settingsDict = settingsDict
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.settings = defaults()

    def start_gui(self):
        self.window.connect("delete_event", gtk.main_quit)
        self.window.set_border_width(10)
        self.window.set_title("Data Paths")
        self.window.set_default_size(1200, 400)
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

    def __init__(self, pdb):
        self.pdb = pdb

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
        for line in open(self.pdb):
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

        self.xtal_label = gtk.Label('')
        self.resolution_label = gtk.Label('')
        self.r_work_label = gtk.Label('')
        self.r_free_label = gtk.Label('')


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
        table = gtk.Table(7, 4, False)

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

        frame = gtk.Frame()
        frame.add(gtk.Label('PDB'))
        table.attach(frame, 0, 1, 1, 2)
        frame = gtk.Frame()
        frame.add(self.index_label)
        table.attach(frame, 1, 2, 1, 2)

        frame = gtk.Frame()
        frame.add(gtk.Label('MTZ'))
        table.attach(frame, 2, 3, 1, 2)
        frame = gtk.Frame()
        frame.add(self.index_total_label)
        table.attach(frame, 3, 4, 1, 2)

        frame = gtk.Frame()
        frame.add(gtk.Label('MTZ free'))
        table.attach(frame, 0, 1, 2, 3)
        frame = gtk.Frame()
        frame.add(self.index_label)
        table.attach(frame, 1, 2, 2, 3)

        frame = gtk.Frame()
        frame.add(gtk.Label('CIF'))
        table.attach(frame, 2, 3, 2, 3)
        frame = gtk.Frame()
        frame.add(self.index_total_label)
        table.attach(frame, 3, 4, 2, 3)

        outer_frame.add(table)
        hbox.add(outer_frame)
        self.vbox.add(hbox)

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
        frame.add(gtk.Label('Resolution'))
        table.attach(frame, 0, 1, 1, 2)
        frame = gtk.Frame()
        frame.add(self.resolution_label)
        table.attach(frame, 1, 2, 1, 2)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rwork'))
        table.attach(frame, 0, 1, 2, 3)
        frame = gtk.Frame()
        frame.add(self.r_work_label)
        table.attach(frame, 1, 2, 2, 3)

        frame = gtk.Frame()
        frame.add(gtk.Label('Rfree'))
        table.attach(frame, 0, 1, 3, 4)
        frame = gtk.Frame()
        frame.add(self.r_free_label)
        table.attach(frame, 1, 2, 3, 4)

        outer_frame.add(table)
        hbox.add(outer_frame)
        self.vbox.add(hbox)

        frame = gtk.Frame(label='Ligand Modeling')
        hbox = gtk.HBox()
        merge_ligand_button = gtk.Button(label="Merge Ligand")
        place_ligand_here_button = gtk.Button(label="Place Ligand here")
        merge_ligand_button.set_sensitive(False)
        hbox.add(place_ligand_here_button)
        place_ligand_here_button.connect("clicked", self.place_ligand_here)
        place_ligand_here_button.set_sensitive(False)
        hbox.add(merge_ligand_button)
        merge_ligand_button.connect("clicked", self.merge_ligand_into_protein)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Save')
        hbox = gtk.HBox()
        self.save_next_button = gtk.Button(label="Save Model")
        hbox.add(self.save_next_button)
        self.save_next_button.connect("clicked", self.save_next)
        self.save_next_button.set_sensitive(False)
        frame.add(hbox)
        self.vbox.pack_start(frame)

        frame = gtk.Frame(label='Refinement')
        vbox = gtk.VBox()
        refinement_parameters_button = gtk.Button(label="Refinement parameters")
        refinement_parameters_button.connect("clicked", self.refinement_parameters_button)
        refinement_parameters_button.set_sensitive(False)
        vbox.add(refinement_parameters_button)
        refine_button = gtk.Button(label="Refine")
        refine_button.connect("clicked", self.refine)
        refine_button.set_sensitive(False)
        vbox.add(refine_button)
        frame.add(vbox)
        self.vbox.pack_start(frame)

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
        self.crystal_progressbar.set_fraction(0)
        n = 0
        n_folders = len(glob.glob(os.path.join(self.projectDir, globString, pdbName)))
        for pdbFile in sorted(glob.glob(os.path.join(self.projectDir, globString, pdbName))):
            if not os.path.isfile(pdbFile):
                # in case of broken sym links
                continue
            if os.name == 'nt':
                sample_ID = pdbFile.split('\\')[len(self.projectDir.split('\\'))]
            else:
                sample_ID = pdbFile.split('/')[len(self.projectDir.split('/'))]
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
            datasetDict['pdb'] = pdbFile
            if os.path.isfile(pdbFile.replace(pdbName, mtzName)):
                datasetDict['mtz'] = pdbFile.replace(pdbName, mtzName)
            self.project_data['datasets'].append((datasetDict))
            n += 1
            self.crystal_progressbar.set_fraction(float(n)/float(n_folders))
        self.crystal_progressbar.set_fraction(0)
        self.index_label.set_label(str(self.index))
        self.index_total_label.set_label(str(len(self.project_data['datasets'])))

    def update_labels(self):
        pdb = pdbtools(self.pdb)
        self.xtal_label.set_label(self.xtal)
        self.resolution_label.set_label(pdb.resolution_high())
        self.r_free_label.set_label(pdb.r_free())
        self.r_work_label.set_label(pdb.r_work())

    def update_params(self):
        self.xtal = self.project_data['datasets'][self.index]['sample_ID']
        self.pdb = self.project_data['datasets'][self.index]['pdb']
        self.mtz = self.project_data['datasets'][self.index]['mtz']

    def RefreshData(self):

        if len(__main__.molecule_number_list()) > 0:
            for item in __main__.molecule_number_list():
                coot.close_molecule(item)

        self.mol_dict = {
            'pdb': None,
            'mtz': None,
            'cif': None
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
        imol = coot.handle_read_draw_molecule_with_recentre(self.pdb, 0)
        self.mol_dict['pdb'] = imol
        imol = coot.auto_read_make_and_draw_maps(self.mtz)
        self.mol_dict['mtz'] = imol
        coot.set_colour_map_rotation_on_read_pdb(0)
        coot.set_colour_map_rotation_for_map(0)

    def place_ligand_here(self, widget):
        print('===> moving ligand to pointer')
        print('LIGAND: ', self.mol_dict['ligand'])
        __main__.move_molecule_here(self.mol_dict['ligand'])

    def merge_ligand_into_protein(self, widget):
        print('===> merge ligand into protein structure')
        # merge_molecules(list(imols), imol) e.g. merge_molecules([1],0)
        coot.merge_molecules_py([self.mol_dict['ligand']], self.mol_dict['protein'])
        print('===> deleting ligand molecule')
        coot.close_molecule(self.mol_dict['ligand'])

    def save_next(self, widget):
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                       'modelled_structures', 'fitted-v0001.pdb')):
            n = []
            for p in sorted(glob.glob(os.path.join(self.panddaDir, 'processed_datasets', self.xtal,
                                                   'modelled_structures', 'fitted-v*.pdb'))):
                n.append(int(p[p.rfind('fitted-v')+8:].replace('.pdb','')))
                new = 'fitted-v' + (4-len(str(max(n)+1))) * '0' + str(max(n)+1) + '.pdb'
        else:
                new = 'fitted-v0001.pdb'
        coot.write_pdb_file(self.mol_dict['protein'], os.path.join(
                    self.panddaDir,'processed_datasets', self.xtal, 'modelled_structures', new))
        if os.path.isfile(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                                       '{0!s}-pandda-model.pdb'.format(self.xtal))):
            os.remove(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures',
                                   '{0!s}-pandda-model.pdb'.format(self.xtal)))
        os.chdir(os.path.join(self.panddaDir, 'processed_datasets', self.xtal, 'modelled_structures'))
        if os.name == 'nt':
            os.popen('copy {0!s} {1!s}-pandda-model.pdb'.format(new, self.xtal))
        else:
            os.symlink(new, '{0!s}-pandda-model.pdb'.format(self.xtal))

    def backward(self, widget):
        self.index -= 1
        self.RefreshData()

    def forward(self, widget):
        self.index += 1
        self.RefreshData()

    def cancel(self, widget):
        self.window.destroy()

    def refinement_parameters_button(self, widget):
        print('hallo')

    def refine(self, widget):
        print('hallo')

if __name__ == '__main__':
    main_window().start_gui()

#    menu = coot_menubar_menu("batch model & refine")
#
#    add_simple_coot_menu_menuitem(
#        menu, "start gui",
#        lambda func:
#        main_window(False).start_gui())
#
#    add_simple_coot_menu_menuitem(
#        menu, "start gui (PanDDA)",
#        lambda func:
#		main_window(True).start_gui())