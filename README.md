# 🛡️ SynapScan — Intelligent Network Scanning, Redefined

A professional network port scanner built with Python and Streamlit. Designed for both security professionals and beginners — no technical knowledge required to use.

---

## 📸 Features

### 🎯 Scanner
- Scan any IP address, hostname, or domain
- 6 built-in scan profiles (Quick, Standard, Extended, Full, Web, Database)
- Custom port range support
- Real-time live terminal output
- Nmap-equivalent command preview

### 🔓 Results & Risk
- Clean structured table of all open ports
- Risk levels: **Critical / High / Medium / Low / Info**
- Known CVE (vulnerability) hints per service
- Export results as **CSV, JSON, or TXT**

### 🧠 Smart Analysis
- Automatic AI-style analysis using pure Python — no API needed
- Plain English explanation of every open port
- Overall risk rating with summary
- Specific recommendations to fix each issue
- Anomaly detection (backdoors, suspicious port combinations)

### 🔬 Case Notes
- Save investigator notes on any scan
- Label scans by case name
- Export individual cases as JSON or TXT
- Delete old scans

### 🔍 Change Detection
- Compare any two scans side by side
- Highlights newly opened ports (potential security breach)
- Highlights closed ports
- Perfect for monitoring a target over time

---

## 🚀 How to Run

### 1. Install the requirement
```bash
pip install streamlit
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Open in browser
The app opens automatically at `http://localhost:8501`

---

## 🖥️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| Streamlit | Web UI framework |
| Socket | Port scanning engine |
| Threading | Parallel scanning |
| SQLite | Scan history storage |

---

## ⚠️ Legal Disclaimer

This tool is intended for **educational purposes** and **authorized security testing only**.

> Only scan systems you own or have **explicit written permission** to scan.
> Unauthorized port scanning may be illegal in your jurisdiction.

---

## 👩‍💻 Author

Made by **Shatakshi**
Project: Network Security Scanner — Academic / Portfolio Project
