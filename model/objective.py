from gurobipy import *
from utils.utils import unpack_sets, unpack_parameters, unpack_variables

def add_objective_function(model, sets, params, vars):
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts,
     mother_vessels, ctvessels, locations) = unpack_sets(sets)

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
     reorder_level, big_m, max_capacity_for_docking,
     additional_time, tech_standby_cost) = unpack_parameters(params)

    # Unpack variables
    (base_use, purchased_vessels, chartered_vessels, task_performed,
     bundle_performed, tasks_late, tasks_not_performed,
     periods_late, hours_spent, inventory_level, order_quantity,
     order_trigger, mv_offshore) = unpack_variables(vars)


    # Objective function
    obj_cost_bases = quicksum(cost_base_operation[b] * base_use[b] for b in bases)
    obj_cost_purchase_vessel = quicksum(cost_vessel_purchase[v] * purchased_vessels[b, v] for v in vessels for b in bases)
    obj_cost_charter_vessel = quicksum(cost_vessel_charter[(v, p)] * chartered_vessels[b, v, p] for v in vessels for b in bases for p in charter_periods)
    obj_cost_operations = quicksum(hours_spent[e, v, p, m] * (cost_vessel_operation[v] + cost_technicians * technicians_required_task[m]) for e in locations for v in ctvessels for p in periods for m in tasks)
    obj_cost_downtime_preventive = quicksum(cost_downtime[p] * time_to_perform_task[m] * task_performed[e, v, p, m] for e in locations for v in ctvessels for p in periods for m in prev_tasks)
    obj_cost_downtime_corrective = quicksum(cost_downtime[p] * (task_performed[e, v, p, m] * (distance_base_OWF[e]/vessel_speed[v] + 2 * transfer_time[v] + time_to_perform_task[m]) + periods_late[p, m]*24) for e in locations for v in ctvessels for p in periods for m in corr_tasks) #multiply with 24 because cost is per hour
    obj_cost_penalty_late = quicksum(penalty_preventive_late * tasks_late[m] for m in prev_tasks)
    obj_cost_penalty_not_performed = quicksum(penalty_not_performed * tasks_not_performed[m] for m in tasks)
    obj_spare_parts_cost = quicksum(holding_cost[s, e] * inventory_level[s, e, p] + order_cost[s] * order_quantity[s, e, p] for s in spare_parts for e in locations for p in periods)


    model.setObjective(
        obj_cost_bases
        + obj_cost_purchase_vessel
        + obj_cost_charter_vessel
        + obj_cost_operations
        + obj_cost_downtime_preventive
        + obj_cost_downtime_corrective
        + obj_cost_penalty_late
        + obj_cost_penalty_not_performed
        + obj_spare_parts_cost,
        GRB.MINIMIZE
    )