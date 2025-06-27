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

    # Unpack variables
    (base_use, purchased_vessels, chartered_vessels, task_performed,
     bundle_performed, tasks_late, tasks_not_performed,
     periods_late, hours_spent, inventory_level, order_quantity,
     order_trigger, mv_offshore, lambda_P, lambda_CH, mu_P, mu_CH) = unpack_variables(vars)


    # Constraint 1: Base capacity for vessels
    # for b in bases:
    #     for v in vessels:
    #         for p in charter_periods:
    #             model.addConstr(purchased_vessels[b, v] + chartered_vessels[b, v, p] <= capacity_base_for_vessels[b, v] * base_use[b], name=f"1.base_capacity_for_vessels_{b},{v},{p}")
    model.addConstrs((purchased_vessels[b, v] + chartered_vessels[b, v, p] <= capacity_base_for_vessels[b, v] * base_use[b] for b in bases for v in vessels for p in charter_periods), name='1.base_capacity_for_vessels')


    # Constraint 2: Maximum number of vessels available for charter
    # for v in vessels:
    #     for p in charter_periods:
    #         model.addConstr(quicksum(chartered_vessels[b, v, p] for b in bases) <= max_vessels_available_charter[v], name=f"2.max_vessels_available_for_charter_{v},{p}")
    model.addConstrs((quicksum(chartered_vessels[b, v, p] for b in bases) <= max_vessels_available_charter[v] for v in vessels for p in charter_periods), name=f"2.max_vessels_available_for_charter")

    # Constraint 3: Maximum time offshore (operating from base)
    # for e in bases:
    #     for v in vessels:
    #         for p in periods:
    #             model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e]/vessel_speed[v])) for k in bundles), name=f"3.max_time_offshore_(base)_{e},{v},{p}")
    model.addConstrs((quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e]/vessel_speed[v])) for k in bundles) for e in bases for v in vessels for p in periods), name='3.max_time_offshore_(base)')

    # Constraint 4: Maximum time offshore (operating from mothervessel)
    # for e in mother_vessels:
    #     for v in ctvessels:
    #         for p in periods:
    #             model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] - transfer_time[v] * (1 + len(bundle_dict[k])))) for k in bundles), name=f"4.max_time_offshore_(mv)_{e},{v},{p}")
    model.addConstrs((quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (max_time_offshore[v] - transfer_time[v] * (1 + len(bundle_dict[k])))) for k in bundles) for e in mother_vessels for v in ctvessels for p in periods), name='4.max_time_offshore_(mv)')

    # Constraint 5: Weather restrictions (for ctvs)
    # for e in locations:
    #     for v in vessels:
    #         for p in periods:
    #             model.addConstr(quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (weather_max_time_offshore[v, p] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e] / vessel_speed[v])) for k in bundles), name=f"5.weather_restrictions_ctv_{e},{v},{p}")
    model.addConstrs((quicksum(hours_spent[e, v, p, m] for m in tasks) <= quicksum(bundle_performed[e, v, p, k] * (len(bundle_dict[k]) * (weather_max_time_offshore[v, p] - transfer_time[v] * (1 + len(bundle_dict[k]))) - 2 * (distance_base_OWF[e] / vessel_speed[v])) for k in bundles) for e in locations for v in vessels for p in periods), name='5.weather_restrictions_ctv')

    # Constraint 6: Location capacity for technicians
    # for e in locations:
    #     for p in periods:
    #         model.addConstr(quicksum(technicians_required_bundle[k] * bundle_performed[e, v, p, k] for v in vessels for k in bundles) <= technicians_available, name=f"6.location_capacity_for_technicians_{e},{p}")
    model.addConstrs((quicksum(technicians_required_bundle[k] * bundle_performed[e, v, p, k] for v in vessels for k in bundles) <= technicians_available for e in locations for p in periods), name='6.location_capacity_for_technicians')

    # Constraint 7: Vessel capacity for technicians
    # for e in locations:
    #     for v in vessels:
    #         for p in periods:
    #             for k in bundles:
    #                 model.addConstr(technicians_required_bundle[k] * bundle_performed[e, v, p, k] <= capacity_vessel_for_technicians[v] * bundle_performed[e, v, p , k], name= f"7.vessel_capacity_for_technicians_{e},{v},{p},{k}")
    model.addConstrs((technicians_required_bundle[k] * bundle_performed[e, v, p, k] <= capacity_vessel_for_technicians[v] * bundle_performed[e, v, p , k] for e in locations for v in vessels for p in periods for k in bundles), name='7.vessel_capacity_for_technicians')

    # Constraint 8: Tasks performed limited by number of vessels available
    # for e in bases:
    #     for v in vessels:
    #         for p in periods:
    #             model.addConstr(quicksum(bundle_performed[e, v, p, k] for k in bundles) <= purchased_vessels[e, v] + chartered_vessels[e, v, return_charter_period(p, charter_dict)], name=f"8.tasks_performed_limit_{b},{v},{p}")
    model.addConstrs((quicksum(bundle_performed[e, v, p, k] for k in bundles) <= purchased_vessels[e, v] + chartered_vessels[e, v, return_charter_period(p, charter_dict)] for e in bases for v in vessels for p in periods), name='8.tasks_performed_limit')

    # Constraint 9: Tasks performed late
    # for m in prev_tasks:
    #     model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in range(latest_period_to_perform_task, periods[-1]+1)) == tasks_late[m], name=f"9.tasks_performed_late_{m}")
    model.addConstrs((quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in range(latest_period_to_perform_task, periods[-1]+1)) == tasks_late[m] for m in prev_tasks), name='9.tasks_performed_late')

    # Constraint 10: Vessel-task compatibility
    # for e in locations:
    #     for m in tasks:
    #         for v in [v for v in vessels if v not in vessel_task_compatibility[m]]:
    #             for p in periods:
    #                 model.addConstr(task_performed[e, v, p, m] == 0, name=f"10.vessel_task_compatibility_{e},{v},{p},{m}")
    model.addConstrs((task_performed[e, v, p, m] == 0 for e in locations for m in tasks for v in [v for v in vessels if v not in vessel_task_compatibility[m]] for p in periods), name='10.vessel_task_compatibility')

    # Constraint 11: Perform scheduled preventive tasks
    # for m in prev_tasks:
    #     model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in periods) + tasks_not_performed[m]  == planned_prev_tasks[m], name=f"11.perform_scheduled_preventive_tasks_{m}")
    model.addConstrs((quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in periods) + tasks_not_performed[m]  == planned_prev_tasks[m] for m in prev_tasks), name='11.perform_scheduled_preventive_tasks')

    # Constraint 12: Perform corrective tasks
    # for m in corr_tasks:
    #     model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in periods) + tasks_not_performed[m]  == quicksum(planned_corr_tasks.loc[m, p] for p in periods), name=f"12.perform_scheduled_corrective_tasks_{m}")
    model.addConstrs((quicksum(task_performed[e, v, p, m] for e in locations for v in vessels for p in periods) + tasks_not_performed[m]  == quicksum(planned_corr_tasks.loc[m, p] for p in periods) for m in corr_tasks), name='12.perform_scheduled_corrective_tasks')

    # Constraint 13: Corrective tasks performed after failure
    # for p in periods:
    #     for m in corr_tasks:
    #         model.addConstr(quicksum(task_performed[e, v, p, m] for e in locations for v in vessels) <= quicksum(planned_corr_tasks.loc[m, q] for q in range(1, p+1)) - quicksum(task_performed[e, v, q, m] for e in locations for v in vessels for q in range(1, p)), name=f"13.corrective_tasks_after_failures{m},{p}")
    model.addConstrs((quicksum(task_performed[e, v, p, m] for e in locations for v in vessels) <= quicksum(planned_corr_tasks.loc[m, q] for q in range(1, p+1)) - quicksum(task_performed[e, v, q, m] for e in locations for v in vessels for q in range(1, p)) for m in corr_tasks for p in periods), name='13.corrective_tasks_after_failures')

    # Constraint 14: Downtime for corrective tasks (periods late)
    # for p in periods:
    #     for m in corr_tasks:
    #         model.addConstr(periods_late[p, m] == planned_corr_tasks.loc[m, p] - quicksum(task_performed[e, v, p, m] for e in locations for v in vessels) + get_periods_late(p-1, m, periods_late), name=f"14.periods_late_{p},{m}")
    model.addConstrs((periods_late[p, m] == planned_corr_tasks.loc[m, p] - quicksum(task_performed[e, v, p, m] for e in locations for v in vessels) + get_periods_late(p-1, m, periods_late) for m in corr_tasks for p in periods), name='14.periods_late')

    # Constraint 15: Tasks performed from bundles
    # for e in locations:
    #     for v in vessels:
    #         for p in periods:
    #             for m in tasks:
    #                 model.addConstr(task_performed[e, v, p, m] <= quicksum(tasks_in_bundles[m, k] * bundle_performed[e, v, p, k] for k in bundles), name=f"15.tasks_performed_from_bundles_{e},{v},{p},{m}")
    model.addConstrs((task_performed[e, v, p, m] <= quicksum(tasks_in_bundles[m, k] * bundle_performed[e, v, p, k] for k in bundles) for e in locations for v in vessels for p in periods for m in tasks), name='15.tasks_performed_from_bundles')

    # Constraint 16: Time spent on tasks
    # for e in locations:
    #     for v in vessels:
    #         for p in periods:
    #             for m in tasks:
    #                 model.addConstr(task_performed[e, v, p, m] == quicksum(hours_spent[c, w, q, m]/time_to_perform_task[m] - task_performed[c, w, q, m] for c in locations for w in ctvessels for q in range(0, p)) + hours_spent[e, v, p, m]/time_to_perform_task[m], name=f"16.time_spent_on_tasks_{e},{v},{p},{m}")
    model.addConstrs((task_performed[e, v, p, m] == quicksum(hours_spent[c, w, q, m]/time_to_perform_task[m] - task_performed[c, w, q, m] for c in locations for w in ctvessels for q in range(0, p)) + hours_spent[e, v, p, m]/time_to_perform_task[m] for e in locations for v in vessels for p in periods for m in tasks), name='16.time_spent_on_tasks')

    # --- Constraints for extensions ---
    # # Constraint 17: Inventory balance for bases
    # for s in spare_parts:
    #     for e in bases:
    #         for p in periods:
    #             model.addGenConstrIndicator(base_use[e], 1, inventory_level[s, e, p] == get_inventory_level(s, e, p-1, inventory_level, initial_inventory) + get_order_quantity(s, e, p-lead_time[s], order_quantity) - quicksum(parts_required[m, s] * task_performed[e, v, p, m] for m in tasks for v in ctvessels) - quicksum(lambda_P[s, e, v, p] + lambda_CH[s, e, v, p] for v in mother_vessels), name=f"17a.inventory_balance_bases_{s},{e},{p}")
    #             model.addGenConstrIndicator(base_use[e], 0, inventory_level[s, e, p] == 0, name=f"17b.inventory_balance_bases_{s},{e},{p}")
    #
    # # Constraint 18: Inventory balance for mothervessels & Constraint 19: order quantity big m
    # for s in spare_parts:
    #     for e in mother_vessels:
    #         for p in periods:
    #             # Constraint 18
    #             model.addConstr(inventory_level[s, e, p] == get_inventory_level(s, e, p-1, inventory_level, initial_inventory) + get_order_quantity(s, e, p-1, order_quantity) - quicksum(parts_required[m, s] * task_performed[e, v, p, m] for m in tasks for v in ctvessels), name=f"18.inventory_balance_mothervessels_{s},{e},{p}")
    #             # Constraint 19
    #             model.addConstr(order_quantity[s, e, p] <= big_m * (1-mv_offshore[e, p]), name=f"19.order_quantity_mv_{s},{e},{p}")
    #
    # # Constraint 20: Parts required for maintenance tasks to take place
    # for s in spare_parts:
    #     for m in tasks:
    #         for p in periods:
    #             for e in locations:
    #                 model.addConstr(quicksum(parts_required[m, s] * task_performed[e, v, p, m] for v in ctvessels) <= inventory_level[s, e, p], name=f"20.parts_required_for_maintenance_tasks_{s},{m},{p},{e}")
    #
    # # Constraint 21: Maximum part capacity
    # for s in spare_parts:
    #     for e in locations:
    #         for p in periods:
    #             model.addConstr(inventory_level[s, e, p] <= max_part_capacity[s, e], name=f"21.max_part_capacity_{s},{e},{p}")
    #
    # # Constraint 22 & 23: Order trigger activate
    # for s in spare_parts:
    #     for e in mother_vessels:  # or mothervessels
    #         for p in periods:
    #             model.addConstr(inventory_level[s, e, p] <= reorder_level[s, e] + big_m * (1 - order_trigger[s, e, p]), name=f"22.order_trigger_activate_MV_{s},{e},{p}")
    #     for e in bases:
    #         for p in periods:
    #             model.addConstr(inventory_level[s, e, p] <= reorder_level[s, e] + big_m * (1 - order_trigger[s, e, p]) + big_m * (1 - base_use[e]), name=f"23.order_trigger_activate_base_{s},{e},{p}")

    # Constraint 24 & 25: Order trigger deactivate
    # for s in spare_parts:
        # for e in mother_vessels:  # or mothervessels
        #     for p in periods:
                # model.addConstr(inventory_level[s, e, p] >= reorder_level[s, e] + 1 - big_m * order_trigger[s, e, p], name=f"24.order_trigger_deactivate_MV_{s},{e},{p}")
        # for e in bases:
        #     for p in periods:
                # model.addConstr(inventory_level[s, e, p] >= reorder_level[s, e] + 1 - big_m * order_trigger[s, e, p] - big_m * (1 - base_use[e]), name=f"25.order_trigger_deactivate_base_{s},{e},{p}")

    # Constraint 26 - 28: Order quantity constraints for bases and mothervessels
    # for s in spare_parts:
    #     for e in bases:
    #         for p in periods:
    #             # Constraint 26
    #             model.addConstr(order_quantity[s, e, p] <= (max_part_capacity[s, e] - inventory_level[s, e, p]) + big_m * (1 - order_trigger[s, e, p]), name=f"26a.order_quantity_(base)_{s},{e},{p}")
    #             # Constraint 27 (?)
    #             model.addConstr(order_quantity[s, e, p] >= (max_part_capacity[s, e] - inventory_level[s, e, p]) - big_m * (1 - order_trigger[s, e, p]), name=f"27.order_quantity_(base)_{s},{e},{p}")
    #             # Constraint 28
    #             model.addConstr(order_quantity[s, e, p] <= big_m * order_trigger[s, e, p], name=f"28a.order_quantity_(base)_{s},{e},{p}")
    #
    # for s in spare_parts:
    #     for e in mother_vessels:
    #         for p in periods:
    #             # Constraint 26 (also for mothervessels)
    #             model.addConstr(order_quantity[s, e, p] <= (max_part_capacity[s, e] - inventory_level[s, e, p]) + big_m * (1 - order_trigger[s, e, p]), name=f"26b.order_quantity_(mv)_{s},{e},{p}")
    #             # Constraint 28 (also for mothervessels)
    #             model.addConstr(order_quantity[s, e, p] <= big_m * order_trigger[s, e, p], name=f"28b.order_quantity_(mv)_{s},{e},{p}")


    # Constraint 29: Bundles performed limited by total vessels in fleet
    # for e in mother_vessels:
    #     for v in ctvessels:
    #         for p in periods:
    #             model.addConstr(quicksum(bundle_performed[e, v, p, k] for k in bundles) <= quicksum(purchased_vessels[b, v] + chartered_vessels[b, v, return_charter_period(p, charter_dict)] for b in bases), name=f"29.tasks_performed_limit_{e},{v},{p}")
    model.addConstrs((quicksum(bundle_performed[e, v, p, k] for k in bundles) <= quicksum(purchased_vessels[b, v] + chartered_vessels[b, v, return_charter_period(p, charter_dict)] for b in bases) for e in mother_vessels for v in ctvessels for p in periods), name='29.tasks_performed_limit')

    # Constraint 30: Max one mothervessel per type
    # for v in mother_vessels:
    #     for p in charter_periods:
    #         model.addConstr(quicksum(purchased_vessels[b, v] + chartered_vessels[b, v, p] for b in bases) <= 1, name=f"30.mother_vessel_limit_{v},{p}")
    model.addConstrs((quicksum(purchased_vessels[b, v] + chartered_vessels[b, v, p] for b in bases) <= 1 for v in mother_vessels for p in charter_periods), name='30.mother_vessel_limit')

    # Constraint 31: Mothervessel docking capacity
    # for e in mother_vessels:
    #     for v in ctvessels:
    #         for p in periods:
    #             model.addConstr(quicksum(bundle_performed[e, v, p, k] for k in bundles) <= max_capacity_for_docking[e, v]*mv_offshore[e, p], name=f"31.mothervessel_docking_capacity_{e},{p}")
    model.addConstrs((quicksum(bundle_performed[e, v, p, k] for k in bundles) <= max_capacity_for_docking[e, v]*mv_offshore[e, p] for e in mother_vessels for v in ctvessels for p in periods), name='31.mothervessel_docking_capacity')

    # Constraint 32: Mothervessel maximum time offshore
    # for e in mother_vessels:
    #     max_periods_offshore = int(max_time_offshore[e]/24)
    #     for p in range(1, periods[-1]+1 - max_periods_offshore):
    #         model.addConstr(quicksum(mv_offshore[e, q] for q in range(p, p + max_periods_offshore + 1)) <= max_periods_offshore, name=f"32.mothervessel_max_time_offshore_{e},{p}")

    # Constraint 33: Mothervessel offshore status
    # for e in mother_vessels:
    #     for p in periods:
    #         model.addConstr(mv_offshore[e, p] <= quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, return_charter_period(p, charter_dict)] for b in bases), name=f"33.mothervessel_offshore_status_{e},{p}")
    model.addConstrs((mv_offshore[e, p] <= quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, return_charter_period(p, charter_dict)] for b in bases) for e in mother_vessels for p in periods), name='33.mothervessel_offshore_status')

    # Constraints 34 - 37: Auxiliary variables linking purchased and chartered vessels with their bases for order quantity and inventory level
    # for s in spare_parts:
    #     for e in bases:
    #         for v in mother_vessels:
    #             for p in periods:
    #                 # Constraint 34
    #                 model.addGenConstrIndicator(purchased_vessels[e, v], 1, lambda_P[s, e, v, p] == order_quantity[s, v, p], name=f"34a.aux_var_lambda_P_{s},{e},{v},{p}")
    #                 model.addGenConstrIndicator(purchased_vessels[e, v], 0, lambda_P[s, e, v, p] == 0, name=f"34b.aux_var_lambda_P_{s},{e},{v},{p}")
    #                 # model.addConstr(lambda_P[s, e, v, p] == order_quantity[s, v, p])
    #
    #                 #Constraint 35
    #                 model.addGenConstrIndicator(chartered_vessels[e, v, return_charter_period(p, charter_dict)], 1, lambda_CH[s, e, v, p] == order_quantity[s, v, p], name=f"35a.aux_var_lambda_CH_{s},{e},{v},{p}")
    #                 model.addGenConstrIndicator(chartered_vessels[e, v, return_charter_period(p, charter_dict)], 0, lambda_CH[s, e, v, p] == 0, name=f"35b.aux_var_lambda_CH_{s},{e},{v},{p}")
    #
    #                 # Constraint 36
    #                 model.addGenConstrIndicator(purchased_vessels[e, v], 1, mu_P[s, e, v, p] == inventory_level[s, e, p], name=f"36a.aux_var_mu_P_{s},{e},{v},{p}")
    #                 model.addGenConstrIndicator(purchased_vessels[e, v], 0, mu_P[s, e, v, p] == 0, name=f"36b.aux_var_mu_P_{s},{e},{v},{p}")
    #                 # model.addConstr(mu_P[s, e, v, p] == inventory_level[s, e, p])
    #
    #                 # Constraint 37
    #                 model.addGenConstrIndicator(chartered_vessels[e, v, return_charter_period(p, charter_dict)], 1, mu_CH[s, e, v, p] == inventory_level[s, e, p], name=f"37a.aux_var_mu_CH_{s},{e},{v},{p}")
    #                 model.addGenConstrIndicator(chartered_vessels[e, v, return_charter_period(p, charter_dict)], 0, mu_CH[s, e, v, p] == 0, name=f"37b.aux_var_mu_CH_{s},{e},{v},{p}")



    # for s in spare_parts:
    #     for e in mother_vessels:
    #         for p in periods:
    #             # Constraint 38: No inventory when no mothervessel use
    #             model.addConstr(inventory_level[s, e, p] <= big_m * quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, return_charter_period(p, charter_dict)] for b in bases), name=f"38.no_inventory_when_no_mothervessel_use_{s},{e},{p}")
    #
    #             # Constraint 39: No order quantity when no mothervessel use
    #             model.addConstr(order_quantity[s, e, p] <= big_m * quicksum(purchased_vessels[b, e] + chartered_vessels[b, e, return_charter_period(p, charter_dict)] for b in bases), name=f"39.no_order_quantity_when_no_mothervessel_use_{s},{e},{p}")

    # for p in charter_periods:
    #     for b in bases:
    #         model.addConstr(chartered_vessels[b, 'V5', p] <= big_m * chartered_vessels[b, 'V4', p], name=f"A.MV_DV_connection_{b},{p}")
    model.addConstrs((chartered_vessels[b, 'V5', p] <= big_m * chartered_vessels[b, 'V4', p] for b in bases for p in charter_periods), name='A.MV_DV_connection')
    model.addConstrs((chartered_vessels[b, 'V5', p] >= 2 * chartered_vessels[b, 'V4', p] for b in bases for p in charter_periods, name='C.MV_is_2DV_connection')

    # for e in mother_vessels:
    #     for m in tasks:
    #         for v in mother_vessels:
    #             for p in periods:
    #                 model.addConstr(task_performed[e, v, p, m] == 0, name=f"B.mothervessel_cannot_deploy_itself_{e},{v},{p},{m}")
    model.addConstrs((task_performed[e, v, p, m] == 0 for e in mother_vessels for v in mother_vessels for p in periods for m in tasks), name='B.mothervessel_cannot_deploy_itself')

    model.update()