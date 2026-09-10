# Phase 2 brief — full device records

You are adding devices to an existing comparison database of 161 hardware
security gadgets. Your output must be indistinguishable in quality from what is
already there.

## Read these first, in this order
1. `/home/hoid/Desktop/sec-gadget-compare/research/SCHEMA.md` — the object shape,
   the controlled vocabularies, and the capability keys. Follow it exactly.
2. `/home/hoid/Desktop/sec-gadget-compare/research/AGENT_BRIEF.md` — the
   anti-marketing standard.
3. One existing batch file, e.g. `research/batch-01-*.json`, to see the bar.

## Capability keys added since SCHEMA.md was written
These are valid in addition to the ones the schema lists:
`hardware_destruct` `device_lock` `emergency_mode` `pc_monitor` `subghz_wardrive`
`drone_spoof` `pwnagotchi_spam` `detect_alpr` `detect_bodycam` `detect_deauth`
`detect_meshcore` `detect_smartglasses` `rgb_backlight` `games` `rpg_leveling`
`timer_stopwatch` `txt_viewer` `video_player`

**Do not invent new capability keys.** If a device does something no key covers,
describe it in `summary` and list it in `research_gaps` as "no capability key
for X" — I will add the key centrally. A typo'd key silently vanishes from the
comparison table, which is worse than a missing one.

## The standard, restated
- **Never guess `yes`.** `unknown` is a correct answer and is respected here.
- `claimed` is for vendor assertions you could not independently confirm. Use it
  freely — a lot of this market runs on unverified claims.
- Every non-obvious claim carries a source URL in `sources`.
- `honest_take` is the field that makes this site worth visiting. Write what the
  device is bad at and the single most common misconception about it. If a
  device is simply worse than something already in the database at the same
  price, say that plainly and name the alternative.
- Do not invent part numbers. `null` beats a plausible guess.
- If a device is a rebadge of an open-source design, say so, name the design, and
  price the difference.

## Firmware variants
If the same hardware runs meaningfully different firmware, emit one object per
firmware sharing a `hardware_id`. Only do this where the firmware genuinely
changes capability — not for point releases.

## Out of scope — do not write records for these
Implantable NFC/RFID chips. Blank/magic cards, fobs and tags. Conference badges,
badgelife hardware and SAOs (a separate project covers those; a general-purpose
tool that happens to be sold at a con is still fine). Apparel, books, bags,
mechanical-only lockpicks, plain cables and antennas.

**In scope, explicitly:** professional gear over $1,000, and bare-PCB or
DIY-only designs with no assembled option.

## Deconflicting
Check `research/expand/HAVE.txt` before writing. If your assigned device turns
out to already be in there under another name, skip it and say so in your report
rather than writing a duplicate record.

## Output
A JSON array of complete objects, written to the single path you are given.
**Do not create, modify or delete any other file anywhere. Never run `rm`.**
Other agents are working in this directory at the same time.

Validate your JSON parses before you finish: `python3 -m json.tool <yourfile>`.

## Depth targets (added mid-run - the first batch came back too thin)

The existing 175 records average **16 capability entries** and **5.4 sources**
each. The first new batch averaged 3.2 and 1.6. That is not good enough, and
here is why it matters concretely: the comparison table and the recommendation
quiz both run on the capability matrix. A device with three filled capabilities
cannot be compared against anything and will never be recommended, so a thin
record is close to no record at all.

**Capabilities.** Aim for 10+ per device; 15-25 is normal for anything
multi-protocol. Include a key with `"v":"no"` whenever the absence is a thing a
buyer would reasonably assume was present - that is the single most useful
signal on the whole site. A Wi-Fi board that cannot do 5GHz should carry
`wifi_scan_5: {"v":"no"}`. An RFID tool that reads but cannot write should carry
the write keys as `"no"`. A sub-GHz device that cannot defeat rolling codes
should say so with `subghz_rolling_code: {"v":"no"}`.

A genuinely single-purpose device is allowed to be sparse - a passive field
detector really does only do one thing - but say so in `research_gaps` so the
sparseness reads as a finding rather than an omission. **Zero capabilities is
never acceptable.** If nothing in the key list fits, the device either belongs
in a different category or needs a new key named in `research_gaps`.

**Sources.** 3 minimum, 5+ preferred. A vendor page alone is not enough for a
capability claim; that is what `"claimed"` is for. Prefer schematics, source
repos, datasheets and teardowns. Where you used a source to establish one
specific fact, say which fact in the `what` field.

If you have already written your file, revise it to this standard rather than
starting over.
