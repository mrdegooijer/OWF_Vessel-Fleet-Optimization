import pandas as pd
import matplotlib.pyplot as plt

def plot_parts_vars(vars, params, sets):
    # Plot spare parts decision variables
    periods = sets['periods']
    spare_parts = sets['spare_parts']
    bases = sets['bases']

    reorder_level = params['reorder_level']




    #Create plot for each spare part at each base
    for b in bases:
        for s in spare_parts:
            plt.title(f"Spare Part: {s} at Base: {b}")
            plt.xlabel("Period")
            plt.ylabel("Inventory Level")
            plt.xticks(periods)
            plt.grid()
            plt.plot(periods, [vars['inventory_level'][s, b, p].X for p in periods], label='Inventory Level')
            plt.plot(periods, [reorder_level[s, b] for p in periods], label='Reorder Level', linestyle='--')
            plt.legend()
            plt.show()
            plt.savefig(f"plots/spare_part_{s}_base_{b}.png")


