import json
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

BROKER_IP = "192.168.1.28"
BROKER_PORT = 1883
TOPIC = "hotel/kamar1"

# Service InfluxDB di K3s
INFLUX_HOST = "10.43.203.175"
INFLUX_PORT = 8086
DB_NAME = "hotel_db"

influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
influx.create_database(DB_NAME)
influx.switch_database(DB_NAME)

def on_connect(client, userdata, flags, rc):
    print(f"[*] Consumer terhubung ke Mosquitto. Mendengarkan topik '{TOPIC}'...")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        point = [
            {
                "measurement": "room_telemetry",
                "tags": {
                    "room": "101",
                    "device": "simulator_01"
                },
                "fields": {
                    "temperature": float(data.get("suhu", 0)),
                    "humidity": float(data.get("kelembapan", 0)),
                    "motion": int(data.get("gerak", 0)),
                    "door": int(data.get("pintu", 0)),
                    "occupancy": int(data.get("status_kamar", 0))
                }
            }
        ]
        influx.write_points(point)
        print(f"[INFLUX WRITE] Suhu: {data.get('suhu')}°C | Status Kamar: {data.get('status_kamar')}")
    except Exception as e:
        print(f"[ERR] Gagal memproses data: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKER_PORT, 60)
client.loop_forever()
