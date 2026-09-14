from flask import Flask, jsonify, request
import pandas as pd
import kagglehub
import os

app = Flask(__name__)

print("Downloading dataset...")
path = kagglehub.dataset_download("utsh0dey/global-medicine-directory-and-healthcare-dataset")

csv_file = None
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.csv'):
            csv_file = os.path.join(root, file)
            break

# Load only the first 30,000 rows to stay safely within Render's 512MB memory limit
df = pd.read_csv(csv_file, nrows=30000) if csv_file else pd.DataFrame()
if not df.empty:
    df.columns = df.columns.str.strip()
    # Convert all columns to string to prevent memory bloat and type mismatch
    df = df.astype(str)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "total_records": len(df)})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    if df.empty:
        return jsonify({"error": "Dataset not loaded"}), 500
        
    search_query = request.args.get("q", "").lower()
    
    if search_query:
        mask = df.apply(lambda row: row.str.lower().str.contains(search_query, na=False).any(), axis=1)
        filtered_df = df[mask].head(100)
    else:
        filtered_df = df.head(50)
        
    return jsonify(filtered_df.to_dict(orient="records"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
