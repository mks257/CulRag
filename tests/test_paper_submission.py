"""Pre-submission checks for the manuscript (paper/paper.md checklist)."""
from pathlib import Path

PAPER = Path(__file__).resolve().parent.parent / "paper"
SECTIONS = [
    "abstract.md", "introduction.md", "related_work.md", "methods.md",
    "results.md", "discussion.md", "conclusion.md",
]


def test_no_placeholders_left_in_sections():
    offenders = {}
    for name in SECTIONS:
        hits = [
            i + 1
            for i, line in enumerate((PAPER / name).read_text(encoding="utf-8").splitlines())
            if "PLACEHOLDER" in line
        ]
        if hits:
            offenders[name] = hits
    assert not offenders, f"PLACEHOLDER still present before submission: {offenders}"
