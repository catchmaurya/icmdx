import re, os, glob
from datetime import datetime, timedelta
from dateutil import parser as dtparser

def parse_window(text: str):
    win = {}
    m = re.search(r"last\s+(\d+)\s*(h|m)", text, re.I)
    if m:
        n = int(m.group(1)); unit = m.group(2).lower()
        from datetime import datetime, timedelta
        delta = timedelta(hours=n) if unit=="h" else timedelta(minutes=n)
        win["since"] = datetime.now() - delta
    m2 = re.search(r"since\s+([0-9:\-\sT/]+)", text, re.I)
    if m2:
        try: win["since"] = dtparser.parse(m2.group(1))
        except: pass
    m3 = re.search(r"until\s+([0-9:\-\sT/]+)", text, re.I)
    if m3:
        try: win["until"] = dtparser.parse(m3.group(1))
        except: pass
    return win

def within_window(ts, win):
    if not win: return True
    try: dt = dtparser.parse(ts)
    except: return True
    if "since" in win and dt < win["since"]: return False
    if "until" in win and dt > win["until"]: return False
    return True

TS_RX = [re.compile(r'(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})'),
         re.compile(r'(?P<ts>[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})')]

def grab_ts(line: str):
    for rx in TS_RX:
        m = rx.search(line)
        if m: return m.group("ts")
    return ""

def norm_level(s: str) -> str:
    t = s.lower()
    if "critical" in t or "fatal" in t: return "CRITICAL"
    if "error" in t: return "ERROR"
    if "warn" in t: return "WARNING"
    if "info" in t: return "INFO"
    if "debug" in t or "trace" in t: return "DEBUG"
    return "INFO"

def recent_n_logs(n=5, pattern="*.log"):
    files = sorted(glob.glob(pattern), key=lambda p: os.path.getmtime(p), reverse=True)
    return files[:n]

# Autocorrect (lightweight)
VOCAB = {"summarise","investigate","operation","postmortem","nurse","doctor","flow","refer","archive","rotate","search","regex","unique","top","follow","first","last","only","exclude","groupby","dedupe","minfreq","since","until","last","show","delta","gaps","recent","json","yaml","md","pager","watch","why","suggest"}
CORRECT = {"sumamrise":"summarise","sumamriaze":"summarise","summarize":"summarise","investgiate":"investigate","opertion":"operation","post-mortem":"postmortem","docotor":"doctor","nursee":"nurse","flo":"flow","reffer":"refer","uniq":"unique","regx":"regex","goupby":"groupby","minfreqe":"minfreq","crtitical":"critical","eror":"error","warnng":"warning","yml":"yaml"}

def edit_distance(a,b):
    la, lb = len(a), len(b)
    dp = list(range(lb+1))
    for i,ca in enumerate(a,1):
        prev = dp[0]; dp[0] = i
        for j,cb in enumerate(b,1):
            cur = dp[j]
            dp[j] = min(dp[j]+1, dp[j-1]+1, prev + (ca!=cb))
            prev = cur
    return dp[-1]

def autocorrect_phrase(phrase: str) -> str:
    for k,v in CORRECT.items():
        phrase = re.sub(rf"\b{k}\b", v, phrase, flags=re.I)
    tokens = re.split(r"(\W+)", phrase)
    out=[]
    for t in tokens:
        lower=t.lower()
        if not re.match(r"\w+", lower): out.append(t); continue
        if lower in VOCAB: out.append(t); continue
        best,score=None,3
        for v in VOCAB:
            d=edit_distance(lower,v)
            if d<score: score, best = d, v
        out.append(best if best and score<=2 else t)
    return "".join(out)
