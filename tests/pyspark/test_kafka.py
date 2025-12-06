from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaConsumer") \
    .getOrCreate()

# Define Kafka parameters
kafka_bootstrap_servers = "localhost:9092"
kafka_topic = "your_topic_name"

# Define schema for the Kafka message
schema = StructType([
    StructField("key", StringType(), True),
    StructField("value", StringType(), True)
])

# Read messages from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .load()

# Parse the Kafka message
parsed_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Write the parsed messages to console
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()