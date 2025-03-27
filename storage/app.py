import functools
import logging.config
import connexion
from connexion import NoContent
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from base import Base
from Quiz import Quiz
from Question import Question
import logging
import yaml
from datetime import datetime
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType

with open("conf_log.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

engine = create_engine(f"mysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.create_all(engine)

def make_session():
    return sessionmaker(bind=engine)()

# kafka configuration
KAFKA_HOST = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
TOPIC_NAME = app_config['events']['topic']

# consume kafka messages
def process_messages():
    """ Process event messages """
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[str.encode(TOPIC_NAME)]
    
    consumer = topic.get_simple_consumer(
        consumer_group=b'event_group',
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST
    )

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info(f"Received message: {msg}")

        payload = msg["payload"]
        event_type = msg["type"]

        session = make_session()

        if event_type == "quiz":
            event = Quiz(
                payload["name"],
                payload["description"],
                payload["time_limit"],
                payload["timestamp"],
                payload["trace_id"]
            )
            session.add(event)
            logger.info(f"Stored quiz event with trace_id {payload['trace_id']}")

        elif event_type == "question":
            event = Question(
                payload["exam_id"],
                payload["text"],
                payload["order"],
                payload["correct_answer"],
                payload["score"],
                payload["timestamp"],
                payload["trace_id"]
            )
            session.add(event)
            logger.info(f"Stored question event with trace_id {payload['trace_id']}")

        session.commit()
        session.close()
        
        # mark message as processed
        consumer.commit_offsets()

# run kafka consumer in a background thread
def setup_kafka_thread():
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

def get_quiz(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")


    statement = select(Quiz).where(Quiz.date_created >= start).where(Quiz.date_created < end)
    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
        ]
    session.close()
    logger.info("Found %d quiz readings (start: %s, end: %s)", len(results), start, end)
    return results


def get_questions(start_timestamp, end_timestamp):
    session = make_session()
    start = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

    statement = select(Question).where(Question.date_created >= start).where(Question.date_created < end)
    results = [
        result.to_dict()
        for result in session.execute(statement).scalars().all()
        ]
    session.close()
    logger.info("Found %d questions readings (start: %s, end: %s)", len(results), start, end)
    return results

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    setup_kafka_thread() 
    app.run(port=8090, host="0.0.0.0")

