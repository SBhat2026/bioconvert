import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bioconvert import convert  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "sample_data")


def _read(name):
    with open(os.path.join(DATA, name)) as fh:
        return fh.read()


def test_vcf_to_tsv():
    out = convert("vcf-to-tsv", _read("sample.vcf")).splitlines()
    header = out[0].split("\t")
    # core columns + sorted INFO keys (AF, DB, DP)
    assert header == ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER",
                      "AF", "DB", "DP"]
    row1 = dict(zip(header, out[1].split("\t")))
    assert row1["DP"] == "30" and row1["DB"] == "."
    row2 = dict(zip(header, out[2].split("\t")))
    assert row2["DB"] == "True"  # flag set


def test_fasta_stats():
    out = convert("fasta-stats", _read("sample.fasta")).splitlines()
    assert out[0] == "id\tlength\tgc_percent\tn_count"
    s1 = out[1].split("\t")
    assert s1[0] == "seq1" and s1[1] == "12"      # ATGCATGCGGCC
    assert s1[2] == "66.67"                         # 8 GC / 12
    s2 = out[2].split("\t")
    assert s2[0] == "seq2" and s2[3] == "2"         # two Ns
    assert s2[2] == "0.0"                           # AATT -> 0% GC


def test_gtf_gff3_roundtrip_shape():
    gff3 = convert("gtf-to-gff3",
                   'chr1\thav\tgene\t1\t9\t.\t+\t.\tgene_id "G1";\n')
    assert gff3.startswith("##gff-version 3")
    assert "ID=G1" in gff3
    gtf = convert("gff3-to-gtf", gff3)
    assert 'gene_id "G1";' in gtf


def test_tsv_to_gtf():
    out = convert("tsv-to-gtf", _read("sample.tsv")).splitlines()
    assert len(out) == 2
    assert out[0].split("\t")[0] == "chr1"
    assert 'gene_id "G1";' in out[0]
    assert 'transcript_id "G1";' in out[0]  # synthesized from gene_id
