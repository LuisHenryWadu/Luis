# Smart Hotel IoT & Monitoring System
> Otomatisasi Layanan Housekeeping dan Manajemen Energi Berbasis Edge Sensing & Distributed Server Infrastructure.

[![Platform](https://img.shields.io/badge/Platform-ESP32%20%7C%20Ubuntu%20Server-orange)](https://espressif.com/)
[![Orchestration](https://img.shields.io/badge/Orchestrator-K3s%20Kubernetes-blue)](https://k3s.io/)
[![Database](https://img.shields.io/badge/Database-InfluxDB%20Time--Series-informational)](https://www.influxdata.com/)
[![Analytics](https://img.shields.io/badge/Analytics-Apache%20Spark-red)](https://spark.apache.org/)
[![VPN](https://img.shields.io/badge/Network-Tailscale%20WireGuard-purple)](https://tailscale.com/)

---

## Ringkasan Sistem

Sistem Smart Hotel IoT & Monitoring System dirancang untuk menjawab dua isu utama operasional perhotelan: pemborosan konsumsi energi listrik dan inefisiensi alur kerja *housekeeping* akibat **False Make Up Room (False MUR)**.

Sistem mengadopsi pendekatan **Edge Computing** menggunakan mikrokontroler ESP32 yang menjalankan algoritma *Finite State Machine* (FSM) secara lokal. Status hunian divalidasi mandiri di tingkat kamar tanpa ketergantungan latensi server, memungkinkan aktuasi pemutus daya relay bekerja instan. Data telemetri kemudian dikirimkan melalui jaringan mesh privat terenkripsi menuju klaster server K3s untuk kebutuhan *micro-batching* database *time-series*, notifikasi otomatis via Telegram Bot, serta komputasi analitik batch menggunakan Apache Spark.

📹 **Tautan Video Pengujian:** [YouTube - Demo Praktikum Smart Hotel IoT](https://youtu.be/qs51M9IOZFo)[cite: 3]

---

## Arsitektur Pipeline Data

Arsitektur sistem terbagi menjadi empat lapisan utama:

```mermaid
flowchart TD
    subgraph Edge Layer [1. Edge Layer: ESP32 Sensing]
        DHT[Sensor DHT11] --> ESP[ESP32 Gateway]
        PIR[Sensor PIR HC-SR501] --> ESP
        Reed[Magnetic Reed Switch] --> ESP
        ESP -->|State Machine Decision| Relay[Relay 5V & Beban Lampu]
    end

    subgraph Network Layer [2. Network Layer: Private Mesh]
        ESP -->|MQTT Telemetry| VPN[Tailscale WireGuard VPN]
    end

    subgraph Server Layer [3. Server Layer: K3s Cluster]
        VPN --> Mosquitto[Mosquitto MQTT: 31883]
        Mosquitto --> Consumer[Python Micro-Batching Service]
        Consumer -->|5s Window Snapshot| Influx[(InfluxDB: 31086)]
        Consumer -->|Event-Driven Trigger| Bot[Telegram Alerting Bot]
        Influx --> Spark[Apache Spark Analytics]
    end

    subgraph Presentation Layer [4. Presentation Layer]
        Nginx[Nginx Web Portal & Reverse Proxy] --> Grafana[Grafana Dashboard]
        Influx --> Grafana
        Bot --> Staff[Housekeeping Mobile App]
    end
