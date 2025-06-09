"""
@author: Mischa de Gooijer
@date: 2025
"""

from utils.utils import load_input_data
from model.sets import create_sets
from model.parameters import create_parameters
from model.variables import create_variables
from model.constraints import add_constraints
from model.objective import add_objective_function
from model.GRASP import GRASP
from utils.results import results
from gurobipy import *
import time
import os


def main():
    # Create directory plots if it does not exist
    os.makedirs('plots', exist_ok=True)

    # Initiate time tracking
    start_time = time.time()

    # Load input data
    file_path = r'data/Inputs.xlsx'
    input_data = load_input_data(file_path)
    # Define the year of the weather data
    year = 2004

    # Initialize the model
    model = Model("de Gooijer, 2025")

    # Create sets, parameters, and variables
    sets = create_sets(input_data)
    params = create_parameters(input_data, sets, year)
    vars = create_variables(model, sets, params)
    model.update()

    # Add constraints
    add_constraints(model, sets, params, vars)

    # Add objective function
    add_objective_function(model, sets, params, vars)
    # model.write("model.lp")

    # Optimize the model
    model.optimize()
    # GRASP(model, sets, params, vars, start_time)
    model.write("solution_dG25_ME-noGRASP.sol")

    # Return the results
    results(model, sets, params, vars, start_time)

if __name__ == "__main__":
    main()

