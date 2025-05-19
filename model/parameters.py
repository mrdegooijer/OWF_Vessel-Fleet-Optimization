
def create_parameters(data):
    """
    Create all parameters for the model
    :return:
    """
    data['bases'].set_index('SET', inplace=True)
    data['vessels'].set_index('SET', inplace=True)

    #Cost Parameters
    cost_base_operation = data['bases']['cost']
    cost_vessel_purchase = data['vessels']['cost_purchase']
    cost_vessel_charter = data['vessels']['cost_charter_day']

    return cost_base_operation, cost_vessel_purchase, cost_vessel_charter