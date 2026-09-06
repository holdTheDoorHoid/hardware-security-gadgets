/* Quiz definition. Goals map plain-language intentions onto weighted capabilities. */
window.QUIZ = {
  goals: [
    { id:"subghz", label:"Play with radio remotes", icon:"((•))",
      desc:"Garage doors, gate remotes, doorbells, some alarm sensors. Record a signal and send it again.",
      caps:{ subghz_rx:3, subghz_tx:3, subghz_replay:2.5, subghz_bruteforce:1, subghz_external_antenna:.5 } },

    { id:"wifi", label:"Test Wi-Fi security", icon:"≈≈≈",
      desc:"See what networks are around, capture the data needed for offline password testing, knock devices off, or stand up a fake login page.",
      caps:{ wifi_scan_24:1, wifi_monitor_mode:2, wifi_handshake_capture:3, wifi_pmkid:1.5,
             wifi_deauth_24:2, wifi_deauth_5:1, wifi_captive_portal:2, wifi_evil_twin:2,
             wifi_injection:2, wifi_scan_5:1 } },

    { id:"nfc", label:"Work with badges & cards", icon:"[]))",
      desc:"Office access badges, hotel keys, transit cards, contactless bank cards. Read them, copy them, pretend to be one.",
      caps:{ lf_125khz_read:2, lf_125khz_write:1.5, lf_125khz_emulate:2, hf_1356_read:2,
             hf_1356_write:1.5, hf_1356_emulate:2, mifare_classic_attacks:3,
             nfc_type4_ndef:1, emv_read:1, iso15693:.5 } },

    { id:"usb", label:"Test plug-in USB attacks", icon:"==D",
      desc:"What happens when someone plugs an unknown stick or cable into a computer. The device types commands by itself.",
      caps:{ usb_hid_inject:3, usb_mass_storage:1, usb_ethernet_attack:2, usb_exfil:2,
             hid_remote_trigger:1.5, usb_payload_lang:1, ble_hid:1 } },

    { id:"detect", label:"Find trackers & surveillance", icon:"(o)",
      desc:"Spot an AirTag following you, a card skimmer on a petrol pump, a rogue Wi-Fi network, a plate-reader camera, or a drone.",
      caps:{ detect_generic_ble:1, ble_tracker_detect:3, detect_airtag:2, detect_tile:1,
             detect_skimmer:2.5, detect_pineapple:2, detect_drone:1.5, detect_alpr:2,
             detect_deauth:1.5, detect_surveillance_cam:2, detect_flipper:1, detect_generic_wifi:1 } },

    { id:"network", label:"Work on wired networks", icon:"<->",
      desc:"Tap an Ethernet cable, sit between a screen and a computer, or leave a small box behind that calls home to you.",
      caps:{ ethernet_tap_passive:3, ethernet_mitm:3, packet_capture:2.5, cloud_c2:2,
             vpn_exfil:2, hdmi_capture:2, usb_keylogger:1.5 } },

    { id:"hwdebug", label:"Take chips apart", icon:"|::|",
      desc:"Pull the firmware off a circuit board, find the hidden serial console manufacturers leave behind, use debug ports, or glitch a chip.",
      caps:{ uart:3, spi_flash_dump:3, jtag_swd:2.5, i2c:1.5, logic_analyzer:2, glitching:2 } },

    { id:"sdr", label:"Learn radio properly", icon:"/\\/\\",
      desc:"A general-purpose radio you can point at almost any frequency. The deepest rabbit hole on this site, and the best long-term investment.",
      caps:{ sdr_rx:3, sdr_tx:2, sdr_bandwidth:1, sdr_full_duplex:1 } },

    { id:"ble", label:"Mess with Bluetooth", icon:"*B*",
      desc:"Scan nearby devices, send pairing pop-ups, act as a wireless keyboard, or capture an actual Bluetooth conversation.",
      caps:{ ble_scan:2, ble_advertise:1.5, ble_spam_apple:1.5, ble_spam_android:1,
             ble_spam_swift_pair:1, ble_hid:2, ble_sniff:3, bt_classic:1 } },

    { id:"ir", label:"Control TVs & IR gear", icon:"-->",
      desc:"Copy remote controls and drive screens, projectors, air conditioners and other infrared devices.",
      caps:{ ir_tx:3, ir_rx:2, ir_learn:2, ir_universal_remote:1.5 } },

    { id:"wardrive", label:"Map networks while moving", icon:"[@]",
      desc:"Walk or drive around logging every wireless network you pass, tagged with where you were.",
      caps:{ wifi_wardriving:3, gps:2, gps_wardrive_log:2.5, sd_logging:1, standalone_untethered:1.5 } }
  ],

  budgets: [
    { id:"b50",   max:50,      label:"Under $50",     desc:"Real capability exists down here, but it is nearly always DIY or single-purpose." },
    { id:"b150",  max:150,     label:"$50 – $150",    desc:"The sweet spot for capable ready-made gadgets and good open-source boards." },
    { id:"b300",  max:300,     label:"$150 – $300",   desc:"Flipper Zero territory, and most of the polished commercial handhelds." },
    { id:"b600",  max:600,     label:"$300 – $600",   desc:"Professional single-purpose tools and serious radio hardware." },
    { id:"bmax",  max:Infinity,label:"Budget is not the constraint", desc:"Research-grade instruments and full professional kit." }
  ],

  skills: [
    { id:"beginner", label:"Brand new to this",
      desc:"You want it to work out of the box with menus, and you would rather not touch a command line." },
    { id:"intermediate", label:"I know the basics",
      desc:"You are comfortable installing firmware, reading a wiki, and using a terminal when you have to." },
    { id:"advanced", label:"I do this seriously",
      desc:"You work in security or have been at this a while. You can read a datasheet and debug your own problems." },
    { id:"expert", label:"Research-grade, please",
      desc:"You want the capable tool even if the documentation is a GitHub issue thread and a schematic." }
  ],

  builds: [
    { id:"assembled",  label:"Buy it and turn it on",
      desc:"Arrives finished. No assembly, no firmware to install." },
    { id:"flash-only", label:"I'll install firmware",
      desc:"Happy to plug it into a computer and flash software onto it, following a guide." },
    { id:"soldering",  label:"I'll solder and assemble",
      desc:"You own a soldering iron and are not afraid of a wiring diagram." },
    { id:"full-diy",   label:"I'll build it from scratch",
      desc:"Order the parts, build the thing, debug why it won't boot. That is the fun part." }
  ],

  stealth: [
    { id:"any",      label:"Doesn't matter",
      desc:"It can look like an obvious hacking gadget." },
    { id:"discreet", label:"Prefer something low-key",
      desc:"Should pass as an ordinary gadget if someone glances at it." },
    { id:"covert",   label:"Must be disguised",
      desc:"Needs to look like a normal cable, charger or USB stick. This matters for authorised physical engagements." }
  ],

  support: [
    { id:"high", label:"Very important",
      desc:"Good documentation, an active community, and a project that will still exist next year." },
    { id:"mid",  label:"Somewhat",
      desc:"You would like decent docs but can cope with gaps." },
    { id:"low",  label:"I can read the source",
      desc:"A dead repo and no docs is an acceptable trade for capability." }
  ]
};
