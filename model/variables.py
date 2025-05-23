from gurobipy import *
from utils.utils import unpack_sets

def create_variables(model, sets):
    """
    Create the variables for the model
    :return:
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles,
     spare_parts) = unpack_sets(sets)


    #z_b
    base_use = model.addVars(bases, vtype=GRB.BINARY, name="base_use")

    #x_bv
    purchased_vessels = model.addVars(bases, vessels, vtype=GRB.INTEGER, name="purchased_vessels")

    #x_bvp
    chartered_vessels = model.addVars(bases, vessels, charter_periods, vtype=GRB.INTEGER, name="chartered_vessels")

    #y_bvpm
    task_performed = model.addVars(bases, vessels, periods, tasks, vtype=GRB.INTEGER, name="task_performance")

    #n_bvpk
    bundle_performed = model.addVars(bases, vessels, periods, bundles, vtype=GRB.INTEGER, name="bundle_performance")

    #e_m
    tasks_late = model.addVars(prev_tasks, vtype=GRB.INTEGER, name="tasks_late")

    #i_m
    tasks_not_performed = model.addVars(tasks, vtype=GRB.INTEGER, name="tasks_not_performed")

    #l_pm
    periods_late = model.addVars(periods, corr_tasks, lb=0, vtype=GRB.INTEGER, name="periods_late")
    for m in tasks:
        periods_late[0, m] = 0

    #r_bvpm
    hours_spent = model.addVars(bases, vessels, periods, tasks, vtype=GRB.INTEGER, name='hours_spent')


    # Extension variables
    #q_sbp
    inventory_level = model.addVars(spare_parts, bases, periods, lb=0, vtype=GRB.INTEGER, name="inventory_level")

    #o_sbp
    order_quantity = model.addVars(spare_parts, bases, periods, lb=0, vtype=GRB.INTEGER, name="order_quantity")

    #o^trig_sbp
    order_trigger = model.addVars(spare_parts, bases, periods, lb=0, ub=1, vtype=GRB.BINARY, name="order_trigger")


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
        'inventory_level': inventory_level,
        'order_quantity': order_quantity,
        'order_trigger': order_trigger
    }

    model.update()
    return vars