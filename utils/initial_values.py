

def get_inventory_level(s, e, p, inventory_level, initial_inventory):
    if p == 0:
        return int(initial_inventory[e])
    else:
        return inventory_level[s, e, p]

def get_inventory_level_base(s, e, p, inventory_level, initial_inventory, base_use):
    if p == 0:
        return initial_inventory[e] * base_use[e]
    else:
        return inventory_level[s, e, p]

def get_order_quantity(s, e, p, order_quantity):
    if p <= 0:
        return 0
    else:
        return order_quantity[s, e, p]

def get_periods_late(p, m, periods_late):
    if p == 0:
        return 0
    else:
        return periods_late[p, m]