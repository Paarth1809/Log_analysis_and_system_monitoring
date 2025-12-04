# Project Overview & Workflow

## 1. What is this project?
This is a **Vulnerability Detection System**. It is a security tool designed to automatically scan computer logs, identify the software running on your servers, and check if that software has any known security holes (Vulnerabilities/CVEs).

Think of it like an **automated security guard**:
1. It reads the diary of your servers (Logs).
2. It figures out what programs are running (Parsing).
3. It checks a global list of "wanted criminals" (CVE Database).
4. It alerts you if any of your programs are on that list (Matching & Alerting).

---

## 2. "System Logs" vs "Normalized Logs"
In your dashboard, **they are the same thing**.
- The "Normalized Logs Viewer" you see in the screenshot **IS** displaying your System Logs.
- We call them "Normalized" because they have been cleaned up.
- **Raw Log (Messy):** `Nov 4 03:59:23 server1 sshd[123]: Failed password...`
- **Normalized Log (Clean):** 
  - **Time:** `2025-11-04 03:59:23`
  - **Host:** `server1`
  - **Software:** `sshd`
  - **Message:** `Failed password...`

So, when you click "System Logs" in the menu, it shows you this exact "Normalized Logs" table.

---

## 3. Full Step-by-Step Process (The Pipeline)

Here is exactly what happens from start to finish when you run the project:

### **Phase 1: Ingestion (The "Reading" Phase)**
*   **Input:** The system takes raw log files (like `syslog.log`, `auth.log`, `sysmon.json`) from the `datasets/` folder.
*   **Action:** The **Parser Script** (`parser.py`) reads these messy text files line-by-line.
*   **Output:** It converts them into clean JSON objects.

### **Phase 2: Normalization (The "Cleaning" Phase)**
*   **Input:** The clean JSON objects from Phase 1.
*   **Action:** The **Insert Script** (`insert_to_mongo.py`) validates the data (checking for timestamps, hostnames) and removes duplicates.
*   **Output:** It saves these clean, structured logs into your **MongoDB database** (`normalized_logs` collection). *This is what you see on your dashboard now.*

### **Phase 3: Detection (The "Matching" Phase)**
*   **Input:** The normalized logs from the database AND the **CVE Database** (a list of all known software vulnerabilities).
*   **Action:** The **Matcher Script** (`matcher.py`) compares the two.
    *   *Example:* It sees "Linux Kernel 5.4.0" in a log. It checks the CVE list. If "Linux Kernel 5.4.0" is listed as having a security flaw, it flags it.
*   **Output:** If a match is found, it creates a "Vulnerability Match" record. *Currently, this is empty because your sample logs don't have vulnerable versions.*

### **Phase 4: Alerting (The "Notification" Phase)**
*   **Input:** The matches found in Phase 3.
*   **Action:** The **Alert Script** (future step) would generate a high-priority alert, send an email, or show a red warning on your dashboard.
*   **Output:** You see "System Alerts" on the dashboard.

---

## Summary for Manager
"This system automates the process of log analysis. It ingests raw server logs, cleans and structures them ('Normalization'), and then cross-references the software versions found in those logs against a global database of known vulnerabilities (CVEs). If a vulnerable version is detected, it triggers an alert, allowing us to patch the system before an attacker exploits it."
