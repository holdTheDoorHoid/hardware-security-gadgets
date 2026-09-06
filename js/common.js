/* Shared helpers. Loaded on every page after data/taxonomy.js + data/devices.js */

const T  = window.TAXONOMY;
const DB = (window.DEVICES || []).slice();

/* ---------- tiny utils ---------- */
const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
  .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
const qp = n => new URLSearchParams(location.search).get(n);
const uniq = a => [...new Set(a)];
const byId = id => DB.find(d => d.id === id);

/* ---------- capability access ---------- */
function cap(dev, key){
  const c = dev.capabilities && dev.capabilities[key];
  if (!c) return { v:"no", note:"", implicit:true };
  if (typeof c === "string") return { v:c, note:"" };
  return { v:c.v || "unknown", note:c.note || "" };
}
const HAS = new Set(["yes","partial","addon","claimed"]);
const hasCap = (dev,key) => HAS.has(cap(dev,key).v);
/* strength for scoring: how much does this really count? */
const CAP_WEIGHT = { yes:1, partial:.75, addon:.5, claimed:.4, no:0, unknown:0 };
const capScore = (dev,key) => CAP_WEIGHT[cap(dev,key).v] || 0;

function capMeta(key){
  return T.caps[key] || { label:key, group:"platform", plain:"", legal:"none" };
}

/* every capability a device actually has, grouped by taxonomy group */
function capsByGroup(dev){
  const out = [];
  for (const g of T.groups){
    const rows = [];
    for (const key of Object.keys(dev.capabilities || {})){
      const m = T.caps[key];
      if (!m || m.group !== g.id) continue;
      rows.push({ key, meta:m, ...cap(dev,key) });
    }
    if (rows.length){
      rows.sort((a,b)=>(HAS.has(b.v)-HAS.has(a.v)) || a.meta.label.localeCompare(b.meta.label));
      out.push({ group:g, rows });
    }
  }
  return out;
}

/* ---------- display ---------- */
function priceStr(d){
  if (d.price_usd == null) return '<span class="dim">unknown</span>';
  if (Number(d.price_usd) === 0) return '<span style="color:var(--cyn)">Free</span>';
  const p = "$" + Number(d.price_usd).toLocaleString();
  return d.price_is_estimate ? "~" + p : p;
}
function priceNum(d){ return d.price_usd == null ? Infinity : Number(d.price_usd); }

const SKILL_ORDER = ["beginner","intermediate","advanced","expert"];
const SKILL_TAG = { beginner:"tag-grn", intermediate:"tag-cyn", advanced:"tag-amb", expert:"tag-red" };
const BUILD_LABEL = {
  assembled:"Buy & use", "flash-only":"Flash firmware", assembly:"Plug together",
  soldering:"Soldering", "full-diy":"Full DIY"
};
const BUILD_ORDER = ["assembled","flash-only","assembly","soldering","full-diy"];
const STEALTH_LABEL = { overt:"Obvious tool", discreet:"Discreet", covert:"Disguised", implant:"Hidden implant" };
const STATUS_TAG = {
  available:"tag-grn", preorder:"tag-cyn", "out-of-stock":"tag-amb",
  discontinued:"tag-red", "diy-only":"tag-blu", vaporware:"tag-red"
};
const RISK_TAG = { low:"tag-grn", medium:"tag-amb", high:"tag-red" };

function valPill(v, note){
  const m = T.values[v] || T.values.unknown;
  const n = note ? ` <span class="dim tiny">${esc(note)}</span>` : "";
  return `<span class="${m.cls} mono tiny">${m.label}</span>${n}`;
}

/* other firmware builds of the same hardware */
const siblings = d => DB.filter(x => x.hardware_id === d.hardware_id && x.id !== d.id);

function deviceCard(d, extra){
  const sib = siblings(d);
  return `<div class="card" data-id="${esc(d.id)}">
    <div class="card-h">
      <div>
        <div class="card-n"><a href="device.html?id=${encodeURIComponent(d.id)}">${esc(d.name)}</a></div>
        ${d.firmware ? `<span class="card-fw">${esc(d.firmware)}</span>` : ""}
      </div>
      <div class="card-pr">${priceStr(d)}${d.price_is_estimate?'<small>est. parts</small>':''}</div>
    </div>
    <div class="card-v">${esc(d.vendor || "unknown vendor")}</div>
    <div class="card-s">${esc(d.summary || "")}</div>
    <div class="card-f">
      <span class="tag ${SKILL_TAG[d.skill_level]||""}">${esc(d.skill_level||"?")}</span>
      <span class="tag">${esc(BUILD_LABEL[d.build_effort]||d.build_effort||"?")}</span>
      <span class="tag ${STATUS_TAG[d.status]||""}">${esc(d.status||"?")}</span>
      ${d.legal && d.legal.risk_level ? `<span class="tag ${RISK_TAG[d.legal.risk_level]||""}">legal: ${esc(d.legal.risk_level)}</span>`:""}
      ${sib.length?`<span class="tag tag-mag">+${sib.length} build${sib.length>1?"s":""}</span>`:""}
      ${extra||""}
    </div>
  </div>`;
}

/* ---------- search ---------- */
function searchBlob(d){
  if (d.__blob) return d.__blob;
  const parts = [
    d.name, d.firmware, d.vendor, d.category, d.subcategory,
    d.summary, d.honest_take, d.skill_level, d.build_effort, d.stealth, d.form_factor,
    ...(d.aliases||[]), ...(d.best_for||[]), ...(d.not_for||[]),
    d.hardware && d.hardware.mcu_primary, d.hardware && d.hardware.mcu_secondary,
    ...((d.hardware && d.hardware.radios || []).map(r => `${r.ic} ${r.role} ${r.note||""}`))
  ];
  /* capability labels AND their original-spreadsheet aliases */
  for (const k of Object.keys(d.capabilities||{})){
    if (!HAS.has(cap(d,k).v)) continue;
    const m = T.caps[k]; if (!m) continue;
    parts.push(k, m.label, ...(m.aliases||[]));
  }
  return d.__blob = parts.filter(Boolean).join(" ").toLowerCase();
}
function searchDevices(list, q){
  q = (q||"").trim().toLowerCase();
  if (!q) return list;
  const terms = q.split(/\s+/);
  return list.filter(d => { const b = searchBlob(d); return terms.every(t => b.includes(t)); });
}

/* ---------- nav ---------- */
function navBar(active){
  const links = [
    ["index.html","browse","Browse"],
    ["quiz.html","quiz","Find my gadget"],
    ["compare.html","compare","Compare"],
    ["glossary.html","glossary","Glossary"],
    ["about.html","about","About"]
  ];
  return `<div class="topbar"><div class="topbar-in">
    <a class="brand" href="index.html">[<span class="bk">sec</span>]gadget<span class="cur">_</span></a>
    <nav class="nav">${links.map(([h,k,l])=>
      `<a href="${h}" class="${k===active?"on":""}">${l}</a>`).join("")}</nav>
  </div></div>`;
}
function footerBar(){
  return `<footer><div class="wrap">
    <p><b>Own it legally, use it legally.</b> Owning most of these devices is lawful in
    most countries. Using their transmit and attack features against systems you do not
    own or have written permission to test is a criminal offence in nearly all of them.
    Per-device legal notes flag known import restrictions, but they are a starting point
    for your own research, not legal advice.</p>
    <p class="tiny dim">Independent, non-commercial, no affiliate links. Prices are
    manufacturer direct in USD and carry the date they were checked. Capability data is
    sourced and marked with a confidence level; "Claimed" means the seller says so and we
    could not confirm it.</p>
  </div></footer>`;
}

/* ---------- glossary tooltips in prose ---------- */
function linkTerms(html){
  let out = html;
  const keys = Object.keys(T.glossary).sort((a,b)=>b.length-a.length);
  const done = new Set();
  for (const k of keys){
    if (done.has(k.toLowerCase())) continue;
    const re = new RegExp(`(?<![\\w>])(${k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")})(?![\\w<])`,"i");
    if (re.test(out)){
      out = out.replace(re, `<span class="term" data-term="${esc(k)}">$1</span>`);
      done.add(k.toLowerCase());
    }
  }
  return out;
}
function initTips(){
  let box = null;
  document.addEventListener("mouseover", e => {
    const t = e.target.closest("[data-term]"); if (!t) return;
    const def = T.glossary[t.dataset.term]; if (!def) return;
    box = document.createElement("div");
    box.className = "tip-b"; box.textContent = def;
    t.style.position = "relative"; t.appendChild(box);
    const r = box.getBoundingClientRect();
    if (r.left < 8) box.style.transform = `translateX(${-r.left + 8}px)`;
    if (r.right > innerWidth - 8) box.style.transform = `translateX(${innerWidth - r.right - 8}px)`;
  });
  document.addEventListener("mouseout", e => {
    if (box && !e.target.closest(".tip-b")) { box.remove(); box = null; }
  });
}

/* ---------- comparison basket (localStorage, best-effort) ---------- */
const BASKET_KEY = "secgadget.compare";
function basketGet(){
  try { return JSON.parse(localStorage.getItem(BASKET_KEY) || "[]"); } catch { return []; }
}
function basketSet(a){
  try { localStorage.setItem(BASKET_KEY, JSON.stringify(a.slice(0,6))); } catch {}
}
function basketToggle(id){
  const a = basketGet(); const i = a.indexOf(id);
  if (i >= 0) a.splice(i,1); else if (a.length < 6) a.push(id);
  basketSet(a); return a;
}

/* ---------- similarity: find genuinely comparable builds ----------
   Jaccard overlap on "capabilities it actually has", nudged by category and price. */
function capSet(d){
  return new Set(Object.keys(d.capabilities||{}).filter(k=>hasCap(d,k)));
}
function similar(d, n){
  const a = capSet(d);
  if (!a.size) return DB.filter(x=>x.category===d.category && x.hardware_id!==d.hardware_id).slice(0,n||4);
  const pa = priceNum(d);
  const scored = DB
    .filter(x => x.hardware_id !== d.hardware_id && x.status !== "vaporware")
    .map(x => {
      const b = capSet(x);
      let inter = 0; for (const k of a) if (b.has(k)) inter++;
      const jac = inter / (a.size + b.size - inter || 1);
      const catBonus   = x.category === d.category ? .18 : 0;
      const priceBonus = (isFinite(pa) && isFinite(priceNum(x)))
        ? .12 * (1 - Math.min(1, Math.abs(priceNum(x)-pa) / Math.max(pa, 60))) : 0;
      return { dev:x, score: jac + catBonus + priceBonus, jac, inter };
    })
    .filter(r => r.jac > 0.04)
    .sort((p,q) => q.score - p.score);

  /* one build per hardware family */
  const seen = new Set(), out = [];
  for (const r of scored){
    if (seen.has(r.dev.hardware_id)) continue;
    seen.add(r.dev.hardware_id); out.push(r);
    if (out.length >= (n||4)) break;
  }
  return out;
}
