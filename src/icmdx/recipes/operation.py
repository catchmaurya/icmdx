import re
def run(phrase: str) -> int:
    p = phrase.lower()
    if p.startswith("archive"):
        m = re.search(r"older\s+(\d+)d", p)
        days = int(m.group(1)) if m else 30
        out = "logs_old.tgz"
        mm = re.search(r"->\s*([^\s]+)", phrase)
        if mm: out = mm.group(1)
        print(f"$ find logs/ -type f -mtime +{days} -print | tar -czf {out} -T -")
        return 0
    if p.startswith("rotate"):
        parts = phrase.split()
        target = parts[-1] if parts else "access.log"
        print(f"$ d=$(date +%Y%m%d); cp {target} ${target}.\"$d\"; : > {target}; gzip ${target}.\"$d\"")
        return 0
    print("# operation: no pattern"); return 0
