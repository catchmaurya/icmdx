from . import doctor
def run(phrase: str) -> int:
    print("# Postmortem\n")
    files = []
    doctor.investigate(doctor._files(phrase.replace("postmortem","").replace("triage","")), phrase)
    print("\n# Timeline\n")
    doctor.flow(doctor._files(phrase), phrase + " show delta")
    return 0
