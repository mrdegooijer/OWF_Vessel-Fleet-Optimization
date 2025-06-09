from gurobipy import *
from utils.utils import unpack_sets, unpack_parameters

def create_variables(model, sets, params):
    """
    Create the variables for the model
    :return:
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts,
     mother_vessels, ctvessels, locations) = unpack_sets(sets)

    #z_b
    base_use = model.addVars(bases, lb=0, ub=1, vtype=GRB.BINARY, name="base_use")

    #x_bv
    purchased_vessels = model.addVars(bases, vessels, lb=0, vtype=GRB.INTEGER, name="purchased_vessels")

    #x_bvp
    chartered_vessels = model.addVars(bases, vessels, charter_periods, lb=0, vtype=GRB.INTEGER, name="chartered_vessels")

    #y_evpm
    task_performed = model.addVars(locations, ctvessels, periods, tasks, lb=0, vtype=GRB.INTEGER, name="task_performance")

    #n_evpk
    bundle_performed = model.addVars(locations, ctvessels, periods, bundles, lb=0, vtype=GRB.INTEGER, name="bundle_performance")

    #e_m
    tasks_late = model.addVars(prev_tasks, lb=0, vtype=GRB.INTEGER, name="tasks_late")

    #i_m
    tasks_not_performed = model.addVars(tasks, lb=0, vtype=GRB.INTEGER, name="tasks_not_performed")

    #l_pm
    periods_late = model.addVars(periods, corr_tasks, lb=0, vtype=GRB.INTEGER, name="periods_late")

    #r_evpm
    hours_spent = model.addVars(locations, ctvessels, periods, tasks, lb=0, vtype=GRB.CONTINUOUS, name='hours_spent')





    # Extension variables
    # q_sep
    inventory_level = model.addVars(spare_parts, locations, periods, lb=0, vtype=GRB.INTEGER, name="inventory_level")

    # o_sep
    order_quantity = model.addVars(spare_parts, locations, periods, lb=0, vtype=GRB.INTEGER, name="order_quantity")

    # o^trig_sep
    order_trigger = model.addVars(spare_parts, locations, periods, lb=0, ub=1, vtype=GRB.BINARY, name="order_trigger")

    # w_ep 
    # docking_available = model.addVars(mother_vessels, periods, lb=0, ub=1, vtype=GRB.BINARY, name="docking_available")

    # d_ep
    mv_offshore = model.addVars(mother_vessels, periods, lb=0, ub=1, vtype=GRB.BINARY, name="mothervessel_offshore")

    # lambda_sevp^P
    lambda_P = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, vtype=GRB.INTEGER, name="lambda_P")

    # lambda_sevp^CH
    lambda_CH = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, vtype=GRB.INTEGER, name="lambda_CH")

    # mu_sevp^P
    mu_P = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, vtype=GRB.INTEGER, name="mu_P")

    #mu_sevp^CH
    mu_CH = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, vtype=GRB.INTEGER, name="mu_CH")

    # Initial values
    for e in locations:
        for v in vessels:
            for m in tasks:
                task_performed[e, v, 0, m] = 0
                hours_spent[e, v, 0, m] = 0


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
        'order_trigger': order_trigger,
        'mv_offshore': mv_offshore,
        'lambda_P': lambda_P,
        'lambda_CH': lambda_CH,
        'mu_P': mu_P,
        'mu_CH': mu_CH
    }

    return vars