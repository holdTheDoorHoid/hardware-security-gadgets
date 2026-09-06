# Sec Gadget Index

An independent, sourced comparison site for hardware security and pentest gadgets.
Dark theme, fully static, no build step, no dependencies at runtime.

## Run it

```bash
./serve.sh          # http://localhost:8080
```

Or just open `index.html` in a browser. The data is plain JavaScript rather than
JSON specifically so the site works from `file://` with no server at all.

## Pages

| Page | What it does |
|---|---|
| `index.html` | Browse, search, and filter every build. Search matches capability names *and* the original spreadsheet column names. |
| `quiz.html` | Six questions, then at most three recommendations with reasons and caveats. |
| `compare.html` | Side-by-side matrix of up to six builds, with a "only show rows that differ" toggle. |
| `device.html?id=…` | Full breakdown: capabilities by group, hardware, legal, project health, sources. |
| `glossary.html` | Every tracked capability in plain English, with reality checks. |
| `about.html` | Method, confidence levels, and the legal position. |

## Data model

Everything lives in two files.

- **`data/taxonomy.js`** — the capability dictionary. 117 capabilities in 13 groups,
  each with a plain-English definition, a technical detail, an optional reality check,
  a legal flag, and `aliases` that preserve the original spreadsheet column names.
- **`data/devices.js`** — the devices. One object per *build*, where a build is
  hardware plus firmware. Objects sharing a `hardware_id` are the same physical device
  running different firmware, and the site links them to each other.

Capability values are `yes` / `partial` / `addon` / `claimed` / `no` / `unknown`.
`claimed` means the vendor asserts it and no independent confirmation was found.
Never upgrade a `claimed` to a `yes` without a source.

## Regenerating

Research lives as one JSON array per batch in `research/`. To rebuild:

```bash
python3 build.py          # research/batch-*.json  ->  data/devices.js
```

`build.py` validates every record against the controlled vocabularies and the
capability dictionary, drops unknown capability keys, de-duplicates ids, and prints a
report of problems and warnings. It is safe to run repeatedly.

To regenerate the expanded spreadsheet:

```bash
.venv/bin/python export_xlsx.py     # -> "Sec Tools - expanded.xlsx"
```

The export preserves the original sheet's 76 columns in their original order and
appends 27 new research columns, plus sheets for the full capability matrix, the
glossary, and every source URL.

## Adding a device by hand

Append an object to `data/devices.js` following `research/SCHEMA.md`. The only truly
required fields are `id`, `hardware_id`, `name`, `vendor`, `category`, `status`,
`skill_level`, `build_effort`, `stealth`, `form_factor`, and `summary`. Everything
else degrades gracefully — a missing section simply does not render.

## Hosting it online

It is a folder of static files, so anything works: GitHub Pages, Netlify drag-and-drop,
Cloudflare Pages, or any web server. There is no backend and nothing to configure.

## Deliberately out of scope

Monitor-mode Wi-Fi adapters as standalone products, automotive and CAN tools, drone
hardware, and physical entry tools.
