"""TSV annotation -> GTF (addresses the recurring "convert .tsv to .gtf" ask).

Expects a header row. Recognized columns (case-insensitive):
  seqid|chrom, start, end  (required)
  source, feature|type, score, strand, frame, gene_id, transcript_id, gene_name
Unknown columns are carried into the GTF attributes. A gene_id is synthesized if
none is present (GTF requires it).
"""

from __future__ import annotations

_ALIASES = {
    "chrom": "seqid", "chr": "seqid", "seqname": "seqid",
    "type": "feature",
}
_FIXED = {"seqid", "source", "feature", "start", "end", "score", "strand", "frame"}


def _norm(col: str) -> str:
    c = col.strip().lower()
    return _ALIASES.get(c, c)


def tsv_to_gtf(tsv_text: str) -> str:
    rows = [r for r in tsv_text.splitlines() if r.strip()]
    if not rows:
        return ""
    header = [_norm(h) for h in rows[0].split("\t")]
    out: list[str] = []
    for i, line in enumerate(rows[1:], start=1):
        vals = line.split("\t")
        rec = dict(zip(header, vals))
        if not {"seqid", "start", "end"} <= rec.keys():
            continue  # row lacks required coordinates
        gene_id = rec.get("gene_id") or rec.get("gene_name") or f"gene{i}"
        tx_id = rec.get("transcript_id") or gene_id
        attrs = [("gene_id", gene_id), ("transcript_id", tx_id)]
        for k, v in rec.items():
            if k not in _FIXED and k not in ("gene_id", "transcript_id"):
                attrs.append((k, v))
        attr_str = " ".join(f'{k} "{v}";' for k, v in attrs)
        out.append("\t".join([
            rec["seqid"], rec.get("source", "tsv2gtf"),
            rec.get("feature", "exon"), rec["start"], rec["end"],
            rec.get("score", "."), rec.get("strand", "+"),
            rec.get("frame", "."), attr_str,
        ]))
    return "\n".join(out) + "\n"
