from utils.utils import *


def create_sets(data):
    """
    Create the model sets
    """
    turbines = int(data['general']['turbines'].iloc[0])

    bases = data['bases']['SET'].tolist()
    tasks = data['tasks']['SET'].tolist()

    periods = list(range(1, int(data['general']['planning_horizon'].iloc[0]) + 1))
    charter_periods = list(periods[i:i+30] for i in range(0, len(periods), data['general']['charter_period'].iloc[0]))
    vessels = data['vessels']['SET'].tolist()
    vessel_task_compatibility = {m: [v for v in vessels if data['task_compatibility'].at[m, v] == 1] for m in tasks}

    data['tasks'].set_index('SET', inplace=True)
    prev_tasks = data['tasks'][data['tasks']['PRE/COR'] == 'PRE'].index.tolist()
    corr_tasks = data['tasks'][data['tasks']['PRE/COR'] == 'COR'].index.tolist()
    planned_prev_tasks = {m: turbines * int(data['tasks'].at[m, 'preventive_rate']) for m in prev_tasks}
    planned_corr_tasks = generate_corrective_maintenance_tasks(corr_tasks, periods, turbines, data['tasks'])
    bundles = generate_task_bundles(tasks)

    weather_availability_per_vessel = 0


    return bases, periods, charter_periods, vessels, vessel_task_compatibility, tasks, prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles, weather_availability_per_vessel