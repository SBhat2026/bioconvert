"""FASTA -> per-sequence stats TSV (length, GC%, N count). A common one-off ask.
GC% is computed over A/C/G/T only (Ns excluded from the denominator).
"""

from __future__ import annotations


def _records(fasta_text: str):
    name, seq = None, []
    for line in fasta_text.splitlines():
        if line.startswith(">"):
            if name is not None:
                yield name, "".join(seq)
            name = line[1:].split()[0] if line[1:].strip() else line[1:]
            seq = []
        elif line.strip():
            seq.append(line.strip())
    if name is not None:
        yield name, "".join(seq)


def fasta_stats(fasta_text: str) -> str:
    lines = ["id\tlength\tgc_percent\tn_count"]
    for name, seq in _records(fasta_text):
        s = seq.upper()
        length = len(s)
        gc = s.count("G") + s.count("C")
        acgt = gc + s.count("A") + s.count("T")
        n_count = s.count("N")
        gc_pct = round(100 * gc / acgt, 2) if acgt else 0.0
        lines.append(f"{name}\t{length}\t{gc_pct}\t{n_count}")
    return "\n".join(lines) + "\n"
