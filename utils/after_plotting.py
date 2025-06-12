import matplotlib.pyplot as plt

#Read the .sol file and plot the results
solution = {}
with open("../solution_dG25_ME-Verification_Case.sol", "r") as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 2:
                var, val = parts[0], float(parts[1])
                solution[var] = val

order_quantity = {k: v for k, v in solution.items() if k.startswith('order_quantity')}
#plot order_quantity with periods on the x-axis and order quantity on the y-axis
periods = list(range(1, 91))  # Assuming periods are from 1 to 90
order_quantities = [order_quantity.get(f'order_quantity[{s},{e},{p}]', 0) for s in order_quantity for e in order_quantity for p in periods]


