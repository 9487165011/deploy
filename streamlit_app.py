

from pulp import *

# -------------------------------
# FACTORY DATA
# -------------------------------

factories = ["Pennsylvania", "New Jersey", "Ohio"]

capacity = {
    "Pennsylvania": 600,
    "New Jersey": 500,
    "Ohio": 450
}

# -------------------------------
# CUSTOMER DEMANDS
# -------------------------------

customers = ["New York", "Boston", "Chicago", "Atlanta"]

demand = {
    "New York": 300,
    "Boston": 250,
    "Chicago": 400,
    "Atlanta": 350
}

# -------------------------------
# SHIPPING COST ($ per unit)
# -------------------------------

shipping_cost = {

("Pennsylvania","New York"):4,
("Pennsylvania","Boston"):6,
("Pennsylvania","Chicago"):8,
("Pennsylvania","Atlanta"):10,

("New Jersey","New York"):3,
("New Jersey","Boston"):5,
("New Jersey","Chicago"):9,
("New Jersey","Atlanta"):11,

("Ohio","New York"):8,
("Ohio","Boston"):9,
("Ohio","Chicago"):4,
("Ohio","Atlanta"):5

}

# -------------------------------
# Create Optimization Model
# -------------------------------

model = LpProblem("Shipping_Optimization", LpMinimize)

# Decision Variables

shipment = LpVariable.dicts(
    "Ship",
    (factories, customers),
    lowBound=0,
    cat='Integer'
)

# -------------------------------
# Objective Function
# -------------------------------

model += lpSum(
    shipping_cost[(f,c)] * shipment[f][c]
    for f in factories
    for c in customers
)

# -------------------------------
# Factory Capacity Constraints
# -------------------------------

for f in factories:
    model += lpSum(
        shipment[f][c]
        for c in customers
    ) <= capacity[f]

# -------------------------------
# Customer Demand Constraints
# -------------------------------

for c in customers:
    model += lpSum(
        shipment[f][c]
        for f in factories
    ) == demand[c]

# -------------------------------
# Solve
# -------------------------------

model.solve()

# -------------------------------
# Results
# -------------------------------

print("="*60)
print("Factory Reallocation & Shipping Recommendation")
print("="*60)

print("\nStatus:", LpStatus[model.status])

print("\nOptimal Shipping Plan\n")

for f in factories:
    for c in customers:
        qty = shipment[f][c].varValue
        if qty > 0:
            print(f"{f:15} --> {c:10} : {qty:.0f} units")

print("\nFactory Utilization")

for f in factories:
    used = sum(shipment[f][c].varValue for c in customers)
    print(f"{f:15}: {used:.0f}/{capacity[f]} units")

print("\nMinimum Total Shipping Cost = $", value(model.objective))
