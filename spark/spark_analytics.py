import os
import sys
from influxdb import InfluxDBClient
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, count, round

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "local[*]")

spark = SparkSession.builder \
    .appName("SmartHotelAnalytics") \
    .master(SPARK_MASTER_URL) \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .config("spark.executor.memory", "1g") \
    .config("spark.cores.max", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Tarik data dari database
INFLUX_HOST = os.getenv("INFLUXDB_HOST", "YOUR_INFLUXDB_HOST")
INFLUX_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
DB_NAME = os.getenv("INFLUXDB_DB_NAME", "hotel_db")

db_client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT, database=DB_NAME)

try:
    hasil = db_client.query("SELECT * FROM room_telemetry")
    poin_data = list(hasil.get_points())
except Exception as e:
    print(f"[ERR] Gagal menarik data dari InfluxDB: {e}")
    sys.exit(1)

if not poin_data:
    print("[WARN] Data telemetri kosong di database.")
    sys.exit(0)

# Konversi dan Analisis DataFrame Spark
df_pandas = pd.DataFrame(poin_data)
if 'time' in df_pandas.columns:
    df_pandas = df_pandas.drop(columns=['time'])

df_spark = spark.createDataFrame(df_pandas)
df_spark.show(5)

# Agregasi
df_spark.groupBy("occupancy").agg(
    count("*").alias("total_records"),
    round(avg("temperature"), 2).alias("avg_temperature"),
    round(avg("humidity"), 2).alias("avg_humidity")
).show()

df_spark.select(
    max("temperature").alias("max_temp"),
    min("temperature").alias("min_temp"),
    max("humidity").alias("max_humidity"),
    min("humidity").alias("min_humidity")
).show()

df_spark.groupBy("door").agg(
    count("*").alias("door_events")
).show()

spark.stop()
