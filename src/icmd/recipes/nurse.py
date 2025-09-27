import re, shlex
def run(phrase: str) -> int:
    p = phrase.lower()
    if m:=re.search(r"last\s+(\d+)\s+from\s+(.+)$", p):
        n, f = m.group(1), phrase.split("from",1)[1].strip()
        print(f"$ tail -n {n} {shlex.quote(f)}"); return 0
    if "follow" in p:
        f = phrase.split("follow",1)[1].strip()
        print(f"$ tail -F {shlex.quote(f)}"); return 0
    if m:=re.search(r"first\s+(\d+)\s+of\s+(.+)$", p):
        n, f = m.group(1), phrase.split("of",1)[1].strip()
        print(f"$ head -n {n} {shlex.quote(f)}"); return 0
    if "search" in p:
        mm = re.search(r"search\s+\"([^\"]+)\"", phrase)
        pat = mm.group(1) if mm else "TODO_PATTERN"
        scope = "*.log" if "*.log" in p else "."
        print(f"$ grep -R -n --color=auto {shlex.quote(pat)} {scope}"); return 0
    if "regex" in p:
        mm = re.search(r"regex\s+\"([^\"]+)\"", phrase)
        pat = mm.group(1) if mm else ".*"
        scope = "*.log" if "*.log" in p else "."
        print(f"$ grep -R -n -E {shlex.quote(pat)} {scope}"); return 0
    if "unique" in p or "top " in p:
        f = "*.log" if "*.log" in p else "file"
        if "top" in p:
            k = re.search(r"top\s+(\d+)", p)
            k = int(k.group(1)) if k else 10
            print(f"$ sort {f} | uniq -c | sort -nr | head -n {k}"); return 0
        print(f"$ sort {f} | uniq"); return 0
    print("# nurse: no pattern matched"); return 0
