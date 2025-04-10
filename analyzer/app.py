import os
import json
import logging.config
import connexion
from connexion import NoContent
from pykafka import KafkaClient
from pykafka.common import OffsetType
import yaml
from flask_cors import CORS

# Load configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open('conf_log.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

# Kafka Configuration
KAFKA_HOST = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
TOPIC_NAME = app_config['events']['topic']
STATS_FILE = "stats.json"

def read_stats():
    if not os.path.isfile(STATS_FILE):
        logger.info("Stats file not found. Initializing with zeros.")
        return {"num_questions": 0, "num_quizzes": 0}
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def write_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def get_event(index, event_type):
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[str.encode(TOPIC_NAME)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    counter = 0
    for msg in consumer:
        message = json.loads(msg.value.decode('utf-8'))
        if message['type'] == event_type:
            if counter == index:
                logger.info(f"Found {event_type} at index {index}")
                return message['payload'], 200
            counter += 1

    logger.warning(f"No {event_type} found at index {index}")
    return {"message": f"No {event_type} at index {index}!"}, 404

def get_quiz_event(index):
    return get_event(index, "quiz")

def get_question_event(index):
    return get_event(index, "question")

def get_event_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        return stats, 200

    # If file doesn't exist, then calculate
    quiz_count = 0
    question_count = 0

    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[str.encode(TOPIC_NAME)]
    consumer = topic.get_simple_consumer(
        auto_offset_reset=OffsetType.EARLIEST,
        reset_offset_on_start=True,
        consumer_timeout_ms=1000
    )


    for msg in consumer:
        message = json.loads(msg.value.decode('utf-8'))
        if message['type'] == "quiz":
            quiz_count += 1
        elif message['type'] == "question":
            question_count += 1

    stats = {"num_quizzes": quiz_count, "num_questions": question_count}
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

    return stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")
