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
from utils.plotting import plot_parts_vars
from model.GRASP import *
from gurobipy import *
import time


def main():
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

    # GRASP algorithm
    solution = GRASP(model, sets, params, vars, start_time)

    # Plot the inventory level of spare parts
    # plot_parts_vars(vars, sets, input_data)

if __name__ == "__main__":
    main()

