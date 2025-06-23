import matplotlib.pyplot as plt
from utils.initial_values import *

def plot_parts_vars(vars, params, sets):
    # Plot spare parts decision variables
    periods = sets['periods']
    periods_0 = [0] + list(periods)
    spare_parts = sets['spare_parts']
    locations = sets['locations']
    bases = sets['bases']
    mother_vessels = sets['mother_vessels']
    mv_offshore = vars['mv_offshore']

    reorder_level = params['reorder_level']
    max_capacity = params['max_part_capacity']

    # Create plot for each spare part at each base
    for e in locations:
        for s in spare_parts:
            plt.figure(figsize=(7.68, 5.76))
            plt.title(f"Spare Part: {s} at Locations: {e}")
            plt.xlabel("Period")
            plt.ylabel("Inventory Level")
            plt.xlim(0, 90)
            plt.ylim(0, int(max_capacity[s, e]) + 10)
            plt.xticks([p - 1 for p in periods[::15]] + [90])
            plt.grid()
            plt.plot(periods, [vars['inventory_level'][s, e, p].X for p in periods], label='Inventory Level')
            order_quantities = [vars['order_quantity'][s, e, p].X for p in periods]
            plt.vlines(periods, ymin=0, ymax=order_quantities, label='Order Quantity', color='green',
                       linestyles='-')
            plt.plot(periods, [reorder_level[s, e] for p in periods], label='Reorder Level', linestyle=':', color='red')
            plt.plot(periods, [max_capacity[s, e] for p in periods], label='Max Capacity', linestyle=':',
                     color='orange')
            plt.legend(loc='upper right')
            plt.savefig(f"plots/spare_part_{s}_locations_{e}.png", bbox_inches='tight')
            plt.close()