from tkinter.font import nametofont

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
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles,
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
    (base_use, purchased_vessels, chartered_vessels, task_performed,
     bundle_performed, tasks_late, tasks_not_performed,
     periods_late, hours_spent) = unpack_variables(vars)




    # Constraint 1: Base capacity for vessels
    for b in bases:
        for v in vessels:
            for p in charter_periods:
                model.addConstr(purchased_vessels[b, v] + chartered_vessels[b, v, p] <= capacity_base_for_vessels[b, v] * base_use[b], name=f"base_capacity_for_vessels_{b},{v},{p}")

    # Constraint 2: Maximum number of vessels available for charter
    for v in vessels:
        for p in charter_periods:
            model.addConstr(quicksum(chartered_vessels[b, v, p] for b in bases) <= max_vessels_available_charter[v], name=f"max_vessels_available_for_charter_{v},{p}")

    # Constraint 3: Maximum time offshore
    for b in bases:
        for v in vessels:
            for p in periods:
                model.addConstr(quicksum(hours_spent[b, v, p, m] for m in tasks) <= quicksum(bundle_performed[b, v, p, k] * (tasks_in_bundles[m, k] * (max_time_offshore[v] - transfer_time[v] * (1 + tasks_in_bundles[m, k])) - 2 * distance_base_OWF[b]/vessel_speed[v]) for k in bundles for m in tasks), name=f"max_time_offshore_{b},{v},{p}")

    # Constraint 4: Base capacity for technicians
    for b in bases:
        for p in periods:
            model.addConstr(quicksum(technicians_required_bundle[k] * bundle_performed[b, v, p, k] for v in vessels for k in bundles) <= technicians_available[b], name=f"base_capacity_for_technicians_{b},{p}")

    # Constraint 5: Vessel capacity for technicians
    for b in bases:
        for v in vessels:
            for p in periods:
                for k in bundles:
                    model.addConstr(technicians_required_bundle[k] * bundle_performed[b, v, p , k] <= capacity_vessel_for_technicians[v] * bundle_performed[b, v, p , k], name= f"vessel_capacity_for_technicians_{b},{v},{p},{k}")

    # Constraint 6: Tasks performed limited by amount of vessels available
    for b in bases:
        for v in vessels:
            for p in periods:
                model.addConstr(quicksum(bundle_performed[b, v, p, k] for k in bundles) <= purchased_vessels[b, v] + chartered_vessels[b, v, return_charter_period(p, charter_dict)], name=f"tasks_performed_limit_{b},{v},{p}")

    # Constraint 7: Tasks performed late
    for m in prev_tasks:
        model.addConstr(quicksum(task_performed[b, v, p, m] for b in bases for v in vessels for p in range(latest_period_to_perform_task, periods[-1])) == tasks_late[m], name=f"tasks_performed_late_{m}")

    # Constraint 8: Weather availability

    # Constraint 9: Vessel-task compatibility
    for b in bases:
        for m in tasks:
            for v in [v for v in vessels if v not in vessel_task_compatibility[m]]:
                for p in periods:
                    model.addConstr(task_performed[b, v, p, m] == 0, name=f"vessel_task_compatibility_{b},{v},{p},{m}")

    # Constraint 10: Perform scheduled preventive tasks
    for m in prev_tasks:
        model.addConstr(quicksum(task_performed[b, v, p, m] + tasks_not_performed[m] for b in bases for v in vessels for p in periods) == planned_prev_tasks[m], name=f"perform_scheduled_preventive_tasks_{m}")

    # Constraint 11: Perform corrective tasks
    for m in corr_tasks:
        model.addConstr(quicksum(task_performed[b, v, p, m] + tasks_not_performed[m] for b in bases for v in vessels for p in periods) == quicksum(planned_corr_tasks.loc[m, p] for p in periods), name=f"perform_scheduled_corrective_tasks_{m}")

    # Constraint 12: Corrective tasks performed after failure
    for p in periods:
        for m in corr_tasks:
            model.addConstr(quicksum(task_performed[b, v, p, m] for b in bases for v in vessels) <= quicksum(planned_corr_tasks.loc[m, q] for q in range(1, p+1)) - quicksum(task_performed[b, v, q, m] for b in bases for v in vessels for q in range(1, p)), name=f"corrective_tasks_after_failures{m},{p}")

    # Constraint 13: Downtime for corrective tasks
    for p in periods:
        for m in corr_tasks:
            model.addConstr(periods_late[p, m] == planned_corr_tasks.loc[m, p] - quicksum(task_performed[b, v, p, m] + periods_late[p-1, m] for b in bases for v in vessels), name=f"periods_late_{p},{m}")

    # Constraint 14: Tasks performed from bundles
    for b in bases:
        for v in vessels:
            for p in periods:
                for m in tasks:
                    model.addConstr(task_performed[b, v, p, m] <= quicksum(tasks_in_bundles[m, k] * bundle_performed[b, v, p, k] for k in bundles), name=f"tasks_performed_from_bundles_{b},{v},{p},{m}")

    # Constraint 15: Time spent on tasks
    for b in bases:
        for v in vessels:
            for p in periods:
                for m in tasks:
                    model.addConstr(task_performed[b, v, p, m] <= quicksum(hours_spent[c, w, q, m]/time_to_perform_task[m] - task_performed[c, w, q, m] for c in bases for w in vessels for q in range(1, p+1)) + hours_spent[b, v, p, m]/time_to_perform_task[m], name=f"time_spent_on_tasks_{b},{v},{p},{m}")


    model.update()