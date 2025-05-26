import pandas as pd
import matplotlib.pyplot as plt

def plot_parts_vars(vars, sets, data):
    inv = vars['inventory_level']
    order_q = vars['order_quantity']
    order_trigger = vars['order_trigger']

    spare_parts = sets['spare_parts']
    bases = sets['bases']
    periods = sets['periods']

    # data['reorder_level'].set_index(data['reorder_level'].columns[0], inplace=True)

    for s in spare_parts:
        for b in bases:
            inv_series = [inv[s, b, p].X for p in periods]
            order_series = [order_q[s, b, p] for p in periods]
            trig_series = [order_trigger[s, b, p].X for p in periods]

            df = pd.DataFrame(
                {
                    'Inventory level': inv_series,
                    'Order quantity': order_series,
                    'Order trigger': trig_series,
                },
                index=periods
            )

            # Plot the reorder level as a horizontal line
            reorder_level = data['reorder_level'].loc[(s, b)]
            df['Reorder level'] = reorder_level
            df.plot(
                marker='o',
                title=f"Spare Part: {s} at Base: {b}",
                ylabel='Units / binary',
                xlabel='Period'
            )

            ax = df.plot(
                marker='o',
                title=f"{s} – {b}",
                ylabel='Units / binary',
                xlabel='Period'
            )
    ax.legend(loc='best')
    plt.tight_layout()
    plt.show()

