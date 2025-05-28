from gurobipy import *
from utils.utils import *
from utils.solution_utils import *

def greedy_construction_IV(model, sets, params, vars):
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

    # --- 2. --- Choose optimal (cheapest) base
    obj_value_b = {}
    for b in bases:
        obj_value_b[b] = []
        base_use[b].lb = 1
        base_use[b].ub = 1
        model.optimize()
        if model.status == GRB.Status.OPTIMAL:
            obj_value_b[b] = model.objVal

    for b in bases:
        base_use[b].lb = 0
        base_use[b].ub = 0
    base_use[min(obj_value_b, key=obj_value_b.get)].lb = 1
    base_use[min(obj_value_b, key=obj_value_b.get)].ub = 1

    b_opt = min(obj_value_b, key=obj_value_b.get)

    # --- 3. --- Choose optimal puchased vessels quantity per type
    obj_value_pv = {}
    for v in vessels:
        obj_value_pv[v] = {}
        for i in range(min(max_vessels_available_charter[v], capacity_base_for_vessels[b_opt, v]) + 1):
            obj_value_pv[v][i] = []
            purchased_vessels[b_opt, v].ub = i
            purchased_vessels[b_opt, v].lb = i
            print(f"Optimizing purchased vessels for base {b_opt}, vessel {v}, quantity {i}")
            model.optimize()
            if model.status == GRB.Status.OPTIMAL:
                obj_value_pv[v][i] = model.objVal
        purchased_vessels[b_opt, v].ub = min(obj_value_pv[v], key=obj_value_pv[v].get)
        purchased_vessels[b_opt, v].lb = min(obj_value_pv[v], key=obj_value_pv[v].get)

    # --- 4. --- Choose optimal chartered vessels quantity per type
    obj_value_cv = {}
    for v in vessels:
        obj_value_cv[v] = {}
        for p in charter_periods:
            obj_value_cv[v][p] = {}
            for i in range(min(max_vessels_available_charter[v], capacity_base_for_vessels[b_opt, v])+1-min(obj_value_pv[v], key=obj_value_pv[v].get)):
                obj_value_cv[v][p][i] = []
                chartered_vessels[b_opt, v, p].ub = i
                chartered_vessels[b_opt, v, p].lb = i
                print(f"Optimizing chartered vessels for base {b_opt}, vessel {v}, period {p}, quantity {i}")
                model.optimize()
                obj_value_cv[v][p][i] = model.objVal
            chartered_vessels[b_opt,v,p].ub = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)
            chartered_vessels[b_opt,v,p].lb = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)

    # --- 5. --- Return the initial solution vector
    model.optimize()
    print('Objective value:', model.objVal)
    print('Base use:', {b: base_use[b].X for b in bases})
    print('Purchased vessels:', {b: {v: purchased_vessels[b, v].X for v in vessels} for b in bases})
    print('Chartered vessels:',
          {b: {v: {p: chartered_vessels[b, v, p].X for p in charter_periods} for v in vessels} for b in bases})

