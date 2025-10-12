import json

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "huydepzai",
    #group_id="group1",
    bootstrap_servers=["localhost:9092"],
    #auto_offset_reset="earliest",
    #enable_auto_commit=True,
    #value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

while True:
    msg = consumer.poll(timeout_ms=500)  # Chờ tin nhắn từ Kafka
    for tp, messageages in msg.items():
        for messeage in messageages:
            print("%s:%d:%d: key = %s value=%s" % (
                tp.topic, tp.partition, messeage.offset,
                messeage.key, messeage.value
            ))
