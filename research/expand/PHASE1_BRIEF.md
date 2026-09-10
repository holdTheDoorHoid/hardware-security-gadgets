# Phase 1 brief — candidate enumeration only

You are enumerating candidate devices for an existing hardware-security-gadget
comparison database. **Phase 1 is a shopping list, not deep research.** Do NOT
write full device records yet. Speed and coverage matter more than depth here.

## Already in the database — DO NOT re-list these
Read `/home/hoid/Desktop/sec-gadget-compare/research/expand/HAVE.txt` (160 names)
before you start. Match loosely: "Flipper Zero" is present, so do not propose
"Flipper Zero" or "Flipper Zero (Momentum)". If a retailer sells a device under a
different name than we use, that is still a duplicate — say so in `dupe_of`.

## What counts as in-scope
A physical device (or a firmware/open-source project that turns cheap hardware
into one) whose purpose includes offensive or defensive security testing:
RF/SDR, sub-GHz, RFID/NFC, Wi-Fi, Bluetooth/BLE, USB HID injection / BadUSB,
implants, network taps and implants, hardware hacking (JTAG/SWD/UART/SPI/I2C,
glitching, side-channel), automotive/CAN, forensics (write blockers, keyloggers),
physical entry electronics, cellular/IMSI, GPS/GNSS spoofing, deauth/jamming,
DMA attack hardware, and firmware/hardware analysis tools.

## Out of scope — do not propose
Apparel, stickers, books, bags, pure lockpicks and mechanical picks with no
electronics, generic cables/adapters/antennas with no capability of their own,
bench multimeters, generic soldering/rework gear, software-only distros,
retail phones/routers with no security firmware, and anything discontinued for
more than ~5 years with no working source of supply.
Borderline: propose it and flag `borderline: true` with one line of reasoning.

## Output
Write a single JSON file to the path you are told, an array of objects:

```json
[{
  "name": "Exact product name",
  "vendor": "Who makes it",
  "seller_url": "URL you actually loaded",
  "price_usd": 123.45,
  "one_line": "What it physically does, no marketing words",
  "category_guess": "rfid | subghz | wifi | ble | usb-hid | sdr | hw-hacking | network | automotive | forensics | cellular | multi | other",
  "why_notable": "One sentence: why it belongs in a comparison DB",
  "dupe_of": null,
  "borderline": false,
  "confidence": "high | medium | low"
}]
```

## Rules
- Only list what you actually saw on a page you loaded. Never invent a product.
- Price: the real listed price in USD. Convert EUR/GBP and say so in one_line.
  If you could not load a price, use null — do not guess.
- No marketing language anywhere. "Sends 433MHz replay attacks" not
  "unleash the power of RF".
- If a page is unreachable, say so in your final report rather than substituting
  a search-result summary for the real page.
- Be thorough on breadth. It is fine to list 60 items. It is not fine to list 10
  and claim that is the whole catalog.
