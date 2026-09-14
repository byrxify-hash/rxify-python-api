from flask import Flask, jsonify, request
import pandas as pd
import kagglehub
import os

app = Flask(__name__)

# Download dataset via kagglehub (reads KAGGLE_API_TOKEN from environment variables automatically)
print("Downloading dataset...")
path = kagglehub.dataset_download("utsh0dey/global-medicine-directory-and-healthcare-dataset")

# Locate the CSV file automatically
csv_file = None
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.csv'):
            csv_file = os.path.join(root, file)
            break

df = pd.read_csv(csv_file) if csv_file else pd.DataFrame()
if not df.empty:
    df.columns = df.columns.str.strip()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "total_records": len(df)})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    if df.empty:
        return jsonify({"error": "Dataset not loaded"}), 500
        
    search_query = request.args.get("q", "").lower()
    
    if search_query:
        mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        filtered_df = df[mask].head(100)
    else:
        filtered_df = df.head(50)
        
    return jsonify(filtered_df.to_dict(orient="records"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
