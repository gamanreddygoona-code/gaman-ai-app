import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import joblib

print("=" * 55)
print("   🤖  Simple AI Model Trainer  —  SQLite + scikit-learn")
print("=" * 55)

# ── Step 1: Connect to SQLite Database ──────────────────────
print("\n✅ Step 1: Connecting to ai_data.db ...")
conn = sqlite3.connect("ai_data.db")

# ── Step 2: Load Data ────────────────────────────────────────
print("✅ Step 2: Loading training_data table ...")
df = pd.read_sql_query("SELECT * FROM training_data", conn)
conn.close()

print(f"\n📊 Data loaded — {len(df)} rows, {len(df.columns)} columns\n")
print(df.to_string(index=False))

# ── Step 3: Prepare Features and Labels ─────────────────────
X = df[["feature1", "feature2", "feature3"]]
y = df["label"]

# ── Step 4: Split into Train / Test sets ────────────────────
print("\n✅ Step 3: Splitting — 80% training, 20% testing ...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"   Training samples : {len(X_train)}")
print(f"   Testing  samples : {len(X_test)}")

# ── Step 5: Train the Model ──────────────────────────────────
print("\n✅ Step 4: Training Linear Regression model ...")
model = LinearRegression()
model.fit(X_train, y_train)

print(f"\n   📌 Model Coefficients:")
for name, coef in zip(X.columns, model.coef_):
    print(f"      {name:10s} → {coef:+.4f}")
print(f"   📌 Intercept: {model.intercept_:.4f}")

# Save the model
model_path = "simple_ai_model.pkl"
joblib.dump(model, model_path)
print(f"\n✅ Model saved to {model_path}")

# ── Step 6: Evaluate ─────────────────────────────────────────
print("\n✅ Step 5: Evaluating model performance ...")
y_pred = model.predict(X_test)
r2  = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

# Cross-validation for more reliable score
cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")

print(f"\n   ┌─────────────────────────────────────────┐")
print(f"   │  📈 R² Score (test)   : {r2:>8.4f}          │")
print(f"   │  📉 RMSE  (test)      : {rmse:>8.4f}          │")
print(f"   │  🔁 CV R² (5-fold)    : {cv_scores.mean():>8.4f} ± {cv_scores.std():.4f}│")
print(f"   └─────────────────────────────────────────┘")

if r2 >= 0.85:
    print("\n   ✅ Great fit! The model learned the pattern well.")
elif r2 >= 0.6:
    print("\n   🟡 Decent fit. More data would improve it.")
else:
    print("\n   🔴 Weak fit. The model needs more / better data.")

# ── Step 7: Predict on New Data ──────────────────────────────
print("\n✅ Step 6: Predicting on 3 brand-new samples ...")
new_samples = pd.DataFrame([
    [2.5, 2.0, 3.0],
    [1.0, 1.0, 1.0],
    [4.5, 3.5, 5.0],
], columns=["feature1", "feature2", "feature3"])

predictions = model.predict(new_samples)

print(f"\n   {'feature1':>9} {'feature2':>9} {'feature3':>9}  →  {'Predicted':>10}")
print(f"   {'─'*9:>9} {'─'*9:>9} {'─'*9:>9}     {'─'*10:>10}")
for i, (_, row) in enumerate(new_samples.iterrows()):
    print(f"   {row.feature1:>9.1f} {row.feature2:>9.1f} {row.feature3:>9.1f}  →  {predictions[i]:>10.2f}")

print("\n" + "=" * 55)
print("   🎉 All done! Your AI model is trained and working.")
print("=" * 55)
print("\n📁 Database : c:\\Gamansai\\ai\\ai_data.db")
print("📄 Script   : c:\\Gamansai\\ai\\train_ai.py")
print("\nTo retrain anytime, just run:  python train_ai.py\n")
