flowchart TD
    A([Mulai: Loop Pembacaan Sensor]) --> B[ESP32 Baca DHT11, PIR, & Reed Switch Pintu]

    %% Logika State Machine Edge ESP32
    B --> C{Pintu Baru Saja Ditutup?<br>Transisi HIGH ke LOW}
    C -- Ya --> D[Mulai Timer Hitung Mundur 8 Detik]
    C -- Tidak --> E{Pintu Terbuka atau<br>PIR Deteksi Gerakan?}

    D --> E
    E -- Ya --> F[Status: Kamar Terisi<br>Reset / Batalkan Countdown]
    E -- Tidak --> G{Countdown 8 Detik Selesai<br>Tanpa Ada Gerakan?}

    G -- Ya --> H[Status: Kamar Kosong]
    G -- Tidak --> I[Pertahankan Status Sebelumnya]

    F --> J[Relay ON: Alirkan Daya Listrik]
    H --> K[Relay OFF: Putus Daya Otomatis]

    %% Transmisi MQTT
    J --> L[Kemas Telemetri ke JSON<br>Interval 2 Detik]
    K --> L
    I --> L

    L --> M[ESP32 Publish ke Topik 'hotel/kamar1'<br>via Tailscale VPN]
    M --> N[Mosquitto MQTT Broker di K3s: Port 31883]

    %% Ingestion & Event-Driven Alert
    N --> O[Python Consumer: Micro-Batching 5s & State Retention]
    O --> P{Status Berubah dari<br>Terisi ke Kosong?}
    
    P -- Ya --> Q[Kirim Alert Housekeeping<br>via Bot Telegram]
    P -- Tidak --> R[Tulis Snapshot Data Lengkap ke InfluxDB]
    Q --> R

    %% Visualisasi & Analisis Batch
    R --> S[Grafana Dashboard & Portal Nginx: Real-Time Monitoring]
    R --> T[Apache Spark Standalone: Batch Analytics Pola Hunian & Suhu]

    S --> U([Selesai / Looping Kembali])
    T --> U
