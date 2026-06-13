"""BioConvert API — one generic conversion endpoint driven by the registry.

GET  /conversions            -> list available conversions
POST /convert/{name}         -> file in, converted text out (download)
No auth; CORS open for local dev. Gate batch/large files behind payment later.
"""

from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from bioconvert import CONVERSIONS, convert

app = FastAPI(title="BioConvert API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/conversions")
def list_conversions():
    return [
        {"name": k, "label": v["label"], "in": v["in"], "out": v["out"]}
        for k, v in CONVERSIONS.items()
    ]


@app.post("/convert/{name}")
async def do_convert(name: str, file: UploadFile = File(...)):
    if name not in CONVERSIONS:
        raise HTTPException(status_code=404, detail=f"Unknown conversion '{name}'")
    text = (await file.read()).decode("utf-8", errors="ignore")
    try:
        result = convert(name, text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Conversion failed: {exc}")
    out_ext = CONVERSIONS[name]["out"]
    stem = (file.filename or "input").rsplit(".", 1)[0]
    return Response(
        content=result,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={stem}.{out_ext}"},
    )
