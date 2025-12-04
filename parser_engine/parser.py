<<<<<<< HEAD
def main(payload=None):
    print("[INFO] Skipping raw log parsing. Using pre-parsed dataset: data/soc_logs.events.json")
    return {"status": "skipped", "reason": "using_preparsed_dataset"}

if __name__ == "__main__":
    main()
=======
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# ------------------------------------------------------------
# 1. REGEX PATTERNS FOR AUTO-DETECTION
# ------------------------------------------------------------

# Linux Syslog Format
SYSLOG_REGEX = re.compile(
    r'^(?P<month>\w{3})\s+'
    r'(?P<day>\d{1,2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
    r'(?P<host>\S+)\s+'
    r'(?P<service>[a-zA-Z0-9_\-]+)\[\d+\]:\s+'
    r'(?P<message>.*)$'
)

# Linux Auth Format
AUTH_REGEX = re.compile(
    r'^(?P<timestamp>[\d\-T:]+)\s+(?P<host>\S+)\s+sshd\[\d+\]:\s+(?P<message>.*)$'
)

MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}


# ------------------------------------------------------------
# 2. AUTO-DETECT FUNCTIONS
# ------------------------------------------------------------

def is_syslog(line: str) -> bool:
    return bool(SYSLOG_REGEX.match(line))


def is_authlog(line: str) -> bool:
    return bool(AUTH_REGEX.match(line))


def is_sysmon_json(line: str) -> bool:
    try:
        obj = json.loads(line)
        return "EventID" in obj and "TimeCreated" in obj
    except:
        return False


def is_elastic_json(line: str) -> bool:
    try:
        obj = json.loads(line)
        return "@timestamp" in obj
    except:
        return False


def is_http_log(line: str) -> bool:
    parts = line.split("\t")
    return len(parts) == 7


def is_dns_log(line: str) -> bool:
    parts = line.split("\t")
    return len(parts) == 5


def is_windows_xml(content: str) -> bool:
    return "<Events>" in content or "<Event>" in content


# ------------------------------------------------------------
# 3. PARSERS
# ------------------------------------------------------------

def parse_syslog(line: str):
    match = SYSLOG_REGEX.match(line)
    if not match:
        return None

    month = MONTH_MAP.get(match.group("month"), "01")
    day = match.group("day").zfill(2)
    time = match.group("time")
    year = "2025"

    timestamp = f"{year}-{month}-{day} {time}"

    return {
        "timestamp": timestamp,
        "host": match.group("host"),
        "os": "Linux",
        "software": match.group("service"),
        "version": "N/A",
        "event_type": "syslog_event",
        "message": match.group("message"),
        "source": "syslog"
    }


def parse_authlog(line: str):
    match = AUTH_REGEX.match(line)
    if not match:
        return None
    
    return {
        "timestamp": match.group("timestamp").replace("T", " "),
        "host": match.group("host"),
        "os": "Linux",
        "software": "sshd",
        "version": "N/A",
        "event_type": "auth_event",
        "message": match.group("message"),
        "source": "authlog"
    }


def parse_sysmon_json(line: str):
    try:
        obj = json.loads(line)
        return {
            "timestamp": obj.get("TimeCreated", "2025-01-01 00:00:00"),
            "host": obj.get("Computer", "WIN-HOST"),
            "os": "Windows",
            "software": obj.get("ProcessName", "Unknown"),
            "version": "N/A",
            "event_type": f"Sysmon_Event_{obj.get('EventID', '0')}",
            "message": obj.get("CommandLine", ""),
            "source": "sysmon"
        }
    except:
        return None


def parse_elastic_json(line: str):
    try:
        obj = json.loads(line)
        return {
            "timestamp": obj.get("@timestamp", "").replace("T", " ").replace("Z", ""),
            "host": obj.get("host", "unknown"),
            "os": "Linux",
            "software": obj.get("event", {}).get("module", "system"),
            "version": "N/A",
            "event_type": obj.get("event", {}).get("dataset", "elastic_event"),
            "message": obj.get("message", ""),
            "source": "elastic"
        }
    except:
        return None


def parse_http_log(line: str):
    parts = line.split("\t")
    if len(parts) != 7:
        return None

    return {
        "timestamp": parts[0].replace("T", " ").replace("Z", ""),
        "host": parts[1],
        "os": "Linux",
        "software": "http",
        "version": "N/A",
        "event_type": "http_event",
        "message": f"{parts[3]} {parts[4]} (status {parts[5]})",
        "source": "http"
    }


def parse_dns_log(line: str):
    parts = line.split("\t")
    if len(parts) != 5:
        return None

    return {
        "timestamp": parts[0],
        "host": parts[1],
        "os": "Linux",
        "software": "dns",
        "version": "N/A",
        "event_type": "dns_event",
        "message": f"Queried {parts[2]} type {parts[3]} -> {parts[4]}",
        "source": "dns"
    }


def parse_windows_xml(file_path: str):
    parsed_logs = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    for event in root.findall("Event"):
        ts = event.find("./System/TimeCreated").attrib.get("SystemTime", "")
        eid = event.find("./System/EventID").text
        user = event.find("./EventData/Data[@Name='TargetUserName']").text

        parsed_logs.append({
            "timestamp": ts.replace("T", " ").replace("Z", ""),
            "host": "WIN-SERVER",
            "os": "Windows",
            "software": "SecurityEvent",
            "version": "N/A",
            "event_type": f"Security_{eid}",
            "message": f"Event for user: {user}",
            "source": "winxml"
        })

    return parsed_logs


# ------------------------------------------------------------
# 4. FILE PARSER
# ------------------------------------------------------------

def parse_file(input_path, output_path):
    print(f"\n[+] Parsing: {input_path}")

    if input_path.endswith(".xml"):
        logs = parse_windows_xml(input_path)
        with open(output_path, "w", encoding="utf-8") as outfile:
            for log in logs:
                outfile.write(json.dumps(log) + "\n")
        print(f"[✓] Parsed Windows XML → {len(logs)} logs")
        return

    parsed_count = 0
    total = 0

    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:

        for line in infile:
            total += 1
            line = line.strip()

            parsed = None

            if is_syslog(line):
                parsed = parse_syslog(line)
            elif is_authlog(line):
                parsed = parse_authlog(line)
            elif is_sysmon_json(line):
                parsed = parse_sysmon_json(line)
            elif is_elastic_json(line):
                parsed = parse_elastic_json(line)
            elif is_http_log(line):
                parsed = parse_http_log(line)
            elif is_dns_log(line):
                parsed = parse_dns_log(line)

            if parsed:
                outfile.write(json.dumps(parsed) + "\n")
                parsed_count += 1

    print(f"[✓] Total lines: {total}")
    print(f"[✓] Parsed lines: {parsed_count}")
    print(f"[✓] Output saved → {output_path}")


# ------------------------------------------------------------
# 5. MAIN ENTRY (RUN ALL DATASETS)
# ------------------------------------------------------------

if __name__ == "__main__":
    datasets = {
        "linux_syslog": ("datasets/linux/syslog.log", "parser_engine/out_syslog.jsonl"),
        "linux_auth": ("datasets/linux/auth.log", "parser_engine/out_auth.jsonl"),
        "sysmon": ("datasets/windows/sysmon.jsonl", "parser_engine/out_sysmon.jsonl"),
        "windows_security": ("datasets/windows/security.xml", "parser_engine/out_security.jsonl"),
        "http": ("datasets/misc/http.log", "parser_engine/out_http.jsonl"),
        "dns": ("datasets/misc/dns.log", "parser_engine/out_dns.jsonl"),
        "elastic": ("datasets/misc/elastic_events.jsonl", "parser_engine/out_elastic.jsonl"),
    }

    for name, (inp, outp) in datasets.items():
        try:
            parse_file(inp, outp)
        except Exception as e:
            print(f"[!] Error parsing {name}: {e}")
>>>>>>> cd260ba9258ba3c2c7ffb1588424565f3f1c9eae
