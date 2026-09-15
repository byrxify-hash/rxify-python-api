from flask import Flask, jsonify, request
import mlcroissant as mlc
import itertools
import os

app = Flask(__name__)

print("Initializing Croissant dataset...")
url = 'https://www.kaggle.com/datasets/utsh0dey/global-medicine-directory-and-healthcare-dataset/croissant/download'
croissant_dataset = mlc.Dataset(url)

record_sets = [rs.id for rs in croissant_dataset.metadata.record_sets]
record_set_id = record_sets[0] if record_sets else None

# Preload first 50 records into memory for instant responses
cached_records = []
if record_set_id:
    try:
        raw_rec = croissant_dataset.records(record_set=record_set_id)
        for record in itertools.islice(raw_rec, 50):
            cleaned = {k.split('/')[-1]: v for k, v in record.items()}
            cached_records.append(cleaned)
    except Exception as e:
        print(f"Error caching records: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "online", "total_cached": len(cached_records)})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    search_query = request.args.get("q", "").strip().lower()
    
    if not search_query:
        return jsonify(cached_records)
        
    filtered = [
        r for r in cached_records 
        if any(search_query in str(v).lower() for v in r.values())
    ]
    return jsonify(filtered if filtered else cached_records[:10])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
