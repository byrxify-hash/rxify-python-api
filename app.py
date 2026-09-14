from flask import Flask, jsonify, request
import mlcroissant as mlc
import itertools
import os

app = Flask(__name__)

print("Initializing Croissant dataset...")
url = 'https://www.kaggle.com/datasets/utsh0dey/global-medicine-directory-and-healthcare-dataset/croissant/download'
croissant_dataset = mlc.Dataset(url)

# Get the available record set
record_sets = [rs.id for rs in croissant_dataset.metadata.record_sets]
record_set_id = record_sets[0] if record_sets else None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "record_set": record_set_id})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    if not record_set_id:
        return jsonify({"error": "No record sets found"}), 500
        
    search_query = request.args.get("q", "").strip().lower()
    
    # Fetch records via Croissant
    record_set = croissant_dataset.records(record_set=record_set_id)
    
    results = []
    # Stream and filter records safely
    for record in itertools.islice(record_set, 1000):
        # Clean dictionary keys (remove dataset prefix if present)
        cleaned_record = {k.split('/')[-1]: v for k, v in record.items()}
        
        if search_query:
            # Check if search query matches any value in the record
            match = any(search_query in str(val).lower() for val in cleaned_record.values())
            if match:
                results.append(cleaned_record)
                if len(results) >= 50: # Limit results for speed
                    break
        else:
            results.append(cleaned_record)
            if len(results) >= 50:
                break
                
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
