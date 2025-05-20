from gurobipy import *
from utils.utils import *

def add_constraints(model, sets, params, vars):
    """
    Add the constraints to the model
    :param model: Gurobi model
    :param sets: Sets
    :param params: Parameters
    :param vars: Variables
    :return:
    """

    # Unpack sets
    (
        bases, vessels, periods, charter_periods, tasks, vessel_task_compatibility,
        prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles,
        weather_availability_per_vessel
    ) = unpack_sets(sets)

    # Unpack parameters
    capacity_base_vessels = params['capacity_base_vessels']

    # Unpack variables
    base_use = vars['base_use']
    purchased_vessels = vars['purchased_vessels']
    chartered_vessels = vars['chartered_vessels']





    # Constraint 1: Amount of vessels in use less than or equal to base capacity
    for b in bases:
        for v in vessels:
            for p in charter_periods:
                model.addConstr(purchased_vessels[b, v] + chartered_vessels[b, v, p] <= capacity_base_vessels[b, v] * base_use[b], name=f"base_capacity_for_vessels_{b},{v},{p}")