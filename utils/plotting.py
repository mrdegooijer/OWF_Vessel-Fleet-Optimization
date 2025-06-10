import matplotlib.pyplot as plt
from utils.initial_values import *

def plot_parts_vars(vars, params, sets):
    # Plot spare parts decision variables
    periods = sets['periods']
    periods_0 = [0]+list(periods)
    spare_parts = sets['spare_parts']
    locations = sets['locations']
    bases = sets['bases']
    mother_vessels = sets['mother_vessels']
    mv_offshore = vars['mv_offshore']

    reorder_level = params['reorder_level']

    # Create plot for each spare part at each base
    for e in bases:
        for s in spare_parts:
            plt.title(f"Spare Part: {s} at Locations: {e}")
            plt.xlabel("Period")
            plt.ylabel("Inventory Level")
            plt.xticks(periods)
            plt.grid()
            plt.plot(periods_0, [params['initial_inventory'][e]] + [vars['inventory_level'][s, e, p].X for p in periods], label='Inventory Level')
            plt.plot(periods, [reorder_level[s, e] for p in periods], label='Reorder Level', linestyle='--')
            plt.legend()
            plt.savefig(f"plots/spare_part_{s}_locations_{e}.png")
            plt.close()

    for e in mother_vessels:
        for s in spare_parts:
            plt.title(f"Spare Part: {s} at Locations: {e}")
            plt.xlabel("Period")
            plt.ylabel("Inventory Level")
            plt.xticks(periods)
            plt.grid()
            plt.plot(periods, [vars['inventory_level'][s, e, p].X for p in periods], label='Inventory Level')
            plt.plot(periods, [reorder_level[s, e] for p in periods], label='Reorder Level', linestyle='--')
            plt.legend()
            for p in periods:
                if mv_offshore[e, p].X > 0:
                    # shade the period gray
                    plt.axvspan(p, p + 1, color='gray', alpha=0.5)
            plt.savefig(f"plots/spare_part_{s}_locations_{e}.png")
            plt.close()
