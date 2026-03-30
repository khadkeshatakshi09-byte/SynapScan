import streamlit as st
import socket
import threading
import time
import queue
import json
import csv
import io
import ipaddress
import sqlite3
from datetime import datetime

import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(
    page_title="SynapScan ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Sora:wght@700;800&display=swap');

:root {
    --bg:      #0d1117;
    --s1:      #161b27;
    --s2:      #1c2333;
    --s3:      #21283a;
    --blue:    #3b82f6;
    --blue-d:  #2563eb;
    --green:   #22c55e;
    --red:     #ef4444;
    --orange:  #f97316;
    --yellow:  #eab308;
    --purple:  #a855f7;
    --cyan:    #06b6d4;
    --text:    #e2e8f0;
    --text2:   #94a3b8;
    --border:  #1e293b;
    --border2: #2d3748;
}

html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1400px !important; }

section[data-testid="stSidebar"] {
    background: var(--s1) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: var(--s2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 0.55rem 0.8rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}

.stButton > button {
    background: var(--blue) !important;
    border: none !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.15s !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}
.stButton > button:hover {
    background: var(--blue-d) !important;
    box-shadow: 0 4px 14px rgba(59,130,246,0.35) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background: var(--s2) !important;
    border-color: var(--border2) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--s1) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    border: none !important;
    padding: 0.7rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
    font-weight: 600 !important;
}

.streamlit-expanderHeader {
    background: var(--s2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

.card {
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text2);
    margin-bottom: 1rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border);
}

.terminal {
    background: #070b10;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.3rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    height: 280px;
    overflow-y: auto;
    line-height: 1.9;
}

.scan-table { width: 100%; border-collapse: collapse; }
.scan-table th {
    background: var(--s2);
    color: var(--text2);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 0.65rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.scan-table td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
    font-size: 13px;
}
.scan-table tr:last-child td { border-bottom: none; }
.scan-table tr:hover td { background: rgba(59,130,246,0.04); }

.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 9px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    white-space: nowrap;
}
.b-critical { background: rgba(239,68,68,0.12);  color: #ef4444; }
.b-high     { background: rgba(249,115,22,0.12); color: #f97316; }
.b-medium   { background: rgba(234,179,8,0.12);  color: #ca8a04; }
.b-low      { background: rgba(34,197,94,0.12);  color: #16a34a; }
.b-info     { background: rgba(6,182,212,0.12);  color: #0891b2; }
.b-open     { background: rgba(34,197,94,0.1);   color: #16a34a; }
.b-new      { background: rgba(168,85,247,0.12); color: #9333ea; }
.b-closed   { background: rgba(100,116,139,0.12);color: #64748b; }

.prog-track { background: var(--s3); border-radius: 99px; height: 5px; overflow: hidden; }
.prog-bar   { background: linear-gradient(90deg, #3b82f6, #06b6d4); height: 100%; border-radius: 99px; transition: width 0.4s ease; }

.metric-tile {
    background: var(--s1);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1rem;
    text-align: center;
}
.metric-tile .val { font-family: 'Sora', sans-serif; font-size: 2rem; font-weight: 800; display: block; line-height: 1.1; margin-bottom: 4px; }
.metric-tile .lbl { font-size: 11px; color: var(--text2); font-weight: 500; letter-spacing: 0.2px; }

.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px; border-radius: 99px; font-size: 12px; font-weight: 600;
}
.pill-idle { background: var(--s2); color: var(--text2); }
.pill-scan { background: rgba(59,130,246,0.12); color: #3b82f6; }
.pill-done { background: rgba(34,197,94,0.12);  color: #16a34a; }
.pill-stop { background: rgba(249,115,22,0.12); color: #f97316; }
.pulse { animation: blink 1s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

.ai-box {
    background: var(--s1);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue);
    border-radius: 0 10px 10px 0;
    padding: 1.3rem 1.5rem;
    font-size: 13.5px;
    line-height: 1.85;
    color: var(--text);
}
.ai-box h2, .ai-box h3 { color: var(--text); font-size: 14px; font-weight: 600; margin: 1rem 0 0.4rem; }
.ai-box ul { padding-left: 1.2rem; }
.ai-box li { margin-bottom: 0.3rem; }
.ai-box strong { color: #e2e8f0; }

.cmd-box {
    background: #070b10;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.65rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #22c55e;
    margin-top: 0.5rem;
    word-break: break-all;
}

.hint-box {
    background: rgba(59,130,246,0.06);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 13px;
    color: var(--text2);
    margin-bottom: 1rem;
}
.hint-box strong { color: var(--blue); }

.app-header {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.2rem 0 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.3rem;
}
.app-logo { font-family: 'Sora', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text); }
.app-logo .hl { color: var(--blue); }
.app-tagline { font-size: 12px; color: var(--text2); margin-top: 2px; }
.chip {
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.22);
    color: var(--blue);
    border-radius: 99px;
    padding: 3px 11px;
    font-size: 11px;
    font-weight: 600;
}
.chip-green {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.22);
    color: #16a34a;
    border-radius: 99px;
    padding: 3px 11px;
    font-size: 11px;
    font-weight: 600;
}

.note-box {
    background: var(--s2); border: 1px solid var(--border);
    border-radius: 8px; padding: 0.85rem 1rem;
    font-size: 13px; color: var(--text2); white-space: pre-wrap;
}
.hist-row {
    background: var(--s1); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 1rem;
    transition: border-color 0.15s, background 0.15s;
}
.hist-row:hover { border-color: var(--blue); background: var(--s2); }

.section-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.6px;
    text-transform: uppercase; color: var(--text2);
    margin-bottom: 0.6rem;
}

.empty-state {
    text-align: center; padding: 4rem 2rem; color: var(--text2);
}
.empty-state .icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
.empty-state p { font-size: 14px; margin: 0; }

label { color: var(--text2) !important; font-size: 12px !important; font-weight: 500 !important; }
.stAlert { border-radius: 8px !important; font-size: 13px !important; }
hr { border-color: var(--border) !important; margin: 0.8rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════
COMMON_PORTS = {
    21:'FTP', 22:'SSH', 23:'Telnet', 25:'SMTP', 53:'DNS',
    80:'HTTP', 110:'POP3', 135:'MSRPC', 139:'NetBIOS', 143:'IMAP',
    161:'SNMP', 389:'LDAP', 443:'HTTPS', 445:'SMB',
    465:'SMTPS', 587:'SMTP-Sub', 636:'LDAPS', 993:'IMAPS', 995:'POP3S',
    1433:'MSSQL', 1521:'Oracle', 2049:'NFS', 2222:'SSH-Alt',
    3000:'Dev-Server', 3306:'MySQL', 3389:'RDP', 4444:'Backdoor',
    5000:'Flask', 5432:'PostgreSQL', 5900:'VNC', 5985:'WinRM',
    6379:'Redis', 8080:'HTTP-Alt', 8443:'HTTPS-Alt', 8888:'Jupyter',
    9200:'Elasticsearch', 11211:'Memcached', 27017:'MongoDB',
    6000:'X11', 9090:'Prometheus', 9100:'Printer',
}

RISK_DB = {
    'Backdoor':      ('CRITICAL','⛔ Known backdoor port. Shut down immediately and investigate.'),
    'Telnet':        ('CRITICAL','⛔ Sends all data in plaintext. Replace with SSH right away.'),
    'VNC':           ('HIGH',    '🔓 Remote desktop — ensure a strong password and use VPN.'),
    'RDP':           ('HIGH',    '🔓 Frequently targeted by hackers. Use VPN and strong auth.'),
    'SMB':           ('HIGH',    '🔓 Used in major ransomware attacks. Ensure fully patched.'),
    'FTP':           ('HIGH',    '🔓 Sends passwords in plaintext. Switch to SFTP instead.'),
    'X11':           ('HIGH',    '🔓 Can leak screen data. Restrict access immediately.'),
    'Memcached':     ('HIGH',    '🔓 No password by default. Used in large-scale attacks.'),
    'Redis':         ('HIGH',    '🔓 No password by default. Restrict to local access only.'),
    'Jupyter':       ('HIGH',    '🔓 Often has no login. Never expose this to the internet.'),
    'Flask':         ('HIGH',    '🔓 Development server. Should never be publicly accessible.'),
    'Dev-Server':    ('HIGH',    '🔓 Development server is public. Remove or restrict access.'),
    'Elasticsearch': ('HIGH',    '🔓 No authentication by default. Check if data is exposed.'),
    'WinRM':         ('HIGH',    '🔓 Windows remote management. Block from external access.'),
    'NetBIOS':       ('MEDIUM',  '⚠️ Old Windows protocol. Disable if not actively used.'),
    'MSRPC':         ('MEDIUM',  '⚠️ Windows RPC service. Should not face the internet.'),
    'LDAP':          ('MEDIUM',  '⚠️ Directory service. Use encrypted version (LDAPS, port 636).'),
    'MongoDB':       ('MEDIUM',  '⚠️ Database — make sure a password is set.'),
    'MySQL':         ('MEDIUM',  '⚠️ Database port is public. Should only be local.'),
    'MSSQL':         ('MEDIUM',  '⚠️ Database port is public. Restrict with a firewall.'),
    'PostgreSQL':    ('MEDIUM',  '⚠️ Database port is public. Should only be local.'),
    'Oracle':        ('MEDIUM',  '⚠️ Database port is public. Verify access is restricted.'),
    'SNMP':          ('MEDIUM',  '⚠️ Old version uses weak passwords. Upgrade to SNMPv3.'),
    'NFS':           ('MEDIUM',  '⚠️ File sharing service. Should not be publicly exposed.'),
    'Prometheus':    ('MEDIUM',  '⚠️ Exposes system metrics. Restrict to internal use only.'),
    'HTTP':          ('LOW',     'ℹ️ Unencrypted website. Redirect users to HTTPS.'),
    'HTTP-Alt':      ('LOW',     'ℹ️ Alternate web port. Check what service is running here.'),
    'HTTPS-Alt':     ('LOW',     'ℹ️ Alternate secure web port. Verify intended service.'),
    'SSH':           ('LOW',     'ℹ️ Secure remote access. Use key-based login, disable root.'),
    'SSH-Alt':       ('LOW',     'ℹ️ SSH on non-standard port. Verify this is intentional.'),
    'SMTP':          ('LOW',     'ℹ️ Email server. Ensure it cannot be used as an open relay.'),
    'SMTPS':         ('INFO',    '✅ Encrypted email. Good configuration.'),
    'SMTP-Sub':      ('LOW',     'ℹ️ Email submission port. Require authentication.'),
    'DNS':           ('LOW',     'ℹ️ DNS service. Restrict who can request zone transfers.'),
    'POP3':          ('LOW',     'ℹ️ Email retrieval. Use the encrypted version POP3S (995).'),
    'POP3S':         ('INFO',    '✅ Encrypted email retrieval. Good configuration.'),
    'IMAP':          ('LOW',     'ℹ️ Email access. Use the encrypted version IMAPS (993).'),
    'IMAPS':         ('INFO',    '✅ Encrypted email access. Good configuration.'),
    'LDAPS':         ('INFO',    '✅ Encrypted directory service. Good configuration.'),
    'HTTPS':         ('INFO',    '✅ Encrypted web traffic. Standard and expected.'),
    'Printer':       ('LOW',     'ℹ️ Network printer. Keep this on the local network only.'),
    'Unknown':       ('INFO',    'ℹ️ Unknown service. Check what is running on this port.'),
}

CVE_DB = {
    'SMB':           ['CVE-2017-0144 (EternalBlue / WannaCry)', 'CVE-2020-0796 (SMBGhost)'],
    'RDP':           ['CVE-2019-0708 (BlueKeep)', 'CVE-2020-0609 (DejaBlue)'],
    'FTP':           ['Anonymous login enabled', 'CVE-2011-2523 (vsftpd backdoor)'],
    'Telnet':        ['All credentials sent in plaintext', 'Susceptible to man-in-the-middle attacks'],
    'MSSQL':         ['CVE-2020-0618 (RCE)', 'Default SA account brute-force'],
    'MySQL':         ['CVE-2012-2122 (auth bypass)', 'Unauthenticated data access'],
    'Redis':         ['CVE-2022-0543 (code execution)', 'Unauthenticated remote access'],
    'Elasticsearch': ['CVE-2021-44228 (Log4Shell)', 'Unauthenticated data read/write'],
    'MongoDB':       ['CVE-2013-4650', 'No-auth admin access if misconfigured'],
    'VNC':           ['CVE-2019-15681 (info leak)', 'Weak or empty password auth'],
    'SNMP':          ['CVE-2002-0013', 'Community string brute-force (public/private)'],
    'Memcached':     ['CVE-2018-1000115', 'Used for massive UDP DDoS amplification'],
    'Jupyter':       ['Unauthenticated remote code execution via notebook'],
    'Backdoor':      ['Active backdoor or attacker C2 channel — treat as compromised'],
    'WinRM':         ['CVE-2021-31166', 'Lateral movement using PowerShell Remoting'],
}

RISK_ORDER = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
RISK_ICON  = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': '🔵'}

SCAN_PROFILES = {
    "⚡  Quick  (ports 1–1,024)":      {"start": 1,     "end": 1024,  "timeout": 0.3, "threads": 400,
                                         "desc": "Fast scan of all common ports. Best for a quick first look."},
    "🔍  Standard  (ports 1–1,024)":   {"start": 1,     "end": 1024,  "timeout": 0.5, "threads": 500,
                                         "desc": "Thorough scan of all well-known service ports."},
    "📡  Extended  (ports 1–10,000)":  {"start": 1,     "end": 10000, "timeout": 0.5, "threads": 500,
                                         "desc": "Covers common + less-known ports used by many services."},
    "🌐  Full  (all 65,535 ports)":    {"start": 1,     "end": 65535, "timeout": 0.5, "threads": 500,
                                         "desc": "Complete scan. Can take several minutes on large targets."},
    "🌍  Web  (HTTP & HTTPS ports)":   {"start": 80,    "end": 8888,  "timeout": 0.4, "threads": 200,
                                         "desc": "Finds web servers, APIs, and web-based admin panels."},
    "🗄️  Database  (DB ports only)":   {"start": 1433,  "end": 27017, "timeout": 0.4, "threads": 100,
                                         "desc": "Checks for exposed databases — MySQL, MongoDB, Redis, etc."},
    "✏️  Custom range":                {"start": None,  "end": None,  "timeout": 0.5, "threads": 500,
                                         "desc": "Specify your own port range."},
}

DB_FILE = "synapscan.db"

# ══════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT, resolved_ip TEXT, port_range TEXT,
        open_ports TEXT, timestamp TEXT,
        elapsed REAL, notes TEXT, case_name TEXT)""")
    conn.commit(); conn.close()

def save_scan(target, resolved_ip, port_range, open_ports, elapsed, notes="", case_name=""):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO scans VALUES (NULL,?,?,?,?,?,?,?,?)",
        (target, resolved_ip, port_range, json.dumps(open_ports),
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), elapsed, notes, case_name))
    conn.commit(); conn.close()

def load_history(limit=50):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    cols = ['id','target','resolved_ip','port_range','open_ports','timestamp','elapsed','notes','case_name']
    result = []
    for r in rows:
        d = dict(zip(cols, r))
        d['open_ports'] = json.loads(d['open_ports']) if isinstance(d['open_ports'], str) else d['open_ports']
        result.append(d)
    return result

def load_by_id(sid):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute("SELECT * FROM scans WHERE id=?", (sid,)).fetchone()
    conn.close()
    if not row: return None
    cols = ['id','target','resolved_ip','port_range','open_ports','timestamp','elapsed','notes','case_name']
    d = dict(zip(cols, row))
    d['open_ports'] = json.loads(d['open_ports']) if isinstance(d['open_ports'], str) else d['open_ports']
    return d

def update_notes(sid, notes):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE scans SET notes=? WHERE id=?", (notes, sid))
    conn.commit(); conn.close()

def delete_scan(sid):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM scans WHERE id=?", (sid,))
    conn.commit(); conn.close()

init_db()

# ══════════════════════════════════════════════════════════════════════
# SCANNER ENGINE
# ══════════════════════════════════════════════════════════════════════
class PortScanner:
    def __init__(self, target, sp, ep, timeout=0.5, workers=500):
        self.target = target
        self.start_port = sp; self.end_port = ep
        self.timeout = timeout; self.max_workers = workers
        self._stop = threading.Event()
        self.total_ports = max(0, ep - sp + 1)
        self.scanned_count = 0; self.open_ports = []
        self._lock = threading.Lock()
        self.result_queue = queue.Queue()

    def stop(self): self._stop.set()

    def _scan(self, port):
        if self._stop.is_set(): return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            if s.connect_ex((self.target, port)) == 0:
                svc = COMMON_PORTS.get(port, 'Unknown')
                with self._lock: self.open_ports.append((port, svc))
                self.result_queue.put(('open', port, svc))
            s.close()
        except Exception: pass
        finally:
            with self._lock: self.scanned_count += 1
            self.result_queue.put(('progress', self.scanned_count, self.total_ports))

    def run(self):
        sem = threading.Semaphore(self.max_workers); threads = []
        for port in range(self.start_port, self.end_port + 1):
            if self._stop.is_set(): break
            sem.acquire()
            t = threading.Thread(target=self._wrap, args=(sem, port), daemon=True)
            threads.append(t); t.start()
        for t in threads: t.join()
        self.result_queue.put(('done', None, None))

    def _wrap(self, sem, port):
        try: self._scan(port)
        finally: sem.release()

# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════
def get_risk(svc):
    return RISK_DB.get(svc, ('INFO', 'ℹ️ Unknown service. Check what is running here.'))

def valid_target(t):
    try: socket.gethostbyname(t); return True
    except: pass
    try: ipaddress.ip_network(t, strict=False); return True
    except: return False

def resolve(t):
    return socket.gethostbyname(t)

def compare_scans(old, new):
    o = {(p, s) for p, s in old}
    n = {(p, s) for p, s in new}
    return sorted(n - o), sorted(o - n), sorted(o & n)

# ── Rule-based AI analysis (no API needed) ──
def analyze_ports(open_ports, target):
    if not open_ports:
        return {
            "summary": "No open ports were found on this target in the scanned range.",
            "risk_rating": "LOW",
            "findings": [],
            "recommendations": ["Consider scanning a wider port range to be thorough."],
            "anomalies": [],
        }

    counts = {}
    for _, s in open_ports:
        r = get_risk(s)[0]; counts[r] = counts.get(r, 0) + 1

    overall = "CRITICAL" if counts.get("CRITICAL") else "HIGH" if counts.get("HIGH") else "MEDIUM" if counts.get("MEDIUM") else "LOW"

    findings = []
    for port, svc in sorted(open_ports, key=lambda x: RISK_ORDER.get(get_risk(x[1])[0], 99)):
        risk, desc = get_risk(svc)
        cves = CVE_DB.get(svc, [])
        findings.append({"port": port, "service": svc, "risk": risk, "desc": desc, "cves": cves})

    recs = []
    services = {s for _, s in open_ports}
    if "Telnet" in services:
        recs.append("🔴 Disable Telnet immediately — it sends all data including passwords unencrypted. Enable SSH instead.")
    if "Backdoor" in services:
        recs.append("🔴 Port 4444 is open — this is commonly used by malware. Investigate and isolate this machine.")
    if any(s in services for s in ["RDP", "VNC"]):
        recs.append("🟠 Remote desktop is exposed — restrict to VPN access only and use strong passwords.")
    if "SMB" in services:
        recs.append("🟠 SMB is exposed — ensure Windows is fully patched and block this port at the firewall.")
    if "FTP" in services:
        recs.append("🟠 FTP sends credentials in plaintext — switch to SFTP or FTPS.")
    if any(s in services for s in ["MySQL", "PostgreSQL", "MongoDB", "MSSQL", "Redis", "Elasticsearch"]):
        recs.append("🟠 Database ports are publicly accessible — databases should never face the internet. Add a firewall rule to block external access.")
    if "HTTP" in services and "HTTPS" not in services:
        recs.append("🟡 HTTP is open but HTTPS is not detected — set up an SSL certificate and redirect all traffic to HTTPS.")
    if any(s in services for s in ["Jupyter", "Flask", "Dev-Server"]):
        recs.append("🟠 A development server is publicly exposed — this is dangerous in production. Restrict access immediately.")
    if "SNMP" in services:
        recs.append("🟡 SNMP is open — change default community strings (public/private) and upgrade to SNMPv3.")
    if not recs:
        recs.append("✅ No critical issues found. Continue monitoring and run scans regularly.")
    recs.append("💡 Run scans periodically to detect new open ports early — especially after system changes.")
    recs.append("🔒 Use a firewall to restrict which ports are accessible from the internet.")

    anomalies = []
    if "Backdoor" in services:
        anomalies.append("🚨 Port 4444 is a well-known backdoor/C2 port — possible malware or intrusion detected.")
    if "Telnet" in services and "SSH" in services:
        anomalies.append("⚠️ Both Telnet and SSH are open — Telnet is redundant and dangerous here.")
    if any(s in services for s in ["Flask", "Dev-Server", "Jupyter"]) and "HTTPS" in services:
        anomalies.append("⚠️ Development tools are exposed alongside a production web server — unusual configuration.")
    db_count = sum(1 for s in services if s in ["MySQL","PostgreSQL","MongoDB","MSSQL","Redis","Elasticsearch","Oracle"])
    if db_count >= 2:
        anomalies.append(f"⚠️ {db_count} different database ports are open — this is unusual and risky.")
    if len(open_ports) > 15:
        anomalies.append(f"⚠️ {len(open_ports)} open ports detected — a large attack surface. Review and close unused services.")

    summary_parts = [f"Scan of **{target}** found **{len(open_ports)} open port{'s' if len(open_ports)!=1 else ''}**."]
    if counts.get("CRITICAL"):
        summary_parts.append(f"**{counts['CRITICAL']} critical risk{'s' if counts['CRITICAL']>1 else ''}** require immediate attention.")
    if counts.get("HIGH"):
        summary_parts.append(f"**{counts['HIGH']} high-risk service{'s' if counts['HIGH']>1 else ''}** should be secured soon.")
    if not counts.get("CRITICAL") and not counts.get("HIGH"):
        summary_parts.append("No critical issues detected, but review the findings below.")

    return {
        "summary": " ".join(summary_parts),
        "risk_rating": overall,
        "findings": findings,
        "recommendations": recs,
        "anomalies": anomalies,
    }

def to_txt(sd):
    lines = [
        "=" * 64,
        "  SYNAPSCAN — NETWORK SECURITY SCAN REPORT",
        "=" * 64,
        f"  Target      : {sd['target']}",
        f"  Resolved IP : {sd.get('resolved_ip','N/A')}",
        f"  Port Range  : {sd['port_range']}",
        f"  Scan Date   : {sd['timestamp']}",
        f"  Duration    : {sd['elapsed']:.1f}s",
        f"  Open Ports  : {len(sd['open_ports'])}",
        f"  Case Label  : {sd.get('case_name') or 'N/A'}",
        "", "-" * 64, "  FINDINGS", "-" * 64,
        f"  {'PORT':<8}{'SERVICE':<16}{'RISK':<10}DESCRIPTION",
        "  " + "-" * 60,
    ]
    for p, s in sorted(sd['open_ports']):
        r, n = get_risk(s)
        lines.append(f"  {p:<8}{s:<16}{r:<10}{n}")

    analysis = analyze_ports(sd['open_ports'], sd['target'])
    lines += [
        "", "-" * 64, "  RISK ASSESSMENT", "-" * 64,
        f"  Overall Risk: {analysis['risk_rating']}",
        "", "  Recommendations:",
    ]
    for rec in analysis['recommendations']:
        lines.append(f"  • {rec}")
    if analysis['anomalies']:
        lines += ["", "  Anomalies Detected:"]
        for a in analysis['anomalies']:
            lines.append(f"  ! {a}")

    lines += [
        "", "-" * 64, "  NOTES", "-" * 64,
        f"  {sd.get('notes') or 'No notes.'}",
        "", "=" * 64,
        "  Generated by SynapScan — Intelligent Network Scanning, Redefined",
    ]
    return "\n".join(lines)

def to_json(sd):
    analysis = analyze_ports(sd['open_ports'], sd['target'])
    return json.dumps({
        "meta": {
            "tool": "SynapScan",
            "target": sd['target'],
            "resolved_ip": sd.get('resolved_ip', ''),
            "port_range": sd['port_range'],
            "timestamp": sd['timestamp'],
            "elapsed_seconds": sd['elapsed'],
            "case": sd.get('case_name', ''),
        },
        "summary": {
            "total_open": len(sd['open_ports']),
            "overall_risk": analysis['risk_rating'],
            "critical": sum(1 for _,s in sd['open_ports'] if get_risk(s)[0]=='CRITICAL'),
            "high": sum(1 for _,s in sd['open_ports'] if get_risk(s)[0]=='HIGH'),
            "medium": sum(1 for _,s in sd['open_ports'] if get_risk(s)[0]=='MEDIUM'),
        },
        "findings": [
            {"port": p, "service": s, "risk": get_risk(s)[0],
             "description": get_risk(s)[1], "cves": CVE_DB.get(s, [])}
            for p, s in sorted(sd['open_ports'])
        ],
        "recommendations": analysis['recommendations'],
        "anomalies": analysis['anomalies'],
        "notes": sd.get('notes', ''),
    }, indent=2)

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════
def init_state():
    defs = {
        "scanner": None, "scanner_thread": None,
        "scan_log": [], "open_ports": [],
        "status": "idle", "progress": 0, "total_ports": 0,
        "start_time": None, "elapsed": 0.0, "resolved_ip": "",
        "current_meta": {}, "scan_running": False,
        "analysis": None,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0 1rem;">
        <div style="font-family:'Sora',sans-serif;font-size:1.2rem;font-weight:800;color:#e2e8f0;">
            🛡️ Synap<span style="color:#3b82f6;">Scan</span>
        </div>
        <div style="font-size:11px;color:#4a5568;margin-top:3px;letter-spacing:0.2px;">
            Intelligent Network Scanning, Redefined
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Recent Scans</div>', unsafe_allow_html=True)
    history = load_history(8)
    if history:
        for h in history:
            rc = {}
            for _, s in h['open_ports']:
                r = get_risk(s)[0]; rc[r] = rc.get(r, 0) + 1
            col = "#ef4444" if rc.get('CRITICAL') else "#f97316" if rc.get('HIGH') else "#22c55e"
            badge = (f"{rc.get('CRITICAL',0)} Critical" if rc.get('CRITICAL') else
                     f"{rc.get('HIGH',0)} High" if rc.get('HIGH') else
                     f"{len(h['open_ports'])} open")
            st.markdown(f"""
            <div class="hist-row">
                <div style="flex:1;min-width:0;">
                    <div style="color:#e2e8f0;font-weight:500;font-size:13px;
                         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{h['target']}</div>
                    <div style="color:#4a5568;font-size:11px;font-family:'JetBrains Mono',monospace;">
                        {h['timestamp'][:16]}
                    </div>
                </div>
                <span style="color:{col};font-size:11px;font-weight:600;white-space:nowrap;">{badge}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#4a5568;font-size:12px;padding:0.5rem 0;">No scans yet.</div>', unsafe_allow_html=True)

    st.markdown("""
    <hr>
    <div style="font-size:11px;color:#2d3748;line-height:1.7;text-align:center;">
        ⚠️ Only scan systems you own<br>or have written permission to test.<br>
        Unauthorized scanning may be illegal.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div>
        <div class="app-logo">🛡️ Synap<span class="hl">Scan</span></div>
        <div class="app-tagline">Intelligent Network Scanning, Redefined</div>
    </div>
    <div style="margin-left:auto;"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5 = st.tabs([
    "🎯  Scanner",
    "🔓  Results & Risk",
    "🧠  Smart Analysis",
    "🔬  Case Notes",
    "🔍  Change Detection",
])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — SCANNER
# ══════════════════════════════════════════════════════════════════════
with t1:
    st.markdown("""
    <div class="hint-box">
        <strong>How to use:</strong> Enter a target IP address or website, choose a scan type, and click <strong>Start Scan</strong>.
        Results appear in real time below.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Scan Configuration</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 2])
    with col1:
        target_input = st.text_input(
            "Target IP or Hostname",
            placeholder="e.g.  192.168.1.1   or   scanme.nmap.org",
            help="Enter the IP address or website you want to scan"
        )
    with col2:
        pname = st.selectbox("What do you want to scan?", list(SCAN_PROFILES.keys()))
        profile = SCAN_PROFILES[pname]
        st.markdown(f'<div style="font-size:12px;color:#64748b;margin-top:-0.5rem;">{profile["desc"]}</div>', unsafe_allow_html=True)

    if pname == "✏️  Custom range":
        rc1, rc2 = st.columns(2)
        with rc1: cs = st.number_input("From port", 1, 65535, 1)
        with rc2: ce = st.number_input("To port",   1, 65535, 1024)
        sp, ep = int(cs), int(ce)
    else:
        sp, ep = profile["start"], profile["end"]

    with st.expander("⚙️  Advanced Settings  (optional — defaults work for most users)"):
        st.markdown('<div style="font-size:12px;color:#64748b;margin-bottom:0.8rem;">These settings are pre-configured for best results. Only change them if you know what you are doing.</div>', unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        with a1:
            timeout = st.slider("Connection timeout (seconds)", 0.1, 3.0, float(profile["timeout"]), 0.1,
                                help="How long to wait for each port to respond. Lower = faster but may miss slow hosts.")
        with a2:
            threads = st.slider("Parallel connections", 50, 1000, int(profile["threads"]), 50,
                                help="How many ports to check at the same time. More = faster. Reduce on slow networks.")
        with a3:
            case_name = st.text_input("Scan label (optional)",
                                      placeholder="e.g. Home Router, Client Audit",
                                      help="Give this scan a name to find it easily in history.")

    if target_input:
        st.markdown(f'<div class="cmd-box">Equivalent nmap command: nmap -sT -p {sp}-{ep} {target_input.strip()}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    b1, b2, b3, _ = st.columns([1.8, 1.5, 1.5, 5])
    with b1: start_btn = st.button("▶  Start Scan",  use_container_width=True)
    with b2: stop_btn  = st.button("⏹  Stop Scan",   use_container_width=True)
    with b3: clear_btn = st.button("🗑  Clear Results", use_container_width=True)

    if clear_btn:
        st.session_state.update({
            "scan_log": [], "open_ports": [], "status": "idle",
            "progress": 0, "total_ports": 0, "elapsed": 0.0,
            "scanner": None, "scan_running": False, "analysis": None,
        })
        st.rerun()

    if stop_btn and st.session_state.scanner:
        st.session_state.scanner.stop()
        st.session_state.status = "stopped"
        st.session_state.scan_running = False

    if start_btn:
        tgt = target_input.strip() if target_input else ""
        if not tgt:
            st.error("Please enter a target IP address or hostname before starting the scan.")
        elif sp > ep:
            st.error("The start port must be smaller than the end port.")
        elif not valid_target(tgt):
            st.error(f"Cannot reach '{tgt}'. Please check the address and your network connection.")
        else:
            try: res = resolve(tgt)
            except Exception as e: st.error(f"Could not resolve hostname: {e}"); st.stop()

            st.session_state.update({
                "scan_log": [], "open_ports": [], "analysis": None,
                "status": "scanning", "start_time": time.time(),
                "scan_running": True, "resolved_ip": res,
                "current_meta": {
                    "target": tgt, "resolved_ip": res,
                    "port_range": f"{sp}-{ep}",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "case_name": case_name,
                },
            })
            scanner = PortScanner(tgt, sp, ep, timeout, threads)
            st.session_state.scanner     = scanner
            st.session_state.total_ports = scanner.total_ports
            st.session_state.scan_log    = [
                f"[{datetime.now().strftime('%H:%M:%S')}]  SynapScan started",
                f"[{datetime.now().strftime('%H:%M:%S')}]  Target   →  {tgt}  ({res})",
                f"[{datetime.now().strftime('%H:%M:%S')}]  Range    →  ports {sp} to {ep}  ({scanner.total_ports:,} ports)",
                f"[{datetime.now().strftime('%H:%M:%S')}]  Threads  →  {threads}   Timeout → {timeout}s",
                "",
            ]
            th = threading.Thread(target=scanner.run, daemon=True)
            st.session_state.scanner_thread = th; th.start()

    # Poll results
    if st.session_state.scan_running and st.session_state.scanner:
        scanner = st.session_state.scanner
        try:
            while True:
                msg, a, b = scanner.result_queue.get_nowait()
                if msg == 'open':
                    r, _ = get_risk(b)
                    icon = RISK_ICON.get(r, "⚪")
                    st.session_state.scan_log.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}]  {icon}  Port {a:<6}  {b:<18}  {r}")
                    st.session_state.open_ports.append((a, b))
                elif msg == 'progress':
                    st.session_state.progress = a
                    if st.session_state.start_time:
                        st.session_state.elapsed = time.time() - st.session_state.start_time
                elif msg == 'done':
                    st.session_state.elapsed = time.time() - (st.session_state.start_time or time.time())
                    st.session_state.status = "done"; st.session_state.scan_running = False
                    n = len(st.session_state.open_ports)
                    st.session_state.scan_log += [
                        "",
                        f"[{datetime.now().strftime('%H:%M:%S')}]  ✅  Scan complete — {n} open port{'s' if n!=1 else ''} found",
                        f"[{datetime.now().strftime('%H:%M:%S')}]  ⏱   Total time: {st.session_state.elapsed:.2f}s",
                    ]
                    meta = st.session_state.current_meta
                    save_scan(meta['target'], meta['resolved_ip'], meta['port_range'],
                              st.session_state.open_ports, st.session_state.elapsed, "", case_name)
                    st.session_state.analysis = analyze_ports(st.session_state.open_ports, meta['target'])
                    break
        except queue.Empty: pass

    # Status bar
    status     = st.session_state.status
    prog       = st.session_state.progress
    total      = st.session_state.total_ports
    elapsed    = st.session_state.elapsed
    open_ports = st.session_state.open_ports
    pct        = int(prog / total * 100) if total > 0 else 0

    pcls = {"idle":"pill-idle","scanning":"pill-scan","done":"pill-done","stopped":"pill-stop"}.get(status,"pill-idle")
    plbl = {"idle":"Ready","scanning":"Scanning…","done":"Scan Complete","stopped":"Stopped"}.get(status,"Ready")
    dot  = '<span class="pulse">●</span>' if status == "scanning" else "●"

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;padding:0.8rem 0;margin:0.5rem 0 0.2rem;">
        <span class="status-pill {pcls}">{dot} {plbl}</span>
        <div style="flex:1;">
            <div class="prog-track"><div class="prog-bar" style="width:{pct}%"></div></div>
            <div style="font-size:11px;color:#4a5568;margin-top:3px;font-family:'JetBrains Mono',monospace;">
                {prog:,} of {total:,} ports checked &nbsp;·&nbsp; {pct}% complete
            </div>
        </div>
        <span style="font-size:12px;color:#64748b;font-family:'JetBrains Mono',monospace;white-space:nowrap;">⏱ {elapsed:.1f}s</span>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    crit = sum(1 for _, s in open_ports if get_risk(s)[0] == 'CRITICAL')
    high = sum(1 for _, s in open_ports if get_risk(s)[0] == 'HIGH')
    med  = sum(1 for _, s in open_ports if get_risk(s)[0] == 'MEDIUM')
    low  = sum(1 for _, s in open_ports if get_risk(s)[0] in ('LOW','INFO'))

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(f'<div class="metric-tile"><span class="val" style="color:#3b82f6;">{len(open_ports)}</span><span class="lbl">Open Ports</span></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-tile"><span class="val" style="color:#ef4444;">{crit}</span><span class="lbl">⛔ Critical</span></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-tile"><span class="val" style="color:#f97316;">{high}</span><span class="lbl">🟠 High Risk</span></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-tile"><span class="val" style="color:#ca8a04;">{med}</span><span class="lbl">🟡 Medium</span></div>', unsafe_allow_html=True)
    m5.markdown(f'<div class="metric-tile"><span class="val" style="color:#16a34a;">{low}</span><span class="lbl">🟢 Low / Info</span></div>', unsafe_allow_html=True)

    # Terminal log
    log_html = "<br>".join([
        f'<span style="color:#22c55e;">{l}</span>'   if 'OPEN' in l and '✅' not in l
        else f'<span style="color:#06b6d4;">{l}</span>'  if '✅' in l or 'complete' in l.lower()
        else f'<span style="color:#3b82f6;">{l}</span>'  if 'SynapScan' in l
        else f'<span style="color:#64748b;">{l}</span>'
        for l in st.session_state.scan_log
    ]) or '<span style="color:#2d3748;">// Scan output will appear here when you start a scan…</span>'

    st.markdown(f'<div class="terminal" style="margin-top:0.8rem;">{log_html}</div>', unsafe_allow_html=True)

    if st.session_state.scan_log and status in ("done", "stopped"):
        st.download_button("⬇  Download Scan Log", "\n".join(st.session_state.scan_log),
                           f"synapscan_log_{int(time.time())}.txt", "text/plain")

    if st.session_state.scan_running:
        time.sleep(0.4); st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — RESULTS & RISK
# ══════════════════════════════════════════════════════════════════════
with t2:
    open_ports = st.session_state.open_ports
    if not open_ports:
        st.markdown('<div class="empty-state"><div class="icon">🔍</div><p>No results yet. Run a scan from the <strong>Scanner</strong> tab to see open ports here.</p></div>', unsafe_allow_html=True)
    else:
        fc1, fc2 = st.columns([2, 3])
        with fc1:
            sort_by = st.selectbox("Sort by", [
                "Risk level (most serious first)",
                "Port number (low → high)",
                "Port number (high → low)",
                "Service name (A → Z)",
            ])
        with fc2:
            fil = st.multiselect(
                "Show only these risk levels",
                ["⛔ Critical", "🟠 High", "🟡 Medium", "🟢 Low", "🔵 Info"],
                default=["⛔ Critical", "🟠 High", "🟡 Medium", "🟢 Low", "🔵 Info"],
            )
        fil_map = {"⛔ Critical":"CRITICAL","🟠 High":"HIGH","🟡 Medium":"MEDIUM","🟢 Low":"LOW","🔵 Info":"INFO"}
        fil_set = {fil_map[f] for f in fil}

        sp2 = list(open_ports)
        if "Risk" in sort_by: sp2.sort(key=lambda x: RISK_ORDER.get(get_risk(x[1])[0], 99))
        elif "low → high" in sort_by: sp2.sort(key=lambda x: x[0])
        elif "high → low" in sort_by: sp2.sort(key=lambda x: x[0], reverse=True)
        else: sp2.sort(key=lambda x: x[1])
        sp2 = [(p, s) for p, s in sp2 if get_risk(s)[0] in fil_set]

        rows = ""
        for port, svc in sp2:
            risk, desc = get_risk(svc)
            cves = CVE_DB.get(svc, [])
            cve_html = ("<br>".join([f'<span style="color:#9333ea;font-size:11px;">⚠ {c}</span>' for c in cves])
                        if cves else '<span style="color:#374151;font-size:11px;">None known</span>')
            icon = RISK_ICON.get(risk, "")
            rows += f"""<tr>
                <td style="color:#3b82f6;font-weight:700;font-family:'JetBrains Mono',monospace;">{port}</td>
                <td style="font-weight:500;">{svc}</td>
                <td><span class="badge b-open">● Open</span></td>
                <td><span class="badge b-{risk.lower()}">{icon} {risk}</span></td>
                <td style="color:#94a3b8;font-size:12.5px;">{desc}</td>
                <td>{cve_html}</td>
            </tr>"""

        st.markdown(f"""
        <div class="card" style="padding:0;overflow:hidden;">
            <table class="scan-table">
                <thead><tr>
                    <th>Port</th><th>Service</th><th>Status</th>
                    <th>Risk Level</th><th>What this means</th><th>Known Vulnerabilities</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>""", unsafe_allow_html=True)

        meta = st.session_state.current_meta
        sd   = {**meta, "open_ports": open_ports, "elapsed": st.session_state.elapsed}

        buf = io.StringIO(); w = csv.writer(buf)
        w.writerow(["Port","Service","Status","Risk Level","Description","Known CVEs"])
        for p, s in sp2:
            r, n = get_risk(s)
            w.writerow([p, s, "Open", r, n, "; ".join(CVE_DB.get(s, []))])

        st.markdown("<br>", unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1: st.download_button("⬇  Export as CSV",  buf.getvalue(),        f"synapscan_{int(time.time())}.csv",  "text/csv",         use_container_width=True)
        with d2: st.download_button("⬇  Export as JSON", to_json(sd),           f"synapscan_{int(time.time())}.json", "application/json", use_container_width=True)
        with d3: st.download_button("⬇  Export as TXT",  to_txt(sd),            f"synapscan_{int(time.time())}.txt",  "text/plain",       use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — SMART ANALYSIS
# ══════════════════════════════════════════════════════════════════════
with t3:
    open_ports = st.session_state.open_ports
    if not open_ports:
        st.markdown('<div class="empty-state"><div class="icon">🧠</div><p>Run a scan first. The analysis will appear here automatically when the scan completes.</p></div>', unsafe_allow_html=True)
    else:
        analysis = st.session_state.analysis or analyze_ports(open_ports, st.session_state.current_meta.get("target",""))

        # Overall risk banner
        rating = analysis['risk_rating']
        rating_color = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#ca8a04","LOW":"#16a34a"}.get(rating,"#3b82f6")
        rating_bg    = {"CRITICAL":"rgba(239,68,68,0.08)","HIGH":"rgba(249,115,22,0.08)",
                        "MEDIUM":"rgba(234,179,8,0.08)","LOW":"rgba(34,197,94,0.08)"}.get(rating,"rgba(59,130,246,0.08)")

        st.markdown(f"""
        <div style="background:{rating_bg};border:1px solid {rating_color}33;border-left:4px solid {rating_color};
             border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:1rem;">
            <div style="font-size:11px;color:{rating_color};font-weight:700;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:4px;">
                Overall Risk Rating
            </div>
            <div style="font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;color:{rating_color};">{RISK_ICON.get(rating,'')} {rating}</div>
            <div style="font-size:13.5px;color:#94a3b8;margin-top:0.4rem;">{analysis['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

        ai_t1, ai_t2, ai_t3 = st.tabs(["📋  Findings", "💡  What You Should Do", "🚨  Anomalies"])

        with ai_t1:
            st.markdown('<div style="font-size:13px;color:#64748b;margin-bottom:0.8rem;">Each open port explained in plain English, with its risk level.</div>', unsafe_allow_html=True)
            for f in analysis['findings']:
                icon = RISK_ICON.get(f['risk'],'')
                border_col = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#ca8a04","LOW":"#22c55e","INFO":"#06b6d4"}.get(f['risk'],"#3b82f6")
                cve_html = ""
                if f['cves']:
                    cve_html = "<br><div style='margin-top:6px;'>" + " ".join([
                        f'<span style="background:rgba(147,51,234,0.1);color:#9333ea;border-radius:4px;padding:1px 7px;font-size:11px;margin-right:4px;">⚠ {c}</span>'
                        for c in f['cves']
                    ]) + "</div>"
                st.markdown(f"""
                <div style="background:var(--s1);border:1px solid var(--border);border-left:3px solid {border_col};
                     border-radius:0 8px 8px 0;padding:0.85rem 1.1rem;margin-bottom:0.5rem;">
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:3px;">
                        <span style="font-family:'JetBrains Mono',monospace;color:#3b82f6;font-weight:700;font-size:14px;">Port {f['port']}</span>
                        <span style="color:#e2e8f0;font-weight:600;">{f['service']}</span>
                        <span class="badge b-{f['risk'].lower()}" style="margin-left:auto;">{icon} {f['risk']}</span>
                    </div>
                    <div style="font-size:13px;color:#94a3b8;">{f['desc']}{cve_html}</div>
                </div>
                """, unsafe_allow_html=True)

        with ai_t2:
            st.markdown('<div style="font-size:13px;color:#64748b;margin-bottom:0.8rem;">Specific steps to improve security on this target, in order of priority.</div>', unsafe_allow_html=True)
            for i, rec in enumerate(analysis['recommendations'], 1):
                st.markdown(f"""
                <div style="display:flex;gap:0.8rem;align-items:flex-start;padding:0.75rem 1rem;
                     background:var(--s1);border:1px solid var(--border);border-radius:8px;margin-bottom:0.5rem;">
                    <span style="background:var(--s2);color:#64748b;border-radius:5px;padding:1px 8px;
                          font-size:11px;font-weight:700;flex-shrink:0;margin-top:1px;">{i}</span>
                    <span style="font-size:13.5px;line-height:1.6;">{rec}</span>
                </div>
                """, unsafe_allow_html=True)

        with ai_t3:
            if analysis['anomalies']:
                st.markdown('<div style="font-size:13px;color:#64748b;margin-bottom:0.8rem;">Unusual patterns or suspicious configurations detected in this scan.</div>', unsafe_allow_html=True)
                for a in analysis['anomalies']:
                    st.markdown(f"""
                    <div style="background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.2);
                         border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.5rem;font-size:13.5px;">
                        {a}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2);
                     border-radius:8px;padding:1rem 1.2rem;font-size:13.5px;">
                    ✅ No anomalies detected. The port profile looks normal for this type of target.
                </div>
                """, unsafe_allow_html=True)

        # Export analysis report
        st.markdown("<br>", unsafe_allow_html=True)
        meta = st.session_state.current_meta
        sd   = {**meta, "open_ports": open_ports, "elapsed": st.session_state.elapsed}
        report_txt = to_txt(sd)
        st.download_button("⬇  Download Full Analysis Report", report_txt,
                           f"synapscan_report_{int(time.time())}.txt", "text/plain",
                           use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — CASE NOTES & FORENSICS
# ══════════════════════════════════════════════════════════════════════
with t4:
    st.markdown("### Case Notes & Scan History")
    st.markdown('<div style="font-size:13px;color:#64748b;margin-bottom:1rem;">Select any past scan to view details, add notes, and export evidence.</div>', unsafe_allow_html=True)

    history = load_history(50)
    if not history:
        st.markdown('<div class="empty-state"><div class="icon">📁</div><p>No scan history yet. Run your first scan to see it here.</p></div>', unsafe_allow_html=True)
    else:
        opts = {f"#{h['id']}  ·  {h['target']}  ·  {h['timestamp']}  ({h['case_name'] or 'No label'})": h['id']
                for h in history}
        sel   = st.selectbox("Select a scan", list(opts.keys()))
        scan  = load_by_id(opts[sel])

        if scan:
            sc1, sc2 = st.columns([2, 1])
            with sc1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Scan Details</div>
                    <table style="font-size:13px;width:100%;border-collapse:collapse;">
                        <tr><td style="color:#64748b;padding:5px 0;width:120px;">Target</td>
                            <td style="color:#3b82f6;font-family:'JetBrains Mono',monospace;font-weight:600;">{scan['target']}</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Resolved IP</td>
                            <td style="color:#22c55e;font-family:'JetBrains Mono',monospace;">{scan['resolved_ip']}</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Port Range</td>
                            <td style="font-family:'JetBrains Mono',monospace;">{scan['port_range']}</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Date & Time</td>
                            <td>{scan['timestamp']}</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Duration</td>
                            <td>{scan['elapsed']:.1f}s</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Open Ports</td>
                            <td style="color:#f97316;font-weight:700;">{len(scan['open_ports'])}</td></tr>
                        <tr><td style="color:#64748b;padding:5px 0;">Label</td>
                            <td style="color:#a855f7;">{scan['case_name'] or '—'}</td></tr>
                    </table>
                </div>""", unsafe_allow_html=True)

                if scan['open_ports']:
                    rows = "".join([
                        f'<tr>'
                        f'<td style="color:#3b82f6;font-family:\'JetBrains Mono\',monospace;font-weight:600;">{p}</td>'
                        f'<td style="font-weight:500;">{s}</td>'
                        f'<td><span class="badge b-{get_risk(s)[0].lower()}">{RISK_ICON.get(get_risk(s)[0],"")} {get_risk(s)[0]}</span></td>'
                        f'<td style="color:#94a3b8;font-size:12px;">{get_risk(s)[1]}</td>'
                        f'</tr>'
                        for p, s in sorted(scan['open_ports'])
                    ])
                    st.markdown(f"""
                    <div class="card" style="padding:0;overflow:hidden;">
                        <table class="scan-table">
                            <thead><tr><th>Port</th><th>Service</th><th>Risk</th><th>Description</th></tr></thead>
                            <tbody>{rows}</tbody>
                        </table>
                    </div>""", unsafe_allow_html=True)

            with sc2:
                st.markdown("**Investigator Notes**")
                st.markdown('<div style="font-size:12px;color:#64748b;margin-bottom:0.5rem;">Write anything useful about this scan — findings, next steps, chain of custody.</div>', unsafe_allow_html=True)
                notes = st.text_area("Notes", value=scan['notes'] or "", height=220,
                                     placeholder="e.g. Found exposed MySQL on client router. Notified IT team. Ticket #1234.",
                                     label_visibility="collapsed")
                if st.button("💾  Save Notes", use_container_width=True):
                    update_notes(opts[sel], notes); st.success("✅ Notes saved.")
                if st.button("🗑  Delete This Scan", use_container_width=True):
                    delete_scan(opts[sel]); st.warning("Scan deleted."); st.rerun()
                st.download_button("⬇  Export as JSON",
                    to_json({**scan, "notes": notes}),
                    f"case_{opts[sel]}.json", "application/json",
                    use_container_width=True)
                st.download_button("⬇  Export as TXT",
                    to_txt({**scan, "notes": notes}),
                    f"case_{opts[sel]}.txt", "text/plain",
                    use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 5 — CHANGE DETECTION
# ══════════════════════════════════════════════════════════════════════
with t5:
    st.markdown("### Change Detection")
    st.markdown("""
    <div class="hint-box">
        <strong>What is this?</strong> Compare two scans of the same target taken at different times.
        SynapScan will tell you if any new ports appeared or old ones closed — useful for spotting unauthorized changes.
    </div>
    """, unsafe_allow_html=True)

    history = load_history(50)
    if len(history) < 2:
        st.markdown('<div class="empty-state"><div class="icon">🔍</div><p>You need at least <strong>2 scans</strong> of the same target to compare. Run a scan, then run it again later.</p></div>', unsafe_allow_html=True)
    else:
        labels = {f"#{h['id']}  ·  {h['target']}  ·  {h['timestamp']}": h['id'] for h in history}
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Baseline scan** *(older — what it looked like before)*")
            old_lbl = st.selectbox("Baseline", list(labels.keys()), index=len(labels)-1, label_visibility="collapsed")
        with cc2:
            st.markdown("**New scan** *(recent — what it looks like now)*")
            new_lbl = st.selectbox("New", list(labels.keys()), index=0, label_visibility="collapsed")

        if st.button("🔍  Compare These Two Scans", use_container_width=False):
            os_ = load_by_id(labels[old_lbl])
            ns_ = load_by_id(labels[new_lbl])
            if os_ and ns_:
                added, removed, same = compare_scans(os_['open_ports'], ns_['open_ports'])

                cm1, cm2, cm3 = st.columns(3)
                cm1.markdown(f'<div class="metric-tile"><span class="val" style="color:#a855f7;">{len(added)}</span><span class="lbl">🆕 New Ports</span></div>', unsafe_allow_html=True)
                cm2.markdown(f'<div class="metric-tile"><span class="val" style="color:#64748b;">{len(removed)}</span><span class="lbl">❌ Closed Ports</span></div>', unsafe_allow_html=True)
                cm3.markdown(f'<div class="metric-tile"><span class="val" style="color:#3b82f6;">{len(same)}</span><span class="lbl">↔ Unchanged</span></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if not added and not removed:
                    st.success("✅ No changes detected. The port profile is identical between both scans.")
                else:
                    if added:
                        st.warning(f"⚠️ **{len(added)} new port{'s' if len(added)>1 else ''} appeared** since the baseline scan. Review these — they may indicate new services or unauthorized access.")
                        rows = "".join([
                            f'<tr>'
                            f'<td><span class="badge b-new">🆕 NEW</span></td>'
                            f'<td style="color:#a855f7;font-family:\'JetBrains Mono\',monospace;font-weight:700;">{p}</td>'
                            f'<td style="font-weight:500;">{s}</td>'
                            f'<td><span class="badge b-{get_risk(s)[0].lower()}">{RISK_ICON.get(get_risk(s)[0],"")} {get_risk(s)[0]}</span></td>'
                            f'<td style="color:#94a3b8;font-size:12px;">{get_risk(s)[1]}</td>'
                            f'</tr>'
                            for p, s in sorted(added)
                        ])
                        st.markdown(f"""
                        <div class="card" style="padding:0;overflow:hidden;">
                            <table class="scan-table">
                                <thead><tr><th>Change</th><th>Port</th><th>Service</th><th>Risk</th><th>What this means</th></tr></thead>
                                <tbody>{rows}</tbody>
                            </table>
                        </div>""", unsafe_allow_html=True)

                    if removed:
                        st.info(f"ℹ️ **{len(removed)} port{'s' if len(removed)>1 else ''} closed** since the baseline scan.")
                        rows = "".join([
                            f'<tr>'
                            f'<td><span class="badge b-closed">❌ CLOSED</span></td>'
                            f'<td style="color:#64748b;font-family:\'JetBrains Mono\',monospace;">{p}</td>'
                            f'<td style="color:#64748b;">{s}</td>'
                            f'</tr>'
                            for p, s in sorted(removed)
                        ])
                        st.markdown(f"""
                        <div class="card" style="padding:0;overflow:hidden;">
                            <table class="scan-table">
                                <thead><tr><th>Change</th><th>Port</th><th>Service</th></tr></thead>
                                <tbody>{rows}</tbody>
                            </table>
                        </div>""", unsafe_allow_html=True)
