from gurobipy import *
from utils.utils import *
from utils.initial_values import *
from utils.plotting import plot_parts_vars
import time
import pickle


def results(model, sets, params, vars, start_time, end_time):
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


    if model.status == GRB.Status.INFEASIBLE:
        model.computeIIS()
        model.write("results/infeasible.ilp")
        print("Model is infeasible. IIS written to 'infeasible.ilp'.")

    elif model.status == GRB.Status.OPTIMAL:
        # Calculate the cost elements of the objective function
        obj_cost_bases = sum(cost_base_operation[b] * base_use[b].x for b in bases)
        # obj_cost_purchase_vessel = sum(cost_vessel_purchase[v] * purchased_vessels[b, v].x for v in vessels for b in bases)
        obj_cost_charter_vessel = sum(cost_vessel_charter[(v, p)] * chartered_vessels[b, v, p].x for v in vessels for b in bases for p in charter_periods)
        # obj_cost_operations = sum(hours_spent[e, v, p, m].x * (cost_vessel_operation[v] + cost_technicians * technicians_required_task[m]) for e in locations for v in ctvessels for p in periods for m in tasks)
        obj_cost_operations_validation = sum(task_performed[e, v, p, m].x * cost_repair[m] for e in locations for v in ctvessels for p in periods for m in tasks)
        obj_cost_downtime_preventive = sum(cost_downtime[p] * time_to_perform_task[m] * task_performed[e, v, p, m].x for e in locations for v in ctvessels for p in periods for m in prev_tasks)
        obj_cost_downtime_corrective = sum(cost_downtime[p] * (task_performed[e, v, p, m].x * (distance_base_OWF[e] / vessel_speed[v] + 2 * transfer_time[v] + time_to_perform_task[m]) + periods_late[p, m].x * 24) for e in locations for v in ctvessels for p in periods for m in corr_tasks)
        obj_cost_penalty_late = sum(penalty_preventive_late * tasks_late[m].x for m in prev_tasks)
        obj_cost_penalty_not_performed = sum(penalty_not_performed * tasks_not_performed[m].x for m in tasks)
        # obj_cost_spare_parts = sum(holding_cost[s, e] * inventory_level[s, e, p].x for s in spare_parts for e in locations for p in periods) + sum(order_cost[s] * order_quantity[s, e, p].x for s in spare_parts for e in bases for p in periods)
        # obj_cost_mothervessels = sum(cost_vessel_operation[v] * mv_offshore[v, p].x for v in mother_vessels for p in periods)
        total_cost = obj_cost_bases + obj_cost_charter_vessel + obj_cost_operations_validation + obj_cost_downtime_preventive + obj_cost_downtime_corrective + obj_cost_penalty_late + obj_cost_penalty_not_performed

        # Print the vessels purchased and chartered at each base
        for b in bases:
            print('At ' + str(b))
            # for v in vessels:
            #     print('The number of purchased vessels of type ' + str(v) + ' is: %d' % purchased_vessels[b, v].x)
            for v in vessels:
                for p in charter_periods:
                    print('The number of chartered vessels of type ' + str(v) + ' in period ' + str(p) + ' is: %d' %
                          chartered_vessels[b, v, p].x)

        # Print the objective value
        print(f"Objective value: {model.objVal:.2f}")

        # Print the cost elements
        print(f"Cost of operating bases: {obj_cost_bases:.2f}")
        # print(f"Cost of purchased vessels: {obj_cost_purchase_vessel:.2f}")
        print(f"Cost of chartered vessels: {obj_cost_charter_vessel:.2f}")
        print(f"Cost of maintenance: {obj_cost_operations_validation:.2f}")
        print(f"Cost of downtime - preventive tasks: {obj_cost_downtime_preventive:.2f}")
        print(f"Cost of downtime - corrective tasks: {obj_cost_downtime_corrective:.2f}")
        print(f"Cost of penalties for late tasks: {obj_cost_penalty_late:.2f}")
        print(f"Cost of penalties for not performed tasks: {obj_cost_penalty_not_performed:.2f}")
        # print(f"Cost of spare parts management: {obj_cost_spare_parts:.2f}")
        # print(f"Cost of mothervessel operations: {obj_cost_mothervessels:.2f}")
        print(f"Total cost: {total_cost:.2f}")

        # Make plots of spare parts
        plot_parts_vars(vars, params, sets)

    print("--- %s seconds ---" % (end_time - start_time))