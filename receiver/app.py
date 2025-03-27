import logging.config
import connexion
from connexion import NoContent
import json
import datetime
import httpx
import uuid
import yaml
import logging
from pykafka import KafkaClient 

MAX_EVENTS = 5
EVENT_FILE = "events.json"

# Load configuration file
with open('receiver_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open("log_config.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

# kafka Configuration
KAFKA_HOST = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
TOPIC_NAME = app_config['events']['topic']

# connect to Kafka
client = KafkaClient(hosts=KAFKA_HOST)
topic = client.topics[str.encode(TOPIC_NAME)]
producer = topic.get_sync_producer()

# Load event data from JSON file
def load_event_data():
    try:
        with open(EVENT_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"num_quiz": 0, "recent_quiz": [], "num_question": 0, "recent_question": []}

# save event data to JSON file
def save_event_data(data):
    with open(EVENT_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Log events
def log_event(event_type, body):
    data = load_event_data()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info(f"Received event {event_type} with a trace id of {body['trace_id']}")

    if event_type == "quiz":
        msg_data = f"Quiz '{body['name']}' with description '{body['description']}' created at {body['timestamp']}."
        data["num_quiz"] += 1
        data["recent_quiz"].insert(0, {"msg_data": msg_data, "received_timestamp": timestamp})
        if len(data["recent_quiz"]) > MAX_EVENTS:
            data["recent_quiz"].pop()

    elif event_type == "question":
        msg_data = f"Question '{body['text']}' added to quiz ID {body['exam_id']} with correct answer '{body['correct_answer']}'."
        data["num_question"] += 1
        data["recent_question"].insert(0, {"msg_data": msg_data, "received_timestamp": timestamp})
        if len(data["recent_question"]) > MAX_EVENTS:
            data["recent_question"].pop()

    # save_event_data(data)

# creating a quiz (Sends to Kafka instead of HTTP POST)
def create_quiz(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    log_event("quiz", body)

    msg = {
        "type": "quiz",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))  # send to Kafka

    logger.info(f"Produced event quiz (id: {trace_id}) to Kafka")
    return NoContent, 201  # hardcoded response

# adding a question (Sends to Kafka instead of HTTP POST)
def create_question(body):
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    log_event("question", body)

    msg = {
        "type": "question",
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))  # send to Kafka

    logger.info(f"Produced event question (id: {trace_id}) to Kafka")
    return NoContent, 201  # hardcoded response

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

