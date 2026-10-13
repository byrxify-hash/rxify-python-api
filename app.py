from flask import Flask, jsonify, request
import mlcroissant as mlc
import os

app = Flask(__name__)

url = 'https://www.kaggle.com/datasets/mohneesh7/indian-medicine-data/croissant/download'

# Safe recursive decoder
def decode_field(val):
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='ignore')
    if isinstance(val, (list, tuple)):
        return [decode_field(x) for x in val]
    if isinstance(val, dict):
        return {decode_field(k): decode_field(v) for k, v in val.items()}
    return str(val) if val is not None else ""

# Publish records only after the entire dataset has loaded successfully.
cached_records = []
dataset_status = "loading"


def initialize_dataset():
    global cached_records, dataset_status
    cached_records = []
    dataset_status = "loading"
    try:
        croissant_dataset = mlc.Dataset(url)
        record_sets = [rs.id for rs in croissant_dataset.metadata.record_sets]
        if not record_sets:
            raise ValueError("Dataset has no record sets")

        records = []
        for record in croissant_dataset.records(record_set=record_sets[0]):
            cleaned_item = {}
            for k, v in record.items():
                clean_key = decode_field(k).split('/')[-1]
                cleaned_item[clean_key] = decode_field(v)
            records.append(cleaned_item)

        cached_records = records
        dataset_status = "ready"
        app.logger.info("Fully cached %s records", len(cached_records))
    except Exception:
        dataset_status = "failed"
        app.logger.exception("Dataset initialization failed")


def dataset_unavailable():
    return jsonify({
        "status": "unavailable",
        "dataset_status": dataset_status,
        "error": {
            "code": "dataset_unavailable",
            "message": "Medicine data is unavailable. Please try again later."
        }
    }), 503


initialize_dataset()


@app.route("/", methods=["GET"])
def home():
    if dataset_status != "ready":
        return dataset_unavailable()
    return jsonify({
        "status": "online",
        "dataset_status": dataset_status,
        "total_cached": len(cached_records),
        "dataset": "Indian Medicine Data - Full Fetch"
    })

@app.route("/medicines", methods=["GET"])
def get_medicines():
    if dataset_status != "ready":
        return dataset_unavailable()
    search_query = request.args.get("q", "").strip().lower()

    # If no search, return only the first 50 to prevent browser freezing
    if not search_query:
        return jsonify(cached_records[:50])

    filtered = []
    for r in cached_records:
        # SMART SEARCH: 1 or 2 letters strictly match the beginning of the name
        if len(search_query) <= 2:
            name_fields = [
                str(r.get('Product Name', '')).lower(),
                str(r.get('product_name', '')).lower(),
                str(r.get('Brand Name', '')).lower(),
                str(r.get('Name', '')).lower(),
                str(r.get('Generic Name', '')).lower()
            ]
            if any(name.startswith(search_query) for name in name_fields if name):
                filtered.append(r)

        # DEEP SEARCH: 3+ letters search anywhere inside all columns
        else:
            if any(search_query in str(v).lower() for v in r.values()):
                filtered.append(r)

    # Return matches, but cap at 100 to keep the PHP frontend fast and responsive
    return jsonify(filtered[:100] if filtered else [])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
