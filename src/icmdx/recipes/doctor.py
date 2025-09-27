import re, glob
from ..utils import grab_ts, norm_level, within_window, parse_window

def _iter(files):
    for f in files:
        try:
            with open(f, "r", errors="ignore") as fh:
                for line in fh:
                    yield f, line.rstrip("\n")
        except FileNotFoundError:
            continue

def _files(text: str):
    text = text.strip()
    if not text: return glob.glob("*.log")
    parts = [t for t in re.split(r"\s+", text) if t and not t.startswith("--")]
    files = [p for p in parts if "." in p or "*" in p] or glob.glob("*.log")
    out=[]; seen=set()
    for f in sum([glob.glob(x) or [x] for x in files], []):
        if f not in seen: seen.add(f); out.append(f)
    return out

def run(phrase: str) -> int:
    p = phrase.lower()
    if p.startswith("summarise"):
        files = _files(phrase.replace("summarise","",1))
        return summarise(files, phrase)
    if p.startswith("flow"):
        files = _files(phrase.replace("flow","",1))
        return flow(files, phrase)
    if p.startswith("refer"):
        files = _files(phrase.replace("refer","",1))
        flow(files, phrase)
        return summary_counts(files)
    if p.startswith("investigate"):
        files = _files(phrase.replace("investigate","",1))
        return investigate(files, phrase)
    print("# doctor: no pattern"); return 0

def summarise(files, phrase):
    win = parse_window(phrase)
    counts = {"INFO":0,"WARNING":0,"ERROR":0,"CRITICAL":0,"DEBUG":0}
    first=last=""; keys=[]
    ex_rx = None
    m2 = re.search(r"exclude\s+([^ \t]+)", phrase, re.I)
    if m2: 
        ex_rx = re.compile(m2.group(1), re.I)
    for f,line in _iter(files):
        ts = grab_ts(line)
        if ts and not first: first=ts
        if ts: last=ts
        if ts and not within_window(ts, win): continue
        if ex_rx and ex_rx.search(line): continue
        lvl = norm_level(line)
        counts[lvl]+=1
        if re.search(r"config|connection|db|timeout|retry|auth|permission|oom|memory|disk|network|latency", line, re.I):
            keys.append((ts or "", lvl, f, line[:120]))
    print(f"start: {first}"); print(f"end:   {last}")
    print("counts:", " ".join(f"{k}={counts[k]}" for k in ["INFO","WARNING","ERROR","CRITICAL","DEBUG"]))
    print("-- key events --")
    for t,l,f,msg in keys[:50]:
        print(f"{t} {l} {msg}")
    return 0

def flow(files, phrase):
    win = parse_window(phrase)
    rows=[]
    for f,line in _iter(files):
        ts = grab_ts(line)
        if not ts: continue
        if not within_window(ts, win): continue
        lvl = norm_level(line)
        rows.append((ts,lvl,f,line))
    rows.sort(key=lambda r:r[0])
    prev=None
    show_delta = "show delta" in phrase.lower()
    for t,l,f,msg in rows:
        if show_delta and prev:
            from dateutil import parser as dtp
            try:
                delta = (dtp.parse(t)-dtp.parse(prev)).total_seconds()
                print(f"{t} (+{int(delta)}s): {l} — \"{f}\" ({msg[:140]})")
            except:
                print(f"{t}: {l} — \"{f}\" ({msg[:140]})")
        else:
            print(f"{t}: {l} — \"{f}\" ({msg[:140]})")
        prev=t
    return 0

def summary_counts(files, phrase=None):
    from collections import Counter
    cnt = Counter()
    for f,line in _iter(files):
        cnt[norm_level(line)]+=1
    print("summary:", " ".join(f"{k}={cnt.get(k,0)}" for k in ["WARNING","ERROR","CRITICAL","INFO","DEBUG"]))
    return 0

def investigate(files, phrase):
    win = parse_window(phrase)
    rows=[]
    for f,line in _iter(files):
        ts = grab_ts(line)
        if not ts: continue
        if not within_window(ts, win): continue
        lvl = norm_level(line)
        rows.append((ts,lvl,f,line))
    rows.sort(key=lambda r:r[0])
    if not rows:
        print("no rows in window"); return 0
    print(f"timeframe: {rows[0][0]} .. {rows[-1][0]}")
    from collections import Counter, defaultdict
    cnt = Counter([r[1] for r in rows])
    for k in ["CRITICAL","ERROR","WARNING","INFO","DEBUG"]:
        if cnt.get(k): print(f"level {k:8} {cnt[k]}")
    print("\n-- top messages --")
    import re as _r
    norm=defaultdict(int)
    for _,_,_,msg in rows:
        s=_r.sub(r"[0-9]{2,}","",msg); s=_r.sub(r"[A-Fa-f0-9]{6,}","",s)
        norm[s]+=1
    for msg,c in sorted(norm.items(), key=lambda x:x[1], reverse=True)[:10]:
        print(f"{c:4}  {msg[:160]}")
    print("\n-- first/last ERROR & CRITICAL --")
    for L in ["ERROR","CRITICAL"]:
        sub=[r for r in rows if r[1]==L]
        if sub:
            print(f"first {L}: {sub[0][0]} {sub[0][2]}")
            print(f"last  {L}: {sub[-1][0]} {sub[-1][2]}")
    print("\n-- gaps >2m --")
    from dateutil import parser as dtp
    prev = dtp.parse(rows[0][0]); prevs = rows[0][0]
    for r in rows[1:]:
        cur = dtp.parse(r[0]); diff = (cur-prev).total_seconds()
        if diff>120: print(f"gap {int(diff)}s between {prevs} and {r[0]}")
        prev, prevs = cur, r[0]
    print("\n-- hottest files --")
    fcnt=Counter([r[2] for r in rows])
    for f,c in fcnt.most_common(5):
        print(f"{c:4} {f}")
    print("\n-- suspects --")
    SUS=re.compile(r"config|connection|timeout|retry|auth|permission|oom|memory|disk|network|latency|deadlock|lock|queue|backpressure", re.I)
    for t,_,_,m in rows:
        if SUS.search(m):
            print(f"{t}  {m[:160]}")
    return 0
