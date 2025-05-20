from utils.utils import unpack_sets

def create_parameters(data, sets):
    """
    Create all parameters for the model
    :return: params
    """
    # Unpack sets
    (
        bases, vessels, periods, charter_periods, tasks, vessel_task_compatibility,
        prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles,
        weather_availability_per_vessel
    ) = unpack_sets(sets)

    data['bases'].set_index('SET', inplace=True)
    data['vessels'].set_index('SET', inplace=True)
    data['capacity_base_vessels'].set_index(data['capacity_base_vessels'].columns[0], inplace=True)

    # Cost Parameters
    cost_base_operation = data['bases']['cost']
    cost_vessel_purchase = data['vessels']['cost_purchase']
    cost_vessel_charter = data['vessels']['cost_charter_day']

    # Capacity Parameters
    capacity_base_vessels = {
        (b, v): data['capacity_base_vessels'].at[b, v]
        for b in bases for v in vessels
    }

    params = {
        'cost_base_operation': cost_base_operation,
        'cost_vessel_purchase': cost_vessel_purchase,
        'cost_vessel_charter': cost_vessel_charter,

        'capacity_base_vessels': capacity_base_vessels,
    }


    return params