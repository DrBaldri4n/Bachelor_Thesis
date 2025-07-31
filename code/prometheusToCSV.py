import requests
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from config_allevents import FEATURES

PROMETHEUS_URL = "http://192.168.1.25:9090"
STEP = "5"  # seconds
CHUNK_HOURS = 2

start_time = datetime.fromisoformat("2025-07-30T15:48:57.226705")
end_time = datetime.fromisoformat("2025-07-30T21:53:41.765919")

def build_chunks(start, end, chunk_hours):
    chunks = []
    chunk_delta = timedelta(hours=chunk_hours)
    current_start = start
    while current_start < end:
        current_end = min(current_start + chunk_delta, end)
        chunks.append((
            current_start.isoformat("T") + "Z",
            current_end.isoformat("T") + "Z"
        ))
        current_start = current_end
    return chunks

def query_metric_chunked(metric, chunks):
    all_results = []
    for chunk_start, chunk_end in chunks:
        url = f"{PROMETHEUS_URL}/api/v1/query_range"
        params = {
            "query": metric,
            "start": chunk_start,
            "end": chunk_end,
            "step": STEP,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        all_results.extend(response.json()["data"]["result"])
    return all_results

def main():
    chunks = build_chunks(start_time, end_time, CHUNK_HOURS)
    data = defaultdict(dict)
    timestamps = set()
    values_dict = {}
    metric_query_map = {}

    for feat in FEATURES:
        prom_name = feat.replace("-", "_")
        url = f"{PROMETHEUS_URL}/api/v1/query"
        hit = False

        # 1. sum(prom_name) abfragen
        query = f"sum({prom_name})"
        params = {'query': query}
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            results = resp.json()['data']['result']
            if results:
                print(f"[Gefunden] sum({prom_name}) für Feature {feat}")
                value = float(results[0]['value'][1])
                values_dict[feat] = value
                metric_query_map[feat] = query
                hit = True
        except Exception:
            pass

        if hit:
            continue

        # 2. sum(perf_prom_name) abfragen
        prom_name_perf = 'perf_' + prom_name
        query = f"sum({prom_name_perf})"
        params = {'query': query}
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            results = resp.json()['data']['result']
            if results:
                print(f"[Gefunden] sum({prom_name_perf}) für Feature {feat}")
                value = float(results[0]['value'][1])
                values_dict[feat] = value
                metric_query_map[feat] = query
                hit = True
        except Exception:
            pass

    # --- Array für den Scaler bauen ---
    values_array = []
    feature_names_for_array = []

    for feat in FEATURES:
        feature_names_for_array.append(feat)
        values_array.append(values_dict.get(feat, np.nan))

    # Zeitreihenabfrage NUR für gefundene Varianten machen
    for feat, querystr in metric_query_map.items():
        results = query_metric_chunked(querystr, chunks)
        for series in results:
            for timestamp, value in series["values"]:
                ts = datetime.utcfromtimestamp(float(timestamp)).isoformat()
                data[ts][feat] = value
                timestamps.add(ts)

    sorted_timestamps = sorted(timestamps)

    all_columns = list(FEATURES)

    with open("night_session.csv", "w", newline="") as f:
        writer = csv.writer(f)
        header = ["timestamp"] + all_columns
        writer.writerow(header)
        for ts in sorted_timestamps:
            row = [ts] + [data[ts].get(col, "") for col in all_columns]
            writer.writerow(row)

if __name__ == "__main__":
    main()
