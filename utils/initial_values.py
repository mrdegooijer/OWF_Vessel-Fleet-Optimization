


def get_inventory_level(s, b, p, inventory_level):
    if p == 0:
        return 0
    else:
        return inventory_level[s, b, p]

def get_order_quantity(s, b, p, order_quantity):
    if p <= 0:
        return 0
    else:
        return order_quantity[s, b, p]