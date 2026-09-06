# Research Agent Brief

You are researching hardware security / pentest gadgets for a **public comparison
website** aimed at readers from total beginner to professional. Accuracy beats
completeness. A well-marked `unknown` is worth more than a confident guess.

**Read `/home/hoid/Desktop/sec-gadget-compare/research/SCHEMA.md` in full before
you start.** It defines the exact JSON object shape, the controlled vocabularies,
and the complete capability-key list. Follow it exactly - do not invent new keys
or new vocabulary values.

Today's date is **2026-09-06**. Use it for `price_checked`.

## Method

- Use `WebSearch` and `WebFetch` aggressively. Expect several searches per device.
- Source priority: official GitHub repo (actually read the README, the source
  tree, the `hardware/` or `schematics/` folder, the release notes) > schematics
  and datasheets for the named ICs > independent teardowns > official docs >
  vendor spec page. **Vendor marketing pages are for price and SKU only.**
- For firmware projects: open the repo. Enumerate what modules/apps genuinely
  exist. Check the date of the last commit and last release - that drives
  `ecosystem.abandoned_risk` and `last_release`.
- Chase the silicon. If a device says "2.4GHz jammer", find whether that is an
  nRF24L01+, an ESP32 radio, or a CC2500, and say what that chip can and cannot
  physically do.
- If a vendor claims a capability you cannot independently confirm, the value is
  `"claimed"`, never `"yes"`.
- If you cannot find a device at all, **still emit an object** with a best-effort
  name, `status` set appropriately, and a `research_gaps` entry saying what you
  could not find. Never silently drop a device from your batch.

## The anti-marketing mandate

`honest_take` is the single most important field in this project. For each device
write what a knowledgeable friend would say over a beer:

- What it genuinely cannot do that people assume it can.
- Whether it is "just an ESP32 in a nice case" - and if so, say which firmware
  does the real work and whether you could flash it onto a $15 board instead.
- Whether a headline "detector" feature is really a BLE or Wi-Fi scan matching a
  MAC OUI / service UUID / SSID pattern list. Say what it matches on.
- Whether "jamming" is real wideband jamming or just protocol-level spam or
  constant-carrier noise on a few channels.
- Whether the price is justified by the hardware, or is mostly brand and case.
- Known reliability problems, supply problems, or a dead maintainer.

Be blunt but fair. Do not sneer at a device that is honestly what it says it is.

## Legal field

`legal.import_restricted` should list real, sourced restrictions (e.g. Brazil's
ANATEL refusing Flipper Zero imports). Do not repeat rumours. `legal.notes`
should distinguish **owning** the device from **using** specific capabilities,
in plain language, and must read as "check your local law", not legal advice.

## Output

Write a JSON **array** of device objects to the output path you are given.
Nothing else in the file - no markdown fences, no prose.

Validate before you finish:

```
python3 -c "import json,sys;d=json.load(open(PATH));print(len(d),'objects OK')"
```

Fix any parse error before returning.

## Return message

Keep it short: how many objects you wrote, which devices you could NOT verify and
why, and the 2-3 most surprising or most marketing-inflated things you found.
