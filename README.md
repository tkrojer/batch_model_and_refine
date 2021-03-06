# batch_model_and_refine

batch_model_and_refine.py is a python plugin for [COOT](https://www2.mrc-lmb.cam.ac.uk/personal/pemsley/coot/) which enables modelling and refinement of multiple datasets within a single session. A typical use case would be modelling and refinement of multiple protein-ligand complexes of the same protein that are generated during a structure-based drug design project or a fragment screening campaign. 

The script is very simple and does not rely on sophisticated database solutions, but rather on a structured file system where filenames adhere to conventions. The basic idea is that all datasets that belong to a project are stored in a single project directory with each dataset having a subfolder that contains all the associated data. The subfolder name corresponds to the dataset name. Furthermore, the files within each subfolder need to stick to a naming convention so that the plugin picks up the correct file. Here is a simple example:

```
project directory: /Users/tobkro/simple

subdirectory tree:
.
├── proteinX-ligandY
│   ├── refine.mtz
│   └── refine.pdb
├── super_compound
│   ├── refine.mtz
│   └── refine.pdb
└── xtal_1
    ├── refine.mtz
    └── refine.pdb
```

Currently, the script recognizes the following file types:

* Refinement PDB
* Refinement MTZ
* MTZ free (implementation pending)
* Ligand restraints (implementation pending)

## Installation
The plugin comes as a single python script and does not require installation of any additional packages. It works on any operating system (Windows, Mac and Linux) and was tested with COOT v0.9.6. All you need to do is download the python file and store it somewhere on your local computer or network drive.

## Usage
### Step 1: start plugin
It can either be started from the command line by typing
```
coot --script batch_model_and_refine.py
```
or from the COOT gui, by selecting
```
Calculate -> Run Script...
```
Use the file selection dialog to locate the script, then press Open and the following window should appear alongside the main COOT window:

![](https://github.com/tkrojer/batch_model_and_refine/blob/main/images/main_window.png)

### Step 2: select project directory
Press "*select project directory*" and a folder selection dialog will appear that allows you to navigate to where the dataset subfolders are located.

### Step 3: set folder structure and file name conventions
Folder and filenames can be anything, but it is strongly recommended to avoid spaces or special characters. This hasn’t been tested extensively, but chances are high that it will not work as expected if such characters are present. Press "*change settings*" and a new window will appear that allows you to view/ change the default settings:

![](https://github.com/tkrojer/batch_model_and_refine/blob/main/images/data_paths_simple.png)

The defaults will work with the simple file structure shown above. If your filenames differ and you decided to call your PDB files e.g. "*final.pdb*" then just alter the respective field and once done, press "*OK*" for the changes to become active. The situation is different if your files are stored with in a subfolder of the sample folder. A reason for this could be that you ran an auto-processing pipeline like [DIMPLE](https://www.ccp4.ac.uk/html/dimple.html) or [PIPEDREAM](https://www.globalphasing.com/buster/manual/pipedream/manual/index.html#_pipedream) which store their results in a separate folder. In this case, you need to change the "*subfolder search field*". Let's imagine our folder structure looks like this:

```
.
├── proteinX-ligandY
│   └── dimple
│       ├── final.mtz
│       └── final.pdb
├── super_compound
│   └── dimple
│       ├── final.mtz
│       └── final.pdb
└── xtal_1
    └── dimple
        ├── final.mtz
        └── final.pdb
```
Now we need to change the "*subfolder search field*" to "\*/dimple" (please note that on windows you would need to use a backslash instead, i.e. "\*\dimple"). Additionally, "*PDB file name*" and "*MTZ auto file name*" need to be changed to "final.pdb" and "final.mtz", respectively. The asteriks (\*) is really important here, because it matches every subdirectory (i.e. dataset directory) in the project directory!

![](https://github.com/tkrojer/batch_model_and_refine/blob/main/images/data_paths_complex.png)

### Step 4: read files
After you you pressed "*OK*" in the "*change settings*" dialogue, you will return to the main plugin window. Now, press "*read datasets*" and the program will parse all folders in the project directory for matching files. In our 3 dataset example, the "*current*" field should show "-1" (since we have not started browsing) and the "*total*" field should show "3".

![](https://github.com/tkrojer/batch_model_and_refine/blob/main/images/main_window_read.png)

### Step 5: browse datasets
Now you can start browsing through your datasets. Use the arrow buttons ("<<<" & ">>>") to move forward and backward within the project directory.

![](https://github.com/tkrojer/batch_model_and_refine/blob/main/images/main_window_browse.png)

### Step 6: save/ load projects
This is an optional step, but you might want to save your settings, so that next time there is no need to navigate to the project directory and to edit any of the search fields. Also, in case you have multiple projects, but you want to keep all the project definitions in a single location in your file system. Press "*save project*" and the plugin will save settings information (and information about each dataset - but this feature is not used, yet) in a json file. You don't have to provide an extenstion, the plugin will automatically call it .json (it will also ignore any other extension). Next time, press "*load project*" to read it the saved settings. 

## Outlook

The plugin is still under development, but in the (hopefully not too distanct future), it will also help with ligand building and refinement. It is also planned to have a selection mechanism for subsets of the data. And if you have any more ideas, please don't hesitate to get in touch!
