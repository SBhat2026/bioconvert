"""VCF -> TSV. Flattens the 8 core columns and expands every INFO key into its
own column (flags become True). Pure-Python; for huge VCFs swap in cyvcf2/pysam.
"""

from __future__ import annotations

_CORE = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER"]


def _parse_info(field: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if field in (".", ""):
        return out
    for item in field.split(";"):
        if not item:
            continue
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
        else:
            out[item] = "True"  # flag
    return out


def vcf_to_tsv(vcf_text: str) -> str:
    rows: list[dict[str, str]] = []
    info_keys: list[str] = []
    for line in vcf_text.splitlines():
        if line.startswith("##") or not line.strip():
            continue
        if line.startswith("#CHROM"):
            continue
        cols = line.split("\t")
        if len(cols) < 8:
            continue
        info = _parse_info(cols[7])
        for k in info:
            if k not in info_keys:
                info_keys.append(k)
        row = {name: cols[i] for i, name in enumerate(_CORE)}
        row.update(info)
        rows.append(row)

    info_keys.sort()
    header = _CORE + info_keys
    lines = ["\t".join(header)]
    for row in rows:
        lines.append("\t".join(row.get(c, ".") for c in header))
    return "\n".join(lines) + "\n"
