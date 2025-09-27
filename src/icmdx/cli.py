import sys, re
from .utils import autocorrect_phrase, parse_window, recent_n_logs
from .recipes import nurse, doctor, operation, postmortem

TINY = r"^ic:\s*(?P<cmd>.+)$"

def run_cli(argv=None):
    argv = argv or sys.argv[1:]
    text = " ".join(argv)
    m = re.search(TINY, text)
    if not m:
        print("Usage: ic 'ic: summarise app.log last 1h'"); return 2
    phrase = autocorrect_phrase(m.group("cmd"))
    phrase = phrase.replace(" here", " *.log")
    phrase = re.sub(r"recent\s+(\d+)", lambda m: " " + " ".join(recent_n_logs(int(m.group(1)))) , phrase)

    p = phrase.lower().strip()
    if p.startswith("summarise") or p.startswith("investigate") or p.startswith("flow") or p.startswith("refer"):
        return doctor.run(phrase)
    if p.startswith("archive") or p.startswith("rotate") or "since" in p or "until" in p or "gaps" in p or "groupby" in p:
        return operation.run(phrase)
    if p.startswith("postmortem") or p.startswith("triage") or p.startswith("flowguard") or p.startswith("spikecheck") or p.startswith("clinic"):
        return postmortem.run(phrase)
    # default to nurse
    return nurse.run(phrase)
