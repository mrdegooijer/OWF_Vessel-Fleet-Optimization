from utils.utils import *


def create_sets(input):
    """
    Create the model sets
    """
    turbines = int(input['general']['turbines'].iloc[0])

    bases = input['bases']['SET'].tolist()
    tasks = input['tasks']['SET'].tolist()

    periods = list(range(1, int(input['general']['planning_horizon'].iloc[0]) + 1))
    charter_periods = list(periods[i:i+30] for i in range(0, len(periods), input['general']['charter_period'].iloc[0]))
    vessels = input['vessels']['SET'].tolist()
    vessel_task_compatibility = {m: [v for v in vessels if input['task_compatibility'].at[m, v] == 1] for m in tasks}

    input['tasks'].set_index('SET', inplace=True)
    prev_tasks = input['tasks'][input['tasks']['PRE/COR'] == 'PRE'].index.tolist()
    corr_tasks = input['tasks'][input['tasks']['PRE/COR'] == 'COR'].index.tolist()
    planned_prev_tasks = {m: turbines * int(input['tasks'].at[m, 'preventive_rate']) for m in prev_tasks}
    planned_corr_tasks = generate_corrective_maintenance_tasks(corr_tasks, periods, turbines, input['tasks'])
    bundles = generate_task_bundles(tasks)

    weather_availability_per_vessel = 0


    return bases, periods, charter_periods, vessels, vessel_task_compatibility, tasks, prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles, weather_availability_per_vessel