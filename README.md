# BioConvert

Browser-based bioinformatics file conversion. Addresses the recurring
"convert X to Y" demand on Biostars / r/bioinformatics (VCF→TSV, GTF↔GFF3,
FASTA stats, TSV→GTF). Sibling product to ChemParse, same monetization pattern.

```
bioconvert/
├── landing/   index.html                 ← single-file Tailwind landing
├── backend/   bioconvert/ + app.py        ← pure-Python converters + FastAPI
└── frontend/  Vite + React                ← pick conversion, upload, preview, gated download
```

## Conversions (all pure-Python, tested)
| Name | In → Out | Notes |
|---|---|---|
| `vcf-to-tsv` | VCF → TSV | expands every INFO key into its own column |
| `gtf-to-gff3` | GTF → GFF3 | derives ID/Parent from gene_id/transcript_id |
| `gff3-to-gtf` | GFF3 → GTF | reverse mapping |
| `fasta-stats` | FASTA → TSV | per-seq length, GC%, N count |
| `tsv-to-gtf` | TSV → GTF | annotation table → valid GTF |

Add a converter: write `text -> text` fn, register in
`backend/bioconvert/registry.py`. It then shows up in the API and the frontend
dropdown automatically.

## Run

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload      # GET /conversions ; POST /convert/{name}
pytest                        # 4 passing
```

**Frontend**
```bash
cd frontend
cp .env.example .env
npm install && npm run dev    # http://localhost:5174
```
> Uses Vite 7 (not 8) — Vite 8 breaks `@vitejs/plugin-react`'s peer range. Don't
> run `npm audit fix --force`; the remaining esbuild advisory is dev-server only.

**Landing** — open `landing/index.html` or `wrangler pages deploy landing`.

## Monetization / where to extend
- Free = single-file preview; Pro = full download + batch (gate behind Stripe
  Payment Link with `?paid=1` unlock, same as ChemParse).
- Next: BAM↔SAM (needs `pysam`), BED tools, liftover, batch `.zip` endpoint.
- For heavy/edge-case real files, swap pure-Python for `pysam` / `gffutils`
  behind the same `text -> text` interface.
