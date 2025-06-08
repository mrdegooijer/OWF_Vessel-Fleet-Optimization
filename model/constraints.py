from tkinter.font import nametofont

from gurobipy import *
from utils.utils import *
from utils.initial_values import *

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




    # Constraint 1: Base capacity for vessels
    for b in bases:
        for v in vessels:
            for p in charter_periods:
                model.addConstr(purchased_vessels[b, v] + chartered_vessels[b, v, p] <= capacity_base_for_vessels[b, v] * base_use[b], name=f"1.base_capacity_for_vessels_{b},{v},{p}")

    # Constraint 2: Maximum number of vessels available for charter
    for v in vessels:
        for p in charter_periods:
            model.addConstr(quicksum(chartered_vessels[b, v, p] for b in bases) <= max_vessels_available_charter[v], name=f"2.max_vessels_available_for_charter_{v},{p}")

    # Constraint 3: Maximum time offshore (operating from base)
    for e in bases:
        for v in ctvessels:
            for p in periods:
                model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e]/vessel_speed[v])) for k in bundles), name=f"3.max_time_offshore_(base)_{e},{v},{p}")

    # Constraint 4: Maximum time offshore (operating from mothervessel)
    for e in mother_vessels:
        for v in ctvessels:
            for p in periods:
                model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] + additional_time[v] - transfer_time[v] * (1 + len(bundle_dict[k])))) for k in bundles), name=f"4.max_time_offshore_(mv)_{e},{v},{p}")

    # Constraint 5: Weather restrictions (for ctvs)
    for e in locations:
        for v in ctvessels:
            for p in periods:
                model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (weather_max_time_offshore[v, p] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e] / vessel_speed[v])) for k in bundles), name=f"5.weather_restrictions_ctv_{e},{v},{p}")

    # Constraint 6: Location capacity for technicians
    for e in locations:
        for p in periods:
            model.addConstr(quicksum(technicians_required_bundle[k] * bundle_performed[e, v, p, k] for v in ctvessels for k in bundles) <= technicians_available[e], name=f"6.location_capacity_for_technicians_{e},{p}")

    # Constraint 7: Vessel capacity for technicians
    for e in locations:
        for v in ctvessels:
            for p in periods:
                for k in bundles:
                    model.addConstr(technicians_required_bundle[k] * bundle_performed[e, v, p, k] <= capacity_vessel_for_technicians[v] * bundle_performed[e, v, p , k], name= f"7.vessel_capacity_for_technicians_{e},{v},{p},{k}")

    # Constraint 8: Tasks performed limited by number of vessels available
    for b in bases:
        for v in ctvessels:
            for p in periods:
                model.addConstr(quicksum(bundle_performed[b, v, p, k] for k in bundles) <= purchased_vessels[b, v] + chartered_vessels[b, v, return_charter_period(p, charter_dict)], name=f"8.tasks_performed_limit_{b},{v},{p}")

    # Constraint 9: Tasks performed late
    for m in prev_tasks:
        model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in ctvessels for p in range(latest_period_to_perform_task, periods[-1]+1)) == tasks_late[m], name=f"9.tasks_performed_late_{m}")


    # Constraint 10: Vessel-task compatibility
    for e in locations:
        for m in tasks:
            for v in [v for v in ctvessels if v not in vessel_task_compatibility[m]]:
                for p in periods:
                    model.addConstr(task_performed[e, v, p, m] == 0, name=f"10.vessel_task_compatibility_{e},{v},{p},{m}")

    # Constraint 11: Perform scheduled preventive tasks
    for m in prev_tasks:
        model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in ctvessels for p in periods) + tasks_not_performed[m]  == planned_prev_tasks[m], name=f"11.perform_scheduled_preventive_tasks_{m}")

    # Constraint 12: Perform corrective tasks
    for m in corr_tasks:
        model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in ctvessels for p in periods) + tasks_not_performed[m]  == quicksum(planned_corr_tasks.loc[m, p] for p in periods), name=f"12.perform_scheduled_corrective_tasks_{m}")

    # Constraint 13: Corrective tasks performed after failure
    for p in periods:
        for m in corr_tasks:
            model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in ctvessels) <= quicksum(planned_corr_tasks.loc[m, q] for q in range(1, p+1)) - quicksum(task_performed[e, v, q, m] for e in locations for v in ctvessels for q in range(1, p)), name=f"13.corrective_tasks_after_failures{m},{p}")

    # Constraint 14: Downtime for corrective tasks (periods late)
    for p in periods:
        for m in corr_tasks:
            model.addConstr(periods_late[p, m] == planned_corr_tasks.loc[m, p] - quicksum(task_performed[e, v, p, m] for e in locations for v in ctvessels) + get_periods_late(p-1, m, periods_late), name=f"14.periods_late_{p},{m}")

    # Constraint 15: Tasks performed from bundles
    for e in locations:
        for v in ctvessels:
            for p in periods:
                for m in tasks:
                    model.addConstr(task_performed[e, v, p, m] <= quicksum(tasks_in_bundles[m, k] * bundle_performed[e, v, p, k] for k in bundles), name=f"15.tasks_performed_from_bundles_{e},{v},{p},{m}")

    # Constraint 16: Time spent on tasks
    for e in locations:
        for v in ctvessels:
            for p in periods:
                for m in tasks:
                    model.addConstr(task_performed[e, v, p, m] == quicksum(hours_spent[c, w, q, m]/time_to_perform_task[m] - task_performed[c, w, q, m] for c in locations for w in ctvessels for q in range(0, p)) + hours_spent[e, v, p, m]/time_to_perform_task[m], name=f"16.time_spent_on_tasks_{e},{v},{p},{m}")




    # --- Constraints for extensions ---
    # Constraint 17: Inventory balance for bases
    for s in spare_parts:
        for e in bases:
            for p in periods:
                model.addConstr(inventory_level[s, e, p] == get_inventory_level(s, e, p-1, inventory_level, max_part_capacity) + get_order_quantity(s, e, p-lead_time[s], order_quantity) - quicksum(parts_required[m, s] * task_performed[e, v, p, m] for m in tasks for v in ctvessels) - quicksum(order_quantity[s, v, p] * quicksum(purchased_vessels[e, v] + chartered_vessels[e, v, q] for q in charter_periods) for v in mother_vessels), name=f"17.inventory_balance_bases_{s},{e},{p}")

    # Constraint 18: Inventory balance for mothervessels
    for s in spare_parts:
        for e in mother_vessels:
            for p in periods:
                model.addConstr(inventory_level[s, e, p] == get_inventory_level(s, e, p-1, inventory_level, max_part_capacity) + order_quantity[s, e, p] * (1-mv_offshore[e, p]) - quicksum(parts_required[m, s] * task_performed[e, v, p, m] for m in tasks for v in ctvessels), name=f"18.inventory_balance_mothervessels_{s},{e},{p}")

    # Constraint 19: Parts required for maintenance tasks to take place
    for s in spare_parts:
        for m in tasks:
            for p in periods:
                for e in locations:
                    model.addConstr(quicksum(parts_required[m, s] * task_performed[e, v, p, m] for v in ctvessels) <= inventory_level[s, e, p], name=f"19.parts_required_for_maintenance_tasks_{s},{m},{p},{e}")

    # Constraint 20: Maximum part capacity
    for s in spare_parts:
        for e in locations:
            for p in periods:
                model.addConstr(inventory_level[s, e, p] <= max_part_capacity[s, e], name=f"20.max_part_capacity_{s},{e},{p}")

    # Constraint 21: Order trigger activate
    for s in spare_parts:
        for e in locations:
            for p in periods:
                model.addConstr(inventory_level[s, e, p] <= reorder_level[s, e] + big_m * (1 - order_trigger[s, e, p]), name=f"21.order_trigger_activate_{s},{e},{p}")

    # Constraint 22: Order trigger deactivate
    for s in spare_parts:
        for e in locations:
            for p in periods:
                model.addConstr(inventory_level[s, e, p] >= reorder_level[s, e] - big_m * order_trigger[s, e, p], name=f"22.order_trigger_deactivate_{s},{e},{p}")

    # Constraint 23: Order quantity (bases)
    for s in spare_parts:
        for e in bases:
            for p in periods:
                model.addGenConstrIndicator(order_trigger[s, e, p], 1, order_quantity[s, e, p] == max_part_capacity[s, e] - inventory_level[s, e, p], name=f"23a.order_quantity_(base)_{s},{e},{p}")
                model.addGenConstrIndicator(order_trigger[s, e, p], 0, order_quantity[s, e, p] == 0, name=f"23b.order_quantity_zero_(base)_{s},{e},{p}")

    # Constraint 24: Order quantity (mothervessels) capacity limit
    for s in spare_parts:
        for e in mother_vessels:
            for p in periods:
                model.addGenConstrIndicator(order_trigger[s, e, p], 1, order_quantity[s, e, p] <= max_part_capacity[s, e] - inventory_level[s, e, p], name=f"24a.order_quantity_(mothervessel)_capacitylimit_{s},{e},{p}")
                model.addGenConstrIndicator(order_trigger[s, e, p], 0, order_quantity[s, e, p] == 0, name=f"24b.order_quantity_zero_(mothervessel)_capacitylimit_{s},{e},{p}")

    # Constraint 25: Order quantity (mothervessels) base inventory limit
    for s in spare_parts:
        for e in mother_vessels:
            for p in periods:
                model.addConstr(order_quantity[s, e, p] <= quicksum(inventory_level[s, b, p] * quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, p] for p in charter_periods) for b in bases), name=f"25.order_quantity_base_limit_(MV)_{s},{e},{p}")


    # Constraint 26: Max one mothervessel per type
    for v in mother_vessels:
        for p in charter_periods:
            model.addConstr(quicksum(purchased_vessels[b, v] + chartered_vessels[b, v, p] for b in bases) <= 1, name=f"26.mother_vessel_limit_{v},{p}")

    # Constraint 27: Mothervessel docking capacity
    for e in mother_vessels:
        for v in ctvessels:
            for p in periods:
                model.addConstr(quicksum(bundle_performed[e, v, p, k] for k in bundles) <= max_capacity_for_docking[e]*mv_offshore[e, p], name=f"27.mothervessel_docking_capacity_{e},{p}")

    # Constraint 28: Mothervessel maximum time offshore
    for e in mother_vessels:
        for p in range(1, periods[-1]+1 - max_time_offshore[e]):
            model.addConstr(quicksum(mv_offshore[e, q] for q in range(p, p + max_time_offshore[e] + 1)) <= max_time_offshore[e], name=f"28.mothervessel_max_time_offshore_{e},{p}")

    # Constraint 29: Mothervessel offshore status
    for e in mother_vessels:
        for p in periods:
            model.addConstr(mv_offshore[e, p] <= quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, return_charter_period(p, charter_dict)] for b in bases), name=f"29.mothervessel_offshore_status_{e},{p}")

    model.update()