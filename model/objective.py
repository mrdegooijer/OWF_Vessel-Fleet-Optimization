from gurobipy import *
from utils.utils import unpack_sets, unpack_parameters, unpack_variables

def add_objective_function(model, sets, params, vars):
    # Unpack sets
    (bases, vessels, periods, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles,
     weather_availability_per_vessel) = unpack_sets(sets)

    # Unpack parameters
    (cost_base_operation, cost_vessel_purchase, cost_vessel_charter,
     cost_vessel_operation, cost_technicians, cost_downtime,
     penalty_preventive_late, penalty_not_performed, vessel_speed,
     transfer_time, max_time_offshore, max_vessels_available_charter,
     distance_base_OWF, technicians_available, capacity_base_for_vessels,
     capacity_vessel_for_technicians, failure_rate, time_to_perform_task,
     technicians_required_task, latest_period_to_perform_task,
     tasks_in_bundles, technicians_required_bundle) = unpack_parameters(params)

    # Unpack variables
    (base_use, purchased_vessels, chartered_vessels, task_performance,
     bundle_performance, tasks_late, tasks_not_performed,
     periods_late, hours_spent) = unpack_variables(vars)


    # Objective function
    cost_bases = quicksum(cost_base_operation[b] * base_use[b] for b in bases)
    cost_purchase_vessel = quicksum(cost_vessel_purchase[v] * purchased_vessels[b, v] for v in vessels for b in bases)


    model.setObjective(
        cost_bases
        + cost_purchase_vessel,
        GRB.MINIMIZE
    )