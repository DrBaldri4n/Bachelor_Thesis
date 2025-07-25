import time
import numpy as np
import csv
from datetime import datetime
from prometheus_api_client import PrometheusConnect, MetricSnapshotDataFrame
import joblib
from config_feature import FEATURES

# --- Initialisierung ---
prom = PrometheusConnect(url="http://192.168.1.25:9090", disable_ssl=True)

# Decision Tree Modell laden (Pfad anpassen!)
model = joblib.load('/home/yannic/Desktop/Uni/Semester8_Regensburg/Bachelorarbeit/Datenbereinigen/final/decision_tree_model.joblib')

csv_file = 'live_data_log_dt.csv'
header = ['timestamp'] + FEATURES + ['benign_prob', 'attack_prob', 'prediction']

# CSV-Datei mit Header anlegen, falls sie noch nicht existiert
try:
    with open(csv_file, 'x', newline='') as f:
        csv.writer(f).writerow(header)
except FileExistsError:
    pass

def build_metric_query(feat):
    if feat[-2:] in ['_1', '_2', '_3', '_4']:
        base_feat = feat[:-2]
        cpu_number = feat[-1]
        prom_query = f'perf_{base_feat}'
    else:
        prom_query = feat.replace('-', '_')
    return prom_query

while True:
    # 1. Werte von Prometheus holen
    values_array = []
    for feat in FEATURES:
        prom_query = build_metric_query(feat)
        value = np.nan
        try:
            metric_data = prom.get_current_metric_value(metric_name=prom_query)
            metric_df = MetricSnapshotDataFrame(metric_data)
            if not metric_df.empty and 'value' in metric_df.columns:
                value = float(metric_df.iloc[0]['value'])
        except Exception:
            pass
        values_array.append(value)

    # 2. Vorhersage mit Decision Tree (ohne Skalieren!)
    input_array = np.array(values_array).reshape(1, -1)
    prediction_result = model.predict_proba(input_array)
    benign_prob = float(prediction_result[0][0])
    attack_prob = float(prediction_result[0][1])
    prediction = np.argmax(prediction_result)

    # 3. Alles ins CSV schreiben
    row = [datetime.now().isoformat()] + values_array + [benign_prob, attack_prob, prediction]
    with open(csv_file, 'a', newline='') as f:
        csv.writer(f).writerow(row)

    # 4. Ergebnis anzeigen
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Wahrscheinlichkeit benign: {benign_prob:.4f}")
    print(f"Wahrscheinlichkeit attack: {attack_prob:.4f}")
    status = "⚠️  Angriff erkannt (attack)!" if prediction == 1 else "✅  Kein Angriff erkannt (benign)."
    print(status)
    print("Warte 5 Sekunden...")
    time.sleep(5)
