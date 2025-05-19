import pandas as pd
import numpy as np
import itertools

def load_input_data(file_path):
    """
    Load input data from a file

    :param file_path: Path to the input data file
    :return: DataFrame with input data
    """

    data = pd.read_excel(file_path, sheet_name=None)
    data['task_compatibility'] = pd.read_excel(file_path, sheet_name='task_compatibility', index_col=0)
    # data['tasks'] = pd.read_excel(file_path, sheet_name='tasks', index_col=0)
    return data


def generate_corrective_maintenance_tasks(corr_tasks, periods, turbines, input_tasks):

    daily_failures = pd.DataFrame(index=corr_tasks, columns=periods)
    failures = {}
    for m in corr_tasks:
        for p in periods:
            failures[p] = np.random.uniform(size=turbines)  # uniform distribution of the failures
            daily_failures.loc[m, p] = sum(x < input_tasks.loc[m, 'failure_rate'] / len(periods) for x in failures[p])

    return daily_failures


def generate_task_bundles(tasks):
    bundle = []
    for i in range(4):
        bundle.append(list(itertools.product(tasks, repeat=i + 1)))
    bundles = [j for sub in bundle for j in sub]
    return bundles