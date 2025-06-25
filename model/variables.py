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

    # Unpack parameters
    (cost_base_operation, cost_vessel_charter,
     cost_repair, cost_downtime,
     penalty_preventive_late, penalty_not_performed, vessel_speed,
     transfer_time, max_time_offshore, max_vessels_available_charter,
     distance_base_OWF, technicians_available, capacity_base_for_vessels,
     capacity_vessel_for_technicians, failure_rate, time_to_perform_task,
     technicians_required_task, latest_period_to_perform_task,
     tasks_in_bundles, technicians_required_bundle, weather_max_time_offshore,
     order_cost, lead_time, holding_cost, parts_required, max_part_capacity,
     reorder_level, big_m, max_capacity_for_docking,
     initial_inventory) = unpack_parameters(params)

    # Find the highest 'max_part_capacity' for all
    capacities = []
    for s in spare_parts:
        for e in locations:
            capacities.append(max_part_capacity[s, e])
    max_capacity = max(capacities)


    #z_b
    base_use = model.addVars(bases, lb=0, ub=1, vtype=GRB.BINARY, name="base_use")

    #x_bv
    # Set to 0 for validation case
    purchased_vessels = model.addVars(bases, vessels, lb=0, ub=0, vtype=GRB.INTEGER, name="purchased_vessels")

    #x_bvp
    chartered_vessels = model.addVars(bases, vessels, charter_periods, lb=0, vtype=GRB.INTEGER, name="chartered_vessels")

    #y_evpm
    task_performed = model.addVars(locations, vessels, periods, tasks, lb=0, vtype=GRB.INTEGER, name="task_performance")

    #n_evpk
    bundle_performed = model.addVars(locations, vessels, periods, bundles, lb=0, vtype=GRB.INTEGER, name="bundle_performance")

    #e_m
    tasks_late = model.addVars(prev_tasks, lb=0, vtype=GRB.INTEGER, name="tasks_late")

    #i_m
    tasks_not_performed = model.addVars(tasks, lb=0, vtype=GRB.INTEGER, name="tasks_not_performed")

    #l_pm
    periods_late = model.addVars(periods, corr_tasks, lb=0, vtype=GRB.INTEGER, name="periods_late")

    #r_evpm
    hours_spent = model.addVars(locations, vessels, periods, tasks, lb=0, vtype=GRB.CONTINUOUS, name='hours_spent')





    # Extension variables
    # q_sep
    # inventory_level = model.addVars(spare_parts, locations, periods, lb=0, ub=0, vtype=GRB.INTEGER, name="inventory_level")
    inventory_level = 0

    # o_sep
    # order_quantity = model.addVars(spare_parts, locations, periods, lb=0, ub=0, vtype=GRB.INTEGER, name="order_quantity")
    order_quantity = 0

    # o^trig_sep
    # order_trigger = model.addVars(spare_parts, locations, periods, lb=0, ub=0, vtype=GRB.BINARY, name="order_trigger")
    order_trigger = 0

    # d_ep
    mv_offshore = model.addVars(mother_vessels, periods, lb=0, ub=0, vtype=GRB.BINARY, name="mothervessel_offshore")
    for v in mother_vessels:
        mv_offshore[v, 1].ub = 0

    # lambda_sevp^P
    # lambda_P = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, ub=max_capacity, vtype=GRB.CONTINUOUS, name="lambda_P")
    lambda_P = 0

    # lambda_sevp^CH
    # lambda_CH = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, ub=max_capacity, vtype=GRB.CONTINUOUS, name="lambda_CH")
    lambda_CH = 0

    # mu_sevp^P
    # mu_P = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, ub=max_capacity, vtype=GRB.CONTINUOUS, name="mu_P")
    mu_P = 0

    #mu_sevp^CH
    # mu_CH = model.addVars(spare_parts, bases, mother_vessels, periods, lb=0, ub=max_capacity, vtype=GRB.CONTINUOUS, name="mu_CH")
    mu_CH = 0

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