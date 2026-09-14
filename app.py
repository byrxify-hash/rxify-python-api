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

df = pd.read_csv(csv_file, nrows=20000) if csv_file else pd.DataFrame()
if not df.empty:
    df.columns = df.columns.str.strip()
    df = df.astype(str)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "total_records": len(df)})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    if df.empty:
        return jsonify({"error": "Dataset not loaded"}), 500
        
    search_query = request.args.get("q", "").strip().lower()
    
    if search_query:
        # Find the best column to search (e.g., name, brand, title, drug)
        target_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ['name', 'brand', 'drug', 'title', 'product']):
                target_col = col
                break
        
        if target_col:
            filtered_df = df[df[target_col].str.lower().str.contains(search_query, na=False)].head(100)
        else:
            # Fallback to general search if no name column is found
            mask = df.apply(lambda row: row.str.lower().str.contains(search_query, na=False).any(), axis=1)
            filtered_df = df[mask].head(100)
    else:
        filtered_df = df.head(50)
        
    return jsonify(filtered_df.to_dict(orient="records"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
