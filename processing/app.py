import functools
import logging.config
import connexion
from connexion import NoContent
import json
import logging
import yaml
from datetime import datetime
from apscheduler.schedulers import background
import httpx
# from flask_cors import CORS


with open("conf_log.yml", "r") as f:
    LOG_CONFIG = yaml.safe_load(f.read())
    logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# save event data to JSON file
def save_event_data(data):
    with open(app_config["EVENT_FILE"], "w") as file:
        json.dump(data, file, indent=4)

# load event data from JSON file
def load_event_data():
    try:
        with open(app_config["EVENT_FILE"], "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"num_quiz_count": 0, "num_questions_count": 0, "max_quiz_time_limit": 0, "max_questions_score": 0, "last_updated": "1996-02-13 23:53:09"}

import logging
import httpx
from datetime import datetime

def populate_stats():
    logger.info("Periodic processing has started")

    results = load_event_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_read = results.get("last_updated", now)  # Use current time if missing

    # Fetch data from API
    response_question = httpx.get(
        f"{app_config['endpoint']['url_questions']}?start_timestamp={last_read}&end_timestamp={now}",
        headers={"Content-Type": "application/json"}
    )
    response_quiz = httpx.get(
        f"{app_config['endpoint']['url_quiz']}?start_timestamp={last_read}&end_timestamp={now}",
        headers={"Content-Type": "application/json"}
    )

    # Print API response for debugging
    print("Quizzes Response:", response_quiz.text)  # Ensure it's JSON
    print("Questions Response:", response_question.text)

    # Convert API responses to JSON safely
    try:
        quizzes_data = response_quiz.json() if response_quiz.status_code == 200 else []
        questions_data = response_question.json() if response_question.status_code == 200 else []
    except ValueError:
        logger.error("Invalid JSON response from API")
        quizzes_data, questions_data = [], []

    # Ensure response is a list
    if not isinstance(quizzes_data, list):
        logger.error(f"Unexpected format for quizzes_data: {type(quizzes_data)} - {quizzes_data}")
        quizzes_data = []

    if not isinstance(questions_data, list):
        logger.error(f"Unexpected format for questions_data: {type(questions_data)} - {questions_data}")
        questions_data = []

    # Update stats safely
    results["num_quiz_count"] += len(quizzes_data)
    results["num_questions_count"] += len(questions_data)

    # Calculate max values safely
    results["max_quiz_time_limit"] = max(
        [results.get("max_quiz_time_limit", 0)] +
        [int(q.get("time_limit", 0)) for q in quizzes_data if isinstance(q, dict) and "time_limit" in q]
    )

    results["max_questions_score"] = max(
        [results.get("max_questions_score", 0)] +
        [float(q.get("score", 0)) for q in questions_data if isinstance(q, dict) and "score" in q]
    )

    results["last_updated"] = now  # Store time in ISO format

    save_event_data(results)


def get_stats():
    logger.info("the request was recieved")
    try:
        with open(app_config["EVENT_FILE"], "r") as file:
            results = json.load(file)
            logger.debug(results)
            logger.info("request has completed")
            return results, 200
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("statistics do not exist")
        return NoContent, 404



def init_scheduler():
    sched = background.BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                'interval',
                seconds=app_config['scheduler']['interval'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
# CORS(app.app) 
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")

