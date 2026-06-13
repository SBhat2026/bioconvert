"""GTF <-> GFF3. Both are 9-column TSV; the work is the attributes column plus
GFF3 ID/Parent relationships. Pure-Python; swap gffutils in for edge cases.
"""

from __future__ import annotations

import re
from urllib.parse import quote

_GTF_ATTR = re.compile(r'(\w+)\s+"([^"]*)"')
_PARENT_OF = {"transcript": "gene", "mrna": "gene"}


def _parse_gtf_attrs(field: str) -> dict[str, str]:
    return dict(_GTF_ATTR.findall(field))


def _parse_gff3_attrs(field: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in field.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def gtf_to_gff3(gtf_text: str) -> str:
    out = ["##gff-version 3"]
    counters: dict[str, int] = {}
    for line in gtf_text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 9:
            continue
        attrs = _parse_gtf_attrs(c[8])
        gene_id, tx_id = attrs.get("gene_id"), attrs.get("transcript_id")
        ft = c[2].lower()
        ordered: list[tuple[str, str]] = []
        if ft == "gene" and gene_id:
            ordered.append(("ID", gene_id))
        elif ft in _PARENT_OF and tx_id:
            ordered.append(("ID", tx_id))
            if gene_id:
                ordered.append(("Parent", gene_id))
        elif tx_id:
            n = counters.get(tx_id, 0) + 1
            counters[tx_id] = n
            ordered += [("ID", f"{tx_id}:{ft}:{n}"), ("Parent", tx_id)]
        for k, v in attrs.items():
            if k not in ("gene_id", "transcript_id"):
                ordered.append((k, quote(v, safe=" :/._-|()")))
        c[8] = ";".join(f"{k}={v}" for k, v in ordered)
        out.append("\t".join(c[:9]))
    return "\n".join(out) + "\n"


def gff3_to_gtf(gff3_text: str) -> str:
    out: list[str] = []
    for line in gff3_text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 9:
            continue
        attrs = _parse_gff3_attrs(c[8])
        ft = c[2].lower()
        gene_id = tx_id = None
        if ft == "gene":
            gene_id = attrs.get("ID")
        elif ft in _PARENT_OF:
            tx_id, gene_id = attrs.get("ID"), attrs.get("Parent")
        else:
            tx_id = attrs.get("Parent")
        pairs: list[tuple[str, str]] = []
        if gene_id:
            pairs.append(("gene_id", gene_id))
        if tx_id:
            pairs.append(("transcript_id", tx_id))
        for k, v in attrs.items():
            if k not in ("ID", "Parent"):
                pairs.append((k, v))
        c[8] = " ".join(f'{k} "{v}";' for k, v in pairs)
        out.append("\t".join(c[:9]))
    return "\n".join(out) + "\n"
