import json
import yaml
import logging.config
from flask_cors import CORS
import connexion
from connexion import NoContent
from pykafka import KafkaClient

# Load config
with open('anomaly_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging config
with open('config/log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

KAFKA_HOST = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
TOPIC_NAME = app_config['events']['topic']
THRESHOLDS = app_config['thresholds']
ANOMALY_FILE = app_config['datastore']['filename']

def detect_anomalies():
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[str.encode(TOPIC_NAME)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    anomalies = []

    for msg in consumer:
        event = json.loads(msg.value.decode('utf-8'))
        etype = event.get("type")
        payload = event.get("payload")
        trace_id = event.get("trace_id")
        event_id = payload.get("id")  # Each payload must have its own id

        if etype not in THRESHOLDS:
            continue

        threshold = THRESHOLDS[etype]
        value = payload.get("value", 0)

        if value > threshold:
            anomalies.append({
                "event_id": event_id,
                "trace_id": trace_id,
                "event_type": etype,
                "anomaly_type": "Threshold Exceeded",
                "description": f"Value {value} exceeded threshold {threshold}"
            })

    with open(ANOMALY_FILE, "w") as f:
        json.dump(anomalies, f)

    logger.info(f"{len(anomalies)} anomalies detected")
    return {"anomalies_detected": len(anomalies)}, 200

def get_anomalies(event_type=None):
    try:
        with open(ANOMALY_FILE, "r") as f:
            data = json.load(f)
    except:
        logger.error("Could not read anomaly file")
        return {"message": "Datastore missing or invalid"}, 404

    if event_type:
        if event_type not in THRESHOLDS:
            return {"message": "Invalid event type"}, 400
        data = [a for a in data if a["event_type"] == event_type]

    if not data:
        return "", 204

    return data, 200

# API setup
app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.add_api("anomaly.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8120)

