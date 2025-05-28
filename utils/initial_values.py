

def get_inventory_level(s, b, p, inventory_level, max_part_capacity):
    if p == 0:
        return int(max_part_capacity[s, b])
    else:
        return inventory_level[s, b, p]

def get_order_quantity(s, b, p, order_quantity):
    if p <= 0:
        return 0
    else:
        return order_quantity[s, b, p]

def get_periods_late(p, m, periods_late):
    if p == 0:
        return 0
    else:
        return periods_late[p, m]