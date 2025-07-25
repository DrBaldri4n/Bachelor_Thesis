import time
import numpy as np
import csv
from datetime import datetime
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
from tensorflow.keras.models import load_model
import joblib
from config_feature import FEATURES


# --- Initialisierung ---
prom = PrometheusConnect(url="http://192.168.1.25:9090", disable_ssl=True)

# Modell und Scaler laden
clf = load_model('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/final/lstm_model_20events.h5')
scaler = joblib.load('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/final/scaler.pkl')

csv_file = 'live_data_log.csv'
header = ['timestamp'] + FEATURES + ['benign_prob', 'attack_prob', 'prediction']

# CSV-Datei mit Header anlegen, falls noch nicht vorhanden
try:
    with open(csv_file, 'x', newline='') as f:
        csv.writer(f).writerow(header)
except FileExistsError:
    pass


# Funktion zum direkten Auslesen des Werts von Prometheus mit fallback auf 'perf_' Prefix
def get_metric_value(prom, feat):
    def query_metric(name):
        try:
            metric_data = prom.get_current_metric_value(metric_name=name)
            metric_df = MetricSnapshotDataFrame(metric_data)
            if not metric_df.empty and 'value' in metric_df.columns:
                return float(metric_df.iloc[0]['value'])
        except Exception:
            pass
        return np.nan

    # Prüfen, ob Feature ein CPU-Suffix _1 bis _4 hat
    if feat[-2:] in ['_1', '_2', '_3', '_4']:
        base_feat = feat[:-2].replace('-', '_')
        # Zuerst ohne perf_
        query = f'sum({base_feat})'
        value = query_metric(query)
        if np.isnan(value):
            # Falls NaN, dann mit perf_
            query = f'sum(perf_{base_feat})'
            value = query_metric(query)
    else:
        base_feat = feat.replace('-', '_')
        query = base_feat
        value = query_metric(query)
        if np.isnan(value):
            query = f'sum(perf_{base_feat})'
            value = query_metric(query)

    return value


# --- Hauptloop ---
while True:
    # 1. Metric-Werte holen
    values_array = []
    for feat in FEATURES:
        value = get_metric_value(prom, feat)
        values_array.append(value)

    # 2. Modell-Lauf vorbereiten & ausführen
    input_array = np.array(values_array).reshape(1, -1)
    input_scaled = scaler.transform(input_array)
    input_lstm = input_scaled.reshape(1, 1, len(FEATURES))

    prediction_result = clf.predict(input_lstm, verbose=0)
    attack_prob = float(prediction_result[0][0])
    benign_prob = 1.0 - attack_prob
    prediction = 0 if attack_prob < 0.5 else 1

    # 3. Log in CSV schreiben
    row = [datetime.now().isoformat()] + values_array + [attack_prob, benign_prob, prediction]
    with open(csv_file, 'a', newline='') as f:
        csv.writer(f).writerow(row)

    # 4. Ergebnis ausgeben
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Wahrscheinlichkeit benign: {benign_prob:.4f}")
    print(f"Wahrscheinlichkeit attack: {attack_prob:.4f}")
    status = "⚠️  Angriff erkannt (attack)!" if prediction == 1 else "✅  Kein Angriff erkannt (benign)."
    print(status)
    print("Warte 5 Sekunden...")
    time.sleep(5)
