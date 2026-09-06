#!/usr/bin/env python3
"""Export the merged dataset to an expanded XLSX that preserves the original
sheet's column layout and appends the new research columns."""
import json, re, os, sys, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "Sec Tools - expanded.xlsx")

# ---------- load generated data ----------
def load_devices():
    src = open(os.path.join(ROOT,"data","devices.js")).read()
    return json.loads(src[src.index("window.DEVICES =")+len("window.DEVICES ="):].rstrip().rstrip(";"))

def load_taxonomy():
    """Evaluate taxonomy.js with node — exact, no regex guessing."""
    import subprocess, tempfile
    js = ("global.window={};require(%r);"
          "process.stdout.write(JSON.stringify({caps:window.TAXONOMY.caps,"
          "glossary:window.TAXONOMY.glossary}));" % os.path.join(ROOT,"data","taxonomy.js"))
    out = subprocess.run(["node","-e",js], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    caps = {}
    for k, m in j["caps"].items():
        caps[k] = {"label":m.get("label",""), "plain":m.get("plain",""),
                   "detail":m.get("detail",""), "group":m.get("group",""),
                   "legal":m.get("legal",""), "myth":m.get("myth",""),
                   "aliases":m.get("aliases",[]) or []}
    return caps, j["glossary"]

DEV, (CAPS, GLOSS) = load_devices(), load_taxonomy()
ALIAS = {}
for k, m in CAPS.items():
    for a in m["aliases"]:
        ALIAS[a.lower()] = k

VAL = {"yes":"Yes","partial":"Partial","addon":"Add-on","claimed":"Claimed (unverified)","no":"No","unknown":"?"}

# original spreadsheet column order, preserved exactly
ORIG = ["Device","Price","Firmware","Hardware Company","Flipper Add-On","FindMy Flipper",
 "BLE Spammer","HID Attack","NFC Type 4 (NDEF on NTAG4xx/DESFire)","NFC EMV (Only basic card info)",
 "Subdriving","RGB Backlight","Primary Microcontroller","Secondary Microcontroller","Display",
 "Power","Battery","Battery Management","Micro SD","Case Body","Size","Weight","2.4Ghz Module",
 "Sub-GHz Mhz Modules","Microphone","Speaker","Vibration","Accelerometer","Gyro","Mag","RTC",
 "light sensor","Temperature","Humidity","NFC","iButton","IR Blaster","IR Reciver","WiFi Scanner",
 "Channel Analyzer","WiFi Deauther","Deauth Scanner","Flipper Scanner","Device Scout",
 "Pineapple Detector","nyanBOX Detector","Flock Detector","Axon Detector","Meshtastic Detector",
 "MeshCore Detector","Skimmer Detector","AirTag Detector","Tile Detector","RayBan Detector",
 "Drone Detector","Pwnagotchi Detector","Pwnagotchi Spam","Beacon Spam","BLE Spoofer","Evil Portal",
 "BLE Scanner","AirTag Spoofer","Swift Pair","Sour Apple","Sour Droid","Samsung Spam","Drone Spoofer",
 "RPG Leveling","Device Lock","Emergency Mode","Games","TxtViewer","Video Scroller","Timer",
 "Stopwatch","PC Monitor"]

NEW = ["Status","Skill Level","Effort to Run","Stealth","Form Factor","Category",
 "Legal Risk","Import Restrictions","Legal Notes","Community","Docs","Abandonment Risk",
 "Last Release","Summary","HONEST TAKE (what marketing won't say)","Good For","Not For",
 "Firmware Type","Firmware Repo","Vendor URL","Product URL","Price Checked","Price Note",
 "Sources","Could Not Confirm","id","hardware_id"]

SENSOR_KEYS = {"Microphone":["mic","microphone","ics-43"],"Speaker":["speaker","buzzer"],
 "Vibration":["vibrat","haptic","motor"],"Accelerometer":["accel","lsm","imu","mpu","bmi"],
 "Gyro":["gyro","imu","mpu","bmi"],"Mag":["magnet","mag ","compass","lsm303","lis3md"],
 "RTC":["rtc","max31329","pcf85","ds323"],"light sensor":["light","lux","ambient","als"],
 "Temperature":["temp","gxhtc","sht","bme","bmp"],"Humidity":["humid","gxhtc","sht","bme280"]}

def capv(d, key):
    c = (d.get("capabilities") or {}).get(key)
    if not c: return ""
    v = c.get("v","unknown")
    if v == "no": return ""
    s = VAL.get(v, v)
    n = (c.get("note") or "").strip()
    return f"{s} — {n}" if n and v in ("partial","addon","claimed") else s

def radios(d, roles):
    out = []
    for r in (d.get("hardware") or {}).get("radios") or []:
        role = (r.get("role") or "").lower()
        if any(x in role for x in roles):
            out.append(r.get("ic") or "")
    return ", ".join(x for x in out if x)

def sensor(d, col):
    s = " ".join(str(x).lower() for x in ((d.get("hardware") or {}).get("sensors") or []))
    s += " " + " ".join(str(x).lower() for x in ((d.get("hardware") or {}).get("notable_physical") or []))
    return "Yes" if any(k in s for k in SENSOR_KEYS[col]) else ""

def orig_cell(d, col):
    h = d.get("hardware") or {}
    if col == "Device": return d.get("name","")
    if col == "Price":
        p = d.get("price_usd")
        return "" if p is None else (f"~{p:g} (est. parts)" if d.get("price_is_estimate") else p)
    if col == "Firmware": return d.get("firmware","") or "Stock"
    if col == "Hardware Company": return d.get("vendor","")
    if col == "Flipper Add-On":
        blob = f"{d.get('category','')} {d.get('summary','')} {d.get('name','')}".lower()
        return "Yes" if d.get("category")=="accessory" and "flipper" in blob else ""
    if col == "Primary Microcontroller":   return h.get("mcu_primary") or ""
    if col == "Secondary Microcontroller": return h.get("mcu_secondary") or ""
    if col == "Display":
        x = h.get("display") or {}
        if not x.get("type"): return ""
        bits = [x.get("type")]
        if x.get("size_in"): bits.append(f'{x["size_in"]}"')
        if x.get("resolution"): bits.append(x["resolution"])
        if x.get("touch"): bits.append("touch")
        return " ".join(str(b) for b in bits)
    if col == "Power":   return h.get("charging") or ""
    if col == "Battery":
        return f'{h["battery_mah"]} mAh' if h.get("battery_mah") else (h.get("battery_note") or "")
    if col == "Battery Management": return h.get("pmic") or ""
    if col == "Micro SD":  return h.get("storage") or ""
    if col == "Case Body": return h.get("case") or ""
    if col == "Size":      return h.get("dimensions_mm") or ""
    if col == "Weight":    return f'{h["weight_g"]} g' if h.get("weight_g") else ""
    if col == "2.4Ghz Module":      return radios(d, ["wifi","ble","bluetooth","2.4","nrf24","zigbee"])
    if col == "Sub-GHz Mhz Modules":return radios(d, ["sub-ghz","subghz","sub ghz","lora"])
    if col in SENSOR_KEYS: return sensor(d, col)
    k = ALIAS.get(col.lower())
    return capv(d, k) if k else ""

def new_cell(d, col):
    L, E = d.get("legal") or {}, d.get("ecosystem") or {}
    j = lambda x: " | ".join(x) if isinstance(x, list) else (x or "")
    return {
     "Status":d.get("status",""), "Skill Level":d.get("skill_level",""),
     "Effort to Run":d.get("build_effort",""), "Stealth":d.get("stealth",""),
     "Form Factor":d.get("form_factor",""), "Category":d.get("category",""),
     "Legal Risk":L.get("risk_level",""), "Import Restrictions":j(L.get("import_restricted")),
     "Legal Notes":L.get("notes",""), "Community":E.get("community",""),
     "Docs":E.get("docs_quality",""), "Abandonment Risk":E.get("abandoned_risk",""),
     "Last Release":E.get("last_release",""), "Summary":d.get("summary",""),
     "HONEST TAKE (what marketing won't say)":d.get("honest_take",""),
     "Good For":j(d.get("best_for")), "Not For":j(d.get("not_for")),
     "Firmware Type":d.get("firmware_kind",""), "Firmware Repo":d.get("firmware_repo",""),
     "Vendor URL":d.get("vendor_url",""), "Product URL":d.get("product_url",""),
     "Price Checked":d.get("price_checked",""), "Price Note":d.get("price_note",""),
     "Sources":" | ".join(s.get("url","") for s in (d.get("sources") or [])),
     "Could Not Confirm":j(d.get("research_gaps")),
     "id":d.get("id",""), "hardware_id":d.get("hardware_id",""),
    }.get(col,"")

# ---------- styling ----------
HDR  = PatternFill("solid", fgColor="1B2733")
HDR2 = PatternFill("solid", fgColor="14302A")
HF   = Font(bold=True, color="D7E4EE", size=9)
GF   = Font(bold=True, color="6EE7A8", size=9)
THIN = Side(style="thin", color="2A3D4D")
BOX  = Border(left=THIN,right=THIN,top=THIN,bottom=THIN)
WRAP = Alignment(vertical="top", wrap_text=True)
TOP  = Alignment(vertical="top")

def style_header(ws, cols, groupcols=()):
    for i,c in enumerate(cols,1):
        cell = ws.cell(1,i,c)
        cell.fill = HDR2 if c in groupcols else HDR
        cell.font = GF if c in groupcols else HF
        cell.alignment = Alignment(vertical="bottom", wrap_text=True, textRotation=0)
        cell.border = BOX
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"

def widths(ws, spec, default=13):
    for i in range(1, ws.max_column+1):
        ws.column_dimensions[get_column_letter(i)].width = spec.get(ws.cell(1,i).value, default)

wb = Workbook(); wb.remove(wb.active)

# ---------- Sheet 1: Devices ----------
ws = wb.create_sheet("Devices")
cols = ORIG + NEW
for d in sorted(DEV, key=lambda x:(x.get("name","").lower(), str(x.get("firmware") or ""))):
    ws.append([orig_cell(d,c) for c in ORIG] + [new_cell(d,c) for c in NEW])
ws.insert_rows(1); style_header(ws, cols, groupcols=set(NEW))
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = TOP; c.border = BOX
W = {c:11 for c in cols}
W.update({"Device":24,"Firmware":16,"Hardware Company":20,"Primary Microcontroller":22,
 "Secondary Microcontroller":20,"Display":24,"Battery":14,"Micro SD":18,"Size":22,
 "Sub-GHz Mhz Modules":16,"2.4Ghz Module":18,"Summary":60,
 "HONEST TAKE (what marketing won't say)":75,"Legal Notes":55,"Good For":36,"Not For":36,
 "Sources":45,"Could Not Confirm":38,"Firmware Repo":38,"Product URL":32,"Vendor URL":26,
 "Price Note":38,"Import Restrictions":26,"Status":13,"Skill Level":13,"Effort to Run":14,
 "NFC Type 4 (NDEF on NTAG4xx/DESFire)":16,"NFC EMV (Only basic card info)":16})
widths(ws, W)
for r in range(2, ws.max_row+1):
    for c in ("Summary","HONEST TAKE (what marketing won't say)","Legal Notes","Good For","Not For","Could Not Confirm","Price Note"):
        ws.cell(r, cols.index(c)+1).alignment = WRAP
    ws.row_dimensions[r].height = 58

# ---------- Sheet 2: Capability matrix ----------
ws2 = wb.create_sheet("Capability Matrix")
order = sorted(CAPS, key=lambda k:(CAPS[k]["group"], CAPS[k]["label"]))
hdr = ["Device","Firmware","Price"] + [CAPS[k]["label"] for k in order]
ws2.append(hdr)
ws2.append(["","",""] + [CAPS[k]["group"] for k in order])
for d in sorted(DEV, key=lambda x:(x.get("name","").lower(), str(x.get("firmware") or ""))):
    ws2.append([d.get("name",""), d.get("firmware","") or "Stock", d.get("price_usd")]
               + [capv(d,k).split(" — ")[0] for k in order])
for i,c in enumerate(hdr,1):
    cell = ws2.cell(1,i); cell.fill=HDR; cell.font=HF
    cell.alignment = Alignment(textRotation=60, vertical="bottom") if i>3 else Alignment(vertical="bottom")
    ws2.column_dimensions[get_column_letter(i)].width = 20 if i<=2 else (9 if i>3 else 8)
for i in range(1, ws2.max_column+1):
    ws2.cell(2,i).font = Font(italic=True, color="7B8E9E", size=8)
ws2.freeze_panes = "D3"; ws2.row_dimensions[1].height = 150

# ---------- Sheet 3: Glossary ----------
ws3 = wb.create_sheet("Glossary")
ws3.append(["Group","Capability","Plain English","Technical detail","Reality check","Also sold as","Legal","Builds with it"])
for k in order:
    m = CAPS[k]
    n = sum(1 for d in DEV if (d.get("capabilities") or {}).get(k,{}).get("v") in ("yes","partial","addon","claimed"))
    ws3.append([m["group"], m["label"], m["plain"], m["detail"], m["myth"], " · ".join(m["aliases"]), m["legal"], n])
style_header(ws3, [c.value for c in ws3[1]])
widths(ws3, {"Group":14,"Capability":26,"Plain English":62,"Technical detail":58,
             "Reality check":62,"Also sold as":26,"Legal":11,"Builds with it":9})
for row in ws3.iter_rows(min_row=2):
    for c in row: c.alignment = WRAP; c.border = BOX
ws3.append([]); ws3.append(["General terms"])
ws3.cell(ws3.max_row,1).font = Font(bold=True, color="6EE7A8")
for t,dfn in sorted(GLOSS.items()):
    ws3.append(["", t, dfn]); ws3.cell(ws3.max_row,3).alignment = WRAP

# ---------- Sheet 4: Sources ----------
ws4 = wb.create_sheet("Sources")
ws4.append(["Device","Firmware","URL","What it establishes"])
for d in sorted(DEV, key=lambda x:x.get("name","").lower()):
    for s in d.get("sources") or []:
        ws4.append([d.get("name",""), d.get("firmware","") or "Stock", s.get("url",""), s.get("what","")])
style_header(ws4, ["Device","Firmware","URL","What it establishes"])
widths(ws4, {"Device":26,"Firmware":16,"URL":78,"What it establishes":52})

# ---------- Sheet 5: Read me ----------
ws5 = wb.create_sheet("Read Me", 0)
for line in [
 ["Sec Tools — expanded"],[""],
 [f"Generated {datetime.date.today().isoformat()} from sourced research. {len(DEV)} builds across "
  f"{len({d.get('hardware_id') for d in DEV})} distinct devices."],[""],
 ["HOW TO READ THIS"],
 ["Every capability cell carries a confidence level, not a tick, because most spec sheets in this space are marketing:"],
 ["   Yes                  Confirmed against a source (schematic, repo, datasheet or teardown)."],
 ["   Partial              Works, but with real limits. The limit is written in the cell."],
 ["   Add-on               Needs extra hardware bought separately. The cell names it."],
 ["   Claimed (unverified) The seller says so and we could not independently confirm it. Ask before buying."],
 ["   (blank)              Confirmed absent, or not applicable."],
 ["   ?                    Could not determine either way."],[""],
 ["SHEETS"],
 ["   Devices             Your original columns, filled in and corrected, plus new research columns (green headers)."],
 ["   Capability Matrix   Every tracked capability against every build, as a dense grid."],
 ["   Glossary            What each capability actually means, in plain English, with reality checks."],
 ["   Sources             The URL behind each device's claims."],[""],
 ["THE HONEST TAKE COLUMN"],
 ["The most useful column on the Devices sheet. It says the thing the seller will not: whether a"],
 ["'detector' is really a Bluetooth scan with a filter list, whether a $200 handheld runs the same free"],
 ["firmware you could flash onto a $15 board, and whether the advertised attack still works on anything modern."],[""],
 ["FIRMWARE IS LISTED SEPARATELY"],
 ["The same hardware running different firmware appears as separate rows sharing a hardware_id, because"],
 ["in daily use they are different products. Compare rows within a hardware_id to see what firmware buys you."],[""],
 ["LEGAL"],
 ["Owning nearly everything here is lawful in most countries. Using the transmit and attack features against"],
 ["systems you do not own or have written permission to test is a criminal offence in most of them. The Legal"],
 ["Risk and Import Restrictions columns are research, not legal advice."],
]:
    ws5.append(line)
ws5.column_dimensions["A"].width = 118
ws5.cell(1,1).font = Font(bold=True, size=16, color="6EE7A8")
for r in range(1, ws5.max_row+1):
    v = ws5.cell(r,1).value
    if v and v.isupper() and len(v) < 40: ws5.cell(r,1).font = Font(bold=True, color="D7E4EE")

wb.save(OUT)
print(f"wrote {OUT}")
print(f"  Devices           {len(DEV)} rows x {len(cols)} cols ({len(ORIG)} original + {len(NEW)} new)")
print(f"  Capability Matrix {len(DEV)} rows x {len(order)} capabilities")
print(f"  Glossary          {len(order)} capabilities + {len(GLOSS)} general terms")
print(f"  Sources           {sum(len(d.get('sources') or []) for d in DEV)} citations")
