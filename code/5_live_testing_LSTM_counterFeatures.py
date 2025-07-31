import os
import time
import numpy as np
import csv
from datetime import datetime
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
from tensorflow.keras.models import load_model
import joblib
from config_features import FEATURES

# Initialisierung
prom = PrometheusConnect(url="http://192.168.1.25:9090", disable_ssl=True)
clf = load_model('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/night_1/lstm_model_20events1.keras')
scaler = joblib.load('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/night_1/scaler1.pkl')

csv_file = 'test_log_prediction.csv'
header = ['timestamp'] + FEATURES + ['benign_prob', 'attack_prob', 'prediction']

# Datei mit Header anlegen, falls nicht vorhanden
try:
    with open(csv_file, 'x', newline='') as f:
        csv.writer(f).writerow(header)
except FileExistsError:
    pass

# Counter-Features, die _delta-Werte benötigen
counter_features = ['skb_kfree_skb', 'syscalls_sys_enter_fcntl', 'sched_sched_stat_runtime', 'syscalls_sys_enter_kill', 
                    'fib_fib_table_lookup', 'sock_inet_sock_set_state', 'mmc_mmc_request_start']

# Puffer zur Berechnung der _delta-Features
previous_counters = {}
window_size = 2
value_buffer = []

def get_metric_value(prom, feat):
    """Query metric value from Prometheus mit Fallback auf perf_-Prefix."""
    def q(name):
        try:
            df = MetricSnapshotDataFrame(prom.get_current_metric_value(metric_name=name))
            if not df.empty and 'value' in df.columns:
                return float(df.iloc[0]['value'])
        except:
            pass
        return np.nan

    base = feat.replace('-', '_')
    for query in [base, f'sum(perf_{base})']:
        v = q(query)
        if not np.isnan(v):
            return v
    return np.nan

# Hauptloop
while True:
    current_raw_values = {}
    current_values = []

    for feat in FEATURES:
        val = get_metric_value(prom, feat)
        current_raw_values[feat] = val

        if feat in counter_features:
            prev_val = previous_counters.get(feat, val)
            delta = max(0, val - prev_val)
            previous_counters[feat] = val
            current_values.append(delta)
        else:
            current_values.append(val)

    value_buffer.append(current_values)

    if len(value_buffer) < window_size:
        print(f"Gathering data ... ({len(value_buffer)}/{window_size})")
        time.sleep(5)
        continue
    if len(value_buffer) > window_size:
        value_buffer.pop(0)

    arr = scaler.transform(np.array(value_buffer)).reshape(1, window_size, len(FEATURES))
    attack_prob = float(clf.predict(arr, verbose=0)[0][0])
    prediction = int(attack_prob >= 0.5)
    benign_prob = 1.0 - attack_prob

    with open(csv_file, 'a', newline='') as f:
        csv.writer(f).writerow([datetime.now().isoformat()] + current_values + [attack_prob, benign_prob, prediction])

    print(f"\n📅 {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Probability benign: {benign_prob:.4f}")
    print(f"Probability attack: {attack_prob:.4f}")
    print("⚠️  Attack detected!" if prediction else "✅  No attack detected.")
    print("Waiting 5 seconds...")
    time.sleep(5)
