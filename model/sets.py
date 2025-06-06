from utils.utils import *


def create_sets(data):
    """
    Create the model sets
    """
    turbines = int(data['general']['turbines'].iloc[0])

    sets={}

    bases = data['bases']['SET'].tolist()
    tasks = data['tasks']['SET'].tolist()

    periods = list(range(1, int(data['general']['planning_horizon'].iloc[0]) + 1))
    charter_dict = list(periods[i:i+30] for i in range(0, len(periods), data['general']['charter_period'].iloc[0]))             #Dict with all the periods p ordered into the charter periods
    charter_periods = list(range(1, int(data['general']['planning_horizon'].iloc[0] / data['general']['charter_period'].iloc[0]) + 1))

    vessels = data['vessels']['SET'].tolist()
    vessel_task_compatibility = {m: [v for v in vessels if data['task_compatibility'].at[m, v] == 1] for m in tasks}

    data['tasks'].set_index('SET', inplace=True)
    prev_tasks = data['tasks'][data['tasks']['PRE/COR'] == 'PRE'].index.tolist()
    corr_tasks = data['tasks'][data['tasks']['PRE/COR'] == 'COR'].index.tolist()
    planned_prev_tasks = {m: turbines * int(data['tasks'].at[m, 'preventive_rate']) for m in prev_tasks}
    planned_corr_tasks = generate_corrective_maintenance_tasks(corr_tasks, periods, turbines, data['tasks'])
    bundle_dict = generate_task_bundles(tasks)      # This is a dict with all bundles as values and 'bundle_ids' as keys
    bundles = list(bundle_dict.keys())              # This is a list of all bundle_ids

    # Extension sets
    spare_parts = data['spare_parts']['SET'].tolist()
    mother_vessels = data['vessels'].loc[data['vessels']['MV'] == 1, 'SET'].tolist()
    locations = data['locations']['SET'].tolist()
      #Create the sets dictionary
    sets['bases'] = bases
    sets['tasks'] = tasks
    sets['periods'] = periods
    sets['charter_dict'] = charter_dict
    sets['charter_periods'] = charter_periods
    sets['vessels'] = vessels
    sets['vessel_task_compatibility'] = vessel_task_compatibility
    sets['prev_tasks'] = prev_tasks
    sets['corr_tasks'] = corr_tasks
    sets['planned_prev_tasks'] = planned_prev_tasks
    sets['planned_corr_tasks'] = planned_corr_tasks
    sets['bundle_dict'] = bundle_dict
    sets['bundles'] = bundles
    sets['spare_parts'] = spare_parts
    sets['mother_vessels'] = mother_vessels
    sets['locations'] = locations

    return sets