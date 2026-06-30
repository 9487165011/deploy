# Factory Reallocation & Shipping Optimization
# Nassau Candy Distributor (Simple Version)

# Factory capacities
capacity = {
    "Pennsylvania": 500,
    "New Jersey": 400,
    "Ohio": 300
}

# Customer demands
demand = {
    "New York": 200,
    "Boston": 150,
    "Chicago": 250
}

# Shipping cost per unit
cost = {
    "Pennsylvania": {"New York": 4, "Boston": 6, "Chicago": 8},
    "New Jersey": {"New York": 3, "Boston": 5, "Chicago": 7},
    "Ohio": {"New York": 6, "Boston": 7, "Chicago": 4}
}

total_cost = 0

print("Factory Shipping Recommendation\n")

for customer in demand:
    qty = demand[customer]

    # Sort factories by lowest shipping cost
    factories = sorted(cost, key=lambda x: cost[x][customer])

    for factory in factories:
        if capacity[factory] >= qty:
            capacity[factory] -= qty
            shipping = qty * cost[factory][customer]
            total_cost += shipping

            print(customer, "->", factory)
            print("Quantity:", qty)
            print("Shipping Cost: $", shipping)
            print()
            break

print("Remaining Factory Capacity:")
for factory in capacity:
    print(factory, ":", capacity[factory])

print("\nTotal Shipping Cost = $", total_cost)
