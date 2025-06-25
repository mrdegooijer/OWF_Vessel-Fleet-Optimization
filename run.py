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
    # Create results and plots directories if it does not exist
    os.makedirs('plots', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    # Load input data
    file_path = r'data/Inputs_Validation.xlsx'
    input_data = load_input_data(file_path)
    print("Input data loaded successfully.")
    # Define the year of the weather data
    year = 2004

    # Initiate time tracking
    start_time = time.time()

    # Initialize the model
    model = Model("de Gooijer, 2025 - Validation")

    # Create sets, parameters, and variables
    sets = create_sets(input_data)
    print("Sets created.")
    params = create_parameters(input_data, sets, year)
    print("Parameters created.")
    vars = create_variables(model, sets, params)
    print("Variables created.")
    model.update()

    # Add constraints
    add_constraints(model, sets, params, vars)
    print("Constraints added.")

    # Add objective function
    add_objective_function(model, sets, params, vars)
    print("Objective function added.")
    print(f"Time taken to create model: {time.time() - start_time:.2f} seconds")

    # Optimize the model
    GRASP(model, sets, params, vars, start_time)
    if model.status == GRB.OPTIMAL:
        model.write("results/solution_dG25_Validation.sol")

    end_time = time.time()
    print(f"Optimization completed in {end_time - start_time:.2f} seconds.")

    # Return the results
    results(model, sets, params, vars, start_time, end_time)

if __name__ == "__main__":
    main()

