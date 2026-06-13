import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
// Stripe Payment Link for the paid/batch tier; success URL -> ?paid=1
const STRIPE_LINK =
  import.meta.env.VITE_STRIPE_LINK || "https://buy.stripe.com/test_PLACEHOLDER";

function download(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const [conversions, setConversions] = useState([]);
  const [selected, setSelected] = useState("");
  const [file, setFile] = useState(null);
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Free preview is capped; full download gated behind ?paid=1 (stateless).
  const unlocked =
    new URLSearchParams(window.location.search).get("paid") === "1";

  useEffect(() => {
    fetch(`${API_BASE}/conversions`)
      .then((r) => r.json())
      .then((list) => {
        setConversions(list);
        if (list[0]) setSelected(list[0].name);
      })
      .catch(() => setError("Could not reach API. Is the backend running?"));
  }, []);

  async function run() {
    if (!file || !selected) return;
    setError(null);
    setOutput("");
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/convert/${selected}`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        throw new Error(b.detail || `Error ${res.status}`);
      }
      setOutput(await res.text());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const meta = conversions.find((c) => c.name === selected);
  const preview = output.split("\n").slice(0, 12).join("\n");
  const truncated = output && output.split("\n").length > 12;

  return (
    <div className="min-h-screen text-slate-100 max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold">
        Bio<span className="text-sky-400">Convert</span>
      </h1>
      <p className="mt-2 text-slate-400">
        Convert between bioinformatics file formats in your browser. No upload to
        third parties beyond your own backend.
      </p>

      <div className="mt-8 space-y-4">
        <label className="block text-sm text-slate-300">
          Conversion
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="mt-1 block w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
          >
            {conversions.map((c) => (
              <option key={c.name} value={c.name}>
                {c.label}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm text-slate-300">
          File {meta && <span className="text-slate-500">(.{meta.in})</span>}
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="mt-1 block w-full text-sm text-slate-400 file:mr-3 file:rounded-lg file:border-0 file:bg-sky-500 file:px-4 file:py-2 file:text-slate-950 hover:file:bg-sky-400"
          />
        </label>

        <button
          onClick={run}
          disabled={!file || loading}
          className="rounded-lg bg-sky-500 px-5 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400 disabled:opacity-40"
        >
          {loading ? "Converting…" : "Convert"}
        </button>
      </div>

      {error && (
        <div className="mt-6 rounded-lg border border-red-800 bg-red-950/40 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {output && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">Result preview</h2>
          <pre className="mt-3 max-h-80 overflow-auto rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-xs text-sky-200">
            {preview}
            {truncated && "\n…"}
          </pre>

          <div className="mt-5">
            {unlocked ? (
              <button
                onClick={() => download(`output.${meta?.out || "txt"}`, output)}
                className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400"
              >
                Download full file
              </button>
            ) : (
              <div className="rounded-xl border border-slate-800 p-5">
                <p className="text-sm text-slate-300">
                  Preview is free. Unlock full-file download + batch conversion.
                </p>
                <a
                  href={STRIPE_LINK}
                  className="mt-3 inline-block rounded-lg bg-sky-500 px-5 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400"
                >
                  Unlock
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
