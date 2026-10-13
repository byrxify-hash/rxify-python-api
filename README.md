# Rxify medicine API

Install `requirements.txt`, then run `python app.py` or `gunicorn app:app`.
Each process loads the Kaggle Croissant dataset once at startup. The cache is
published only after all records have been decoded successfully.

## Client responses

When initialization succeeds, `GET /` returns HTTP **200**:

```json
{
  "status": "online",
  "dataset_status": "ready",
  "total_cached": 123,
  "dataset": "Indian Medicine Data - Full Fetch"
}
```

`total_cached` is the actual record count; 123 is illustrative. The
`dataset_status` field is additive. Successful `GET /medicines` responses remain
JSON arrays: up to 50 records without `q`, or up to 100 matches with `q`.
One- and two-character queries match name prefixes; longer queries match any
field. A successful load with zero records, or a search with no matches, returns
HTTP 200 and `[]`.

If dataset creation, metadata access, download, or decoding fails, both `GET /`
and `GET /medicines` (with or without `q`) return HTTP **503**:

```json
{
  "status": "unavailable",
  "dataset_status": "failed",
  "error": {
    "code": "dataset_unavailable",
    "message": "Medicine data is unavailable. Please try again later."
  }
}
```

Clients should check the HTTP status before treating the body as a medicine
array. On 503, show the error message instead of a “no results” message.
`GET /` can be used as a readiness check. If a request can be handled during
initialization, the same 503 format uses `dataset_status: "loading"`; normal
startup loads synchronously before serving requests.

Partial downloads are never served. Exception details and tracebacks remain in
server logs, rather than being exposed in the JSON response. There is no automatic
reload: after fixing the upstream issue, restart the affected process to retry.

## Validation

```sh
python -m pip install Flask
python -m unittest discover -s tests -v
```

Tests use Flask's real test client and a mocked Croissant data source, without
network access or Kaggle credentials. They cover successful loads, decoding,
search behavior, result limits, valid empty datasets, dataset-constructor
failures, missing record sets, interrupted downloads, and invalid records.
