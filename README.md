# Sec Gadget Index

An independent, sourced comparison site for hardware security and pentest gadgets.
Dark theme, fully static, no build step, no dependencies at runtime.

**176 builds across 161 distinct devices, 947 cited sources, 118 tracked capabilities.**

**Live at <https://holdthedoorhoid.github.io/hardware-security-gadgets/>**

---

## Updating the data (no software needed)

This is the whole loop. It does not change, and it needs nothing installed.

1. Go to **github.com** and sign in.
2. Open the **hardware-security-gadgets** repository.
3. Click into the **`data`** folder. *This step matters — see the warnings.*
4. Click **Add file → Upload files**.
5. Drag the new **`devices.js`** into the browser window.
6. Type what changed, e.g. *"March 2027 data update"*.
7. Click **Commit changes**.
8. Wait about a minute, open the site, and press **Ctrl+Shift+R** (**Cmd+Shift+R** on a Mac).
   The "builds listed" number on the browse page should reflect the new data.

**Two ways this goes wrong, both silent:**

- The file must be named exactly `devices.js`. Not `devices (1).js`. Browsers rename
  downloads automatically, so check before you drag.
- It must go **inside the `data` folder**. Drop it at the top level and GitHub accepts it,
  the site rebuilds successfully, and it quietly keeps serving the old data. No error appears.

**If something breaks:** on the repository page click **Commits**, find the one before the
break, and press **Revert**. The site is back within a minute. Nothing here is permanent.

If you regenerate the data rather than hand-editing it, run `python3 build.py` first — that
writes the new `data/devices.js` — then follow the eight steps above unchanged.

---

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

The browse page and every device page automatically surface **same firmware, cheaper
hardware** pairs. `valueGaps()` and `cheaperEquivalents()` in `js/common.js` group
builds by named open-source firmware project, ignoring generic labels like "Stock",
and flag where identical software runs on very differently priced hardware.
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
