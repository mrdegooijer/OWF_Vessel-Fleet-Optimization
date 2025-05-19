from gurobipy import *

def create_variables(model, sets):
    """
    Create the variables for the model
    :return:
    """


    base_use = model.addVars(sets['bases'], vtype=GRB.BINARY, name="base_use")

    purchased_vessels = model.addVars(sets['bases'], sets['vessels'], vtype=GRB.INTEGER, name="purchased_vessels")

    chartered_vessels = model.addVars(sets['bases'], sets['vessels'], sets['periods'], vtype=GRB.INTEGER, name="chartered_vessels")