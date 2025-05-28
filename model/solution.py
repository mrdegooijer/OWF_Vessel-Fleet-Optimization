"""
This file contains the solution method as developed by Versluijs (2023)
"""

from gurobipy import *
from utils.utils import *
from utils.solution_utils import *

def greedy_construction(model, sets, params, vars):
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts) = unpack_sets(sets)

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

    (base_use, purchased_vessels, chartered_vessels, task_performed,
     bundle_performed, tasks_late, tasks_not_performed,
     periods_late, hours_spent, inventory_level, order_quantity,
     order_trigger) = unpack_variables(vars)


    # --- 1. --- Set all bases and vessels to zero
    for b in bases:
        base_use[b].ub = 0
        for v in vessels:
            purchased_vessels[b, v].ub = 0
            for p in charter_periods:
                chartered_vessels[b, v, p].ub = 0

    model.update()

    # --- 2. --- Choose optimal (cheapest) bases
    best_base = None
    best_obj = float("inf")
    for b in bases:
        base_use[b].lb = base_use[b].ub = 1
        obj = solve_return_obj(model)
        if obj < best_obj:
            best_obj, best_base = obj, b
        base_use[b].lb = 0
        base_use[b].ub = 0
    print(best_base)
    # lock the best base to be included
    base_use[best_base].lb = base_use[best_base].ub = 1
    model.update()

    # --- 3. --- Choose optimal purchased vessels quantity per type
    for v in vessels:
        capacity = capacity_base_for_vessels[best_base, v]
        best_quantity = 0
        best_obj = float("inf")
        for q in range(capacity + 1):
            purchased_vessels[best_base, v].lb = purchased_vessels[best_base, v].ub = q
            obj = solve_return_obj(model)
            if obj < best_obj:
                best_quantity, best_obj = q, obj

        # lock the best quantity
        purchased_vessels[best_base, v].lb = purchased_vessels[best_base, v].ub = best_quantity
    model.update()

    # --- 4. --- Choose optimal chartered vessels quantity per type and charter_period
    for v in vessels:
        remaining_capacity = capacity_base_for_vessels[best_base, v] - purchased_vessels[best_base, v].lb

        if remaining_capacity <= 0:
            continue

        for p in charter_periods:
            best_quantity = 0
            best_obj = float("inf")
            for q in range(int(remaining_capacity) + 1):
                chartered_vessels[best_base, v, p].lb = chartered_vessels[best_base, v, p].ub = q
                obj = solve_return_obj(model)
                if obj < best_obj:
                    best_quantity, best_obj = q, obj

            # lock the best quantity, per charter_period
            chartered_vessels[best_base, v, p].lb = chartered_vessels[best_base, v, p].ub = best_quantity

    # --- 5. --- Return the integer decision vector
    model.optimize()

    print('Objective value:', model.objVal)
    print('Base use:', {b: base_use[b].X for b in bases})
    print('Purchased vessels:', {b: {v: purchased_vessels[b, v].X for v in vessels} for b in bases})
    print('Chartered vessels:', {b: {v: {p: chartered_vessels[b, v, p].X for p in charter_periods} for v in vessels} for b in bases})


    ordered = flatten_decision_vars(model._Vars)
    solution_vector = [x.X for x in ordered]

    return solution_vector