from utils.utils import load_input_data
from model.sets import create_sets
from model.parameters import create_parameters


def main():
    # Load input data
    file_path = r'data/Inputs.xlsx'
    input_data = load_input_data(file_path)

    create_sets(input_data)
    create_parameters(input_data)


if __name__ == "__main__":
    main()

