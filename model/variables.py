from gurobipy import *
from utils.utils import unpack_sets, unpack_parameters

def create_variables(model, sets, params):
    """
    Create the variables for the model
    :return:
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles) = unpack_sets(sets)




    #z_b
    base_use = model.addVars(bases, lb=0, ub=1, vtype=GRB.BINARY, name="base_use")

    #x_bv
    purchased_vessels = model.addVars(bases, vessels, lb=0, vtype=GRB.INTEGER, name="purchased_vessels")

    #x_bvp
    chartered_vessels = model.addVars(bases, vessels, charter_periods, lb=0, vtype=GRB.INTEGER, name="chartered_vessels")

    #y_bvpm
    task_performed = model.addVars(bases, vessels, periods, tasks, lb=0, vtype=GRB.INTEGER, name="task_performance")

    #n_bvpk
    bundle_performed = model.addVars(bases, vessels, periods, bundles, lb=0, vtype=GRB.INTEGER, name="bundle_performance")

    #e_m
    tasks_late = model.addVars(prev_tasks, lb=0, vtype=GRB.INTEGER, name="tasks_late")

    #i_m
    tasks_not_performed = model.addVars(tasks, lb=0, vtype=GRB.INTEGER, name="tasks_not_performed")

    #l_pm
    periods_late = model.addVars(periods, corr_tasks, lb=0, vtype=GRB.INTEGER, name="periods_late")

    #r_bvpm
    hours_spent = model.addVars(bases, vessels, periods, tasks, lb=0, vtype=GRB.CONTINUOUS, name='hours_spent')





    # Initial values
    for b in bases:
        for v in vessels:
            for m in tasks:
                task_performed[b, v, 0, m] = 0
                hours_spent[b, v, 0, m] = 0






    vars = {
        'base_use': base_use,
        'purchased_vessels': purchased_vessels,
        'chartered_vessels': chartered_vessels,
        'task_performed': task_performed,
        'bundle_performed': bundle_performed,
        'tasks_late': tasks_late,
        'tasks_not_performed': tasks_not_performed,
        'periods_late': periods_late,
        'hours_spent': hours_spent,
    }




    model.update()
    return vars

