import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
MEMORY_PATH = os.path.join(BASE_DIR, "data", "case_memory.json")

def ensure_memory_file():
    if not os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_memory():
    ensure_memory_file()
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_case(case_record):
    memory = load_memory()
    case_record["timestamp"] = datetime.utcnow().isoformat()
    memory.append(case_record)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def get_memory():
    return load_memory()

def approve_alert(alert_id, reviewer):

    memory = load_memory()

    for record in reversed(memory):

        if (
            record["alert_id"] == alert_id
            and record.get("review_status") == "pending"
        ):

            record["approved"] = True
            record["review_status"] = "approved"
            record["reviewer"] = reviewer

            if (
                record.get("execution_status")
                == "pending_review"
            ):

                record["execution_status"] = "approved"

                record[
                    "execution_action"
                ] = (
                    "Analyst approved AI recommendation."
                )

            break

    with open(
        MEMORY_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=2
        )

    return {
        "status": "approved",
        "alert_id": alert_id,
        "reviewer": reviewer
    }

def reject_alert(alert_id, reviewer):

    memory = load_memory()

    for record in reversed(memory):

        if (
            record["alert_id"] == alert_id
            and record.get(
                "review_status"
            ) == "pending"
        ):

            record["approved"] = False

            record["review_status"] = "rejected"

            record["reviewer"] = reviewer

            record[
                "execution_status"
            ] = "rejected"

            record[
                "execution_action"
            ] = (
                "Analyst rejected AI recommendation."
            )

            break

    with open(
        MEMORY_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=2
        )

    return {
        "status": "rejected",
        "alert_id": alert_id,
        "reviewer": reviewer
    }