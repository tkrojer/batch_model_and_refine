# batch_model_and_refine

batch_model_and_refine.py is a python plugin for COOT which enables modelling and refinement of multiple datasets within a single session. A typical use case would be modelling and refinement of multiple protein-ligand complexes of the same protein that are generated during a structure-based drug design project or a fragment screening campaign. 

The script is very simple and does not rely on sophisticated database solutions, but rather on a structured file system where filenames adhere to conventions. The basic idea is that all datasets that belong to a project are stored in a single project directory with each dataset having a subfolder that contains all the associated data. The subfolder name corresponds to the dataset name. For example:

'''
project directory: /Users/tobkro/simple

subdirectory tree
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
'''
