from gurobipy import *

def solve_return_obj(model):
    """
    This function quickly finds objective value of the current solution and returns it.
    If infeasible, it returns 'inf'.
    """
    model.optimize()
    if model.Status in (GRB.INFEASIBLE, GRB.INF_OR_UNBD):
        print("Model is infeasible -- computing IIS …")
        model.computeIIS()  # asks Gurobi for a minimal conflicting set
        model.write("infeasible.ilp")  # or .lp / .json / .mps
        print("Wrote infeasible.ilp  (open it in a text editor or IDE)")


    if model.status == GRB.OPTIMAL:
        return model.ObjVal
    return float("inf")

def flatten_decision_vars(vars_dict):
    """
    Return an ordered list with every perchased vessel, chartered vessel and base used variable.
    """
    ordered = []
    ordered.extend(vars_dict["purchased_vessel"].values())
    ordered.extend(vars_dict["chartered_vessel"].values())
    ordered.extend(vars_dict["base_used"].values())

    return ordered
