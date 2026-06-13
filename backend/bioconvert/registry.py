"""Conversion registry. Each entry: input ext -> output ext + function.
Add a new converter here and it appears in the API + frontend automatically."""

from __future__ import annotations

from .fasta_stats import fasta_stats
from .gff import gff3_to_gtf, gtf_to_gff3
from .tsv_gtf import tsv_to_gtf
from .vcf_tsv import vcf_to_tsv

CONVERSIONS = {
    "vcf-to-tsv": {"fn": vcf_to_tsv, "in": "vcf", "out": "tsv",
                   "label": "VCF → TSV (flatten INFO)"},
    "gtf-to-gff3": {"fn": gtf_to_gff3, "in": "gtf", "out": "gff3",
                    "label": "GTF → GFF3"},
    "gff3-to-gtf": {"fn": gff3_to_gtf, "in": "gff3", "out": "gtf",
                    "label": "GFF3 → GTF"},
    "fasta-stats": {"fn": fasta_stats, "in": "fasta", "out": "tsv",
                    "label": "FASTA → stats TSV (length, GC%)"},
    "tsv-to-gtf": {"fn": tsv_to_gtf, "in": "tsv", "out": "gtf",
                   "label": "TSV → GTF"},
}


def convert(name: str, text: str) -> str:
    if name not in CONVERSIONS:
        raise KeyError(f"Unknown conversion '{name}'")
    return CONVERSIONS[name]["fn"](text)
