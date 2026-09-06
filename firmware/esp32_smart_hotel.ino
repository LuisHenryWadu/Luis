#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// Konfigurasi Kredensial & Jaringan (Placeholder)
const char* ssid        = "YOUR_WIFI_SSID";
const char* password    = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
const int mqtt_port     = 1883;

// Pin Mapping Hardware
#define DHTPIN 23
#define DHTTYPE DHT11
#define PIRPIN 13
#define DOORPIN 14
#define RELAYPIN 26

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
bool kamarTerisi = false;
unsigned long waktuPintuDitutup = 0;
bool hitungMundurKosong = false;
int statusPintuSbelumnya = LOW;

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    String clientId = "ESP32-SmartHotel-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      // Terhubung ke broker
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIRPIN, INPUT);
  pinMode(DOORPIN, INPUT_PULLUP); 
  pinMode(RELAYPIN, OUTPUT);
  digitalWrite(RELAYPIN, HIGH); 

  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  int statusPIR = digitalRead(PIRPIN);
  int statusPintuRaw = digitalRead(DOORPIN); 
  int statusPintu = (statusPintuRaw == 1) ? 0 : 1; 

  // Algoritma State Machine Okupansi
  if (statusPintuSbelumnya == HIGH && statusPintu == LOW) {
    waktuPintuDitutup = now;
    hitungMundurKosong = true;
  }
  statusPintuSbelumnya = statusPintu;

  if (statusPintu == HIGH) {
    kamarTerisi = true;
    hitungMundurKosong = false;   
    waktuPintuDitutup = 0;
  }

  if (statusPintu == LOW && statusPIR == HIGH) {
    if (hitungMundurKosong) {
      kamarTerisi = true;
      hitungMundurKosong = false;
    }
  }

  if (hitungMundurKosong && (now - waktuPintuDitutup > 8000)) { 
    kamarTerisi = false;
    hitungMundurKosong = false;
    waktuPintuDitutup = 0;
  }

  digitalWrite(RELAYPIN, kamarTerisi ? LOW : HIGH);

  if (now - lastMsg > 2000) {
    lastMsg = now;
    float suhu = dht.readTemperature();
    float lembab = dht.readHumidity();
    
    if (isnan(suhu)) suhu = 26.0; 
    if (isnan(lembab)) lembab = 60.0;

    int payloadStatusKamar = (kamarTerisi) ? 1 : 0;
    String payload = "{\"suhu\":" + String(suhu) + 
                     ",\"kelembapan\":" + String(lembab) + 
                     ",\"gerak\":" + String(statusPIR) + 
                     ",\"pintu\":" + String(statusPintu) + 
                     ",\"status_kamar\":" + String(payloadStatusKamar) + "}";
    
    client.publish("hotel/kamar1", payload.c_str());
  }
}
