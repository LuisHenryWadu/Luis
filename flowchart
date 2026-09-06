```mermaid
flowchart TD
    A([Mulai: Sensor Membaca Data Kamar]) --> B{Apakah Tombol DND Aktif?}

    %% Alur DND (Prioritas Utama)
    B -- Ya --> C[Sistem Mengunci Status Privasi]
    C --> D[Abaikan Semua Notif Housekeeping]

    %% Alur MUR & PIR (Housekeeping)
    B -- Tidak --> E{Apakah Tombol MUR Aktif?}
    E -- Ya --> F{Apakah Kamar Kosong? <br> Sensor PIR = 0}

    F -- Ya --> G[Update Dashboard Lobi: <br> 'Kamar Siap Dibersihkan']
    F -- Tidak --> H[Pending: Tunggu Hingga Tamu Keluar]

    %% Alur Pengiriman Data IoT
    E -- Tidak --> I[Bungkus Data Lingkungan & Status <br> ke Format JSON]
    H --> I
    D --> I
    G --> I

    I --> J[ESP32 Publish Data via Wi-Fi]
    J --> K{Mosquitto MQTT Broker}
    K --> L[Apache Spark: Filter & Analisis Big Data]
    L --> M[(InfluxDB: Simpan Time-Series)]
    M --> N[Visualisasi di Grafana & Portal Nginx]

    N --> O([Looping: Kembali Baca Sensor])
