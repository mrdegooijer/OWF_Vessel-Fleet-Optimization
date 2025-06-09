from gurobipy import *
from utils.utils import *
from utils.solution_utils import *
from utils.initial_values import *
import time

def GRASP(model, sets, params, vars, start_time):
    """
    Developed by: Ivana Versluijs, 2023
    """
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts,
     mother_vessels, ctvessels, locations) = unpack_sets(sets)

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

    (base_use, purchased_vessels, chartered_vessels, task_performed,
     bundle_performed, tasks_late, tasks_not_performed,
     periods_late, hours_spent, inventory_level, order_quantity,
     order_trigger, mv_offshore, lambda_P, lambda_CH, mu_P, mu_CH) = unpack_variables(vars)

    # ========== Greedy Construction Algorithm ==========
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
            obj_value_pv[v][i] = float('inf')
            purchased_vessels[b_opt, v].ub = i
            purchased_vessels[b_opt, v].lb = i
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
                model.optimize()
                obj_value_cv[v][p][i] = model.objVal
            chartered_vessels[b_opt,v,p].ub = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)
            chartered_vessels[b_opt,v,p].lb = min(obj_value_cv[v][p], key=obj_value_cv[v][p].get)

    # --- 5. --- Optimize for initial solution (starting point)
    model.optimize()

    # print('Objective value:', model.objVal)
    # print('Base use:', {b: base_use[b].X for b in bases})
    # print('Purchased vessels:', {b: {v: purchased_vessels[b, v].X for v in vessels} for b in bases})
    # print('Chartered vessels:',
    #       {b: {v: {p: chartered_vessels[b, v, p].X for p in charter_periods} for v in vessels} for b in bases})

    # ========== TABU SEARCH ==========
    # --- 6. --- Create solution vector
    iteration = 0                   # initial solution
    objective = {}                  # list of the minimum objective values
    solution = {}                   # list of solution, consisting of number of purchased vessels, chartered vessels and bases used
    it_objectives = {}              # objective values for each neighbor at each iteration
    tabu = []                       # list of tabu moves
    solution[iteration] = []        # solution for each neighbor at each iteration

    # Purchased vessels
    for b in bases:
        for v in vessels:
            solution[iteration].append(purchased_vessels[b, v].X)

    # Chartered vessels
    for b in bases:
        for v in vessels:
            for p in charter_periods:
                solution[iteration].append(chartered_vessels[b, v, p].X)

    # Base use
    for b in bases:
        solution[iteration].append(base_use[b].X)

    objective[iteration] = model.objVal
    best_objective_so_far = []
    it_objectives[iteration] = [model.objVal]

    iteration = 1           # start of the iterations
    max_it = 15             # maximum number of iterations
    while iteration < max_it and time.time() - start_time < 3600:       # stopping criteria
        neighbours = []                  # list of neighbours of the current solution
        sol = solution[iteration-1]     # current solution
        it_move = []                    # move that results in the neighbor

        # neighbours for purchased vessels
        for b in bases:
            for v in vessels:
                i = bases.index(b)*len(vessels) + vessels.index(v)
                # add a purchased vessel
                nb = sol.copy()
                if nb[i] < capacity_base_for_vessels[b, v] and 'add '+str(b)+str(v) not in tabu:
                    nb[i] += 1
                    neighbours.append(nb.copy())
                    it_move.append('remove '+str(b)+str(v))

                if sol[i] > 0.5:
                    # remove a purchased vessel
                    if 'remove ' + str(b) + str(v) not in tabu:
                        nb = sol.copy()
                        nb[i] -= 1
                        neighbours.append(nb.copy())
                        it_move.append('add ' + str(b) + str(v))

                    nb = sol.copy()
                    for j in range(len(vessels)):
                        if j != i and nb[j] < capacity_base_for_vessels[b, vessels[j]] and 'switch '+str(b)+vessels[j]+str(v) not in tabu:
                            # change type of a purchased vessel
                            nb[i] -= 1
                            nb[j] += 1
                            neighbours.append(nb.copy())
                            it_move.append('switch '+str(b)+str(v)+ vessels[j])

                    nb = sol.copy()
                    for k in range(len(bases)):
                        l = (k-bases.index(b))*len(purchased_vessels) + i
                        if k != bases.index(b) and nb[l] < capacity_base_for_vessels[b, vessels[l-(k*len(purchased_vessels))]] and 'switch '+bases[k]+str(b)+str(v) not in tabu:
                            # change base of a purchased vessel
                            nb[i] -= 1
                            nb[l] += 1
                            neighbours.append(nb.copy())
                            it_move.append('switch '+str(b)+bases[k]+str(v))
        print("Purchased vessels neighbours:", len(neighbours))
        # neighbours for chartered vessels
        for b in bases:
            for v in vessels:
                for p in charter_periods:
                    i = len(purchased_vessels) + bases.index(b)*(len(vessels)+len(charter_periods)) + vessels.index(v)*len(charter_periods) + p
                    # add a chartered vessel
                    nb = sol.copy()
                    if nb[i] < capacity_base_for_vessels[b, v] and 'add '+str(b)+str(v)+str(p) not in tabu:
                        nb[i] += 1
                        neighbours.append(nb.copy())
                        it_move.append('remove '+str(b)+str(v)+str(p))

                    if sol[i]> 0.5:
                        # remove a chartered vessel
                        if 'remove ' + str(b) + str(v) + str(p) not in tabu:
                            nb = sol.copy()
                            nb[i] -= 1
                            neighbours.append(nb.copy())
                            it_move.append('add ' + str(b) + str(v) + str(p))

                        # change type of a chartered vessel in the same period
                        nb = sol.copy()
                        for j in range(len(vessels)):
                            k = (j-vessels.index(v))*len(charter_periods) + i
                            if j != vessels.index(v) and nb[k] < capacity_base_for_vessels[b, vessels[j]] and 'switch '+str(b)+vessels[j]+str(v)+str(p) not in tabu:
                                nb[i] -= 1
                                nb[j] += 1
                                neighbours.append(nb.copy())
                                it_move.append('switch '+str(b)+str(v)+vessels[j]+str(p))

                        # change the period of a chartered vessel
                        nb = sol.copy()
                        for l in charter_periods:
                            m = i + (l-p)
                            if l != p and nb[m] < capacity_base_for_vessels[b, v] and 'switch '+str(b)+str(v)+str(l)+str(p) not in tabu:
                                nb[i] -= 1
                                nb[m] += 1
                                neighbours.append(nb.copy())
                                it_move.append('switch '+str(b)+str(v)+str(p)+str(l))

                        # change base of a chartered vessel
                        nb = sol.copy()
                        for m in range(len(bases)):
                            n = (m-bases.index(b))*len(vessels)*len(charter_periods) + i
                            if m != bases.index(b) and nb[n] < capacity_base_for_vessels[bases[m], v] and 'switch '+bases[m]+str(b)+str(v)+str(p) not in tabu:
                                nb[i] -= 1
                                nb[n] += 1
                                neighbours.append(nb.copy())
                                it_move.append('switch '+str(b)+bases[m]+str(v)+str(p))
        print("Chartered vessels neighbours:", len(neighbours))
        # neighbours for bases
        for b in bases:
            i = len(purchased_vessels) + len(chartered_vessels) + bases.index(b)
            j = bases.index(b)*len(vessels)
            k = len(bases)*len(vessels) + bases.index(b)*len(vessels)*len(charter_periods)

            # remove base + vessels
            nb = sol.copy()
            if nb[i] > 0.5:
                nb[i] = 0
                for l in range(j, j + len(vessels)):
                    nb[l] = 0
                for m in range(k, k + len(vessels) * len(charter_periods)):
                    nb[m] = 0
                neighbours.append(nb.copy())
                it_move.append('remove ' + str(b))

            # replace base and vessels with another base
            nb = sol.copy()
            if nb[i] > 0.5:
                for l in range(len(bases)):
                    if l != bases.index(b) and nb[len(purchased_vessels) + len(chartered_vessels) + l] < 0.5 and 'switch '+bases[l]+str(b) not in tabu:
                        for x in range(l*len(vessels), (l+1)*len(vessels)):
                            nb[x] = nb[x - (l - bases.index(b)) * len(vessels)]
                            nb[x - (l - bases.index(b)) * len(vessels)] = 0
                        m = len(bases)*len(vessels) + l*len(vessels)*len(charter_periods)
                        for y in range(m, m + len(vessels)*len(charter_periods)):
                            nb[y] = nb[y - (l - bases.index(b)) * (len(vessels) * len(charter_periods))]
                            nb[y - (l - bases.index(b)) * (len(vessels) * len(charter_periods))] = 0
                        nb[len(purchased_vessels) + len(chartered_vessels) + l] = 1
                        nb[i] = 0
                        neighbours.append(nb.copy())
                        it_move.append('switch '+str(b)+bases[l])
        print("Bases neighbours:", len(neighbours))
        # Delete neighbours that have already been considered
        existing = []
        for o in range(len(neighbours)):
            for i in solution:
                if neighbours[o] == solution[i]:
                    existing.append(neighbours[o])
        for i in range(len(existing)):
            if existing[i] in neighbours:
                neighbours.remove(existing[i])
        print('total neighbours:', len(neighbours))

        # Calculate objective values for neighbours
        it_objectives[iteration] = []
        for x in neighbours:
            for b in bases:
                l = len(purchased_vessels) + len(chartered_vessels) + bases.index(b)
                base_use[b].lb = x[l]
                base_use[b].lb = x[l]       #MISTAKE?
                for v in vessels:
                    i = bases.index(b)*len(vessels) + vessels.index(v)
                    purchased_vessels[b, v].lb = x[i]
                    purchased_vessels[b, v].ub = x[i]
                    for p in charter_periods:
                        j = bases.index(b)*len(vessels)*len(charter_periods) + vessels.index(v)*len(charter_periods) + p + len(purchased_vessels)
                        chartered_vessels[b, v, p].lb = x[j]
                        chartered_vessels[b, v, p].ub = x[j]
            model.optimize()
            if model.status == GRB.Status.OPTIMAL:
                it_objectives[iteration].append(model.objVal)
            else:
                it_objectives[iteration].append(float('inf'))

        solution[iteration] = neighbours[it_objectives[iteration].index(min(it_objectives[iteration]))]
        objective[iteration] = min(it_objectives[iteration])
        best_objective_so_far.append(min(objective[o] for o in range(iteration)))

        tabu_addition = it_move[it_objectives[iteration].index(min(it_objectives[iteration]))]
        tabu.append(tabu_addition)

        # stopping criteria if no improvements in objective value have been found
        if iteration > 3:
            if objective[iteration-1] > min(best_objective_so_far) and objective[iteration-2] > min(best_objective_so_far) and objective[iteration] > min(best_objective_so_far):
                iteration += max_it

        iteration += 1

    final_objective = min(objective[i] for i in range(len(objective)))  # the resulting objective value
    final_solution = solution[min(objective, key=objective.get)]  # the resulting solution corresponding to the objective value

    # --- 7. --- Set the final solution and optimize the model
    for b in bases:
        l = len(purchased_vessels) + len(chartered_vessels) + bases.index(b)
        base_use[b].lb = final_solution[l]
        base_use[b].lb = final_solution[l]
        for v in vessels:
            i = bases.index(b)*len(vessels) + vessels.index(v)
            purchased_vessels[b, v].lb = final_solution[i]
            purchased_vessels[b, v].ub = final_solution[i]
            for p in charter_periods:
                j = bases.index(b)*len(vessels)*len(charter_periods) + vessels.index(v) * len(charter_periods) + p-1 + len(purchased_vessels)
                chartered_vessels[b, v, p].lb = final_solution[j]
                chartered_vessels[b, v, p].ub = final_solution[j]

    model.optimize()
