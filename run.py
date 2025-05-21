from utils.utils import load_input_data
from model.sets import create_sets
from model.parameters import create_parameters
from model.variables import create_variables
from model.constraints import add_constraints
from model.objective import add_objective_function
from gurobipy import *


def main():
    # Load input data
    file_path = r'data/Inputs.xlsx'
    input_data = load_input_data(file_path)

    # Initialize the model
    model = Model("de Gooijer, 2025")

    # Create sets, parameters, and variables
    sets = create_sets(input_data)
    params = create_parameters(input_data, sets)
    vars = create_variables(model, sets)
    model.update()

    # Add constraints
    add_constraints(model, sets, params, vars)

    # Add objective function
    add_objective_function(model, sets, params, vars)


    # Optimize the model
    model.optimize()

if __name__ == "__main__":
    main()

