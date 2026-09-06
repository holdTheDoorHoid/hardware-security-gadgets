# Device Research Schema (v1)

Every researched device is ONE JSON object. A single physical device running
different firmware becomes MULTIPLE objects (one per firmware), sharing the same
`hardware_id` but having different `id` and `firmware`.

Output a JSON **array** of these objects. Nothing else in the file.

## Hard rules

1. **Cut marketing language.** Never copy a vendor bullet. State what the
   silicon can actually do. If a vendor claims "military-grade jammer" and it is
   an nRF24 spamming 2.4 GHz, say that.
2. **Every non-obvious claim needs a source.** Put URLs in `sources`. Prefer, in
   order: official schematics/repos, GitHub source, teardowns, datasheets,
   vendor spec pages. Reddit/YouTube only as last resort and mark as such.
3. **Confidence is mandatory.** For each capability use one of:
   `"yes"` (confirmed by source), `"no"` (confirmed absent),
   `"partial"` (works with caveats - explain in note),
   `"addon"` (needs extra hardware - name it in note),
   `"claimed"` (vendor says so, NOT independently confirmed),
   `"unknown"` (could not determine).
   **Never guess `yes`.** `unknown` is a correct and useful answer.
4. **Prices** are USD, direct from vendor, and you MUST set `price_checked`
   to the date you looked (YYYY-MM-DD). If it is a kit/DIY with no vendor,
   estimate parts cost and set `price_is_estimate: true`.
5. **Do not invent part numbers.** If you cannot find the exact MCU or radio IC,
   use `null`, not a plausible-sounding guess.

## Object shape

```json
{
  "id": "flipper-zero-momentum",
  "hardware_id": "flipper-zero",
  "name": "Flipper Zero",
  "firmware": "Momentum",
  "firmware_kind": "community",
  "firmware_repo": "https://github.com/Next-Flip/Momentum-Firmware",
  "firmware_note": "One-line plain English: what this firmware changes vs stock.",
  "vendor": "Flipper Devices",
  "vendor_url": "https://flipperzero.one",
  "product_url": "https://shop.flipperzero.one/...",
  "category": "multitool",
  "subcategory": "rf-multitool",
  "status": "available",
  "released": "2020",

  "price_usd": 199,
  "price_note": "Frequently out of stock; grey-market resellers charge 250-400.",
  "price_is_estimate": false,
  "price_checked": "2026-09-06",

  "skill_level": "beginner",
  "skill_note": "Why. One sentence.",
  "build_effort": "assembled",
  "build_note": "Flashing Momentum takes ~5 min via web updater, no soldering.",

  "stealth": "overt",
  "form_factor": "handheld",

  "summary": "2-3 sentences. What it genuinely is and who it's for. No hype.",
  "honest_take": "1-3 sentences. What it is NOT good at, and the single most common misconception. This is the anti-marketing field. Be blunt.",
  "best_for": ["Learning RF basics", "Physical red team access testing"],
  "not_for": ["Wi-Fi attacks without the add-on board", "Cracking modern rolling-code cars"],

  "hardware": {
    "mcu_primary": "STM32WB55RG",
    "mcu_primary_note": "Cortex-M4 @64MHz + Cortex-M0+ radio core, 1MB flash, 256KB RAM",
    "mcu_secondary": null,
    "radios": [
      {"ic": "CC1101", "role": "sub-ghz", "note": "300-348, 387-464, 779-928 MHz"},
      {"ic": "ST25R3916", "role": "nfc", "note": "13.56MHz reader/emulator + 125kHz via same coil"}
    ],
    "display": {"type": "Monochrome LCD", "size_in": 1.4, "resolution": "128x64", "color": false, "touch": false},
    "battery_mah": 2100,
    "battery_note": "Li-Po, ~7 days idle / ~24h active",
    "charging": "USB-C",
    "pmic": null,
    "storage": "microSD up to 256GB (exFAT)",
    "connectivity": ["USB-C", "Bluetooth LE", "GPIO 18-pin"],
    "gpio": "18-pin header, 3.3V, SPI/I2C/UART/1-Wire exposed",
    "sensors": ["none"],
    "dimensions_mm": "100.3 x 40.1 x 25.6",
    "weight_g": 102,
    "case": "PC/ABS/PMMA",
    "notable_physical": ["5-way D-pad", "IR window", "iButton contact", "GPIO header"]
  },

  "capabilities": {
    "subghz_rx":            {"v": "yes", "note": "300-348/387-464/779-928 MHz via CC1101"},
    "subghz_tx":            {"v": "yes", "note": "Region-locked in stock fw; Momentum unlocks full TX range"},
    "wifi_deauth":          {"v": "addon", "note": "Requires ESP32 Wi-Fi Dev Board on GPIO"},
    "sdr_rx":               {"v": "no",  "note": "Not an SDR. Fixed-function transceiver only."}
  },

  "legal": {
    "import_restricted": ["Canada (2024 proposal, not enacted)", "Brazil (ANATEL seizures)"],
    "risk_level": "medium",
    "notes": "Owning is legal in the US. Transmitting on sub-GHz without a licence, and deauthing networks you don't own, are separate offences in most countries."
  },

  "ecosystem": {
    "community": "very-active",
    "docs_quality": "excellent",
    "last_release": "2026-08",
    "app_store": "Yes - official + community app catalogs",
    "abandoned_risk": "low"
  },

  "aliases": ["Flipper", "Dolphin"],
  "sources": [
    {"url": "https://github.com/...", "what": "schematic confirming CC1101"},
    {"url": "https://docs.flipper.net/...", "what": "official frequency ranges"}
  ],
  "research_gaps": ["Could not confirm exact TX power in dBm"]
}
```

## Controlled vocabularies (use ONLY these values)

- `firmware_kind`: `stock` | `community` | `third-party-product` | `diy` | `n/a`
- `category`: `multitool` | `wifi` | `rfid-nfc` | `subghz` | `bluetooth` |
  `usb-hid` | `network-implant` | `sdr` | `hardware-debug` | `wardriving` |
  `detection-defense` | `accessory`
- `status`: `available` | `preorder` | `out-of-stock` | `discontinued` |
  `diy-only` | `vaporware`
- `skill_level`: `beginner` | `intermediate` | `advanced` | `expert`
- `build_effort`: `assembled` (buy and use) | `flash-only` (buy hw, flash firmware) |
  `assembly` (plug modules together, no solder) | `soldering` | `full-diy`
- `stealth`: `overt` (obviously a hacking tool) | `discreet` (looks like generic gadget) |
  `covert` (disguised as a normal cable/charger/USB stick) | `implant` (hidden in place)
- `form_factor`: `handheld` | `pocket` | `keychain` | `usb-stick` | `cable` |
  `wearable` | `board` | `box` | `hat-shield` | `desktop`
- `legal.risk_level`: `low` | `medium` | `high`
- `ecosystem.community`: `very-active` | `active` | `slow` | `dormant` | `dead` | `commercial`
- `ecosystem.docs_quality`: `excellent` | `good` | `sparse` | `poor` | `none`
- `ecosystem.abandoned_risk`: `low` | `medium` | `high` | `already-abandoned`

## Capability keys (use EXACTLY these; omit any that don't apply)

Only include keys relevant to the device. Omitted == treated as "no".
Include a key with `"v":"no"` only when the absence is *notable* (e.g. a
"Flipper killer" that has no NFC).

### Sub-GHz (300-950 MHz)
`subghz_rx` `subghz_tx` `subghz_replay` `subghz_rolling_code` `subghz_bruteforce`
`subghz_external_antenna` `subghz_amplified`

### RFID / NFC
`lf_125khz_read` `lf_125khz_write` `lf_125khz_emulate`
`hf_1356_read` `hf_1356_write` `hf_1356_emulate`
`mifare_classic_attacks` `mifare_desfire` `nfc_type4_ndef` `emv_read`
`iso15693` `felica` `magspoof` `nfc_relay`

### Bluetooth / BLE
`ble_scan` `ble_advertise` `ble_spam_apple` `ble_spam_android` `ble_spam_samsung`
`ble_spam_swift_pair` `ble_hid` `bt_classic` `ble_sniff` `ble_tracker_detect`
`ble_tracker_spoof` `findmy_track`

### Wi-Fi
`wifi_scan_24` `wifi_scan_5` `wifi_monitor_mode` `wifi_injection`
`wifi_deauth_24` `wifi_deauth_5` `wifi_evil_twin` `wifi_captive_portal`
`wifi_handshake_capture` `wifi_pmkid` `wifi_beacon_spam` `wifi_karma`
`wifi_probe_sniff` `wifi_wardriving` `wifi_ap_mode`

### 2.4 GHz non-Wi-Fi
`nrf24_scan` `nrf24_jam` `mousejack` `zigbee` `ble_jam`

### Infrared
`ir_tx` `ir_rx` `ir_learn` `ir_universal_remote` `ir_flood`

### USB / HID
`usb_hid_inject` `usb_mass_storage` `usb_ethernet_attack` `usb_keylogger`
`usb_exfil` `hid_remote_trigger` `usb_payload_lang`

### Network
`ethernet_tap_passive` `ethernet_mitm` `packet_capture` `cloud_c2`
`vpn_exfil` `hdmi_capture`

### Hardware debug
`uart` `spi_flash_dump` `i2c` `jtag_swd` `logic_analyzer` `glitching`

### SDR
`sdr_rx` `sdr_tx` `sdr_bandwidth` `sdr_full_duplex`

### Other
`ibutton_1wire` `gps` `gps_wardrive_log` `sd_logging` `scriptable`
`app_store` `web_ui` `standalone_untethered`

### Detection / defense
(These are almost always a scan + signature list. In `note`, say what it is
actually matching on: BLE MAC OUI, service UUID, SSID pattern, etc.)
`detect_flipper` `detect_airtag` `detect_tile` `detect_skimmer`
`detect_pineapple` `detect_pwnagotchi` `detect_drone` `detect_meshtastic`
`detect_surveillance_cam` `detect_generic_ble` `detect_generic_wifi`
