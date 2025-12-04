from datetime import datetime

# ------------------------------------------------------------
# Required fields for normalized logs
# ------------------------------------------------------------

REQUIRED_FIELDS = [
    "timestamp",
    "host",
    "os",
    "software",
    "version",
    "event_type",
    "message",
    "source"
]

# ------------------------------------------------------------
# Timestamp formats allowed
# ------------------------------------------------------------

VALID_TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",          # Normalized syslog/auth/http/dns
    "%Y-%m-%d %H:%M:%S.%f",      # JSON events with microseconds
]


# ------------------------------------------------------------
# VALIDATION FUNCTION
# ------------------------------------------------------------

def validate_log(log: dict):
    """
    Validates a normalized log before inserting into MongoDB.
    Ensures:
        - required fields exist
        - no empty values
        - timestamp is valid
    """

    if not log:
        raise ValueError("Log object is empty or None")

    # 1. Check required fields exist
    missing = [field for field in REQUIRED_FIELDS if field not in log]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # 2. Check no empty string values
    empty_fields = [field for field, value in log.items() if value in ["", None]]
    if empty_fields:
        raise ValueError(f"Empty or null values in: {empty_fields}")

    # 3. Validate timestamp format
    ts = log["timestamp"]
    valid_timestamp = False

    for fmt in VALID_TIMESTAMP_FORMATS:
        try:
            datetime.strptime(ts, fmt)
            valid_timestamp = True
            break
        except:
            continue

    if not valid_timestamp:
        raise ValueError(f"Invalid timestamp format: {ts}")

    return True


# ------------------------------------------------------------
# TEST BLOCK
# ------------------------------------------------------------
if __name__ == "__main__":
    sample_good = {
        "timestamp": "2025-11-09 13:45:12",
        "host": "server1",
        "os": "Linux",
        "software": "sshd",
        "version": "N/A",
        "event_type": "syslog_event",
        "message": "Accepted password for root",
        "source": "syslog"
    }

    sample_bad = {
        "timestamp": "",
        "host": "server1",
        "os": "Linux",
        "software": "sshd",
        "version": "N/A",
        "event_type": "syslog_event",
        "message": "",
        "source": "syslog"
    }

    print("Testing valid log:")
    try:
        print(validate_log(sample_good))
    except Exception as e:
        print("Error:", e)

    print("\nTesting invalid log:")
    try:
        print(validate_log(sample_bad))
    except Exception as e:
        print("Error:", e)
