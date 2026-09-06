import os
import time
import json
import random
import paho.mqtt.client as mqtt

BROKER_IP = os.getenv("MQTT_BROKER_IP", "YOUR_MQTT_BROKER_IP")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
TOPIC = "hotel/kamar1"

client = mqtt.Client(client_id="Mock-ESP32-Kamar101")

def run_simulator():
    client.connect(BROKER_IP, BROKER_PORT, 60)
    print(f"[*] Terhubung ke broker {BROKER_IP}:{BROKER_PORT}")
    print(f"[*] Mengirim payload ke topik '{TOPIC}' setiap 2 detik...\n")

    kamar_terisi = 0
    pintu_terbuka = 0

    while True:
        if random.random() < 0.15:
            kamar_terisi = 1 if kamar_terisi == 0 else 0
            pintu_terbuka = 1
        else:
            pintu_terbuka = 0

        suhu = round(random.uniform(23.0, 27.5), 1)
        kelembapan = round(random.uniform(55.0, 68.0), 1)
        gerak = kamar_terisi if random.random() < 0.8 else 0

        payload = {
            "suhu": suhu,
            "kelembapan": kelembapan,
            "gerak": gerak,
            "pintu": pintu_terbuka,
            "status_kamar": kamar_terisi
        }

        payload_str = json.dumps(payload)
        client.publish(TOPIC, payload_str)
        print(f"[MQTT SEND] -> {payload_str}")
        time.sleep(2)

if __name__ == "__main__":
    try:
        run_simulator()
    except KeyboardInterrupt:
        print("\n[!] Simulator dihentikan.")
        client.disconnect()
