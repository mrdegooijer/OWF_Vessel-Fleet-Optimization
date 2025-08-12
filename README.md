# OWF_Vessel-Fleet-Optimization
Research assignment for ME54015.

This GitHub repository contains the accompanying code for the model set up in the report "ME54015 Supply Lines at Sea" by Mischa de Gooijer. The code is used to run a model which aims to find the optimal vessel fleet composition for offshore wind farm maintenance. 

The full model with all the extensions is featured in the branch 'deGooijer25-Multi-Echelon', which is the main branch. Two other versions of the code are present in 'deGooijer25-Single-Echelon' and 'deGooijer25-Initial-Model'. The validation and verification steps described in the report are all performed on the  main branch, with the exception of the functional equivalence test, which was performed on the 'deGooijer25-Initial-Model' branch. The initial model was the starting point for the other two branches. 

Each branch contains a number of files and directories. The most important file is run.py; the file that is used to initialise the model and run it. All data files (such as weather data and inputs) are found in the data directory. All sets, variables and parameters are controlled from the input file: Inputs.xlsx. It contains multiple sheets, each tied to specific attributes of the model. When using the model, make sure to check that every sheet is correctly filled out. If, when running the model, an error with the Excel sheet occurs, try to manually enter all data (some of the sets are automatically filled out after initial entry). This might solve the issue.

The model is set up using the python files in the directory 'model'. Each step has its own file: sets.py, parameters.py, variables.py, objective.py, and constraints.py. Furthermore, the solution method, GRASP, is set up in this directory as well: GRASP.py. 

All helper functions are found in the 'utils' directory, as well as plotting and result printing code. 

Finally, the old model, presented by Versluijs, 2023, is given in the 'Ivana' directory.

If you have any questions about the code, feel free to send an email to 'misch.deg@gmail.com'.
