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

# Safe recursive decoder for all bytes fields
def decode_field(val):
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='ignore')
    if isinstance(val, (list, tuple)):
        return [decode_field(x) for x in val]
    if isinstance(val, dict):
        return {decode_field(k): decode_field(v) for k, v in val.items()}
    return str(val) if val is not None else ""

cached_records = []
if record_set_id:
    try:
        raw_rec = croissant_dataset.records(record_set=record_set_id)
        for record in itertools.islice(raw_rec, 100):
            cleaned_item = {}
            for k, v in record.items():
                clean_key = decode_field(k).split('/')[-1]
                clean_val = decode_field(v)
                cleaned_item[clean_key] = clean_val
            cached_records.append(cleaned_item)
        print(f"Successfully cached {len(cached_records)} records!")
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
