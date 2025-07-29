import time
import numpy as np
import csv
from datetime import datetime
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
from tensorflow.keras.models import load_model
import joblib
from config_features import FEATURES

# Initialize Prometheus client, model, and scaler
prom = PrometheusConnect(url="http://192.168.1.25:9090", disable_ssl=True)
clf = load_model('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/tests/lstm_model_final.h5')
scaler = joblib.load('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/tests/scaler_final.pkl')

csv_file = 'test_log_prediction.csv'
header = ['timestamp'] + FEATURES + ['benign_prob', 'attack_prob', 'prediction']

# Create CSV with header if it doesn't exist yet
try:
    with open(csv_file, 'x', newline='') as f:
        csv.writer(f).writerow(header)
except FileExistsError:
    pass

def get_metric_value(prom, feat):
    """Query metric value from Prometheus with fallback to 'perf_' prefix."""
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

window_size, value_buffer = 5, []

while True:
    # Collect current metric values
    values = [get_metric_value(prom, feat) for feat in FEATURES]
    value_buffer.append(values)

    # Wait until enough data points for sequence input
    if len(value_buffer) < window_size:
        print(f"Gathering data ... ({len(value_buffer)}/{window_size})")
        time.sleep(5)
        continue
    if len(value_buffer) > window_size:
        value_buffer.pop(0)  # Keep only the last 'window_size' elements

    # Prepare input sequence and predict with LSTM model
    arr = scaler.transform(np.array(value_buffer)).reshape(1, window_size, len(FEATURES))
    attack_prob = float(clf.predict(arr, verbose=0)[0][0])
    prediction = int(attack_prob >= 0.5)
    benign_prob = 1.0 - attack_prob

    # Log results to CSV file
    with open(csv_file, 'a', newline='') as f:
        csv.writer(f).writerow([datetime.now().isoformat()] + values + [attack_prob, benign_prob, prediction])

    # Print prediction results with timestamp
    print(f"\n📅 {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Probability benign: {benign_prob:.4f}")
    print(f"Probability attack: {attack_prob:.4f}")
    print("⚠️  Attack detected!" if prediction else "✅  No attack detected.")
    print("Waiting 5 seconds...")
    time.sleep(5)
