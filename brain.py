import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
# 1. Training Data (Rainfall in mm, Tide in meters -> Risk %)
data = {
    'rainfall': [0, 50, 100, 200, 300, 500, 10, 150, 400, 20, 80, 250, 600],
    'tide':     [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 1.1, 1.8, 2.9, 1.3, 1.4, 2.2, 3.5],
    'risk':     [0, 10, 30, 70, 90, 100, 5, 45, 95, 8, 25, 75, 100]
}
df = pd.DataFrame(data)

# 2. Initialize and Train the Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(df[['rainfall', 'tide']], df['risk'])

def get_flood_prediction(rain, tide_level):
    prediction = model.predict(pd.DataFrame([[rain, tide_level]], columns=['rainfall', 'tide']))
    return f"Calculated Flood/Salinity Risk: {prediction[0]:.2f}%"

## 3. Interactive Risk Simulator
print("\n" + "="*40)
print("   AQUAHEURISTIC AI: STRATEGIC MONITOR   ")
print("="*40)

while True:
    print("\n[NEW SIMULATION - Type 'exit' to stop]")
    try:
        val = input("Enter Current Rainfall (mm): ")
        if val.lower() == 'exit':
            print("Shutting down Strategic Monitor... System Offline.")
            break
            
        user_rain = float(val)
        user_tide = float(input("Enter Current Tide Level (m): "))

        # 1. Get AI Prediction
        result_text = get_flood_prediction(user_rain, user_tide)
        # Extract numerical value from the string for logic
        prediction_val = float(result_text.split(": ")[1].replace("%", ""))

        # 2. Display Result with Visual Alerts
        print("-" * 40)
        print("ANALYSIS COMPLETE:")
        print(result_text)

        status = "NORMAL"
        if prediction_val > 80:
            print("🚨 ALERT: CRITICAL RISK! ACTIVATE FLOOD BARRIERS. 🚨")
            status = "CRITICAL"
        elif prediction_val > 50:
            print("⚠️ WARNING: ELEVATED RISK. MONITOR SENSORS. ⚠️")
            status = "WARNING"
        else:
            print("✅ STATUS: STABLE. NO IMMEDIATE ACTION REQUIRED.")
        print("-" * 40)

        # 3. BLACK BOX LOGGING
        log_entry = {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Rainfall': user_rain,
            'Tide': user_tide,
            'Risk_Pct': prediction_val,
            'Status': status
        }
        
        # Save instantly to a CSV file
        log_df = pd.DataFrame([log_entry])
        file_exists = __import__('os').path.exists('flood_logs.csv')
        log_df.to_csv('flood_logs.csv', mode='a', index=False, header=not file_exists)
        print("✓ Data successfully logged to flood_logs.csv")

    except ValueError:
        print("Error: Invalid input. Please enter numbers for rainfall and tide.")