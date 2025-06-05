from gurobipy import *
from utils.utils import unpack_sets, unpack_parameters

def create_variables(model, sets, params):
    """
    Create the variables for the model
    :return:
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts
     ) = unpack_sets(sets)

    # Unpack parameters
    (cost_base_operation, cost_vessel_purchase, cost_vessel_charter,
     cost_vessel_operation, cost_technicians, cost_downtime,
     penalty_preventive_late, penalty_not_performed, vessel_speed,
     transfer_time, max_time_offshore, max_vessels_available_charter,
     distance_base_OWF, technicians_available, capacity_base_for_vessels,
     capacity_vessel_for_technicians, failure_rate, time_to_perform_task,
     technicians_required_task, latest_period_to_perform_task,
     tasks_in_bundles, technicians_required_bundle, weather_max_time_offshore,
     order_cost, lead_time, holding_cost, parts_required, max_part_capacity,
     reorder_level, big_m) = unpack_parameters(params)


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





    # Extension variables
    # q_sbp
    inventory_level = model.addVars(spare_parts, bases, periods, lb=0, vtype=GRB.INTEGER, name="inventory_level")

    # o_sbp
    order_quantity = model.addVars(spare_parts, bases, periods, lb=0, vtype=GRB.INTEGER, name="order_quantity")

    # o^trig_sbp
    order_trigger = model.addVars(spare_parts, bases, periods, lb=0, ub=1, vtype=GRB.BINARY, name="order_trigger")


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
        'inventory_level': inventory_level,
        'order_quantity': order_quantity,
        'order_trigger': order_trigger
    }

    model.update()
    return vars