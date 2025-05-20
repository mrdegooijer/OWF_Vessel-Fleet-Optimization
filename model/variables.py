from gurobipy import *

def create_variables(model, sets):
    """
    Create the variables for the model
    :return:
    """
    base_use = model.addVars(sets['bases'], vtype=GRB.BINARY, name="base_use")

    purchased_vessels = model.addVars(sets['bases'], sets['vessels'], vtype=GRB.INTEGER, name="purchased_vessels")

    chartered_vessels = model.addVars(sets['bases'], sets['vessels'], sets['charter_periods'], vtype=GRB.INTEGER, name="chartered_vessels")


    vars = {
        'base_use': base_use,
        'purchased_vessels': purchased_vessels,
        'chartered_vessels': chartered_vessels
    }

    return vars