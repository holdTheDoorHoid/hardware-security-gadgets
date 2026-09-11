#!/usr/bin/env python3
"""Validate research/expand/records/*.json and stage them as research/ batches.

Run with --check to validate only. Without it, writes the batch files.
Never deletes anything; refuses to overwrite an existing research/batch-* file
unless it was written by this script (it stamps _staged_by).
"""
import json, glob, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REC  = os.path.join(ROOT, "research", "expand", "records")
RES  = os.path.join(ROOT, "research")
TAX  = os.path.join(ROOT, "data", "taxonomy.js")

CAPVALS = {"yes","no","partial","addon","claimed","unknown"}
REQUIRED = ["id","hardware_id","name","vendor","category","status","skill_level",
            "summary","honest_take"]
ENUMS = {
 "firmware_kind": {"stock","community","third-party-product","diy","n/a"},
 "category": {"multitool","wifi","rfid-nfc","subghz","bluetooth","usb-hid",
              "network-implant","sdr","hardware-debug","wardriving",
              "detection-defense","accessory","automotive"},
 "status": {"available","preorder","out-of-stock","discontinued","diy-only","vaporware"},
 "skill_level": {"beginner","intermediate","advanced","expert"},
 "build_effort": {"assembled","flash-only","assembly","soldering","full-diy"},
 "stealth": {"overt","discreet","covert","implant"},
 "form_factor": {"handheld","pocket","keychain","usb-stick","cable","wearable","board",
                 "box","hat-shield","desktop"},
}

def known_caps():
    s = open(TAX).read()
    body = s[s.index("caps:"): s.index("glossary:")]
    return set(re.findall(r'^\s{4}([a-z0-9_]+)\s*:\s*\{', body, re.M))

def main():
    check = "--check" in sys.argv
    caps_ok = known_caps()
    files = sorted(glob.glob(os.path.join(REC, "*.json")))
    if not files:
        print("no record files yet"); return
    allrec, problems, thin = [], [], []
    wanted_keys = collections.Counter()
    seen_id = {}
    for f in files:
        base = os.path.basename(f)
        try:
            data = json.load(open(f))
        except Exception as e:
            problems.append(f"{base}: will not parse - {e}"); continue
        if not isinstance(data, list):
            problems.append(f"{base}: top level is not a list"); continue
        for i, r in enumerate(data):
            tag = f"{base}[{i}] {r.get('name','?')}"
            for k in REQUIRED:
                if not r.get(k): problems.append(f"{tag}: missing {k}")
            for k, allowed in ENUMS.items():
                if r.get(k) and r[k] not in allowed:
                    problems.append(f"{tag}: {k}='{r[k]}' not in vocabulary")
            rid = r.get("id")
            if rid in seen_id:
                problems.append(f"{tag}: duplicate id, also in {seen_id[rid]}")
            elif rid: seen_id[rid] = base
            caps = r.get("capabilities") or {}
            for k, v in caps.items():
                if k not in caps_ok:
                    wanted_keys[k] += 1
                    problems.append(f"{tag}: capability key '{k}' unknown - WILL BE DROPPED")
                val = v.get("v") if isinstance(v, dict) else v
                if val not in CAPVALS:
                    problems.append(f"{tag}: capability '{k}' value '{val}' invalid")
            ncap, nsrc = len(caps), len(r.get("sources") or [])
            if ncap < 8 or nsrc < 3:
                thin.append((base, r.get("name"), ncap, nsrc))
            r["_batch_src"] = base
            allrec.append(r)
    # capability keys agents asked for in research_gaps
    asked = collections.Counter()
    for r in allrec:
        for g in (r.get("research_gaps") or []):
            m = re.search(r"no capability key for ([a-z0-9_ /-]+)", str(g), re.I)
            if m: asked[m.group(1).strip()] += 1

    print(f"files            : {len(files)}")
    print(f"records          : {len(allrec)}")
    caps=[len(r.get('capabilities') or {}) for r in allrec] or [0]
    src =[len(r.get('sources') or []) for r in allrec] or [0]
    print(f"capabilities avg : {sum(caps)/len(caps):.1f}   (existing DB: 16.2)")
    print(f"sources avg      : {sum(src)/len(src):.1f}   (existing DB: 5.4)")
    print(f"thin records     : {len(thin)}  (<8 caps or <3 sources)")
    for b,n,c,s in thin[:25]: print(f"    {n[:44]:<46} caps={c:<3} src={s} [{b}]")
    if wanted_keys:
        print(f"\nunknown capability keys used ({len(wanted_keys)}) - add to taxonomy or they vanish:")
        for k,c in wanted_keys.most_common(): print(f"    {k:<28} x{c}")
    if asked:
        print(f"\ncapability keys agents asked for in research_gaps:")
        for k,c in asked.most_common(): print(f"    {k:<34} x{c}")
    print(f"\nproblems: {len(problems)}")
    for p in problems[:40]: print("   ", p)
    if len(problems) > 40: print(f"    ... and {len(problems)-40} more")

    if check: return
    if problems:
        print("\nNOT staging - fix the problems above first."); return
    for f in files:
        base = os.path.basename(f).replace(".json","")
        out = os.path.join(RES, f"batch-20-{base}.json")
        if os.path.exists(out):
            prev = json.load(open(out))
            if not (prev and isinstance(prev, list) and prev[0].get("_staged_by") == "integrate.py"):
                print(f"refusing to overwrite {out} (not staged by this script)"); continue
        data = json.load(open(f))
        for r in data: r["_staged_by"] = "integrate.py"
        json.dump(data, open(out, "w"), indent=1, ensure_ascii=False)
        print(f"staged {out} ({len(data)})")

main()
