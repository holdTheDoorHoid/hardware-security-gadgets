#!/usr/bin/env python3
"""Merge phase-1 candidate files, drop duplicates against HAVE.txt and each other."""
import json, os, glob, re, sys, difflib

D = os.path.dirname(os.path.abspath(__file__))
have = [l.strip() for l in open(os.path.join(D,"HAVE.txt")) if l.strip()]

# "Pro", "Plus", "Mini", "Ultra" etc are how this market names genuinely
# different hardware (Biscuit Pro vs Biscuit Ultra: 3x battery, RP-SMA, SD
# slot). Stripping them as noise silently eats real devices, so they stay.
# Only true packaging words are removed.
NOISE = r"\b(the|kit|bundle|edition|version|new|original|official)\b"

def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    # Version tokens are NOT stripped: "Marauder v6.1" and "Marauder v7" are
    # different boards at different prices, and collapsing them loses one.
    s = re.sub(NOISE, " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# Words that may differ between two names and still mean the same product.
# Anything NOT in here is treated as a model distinction.
IGNORABLE = {"usb","board","device","tool","module","dongle","adapter","for","and",
             "with","by","sdr","rf","wifi","wi","fi","nfc","rfid"}

def same_product(a, b):
    """True only if the leftover words between two names are all ignorable."""
    ta, tb = set(a.split()), set(b.split())
    if not ta or not tb: return False
    if ta == tb: return True
    if not (ta <= tb or tb <= ta): return False
    return (ta ^ tb) <= IGNORABLE

have_n = {norm(h): h for h in have}
have_keys = list(have_n)

def match_have(name):
    """Returns (certain_dupe_of, possible_dupe_of). Only a certain match is
    dropped. Anything merely similar is kept as new and flagged for review -
    a false 'new' costs one glance, a false 'dupe' loses a device silently."""
    n = norm(name)
    if not n: return None, None
    if n in have_n: return have_n[n], None
    for k in have_keys:
        if same_product(n, k): return have_n[k], None
    c = difflib.get_close_matches(n, have_keys, n=1, cutoff=0.80)
    return (None, have_n[c[0]]) if c else (None, None)

rows, bad = [], []
for f in sorted(glob.glob(os.path.join(D,"cand-*.json"))):
    src = os.path.basename(f)[5:-5]
    try:
        data = json.load(open(f))
    except Exception as e:
        bad.append(f"{src}: {e}"); continue
    if not isinstance(data, list): bad.append(f"{src}: not a list"); continue
    for r in data:
        if isinstance(r, dict) and r.get("name"):
            r["_src"] = src; rows.append(r)

BADGE = re.compile(r"\b(badge|sao|shitty add-?on|defcon \d|def con \d)\b", re.I)
OUT   = re.compile(r"\b(implant(able)?|xseries|x-?series|magic card|gen1a|gen 1a|t5577|blank (card|tag|fob))\b", re.I)

new, dupes, dropped, near, seen = [], [], [], [], {}
for r in rows:
    name = r["name"].strip()
    blob = f"{name} {r.get('one_line','')} {r.get('why_notable','')}"
    if BADGE.search(name) or OUT.search(blob):
        dropped.append((r["_src"], name, "out of scope")); continue
    # the researching agent's own dupe_of call is evidence: it read the page
    declared = (r.get("dupe_of") or "").strip()
    if declared:
        dupes.append((r["_src"], name, declared + " [agent-declared]")); continue
    h, maybe = match_have(name)
    if h:
        dupes.append((r["_src"], name, h)); continue
    if maybe:
        r["_possible_dupe_of"] = maybe; near.append((r["_src"], name, maybe))
    n = norm(name)
    hit = n if n in seen else next((k for k in seen if same_product(n, k)), None)
    if hit:
        prev = seen[hit]
        prev["_also"] = sorted(set((prev.get("_also") or []) + [r["_src"]]))
        if not prev.get("price_usd") and r.get("price_usd"):
            prev["price_usd"] = r["price_usd"]; prev["seller_url"] = r.get("seller_url")
        elif r.get("price_usd") and prev.get("price_usd") and \
             abs(float(r["price_usd"]) - float(prev["price_usd"])) > 0.01:
            prev.setdefault("_price_seen", [prev["price_usd"]])
            if r["price_usd"] not in prev["_price_seen"]:
                prev["_price_seen"].append(r["price_usd"])
        continue
    seen[n] = r; new.append(r)

new.sort(key=lambda r: (r.get("category_guess") or "zz", -(r.get("price_usd") or 0)))
json.dump(new, open(os.path.join(D,"candidates-new.json"),"w"), indent=1)

print(f"files parsed : {len(set(r['_src'] for r in rows))}")
print(f"raw rows     : {len(rows)}")
print(f"dup of HAVE  : {len(dupes)}")
print(f"out of scope : {len(dropped)}")
print(f"NEW unique   : {len(new)}")
print(f"near-misses  : {len(near)}  (kept as new, flagged _possible_dupe_of)")
for s_, n_, m_ in near: print(f"    {n_}  ~=  {m_}   [{s_}]")
if bad: print("PARSE ERRORS :", *bad, sep="\n  ")
from collections import Counter
print("\nby category:", dict(Counter(r.get("category_guess","?") for r in new)))
print("by source  :", dict(Counter(r["_src"] for r in new)))
