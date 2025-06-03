from utils.utils import unpack_sets, generate_downtime_cost, generate_availability_set

def create_parameters(data, sets, year):
    """
    Create all parameters for the model
    :return: params
    """
    # Unpack sets
    (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
     prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles) = unpack_sets(sets)

    # Set index for dataframes
    data['bases'].set_index('SET', inplace=True)
    data['vessels'].set_index('SET', inplace=True)
    data['capacity_base_vessels'].set_index(data['capacity_base_vessels'].columns[0], inplace=True)


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
    distance_base_OWF = data['bases']['distance']
    technicians_available = data['bases']['technicians_available']

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
    }

    return params