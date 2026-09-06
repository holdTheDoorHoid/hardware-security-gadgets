#!/usr/bin/env python3
"""Verify every device named in the original spreadsheet appears in the built dataset."""
import json, os, re, zipfile, sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX = os.environ.get("ORIG_XLSX", "/home/hoid/Downloads/sec tools.xlsx")
NS   = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def original_names():
    z = zipfile.ZipFile(XLSX)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            ss.append("".join(t.text or "" for t in si.iter(NS+"t")))
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    names, fw = [], []
    for row in root.iter(NS+"row"):
        cells = {}
        for c in row.findall(NS+"c"):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find(NS+"v")
            if v is None: continue
            cells[col] = ss[int(v.text)] if c.get("t") == "s" else v.text
        if row.get("r") == "1": continue
        if cells.get("A"):
            names.append((cells["A"].strip(), (cells.get("C") or "").strip()))
    return names

def norm(s):
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\b(v|ver|version|mark|mk)\s*([0-9])", r"\2", s)
    return " ".join(s.split())

def tokens(s):
    stop = {"the","a","of","and","for","with","pro","basic","mini","plus"}
    return {t for t in norm(s).split() if t not in stop and len(t) > 1}

def main():
    src = open(os.path.join(ROOT,"data","devices.js")).read()
    dev = json.loads(src[src.index("window.DEVICES =")+len("window.DEVICES ="):].rstrip().rstrip(";"))

    hay = []
    for d in dev:
        blob = " ".join(filter(None, [d.get("name",""), d.get("firmware") or "",
                d.get("hardware_id",""), " ".join(d.get("aliases") or [])]))
        hay.append((d, norm(blob), tokens(blob)))

    orig = original_names()
    seen, missing, weak = [], [], []
    for name, fw in orig:
        nt, nn = tokens(name), norm(name)
        best, bestscore = None, 0.0
        for d, hn, ht in hay:
            if nn and nn in hn: score = 1.0
            elif nt and ht:     score = len(nt & ht) / len(nt)
            else:               score = 0.0
            if score > bestscore: best, bestscore = d, score
        if bestscore >= 0.75:  seen.append((name, fw, best["name"], bestscore))
        elif bestscore >= 0.4: weak.append((name, fw, best["name"] if best else "-", bestscore))
        else:                  missing.append((name, fw))

    uniq_orig = {n for n,_ in orig}
    print(f"original sheet: {len(orig)} rows, {len(uniq_orig)} distinct device names")
    print(f"built dataset : {len(dev)} builds\n")
    print(f"MATCHED  {len(seen)}")
    print(f"WEAK     {len(weak)}   (probably fine, verify)")
    print(f"MISSING  {len(missing)}\n")
    if weak:
        print("--- weak matches ---")
        for n,f,m,s in sorted(set(weak)): print(f"  {n!r:52s} -> {m!r}  ({s:.2f})")
    if missing:
        print("\n--- NOT FOUND IN DATASET ---")
        for n,f in sorted(set(missing)): print(f"  {n}" + (f"   [fw: {f}]" if f else ""))
    return 1 if missing else 0

if __name__ == "__main__":
    sys.exit(main())
