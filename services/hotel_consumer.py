import os
import json
import threading
import requests
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

# Setup Alerting Telegram
TOKEN_BOT = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")

def kirim_notif_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": pesan,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[ERR] Gagal kirim Telegram: {e}")

# Database InfluxDB
INFLUX_HOST = os.getenv("INFLUXDB_HOST", "YOUR_INFLUXDB_HOST")
INFLUX_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
DB_NAME = os.getenv("INFLUXDB_DB_NAME", "hotel_db")

db_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=DB_NAME)
db_client.create_database(DB_NAME)
db_client.switch_database(DB_NAME)

buffer = {
    "temperature": 0.0,
    "humidity": 0.0,
    "motion": 0,
    "door": 0,
    "occupancy": 0
}
status_terakhir = "Belum Terdeteksi"

def snapshot_ke_db():
    threading.Timer(5.0, snapshot_ke_db).start()
    json_body = [{
        "measurement": "room_telemetry",
        "tags": {"room": "kamar101"},
        "fields": buffer
    }]
    try:
        db_client.write_points(json_body)
    except Exception as e:
        print(f"[ERR] InfluxDB write error: {e}")

def on_message(client, userdata, msg):
    global status_terakhir
    try:
        payload = json.loads(msg.payload.decode())
        
        if "suhu" in payload:
            buffer["temperature"] = float(payload["suhu"])
        if "kelembapan" in payload:
            buffer["humidity"] = float(payload["kelembapan"])
        if "gerak" in payload:
            buffer["motion"] = int(payload["gerak"])
        if "pintu" in payload:
            buffer["door"] = int(payload["pintu"])

        if "status_kamar" in payload:
            status_kamar = int(payload["status_kamar"])
            buffer["occupancy"] = status_kamar
            
            # Notifikasi housekeeping saat status berubah dari Terisi ke Kosong
            if status_kamar == 0 and status_terakhir == "Terisi":
                pesan_tele = "🧹 *INFO HOUSEKEEPING* 🧹\nKamar 101 baru saja *KOSONG*.\nSilakan lakukan pembersihan!"
                kirim_notif_telegram(pesan_tele)
                
            status_terakhir = "Terisi" if status_kamar == 1 else "Kosong"

    except Exception as e:
        print(f"[ERR] Message parsing error: {e}")

snapshot_ke_db()

# Broker MQTT
BROKER_IP = os.getenv("MQTT_BROKER_IP", "YOUR_MQTT_BROKER_IP")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER_IP, BROKER_PORT, 60)
mqtt_client.subscribe("hotel/#")
mqtt_client.loop_forever()
