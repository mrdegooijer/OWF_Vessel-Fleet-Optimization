from utils.utils import unpack_sets, generate_downtime_cost, generate_availability_set

def create_parameters(data, sets, year):
    """
    Create all parameters for the model
    :return: params
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts,
     mother_vessels, ctvessels, locations) = unpack_sets(sets)

    # Set index for dataframes
    data['bases'].set_index('SET', inplace=True)
    data['vessels'].set_index('SET', inplace=True)
    data['capacity_base_vessels'].set_index(data['capacity_base_vessels'].columns[0], inplace=True)
    data['spare_parts'].set_index('SET', inplace=True)
    data['spare_parts_required'].set_index(data['spare_parts_required'].columns[0], inplace=True)
    data['holding_costs'].set_index(data['holding_costs'].columns[0], inplace=True)
    data['max_capacity'].set_index(data['max_capacity'].columns[0], inplace=True)
    data['reorder_level'].set_index(data['reorder_level'].columns[0], inplace=True)
    data['locations'].set_index('SET', inplace=True)

    # Cost Parameters
    cost_base_operation = data['bases']['cost']
    cost_vessel_purchase = data['vessels']['cost_purchase']
    cost_vessel_charter = {
        (v, p): data['vessels']['cost_charter_day'][v] * len(charter_dict[p-1])
        for v in vessels for p in charter_periods
    }
    cost_vessel_operation = data['vessels']['cost_operation']                      # Hourly cost?
    cost_technicians = data['general']['cost_technicians'].iloc[0]          # Hourly cost
    cost_downtime = generate_downtime_cost(periods, year)

    # Penalty Parameters (implemented as cost parameters)
    penalty_preventive_late = data['general']['penalty_cost_late'].iloc[0]                  # Cost per hour?
    penalty_not_performed = data['general']['penalty_cost_not_performed'].iloc[0]           # Cost per hour?

    # Vessel Parameters
    vessel_speed = data['vessels']['speed'] * 1.852  # Convert from knots to km/h
    transfer_time = data['vessels']['transfer_time']
    max_time_offshore = data['vessels']['max_time_offshore']
    max_vessels_available_charter = data['vessels']['available']                            # Remove?

    # Base Parameters
    distance_base_OWF = data['locations']['distance']
    technicians_available = data['locations']['technicians_available']

    # Capacity Parameters
    capacity_base_for_vessels = {
        (b, v): data['capacity_base_vessels'].at[b, v]
        for b in bases for v in vessels
    }
    capacity_vessel_for_technicians = data['vessels']['tech_cap']

    # Maintenance Task Parameters
    failure_rate = data['tasks']['failure_rate']
    time_to_perform_task = data['tasks']['active_time']
    technicians_required_task = data['tasks']['technicians']
    latest_period_to_perform_task = data['general']['latest_period'].iloc[0]            # Last period to perform a preventive task w/o penalty

    # Maintenance Bundle Parameters
    tasks_in_bundles = {}
    for k, task_combo in bundle_dict.items():
        for m in tasks:
            tasks_in_bundles[m, k] = task_combo.count(m)

    technicians_required_bundle = {
        k: sum(technicians_required_task[m] for m in bundle_dict[k])
        for k in bundles
    }

    # Weather Parameter
    weather_max_time_offshore = generate_availability_set(vessels, periods, year, data)

    # Spare Parts Parameters
    order_cost = data['spare_parts']['order_cost']
    lead_time = data['spare_parts']['lead_time']
    holding_cost = {
        (s, e): data['holding_costs'].at[s, e]
        for s in spare_parts for e in locations
    }
    parts_required = {
        (m, s): data['spare_parts_required'].at[s, m]
        for s in spare_parts for m in tasks
    }
    max_part_capacity = {
        (s, e): data['max_capacity'].at[s, e]
        for s in spare_parts for e in locations
    }
    reorder_level = {
        (s, e): data['reorder_level'].at[s, e]
        for s in spare_parts for e in locations
    }
    initial_inventory = data['locations']['initial_inventory']

    # Big-M parameter
    max_capacity = []
    for s in spare_parts:
        for e in locations:
            max_capacity.append(max_part_capacity[s, e])
    # big_M = 10000
    big_M = max(max_capacity)*100  # Use the maximum capacity as Big-M


    # Mother Vessel Parameters
    max_capacity_for_docking = data['locations']['max_capacity_for_docking']
    additional_time = data['vessels']['additional_time']                # additional hours for CTVs when docking at mother vessel
    tech_standby_cost = data['general']['tech_standby_cost'].iloc[0]  # Cost per hour for technicians on standby

    # Create the parameters dictionary
    params = {
        'cost_base_operation': cost_base_operation,
        'cost_vessel_purchase': cost_vessel_purchase,
        'cost_vessel_charter': cost_vessel_charter,
        'cost_vessel_operation': cost_vessel_operation,
        'cost_technicians': cost_technicians,
        'cost_downtime': cost_downtime,
        'penalty_preventive_late': penalty_preventive_late,
        'penalty_not_performed': penalty_not_performed,
        'vessel_speed': vessel_speed,
        'transfer_time': transfer_time,
        'max_time_offshore': max_time_offshore,
        'max_vessels_available_charter': max_vessels_available_charter,
        'distance_base_OWF': distance_base_OWF,
        'technicians_available': technicians_available,
        'capacity_base_for_vessels': capacity_base_for_vessels,
        'capacity_vessel_for_technicians': capacity_vessel_for_technicians,
        'failure_rate': failure_rate,
        'time_to_perform_task': time_to_perform_task,
        'technicians_required_task': technicians_required_task,
        'latest_period_to_perform_task': latest_period_to_perform_task,
        'tasks_in_bundles': tasks_in_bundles,
        'technicians_required_bundle': technicians_required_bundle,
        'weather_max_time_offshore': weather_max_time_offshore,
        'order_cost': order_cost,
        'lead_time': lead_time,
        'holding_cost': holding_cost,
        'parts_required': parts_required,
        'max_part_capacity': max_part_capacity,
        'reorder_level': reorder_level,
        'big_m': big_M,
        'max_capacity_for_docking': max_capacity_for_docking,
        'additional_time': additional_time,
        'tech_standby_cost': tech_standby_cost,
        'initial_inventory': initial_inventory
    }

    return params