import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder

# ==========================================
# STEP 1: GENERATE MOCK HISTORICAL ORDER DATA
# ==========================================
# Simulating the Nassau Candy order dataset parameters (15 products, 5 factories)
np.random.seed(42)
n_orders = 1000

products = [f"Product_{i}" for i in range(1, 16)]
factories = ["Factory_A", "Factory_B", "Factory_C", "Factory_D", "The_Other_Factory"]
shipping_modes = ["Standard Class", "First Class", "Same Day"]

# Create historical baseline where some assignments are inherently unoptimized
mock_data = {
    "Product": np.random.choice(products, n_orders),
    "Current_Factory": np.random.choice(factories, n_orders),
    "Shipping_Mode": np.random.choice(shipping_modes, n_orders),
    "Gross_Profit": np.random.uniform(5, 50, n_orders),
    "Sales": np.random.uniform(50, 200, n_orders)
}

df = pd.DataFrame(mock_data)

# Feature engineering: calculate historical lead time and profit margins
# Note: Operational findings show premium shipping modes sometimes increase dispatch bottlenecks
df["Profit_Margin"] = (df["Gross_Profit"] / df["Sales"]) * 100
df["Lead_Time"] = np.random.randint(3, 15, n_orders)

# Inject controlled inefficiency behavior patterns for the ML model to learn
# e.g., Product_1 currently built at Factory_A takes much longer than if it were built at Factory_B
df.loc[(df["Product"] == "Product_1") & (df["Current_Factory"] == "Factory_A"), "Lead_Time"] += 6
df.loc[(df["Product"] == "Product_1") & (df["Current_Factory"] == "Factory_B"), "Lead_Time"] -= 2

print("--- Historical Order Sample Data ---")
print(df[["Product", "Current_Factory", "Shipping_Mode", "Profit_Margin", "Lead_Time"]].head(), "\n")


# ==========================================
# STEP 2: TRAIN PREDICTIVE MODEL
# ==========================================
# Encode categorical features for the Machine Learning algorithm
le_product = LabelEncoder()
le_factory = LabelEncoder()
le_shipping = LabelEncoder()

df_ml = df.copy()
df_ml["Product_Enc"] = le_product.fit_transform(df_ml["Product"])
df_ml["Factory_Enc"] = le_factory.fit_transform(df_ml["Current_Factory"])
df_ml["Shipping_Enc"] = le_shipping.fit_transform(df_ml["Shipping_Mode"])

# Features (X) and Target (y)
X = df_ml[["Product_Enc", "Factory_Enc", "Shipping_Enc", "Profit_Margin"]]
y = df_ml["Lead_Time"]

# Train Gradient Boosting Regressor (identified as the optimal model for this pipeline)
model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X, y)


# ==========================================
# STEP 3: SCENARIO SIMULATION ENGINE
# ==========================================
def simulate_reallocation(target_product, current_factory):
    """
    Simulates sending a product to all possible alternate factories 
    to evaluate predicted lead times and profit metrics.
    """
    recommendations = []
    
    # Isolate product historical baselines
    product_base = df[df["Product"] == target_product]
    avg_margin = product_base["Profit_Margin"].mean()
    
    # Baseline performance
    baseline_lead = product_base[product_base["Current_Factory"] == current_factory]["Lead_Time"].mean()
    
    if pd.isna(baseline_lead):
        return pd.DataFrame() # Skip if no baseline historical data exists

    # Test all possible factory options
    for factory in factories:
        if factory == current_factory:
            continue
            
        # Hardcoded constraints based on real case findings: 
        # "The Other Factory" has structural margin constraints for specific items
        simulated_margin = avg_margin
        if factory == "The_Other_Factory":
            simulated_margin = 10.49 
            
        # Prepare vector input payload for trained model matrix evaluation
        sim_input = pd.DataFrame({
            "Product_Enc": [le_product.transform([target_product])[0]],
            "Factory_Enc": [le_factory.transform([factory])[0]],
            "Shipping_Enc": [le_shipping.transform(["Standard Class"])[0]], # Target optimization baseline
            "Profit_Margin": [simulated_margin]
        })
        
        # Predict Lead Time using the ML model
        predicted_lead = model.predict(sim_input)[0]
        lead_time_reduction = baseline_lead - predicted_lead
        pct_reduction = (lead_time_reduction / baseline_lead) * 100
        margin_change = simulated_margin - avg_margin
        
        # Scoring function logic balancing operational speed vs commercial impact
        # Score = (Lead Time % Improvement * 1.0) + (Margin Change % * 0.5)
        optimization_score = pct_reduction + (margin_change * 0.5)
        
        recommendations.append({
            "Product": target_product,
            "Current_Factory": current_factory,
            "Proposed_Factory": factory,
            "Baseline_Lead_Time": round(baseline_lead, 2),
            "Predicted_Lead_Time": round(predicted_lead, 2),
            "Lead_Time_Improvement_%": round(pct_reduction, 2),
            "Estimated_Margin_%": round(simulated_margin, 2),
            "Optimization_Score": round(optimization_score, 2)
        })
        
    return pd.DataFrame(recommendations)


# ==========================================
# STEP 4: GENERATE RECOMMENDATION SYSTEM REPORT
# ==========================================
# Run simulation across product allocation bottlenecks (Example: Product_1 at Factory_A)
all_recommendations = simulate_reallocation(target_product="Product_1", current_factory="Factory_A")

# Rank reallocations based on the optimization metrics engine 
all_recommendations = all_recommendations.sort_values(by="Optimization_Score", ascending=False).reset_index(drop=True)

print("--- REALLOCATION RECOMMENDATIONS FOR PRODUCT_1 ---")
print(all_recommendations.to_string())
