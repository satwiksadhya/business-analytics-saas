import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def validate_and_clean_csv(file_path):
    
    required_columns = [
        "date",
        "product_name",
        "quantity_sold",
        "current_stock"
    ]
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return None, f"Error reading file: {e}"
    
    # Check required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return None, f"Missing required columns: {missing_cols}"
    
    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isnull().any():
        return None, "Invalid date format detected."
    
    # Convert numeric columns
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
    df["current_stock"] = pd.to_numeric(df["current_stock"], errors="coerce")
    
    if df[["quantity_sold", "current_stock"]].isnull().any().any():
        return None, "Invalid numeric values detected."
    
    # Minimum data check per product
    for product in df["product_name"].unique():
        if len(df[df["product_name"] == product]) < 45:
            return None, f"Not enough data for product: {product} (Minimum 45 days required)"
    
    return df, "File validated successfully"

def run_forecasting_pipeline(df):
    
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    
    results = {}
    
    products = df["product_name"].unique()
    
    for product in products:
        
        product_df = df[df["product_name"] == product].copy()
        
        # Feature engineering
        product_df["time_index"] = range(len(product_df))
        product_df["day_of_week"] = product_df["date"].dt.dayofweek
        product_df["month"] = product_df["date"].dt.month
        
        product_df["lag_1"] = product_df["quantity_sold"].shift(1)
        product_df["lag_2"] = product_df["quantity_sold"].shift(2)
        product_df["lag_3"] = product_df["quantity_sold"].shift(3)
        product_df["lag_7"] = product_df["quantity_sold"].shift(7)
        product_df["lag_14"] = product_df["quantity_sold"].shift(14)
        product_df["lag_30"] = product_df["quantity_sold"].shift(30)
        
        product_df = product_df.dropna()
        
        features = [
            "lag_1", "lag_2", "lag_3",
            "lag_7", "lag_14", "lag_30",
            "day_of_week", "month",
            "time_index"
        ]
        
        X = product_df[features]
        y = product_df["quantity_sold"]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Inventory logic
        avg_demand = product_df["quantity_sold"].mean()
        lead_time = 7
        safety_stock = 0.2 * avg_demand
        
        reorder_point = (avg_demand * lead_time) + safety_stock
        current_stock = int(product_df["current_stock"].iloc[-1])

        
        if current_stock < reorder_point:
            reorder_status = "Reorder Needed"
        else:
            reorder_status = "Stock Safe"
        
        results[product] = {
            "MAE": round(mae, 2),
            "Reorder Point": int(round(reorder_point))
,
            "Current Stock": current_stock,
            "Status": reorder_status
        }
    
    return results
