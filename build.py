#!/usr/bin/env python3
"""Merge research/batch-*.json into data/devices.js, validating against the taxonomy."""
import json, glob, os, re, sys, datetime
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
RES  = os.path.join(ROOT, "research")
OUT  = os.path.join(ROOT, "data", "devices.js")
LITE = os.path.join(ROOT, "data", "devices-lite.js")
TAX  = os.path.join(ROOT, "data", "taxonomy.js")

VOCAB = {
 "firmware_kind": {"stock","community","third-party-product","diy","n/a"},
 "category": {"multitool","wifi","rfid-nfc","subghz","bluetooth","usb-hid","network-implant",
              "sdr","hardware-debug","wardriving","detection-defense","accessory",
              "automotive"},
 "status": {"available","preorder","out-of-stock","discontinued","diy-only","vaporware"},
 "skill_level": {"beginner","intermediate","advanced","expert"},
 "build_effort": {"assembled","flash-only","assembly","soldering","full-diy"},
 "stealth": {"overt","discreet","covert","implant"},
 "form_factor": {"handheld","pocket","keychain","usb-stick","cable","wearable","board","box","hat-shield","desktop"},
}
NESTED_VOCAB = {
 ("legal","risk_level"): {"low","medium","high"},
 ("ecosystem","community"): {"very-active","active","slow","dormant","dead","commercial"},
 ("ecosystem","docs_quality"): {"excellent","good","sparse","poor","none"},
 ("ecosystem","abandoned_risk"): {"low","medium","high","already-abandoned"},
}
CAPVALS = {"yes","no","partial","addon","claimed","unknown"}
REQUIRED = ["id","hardware_id","name","vendor","category","status","skill_level",
            "build_effort","stealth","form_factor","summary"]

def known_cap_keys():
    src = open(TAX).read()
    body = src[src.index("caps:"): src.index("glossary:")]
    return set(re.findall(r'^\s{4}([a-z0-9_]+)\s*:\s*\{', body, re.M))

def slug(s):
    return re.sub(r"[^a-z0-9]+","-", str(s).lower()).strip("-")

def main():
    caps_ok = known_cap_keys()
    files = sorted(glob.glob(os.path.join(RES,"batch-*.json")))
    if not files:
        print("no batch files found in research/"); return 1

    devices, problems, warns = [], [], []
    per_file = {}

    for f in files:
        base = os.path.basename(f)
        try:
            data = json.load(open(f))
        except Exception as e:
            problems.append(f"{base}: JSON parse failed - {e}"); continue
        if not isinstance(data, list):
            problems.append(f"{base}: top level is not an array"); continue
        per_file[base] = len(data)
        for i, d in enumerate(data):
            if not isinstance(d, dict):
                problems.append(f"{base}[{i}]: not an object"); continue
            d["_src"] = base
            devices.append(d)

    # --- ids ---
    # Two research agents working different batches can independently write the
    # same device. Renaming the second one to '<id>-2' hides that: the site then
    # shows the same product twice with two different capability matrices, and
    # whichever agent researched it less thoroughly gets equal billing.
    # So: same id AND same hardware => merge the records. Only a genuine slug
    # collision between different hardware gets renamed.
    CONF = {"yes": 4, "no": 4, "partial": 4, "addon": 4, "claimed": 2, "unknown": 1}
    LIST_FIELDS = ["best_for", "not_for", "aliases", "research_gaps", "sources"]

    def merge_into(keep, drop):
        """Fold `drop` into `keep`. Prefer confirmed data over vendor claims."""
        for k, v in drop.items():
            if k in ("_src", "id", "capabilities") or k in LIST_FIELDS:
                continue
            cur = keep.get(k)
            if cur in (None, "", {}, []):
                keep[k] = v
            elif k in ("summary", "honest_take") and isinstance(v, str) and isinstance(cur, str) \
                 and len(v) > len(cur):
                keep[k] = v            # the fuller write-up wins
        for k in LIST_FIELDS:
            a, b = keep.get(k) or [], drop.get(k) or []
            if isinstance(a, list) and isinstance(b, list):
                out, marks = [], set()
                for item in a + b:
                    mark = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
                    if mark not in marks:
                        marks.add(mark); out.append(item)
                keep[k] = out
        kc = keep.setdefault("capabilities", {})
        for cap, val in (drop.get("capabilities") or {}).items():
            if cap not in kc:
                kc[cap] = val; continue
            a, b = kc[cap], val
            av = a.get("v") if isinstance(a, dict) else None
            bv = b.get("v") if isinstance(b, dict) else None
            if CONF.get(bv, 0) > CONF.get(av, 0):
                kc[cap] = b
            elif av != bv and CONF.get(av, 0) == CONF.get(bv, 0):
                warns.append(f"MERGE CONFLICT {keep['id']}.{cap}: "
                             f"'{av}' ({keep.get('_src')}) vs '{bv}' ({drop.get('_src')}) - kept '{av}'")
        keep["_merged_from"] = sorted(set((keep.get("_merged_from") or []) + [drop.get("_src")]))

    seen, merged_out = {}, []
    for d in devices:
        if not d.get("id"):
            d["id"] = slug(f"{d.get('name','unknown')}-{d.get('firmware','')}") or "unknown"
        if not d.get("hardware_id"):
            d["hardware_id"] = slug(d.get("name", "unknown"))
        base_id = d["id"]
        prior = seen.get(base_id)
        if prior is not None and prior.get("hardware_id") == d.get("hardware_id"):
            warns.append(f"MERGED duplicate '{base_id}': {d.get('_src')} folded into {prior.get('_src')}")
            merge_into(prior, d)
            merged_out.append(d)
            continue
        n = 2
        while d["id"] in seen:
            d["id"] = f"{base_id}-{n}"; n += 1
            warns.append(f"id collision '{base_id}' (different hardware) -> renamed '{d['id']}' ({d.get('_src')})")
        seen[d["id"]] = d
    devices = [d for d in devices if d not in merged_out]

    # --- normalise firmware labels (they must work as a short badge) ---
    for d in devices:
        fw = (d.get("firmware") or "").strip()
        if not fw:
            d["firmware"] = None
            continue
        original = fw
        if re.match(r"^n/?a\b", fw, re.I):
            rest = re.sub(r"^n/?a\s*[-–—:]?\s*", "", fw, flags=re.I).strip()
            d["firmware"] = None
            if rest:
                d["firmware_note"] = d.get("firmware_note") or rest[0].upper()+rest[1:]
            continue
        if len(fw) > 30:
            head = re.split(r"\s+[-–—]\s+|\s*\(", fw)[0].strip()
            if not head or len(head) > 30:
                head = "Custom"
            d["firmware"] = head
            if original.lower() not in (d.get("firmware_note") or "").lower():
                d["firmware_note"] = ((d.get("firmware_note") or "") + " " + original).strip()
            warns.append(f"{d.get('name')}: long firmware label shortened to '{head}' (full text kept in firmware_note)")

    # --- validate ---
    for d in devices:
        tag = f"{d.get('name','?')} [{d.get('_src')}]"
        for r in REQUIRED:
            if not d.get(r):
                problems.append(f"{tag}: missing required field '{r}'")
        for k, allowed in VOCAB.items():
            v = d.get(k)
            if v and v not in allowed:
                problems.append(f"{tag}: {k}='{v}' not in vocabulary")
        for (parent, child), allowed in NESTED_VOCAB.items():
            v = (d.get(parent) or {}).get(child)
            if v and v not in allowed:
                problems.append(f"{tag}: {parent}.{child}='{v}' not in vocabulary")
        caps = d.get("capabilities") or {}
        if not isinstance(caps, dict):
            problems.append(f"{tag}: capabilities is not an object"); caps = {}
        fixed = {}
        for k, v in caps.items():
            if k not in caps_ok:
                warns.append(f"{tag}: unknown capability key '{k}' (dropped)"); continue
            if isinstance(v, str):
                v = {"v": v, "note": ""}
            if not isinstance(v, dict):
                warns.append(f"{tag}: capability '{k}' malformed (dropped)"); continue
            val = v.get("v","unknown")
            if val not in CAPVALS:
                warns.append(f"{tag}: capability '{k}' value '{val}' invalid -> unknown"); val = "unknown"
            fixed[k] = {"v": val, "note": v.get("note","") or ""}
        d["capabilities"] = fixed
        if d.get("price_usd") is not None:
            try: d["price_usd"] = float(d["price_usd"])
            except Exception:
                warns.append(f"{tag}: price_usd '{d['price_usd']}' not numeric -> null")
                d["price_usd"] = None
        if not d.get("honest_take"):
            warns.append(f"{tag}: no honest_take (the most important field)")
        if not d.get("sources"):
            warns.append(f"{tag}: no sources listed")

    # --- apply gapfill patches (research/gapfill.json) ---
    gp = os.path.join(RES, "gapfill.json")
    if os.path.exists(gp):
        try:
            patches = json.load(open(gp))
        except Exception as e:
            problems.append(f"gapfill.json: parse failed - {e}")
            patches = []
        applied = skipped = 0
        for pt in patches:
            key = pt.get("capability")
            if key not in caps_ok:
                warns.append(f"gapfill: unknown capability '{key}' (skipped)"); continue
            val = pt.get("v", "unknown")
            if val not in CAPVALS:
                warns.append(f"gapfill: bad value '{val}' for '{key}' (skipped)"); continue
            nc = (pt.get("name_contains") or "").lower()
            fc = (pt.get("firmware_contains") or "")
            hit = 0
            for d in devices:
                if nc and nc not in d.get("name", "").lower():
                    continue
                if fc and fc.lower() not in str(d.get("firmware") or "").lower():
                    continue
                d.setdefault("capabilities", {})[key] = {"v": val, "note": pt.get("note", "") or ""}
                for src in (pt.get("sources") or []):
                    d.setdefault("sources", []).append(src)
                hit += 1
            if hit: applied += 1
            else:
                skipped += 1
                warns.append(f"gapfill: '{nc}'{' / '+fc if fc else ''} matched no build for '{key}'")
        print(f"gapfill: {applied} patches applied, {skipped} matched nothing")

    for d in devices:
        d.pop("_src", None)

    devices.sort(key=lambda d: (d.get("name","").lower(), str(d.get("firmware") or "")))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT,"w") as fh:
        fh.write("/* GENERATED by build.py — edit research/batch-*.json and re-run, or edit here directly.\n")
        fh.write(f"   built {datetime.date.today().isoformat()} · {len(devices)} builds */\n")
        fh.write("window.DEVICES = ")
        json.dump(devices, fh, indent=1, ensure_ascii=False)
        fh.write(";\n")

    # --- lite dataset -------------------------------------------------------
    # The browse grid and the quiz need every device but almost none of the
    # prose. Capability NOTES alone are a quarter of the full file, and
    # hardware/sources/research_gaps another third, yet only the device and
    # compare pages ever read them. Serving the full file everywhere made every
    # visit a ~950KB download.
    LITE_KEEP = ["id","hardware_id","name","firmware","firmware_kind","vendor","category",
                 "subcategory","status","price_usd","price_is_estimate","skill_level",
                 "skill_note","build_effort","stealth","form_factor","summary",
                 "honest_take","released","aliases"]
    lite = []
    for d in devices:
        o = {k: d[k] for k in LITE_KEEP if d.get(k) is not None}
        # cap() in common.js already accepts a bare string, so drop the notes
        o["capabilities"] = {k: v["v"] for k, v in (d.get("capabilities") or {}).items()}
        lg = d.get("legal") or {}
        first = (lg.get("notes") or "").split(".")[0].strip()
        o["legal"] = {"risk_level": lg.get("risk_level")}
        if first: o["legal"]["notes"] = first + "."
        o["ecosystem"] = d.get("ecosystem") or {}
        lite.append(o)
    with open(LITE, "w", encoding="utf-8") as fh:
        fh.write("/* GENERATED by build.py - trimmed dataset for the browse grid and quiz.\n")
        fh.write("   No capability notes, hardware, sources or research gaps: those pages\n")
        fh.write("   never read them. Use devices.js for device and compare pages. */\n")
        fh.write("window.DEVICES = ")
        json.dump(lite, fh, separators=(",", ":"), ensure_ascii=False)
        fh.write(";\n")
    print(f"wrote {LITE} ({os.path.getsize(LITE)/1024:.0f} KB vs {os.path.getsize(OUT)/1024:.0f} KB full)")

    # --- report ---
    hw = len({d["hardware_id"] for d in devices})
    print(f"merged {len(files)} files -> {len(devices)} builds across {hw} distinct devices")
    for f,n in per_file.items(): print(f"   {f:38s} {n:3d}")
    print(f"\nby category:")
    for c,n in Counter(d.get("category") for d in devices).most_common(): print(f"   {str(c):20s} {n}")
    print(f"by skill:")
    for c,n in Counter(d.get("skill_level") for d in devices).most_common(): print(f"   {str(c):20s} {n}")
    used = Counter()
    for d in devices:
        for k,v in d["capabilities"].items():
            if v["v"] in ("yes","partial","addon","claimed"): used[k]+=1
    print(f"\ncapabilities used: {len(used)} of {len(caps_ok)} defined")
    unused = sorted(caps_ok - set(used))
    if unused: print(f"   never used: {', '.join(unused)}")
    priced = [d for d in devices if d.get("price_usd") is not None]
    if priced:
        print(f"\nprices: {len(priced)}/{len(devices)} have one, "
              f"${min(d['price_usd'] for d in priced):.0f}–${max(d['price_usd'] for d in priced):.0f}")

    if warns:
        print(f"\n--- {len(warns)} warnings ---")
        for w in warns[:40]: print("  ! "+w)
        if len(warns)>40: print(f"  ... and {len(warns)-40} more")
    if problems:
        print(f"\n--- {len(problems)} PROBLEMS ---")
        for p in problems[:60]: print("  X "+p)
        if len(problems)>60: print(f"  ... and {len(problems)-60} more")
    print(f"\nwrote {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
