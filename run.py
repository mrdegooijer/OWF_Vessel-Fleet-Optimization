from utils.utils import load_input_data
from model.sets import create_sets
from model.parameters import create_parameters
from model.variables import create_variables
from gurobipy import *


def main():
    # Load input data
    file_path = r'data/Inputs.xlsx'
    input_data = load_input_data(file_path)

    #Initialize the model
    model = Model("de Gooijer, 2025")

    sets = create_sets(input_data)
    create_parameters(input_data)
    create_variables(model, sets)


if __name__ == "__main__":
    main()

