# Phase 3 brief — deepening pass

You are not researching new devices. You are filling in capability matrices on
records that already exist and are otherwise good.

## The problem you are fixing

The records in your assigned file have solid hardware detail, honest takes and
legal notes, but their capability matrices are far too sparse — around 3 entries
each against a database average of 16. That happened because the earlier pass
recorded only what a device *does* and stayed silent about what it does not.

Silence is the bug. In this schema an omitted key is treated as "no", so an
omission and a denial look identical to the reader but only one of them was
actually checked. Worse, the comparison table and the recommendation quiz both
run off this matrix: a device with three filled capabilities cannot be compared
against anything and will never be recommended.

## What to do

For each record in your file:

1. Look up its `category`, then read the matching key list in
   `research/expand/category_keys.json`. Those are the keys that at least a
   quarter of the existing devices in that category carry — treat the list as a
   checklist, not a suggestion.
2. Assign every key on that list a value: `yes`, `no`, `partial`, `addon`,
   `claimed` or `unknown`. **A confident `no` is the most valuable output of
   this pass.** "This $139 board cannot do 5 GHz" is what a reader is here for.
3. Add any keys beyond the checklist that genuinely apply.
4. Where you assert `yes` or `no` on something non-obvious, cite it. Get each
   record to at least 3 sources, 5 where you can.
5. Where you genuinely could not determine a value, use `unknown` and say why in
   the note. Do not guess, and do not use `no` as a synonym for "did not check" —
   that is the same bug in a new costume.

Every `note` should say something a spec sheet would not. "2.4 GHz only, the
ESP32-S3 has no 5 GHz radio" beats "no 5 GHz support".

## What not to touch

Leave `summary`, `honest_take`, `hardware`, `legal`, `price_usd`, `id`,
`hardware_id` and `name` exactly as they are unless you find something factually
wrong — and if you do, fix it and say so in your report. This pass is about the
capability matrix and sources.

Do not invent capability keys. `research/expand/category_keys.json` and
`research/SCHEMA.md` between them list every valid key. If a device does
something no key covers, add "no capability key for X" to `research_gaps`.

## Output

Rewrite your assigned file in place, same path, same records, same order.
Validate with `python3 -m json.tool` before finishing. Do not create, modify or
delete any other file, and never run `rm`.

Report: the before and after average capability count, and any record you could
not bring up to standard.
