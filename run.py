from utils.utils import load_input_data
from model.sets import create_sets
from model.parameters import create_parameters
from model.variables import create_variables
from model.constraints import add_constraints
from model.objective import add_objective_function
from utils.plotting import plot_parts_vars
from gurobipy import *


def main():
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


    # Optimize the model
    model.optimize()

    model.computeIIS()
    model.write("infeasible.ilp")

    # Print the results
    # if model.status == GRB.OPTIMAL:
    #     print("Optimal solution found:")
    #     for v in model.getVars():
    #         if v.X > 0:
    #             print(f"{v.VarName}: {v.X}")
    # else:
    #     print("No optimal solution found.")

    # Plot the results
    # plot_parts_vars(vars, sets)
    #print the inventory levels
    # for s in sets['spare_parts']:
    #     for b in sets['bases']:
    #         for p in sets['periods']:
    #             print(f"Inventory level of spare part {s} at base {b} in period {p}: {vars['inventory_level'][s, b, p].X}")
    #             print(f"Order quantity of spare part {s} at base {b} in period {p}: {vars['order_quantity'][s, b, p]}")

    # Plot the inventory level of spare parts
    # plot_parts_vars(vars, sets, input_data)

if __name__ == "__main__":
    main()

