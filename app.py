from flask import Flask, jsonify, request
import mlcroissant as mlc
import itertools
import os

app = Flask(__name__)

print("Initializing New Croissant dataset (Indian Medicine Data)...")
url = 'https://www.kaggle.com/datasets/mohneesh7/indian-medicine-data/croissant/download'
croissant_dataset = mlc.Dataset(url)

record_sets = [rs.id for rs in croissant_dataset.metadata.record_sets]
record_set_id = record_sets[0] if record_sets else None

# Safe recursive decoder
def decode_field(val):
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='ignore')
    if isinstance(val, (list, tuple)):
        return [decode_field(x) for x in val]
    if isinstance(val, dict):
        return {decode_field(k): decode_field(v) for k, v in val.items()}
    return str(val) if val is not None else ""

# Pre-cache records (Bumped to 200 for better alphabetical results)
cached_records = []
if record_set_id:
    try:
        raw_rec = croissant_dataset.records(record_set=record_set_id)
        for record in itertools.islice(raw_rec, 200):
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
    return jsonify({"status": "online", "total_cached": len(cached_records), "dataset": "Indian Medicine Data"})

@app.route("/medicines", methods=["GET"])
def get_medicines():
    search_query = request.args.get("q", "").strip().lower()
    
    if not search_query:
        return jsonify(cached_records)
        
    filtered = []
    for r in cached_records:
        # SMART SEARCH: If 1 or 2 letters, strictly match the beginning of the medicine name
        if len(search_query) <= 2:
            name_fields = [
                str(r.get('Product Name', '')).lower(),
                str(r.get('product_name', '')).lower(),
                str(r.get('Brand Name', '')).lower(),
                str(r.get('Name', '')).lower(),
                str(r.get('Generic Name', '')).lower()
            ]
            
            # Check if any main name starts with the user's 1 or 2 letters
            if any(name.startswith(search_query) for name in name_fields if name):
                filtered.append(r)
        
        # DEEP SEARCH: If 3+ letters, search anywhere inside all columns
        else:
            if any(search_query in str(v).lower() for v in r.values()):
                filtered.append(r)

    # Return results (or default back to top 10 if no match is found)
    return jsonify(filtered if filtered else cached_records[:10])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
