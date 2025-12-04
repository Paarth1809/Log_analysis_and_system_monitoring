import re
from datetime import datetime

# ------------------------------------------------------------
# NORMALIZATION UTILITIES
# ------------------------------------------------------------

def normalize_timestamp(ts: str):
    """
    Convert various timestamp formats to:
    YYYY-MM-DD HH:MM:SS
    """

    # Replace T with space, remove Z if present
    ts = ts.replace("T", " ").replace("Z", "")

    # Try known formats
    known_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%b %d %H:%M:%S",           # syslog (missing year)
        "%Y-%m-%d",                 # fallback
    ]

    for fmt in known_formats:
        try:
            dt = datetime.strptime(ts, fmt)

            # If no year in syslog, assign 2025
            if fmt == "%b %d %H:%M:%S":
                dt = dt.replace(year=2025)

            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            continue

    # last fallback — return raw
    return ts


def normalize_os(os_field: str):
    os_field = (os_field or "").lower().strip()

    if "win" in os_field:
        return "Windows"
    if "linux" in os_field:
        return "Linux"
    if "ubuntu" in os_field:
        return "Linux"
    if "debian" in os_field:
        return "Linux"

    if os_field == "":
        return "Unknown"

    return os_field.capitalize()


def normalize_software(name: str):
    """
    Clean common software names
    """
    if not name:
        return "Unknown"

    name = name.lower().strip()

    replacements = {
        "sshd": "sshd",
        "systemd": "systemd",
        "cron": "cron",
        "sysmon": "Sysmon",
        "dns": "DNS",
        "http": "HTTP",
    }

    for key, value in replacements.items():
        if key in name:
            return value

    return name.capitalize()


def clean_message(msg: str):
    return (msg or "").strip()


# ------------------------------------------------------------
# FULL NORMALIZE FUNCTION
# ------------------------------------------------------------

def normalize_log(parsed: dict):
    """
    Takes parsed JSON from parser.py
    returns fully normalized log
    """

    if not parsed:
        return None

    normalized = {}

    # Timestamp
    normalized["timestamp"] = normalize_timestamp(parsed.get("timestamp", ""))

    # Host
    normalized["host"] = parsed.get("host", "").strip()

    # OS
    normalized["os"] = normalize_os(parsed.get("os", ""))

    # Software / Service name
    normalized["software"] = normalize_software(parsed.get("software", ""))

    # Version (keep raw)
    normalized["version"] = (parsed.get("version", "") or "").strip()

    # Event type
    normalized["event_type"] = (parsed.get("event_type", "") or "").lower().replace(" ", "_")

    # Message
    normalized["message"] = clean_message(parsed.get("message", ""))

    # Source (syslog/auth/sysmon/http/etc.)
    normalized["source"] = parsed.get("source", "").lower().strip()

    return normalized


# ------------------------------------------------------------
# TEST BLOCK
# ------------------------------------------------------------
if __name__ == "__main__":
    import json

    sample = {
        "timestamp": "2025-11-09 13:45:12",
        "host": "server1",
        "os": "Linux",
        "software": "sshd",
        "version": "N/A",
        "event_type": "syslog_event",
        "message": "Accepted password for root",
        "source": "syslog"
    }

    print("\n--- Normalized Output (JSON Format) ---")
    print(json.dumps(normalize_log(sample), indent=4))

