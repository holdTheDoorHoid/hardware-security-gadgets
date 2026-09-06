/* Recommendation engine. Depends on common.js (capScore, SKILL_ORDER, priceNum, siblings). */

const W = { goal:100, budget:22, skill:26, build:20, stealth:14, support:14 };

const COMMUNITY_SCORE = { "very-active":1, active:.85, commercial:.8, slow:.5, dormant:.25, dead:.05 };
const DOCS_SCORE      = { excellent:1, good:.8, sparse:.4, poor:.2, none:.05 };
const ABANDON_SCORE   = { low:1, medium:.6, high:.25, "already-abandoned":.05 };
const STATUS_MULT     = { available:1, preorder:.93, "out-of-stock":.9, "diy-only":.97, discontinued:.6, vaporware:.12 };
/* how much willingness each build_effort demands */
const BUILD_DEMAND = { assembled:0, "flash-only":1, assembly:2, soldering:3, "full-diy":4 };
const BUILD_WILLING = { assembled:0, "flash-only":1, soldering:3, "full-diy":4 };
const STEALTH_FIT = {
  any:      { overt:1,   discreet:1,  covert:1,  implant:1 },
  discreet: { overt:.55, discreet:1,  covert:1,  implant:.9 },
  covert:   { overt:.10, discreet:.5, covert:1,  implant:1 }
};

const clamp01 = n => Math.max(0, Math.min(1, n));

/* coverage of one goal by one device, 0..1, plus which caps carried it */
function goalCoverage(dev, goal){
  let got = 0, total = 0; const hits = [];
  for (const [k, w] of Object.entries(goal.caps)){
    total += w;
    const s = capScore(dev, k);
    if (s > 0){ got += s * w; hits.push({ key:k, w, s }); }
  }
  hits.sort((a,b) => (b.w*b.s) - (a.w*a.s));
  return { cov: total ? clamp01(got/total) : 0, hits };
}

function supportScore(dev){
  const e = dev.ecosystem || {};
  const c = COMMUNITY_SCORE[e.community]  ?? .5;
  const d = DOCS_SCORE[e.docs_quality]    ?? .5;
  const a = ABANDON_SCORE[e.abandoned_risk] ?? .5;
  return c*.35 + d*.3 + a*.35;
}

function scoreDevice(dev, ans, goals){
  const per = goals.map(g => ({ goal:g, ...goalCoverage(dev, g) }));
  const goalFit = per.length ? per.reduce((s,p)=>s+p.cov,0)/per.length : .5;

  const budget = QUIZ.budgets.find(b=>b.id===ans.budget) || QUIZ.budgets.at(-1);
  const p = priceNum(dev);
  let budgetFit;
  if (!isFinite(p))         budgetFit = .5;
  else if (p <= budget.max) budgetFit = 1;
  else                      budgetFit = clamp01(budget.max / p);

  const ui = SKILL_ORDER.indexOf(ans.skill);
  const di = SKILL_ORDER.indexOf(dev.skill_level);
  const skillFit = di < 0 ? .6
    : di <= ui ? clamp01(1 - .06*(ui-di))
               : clamp01(1 - .34*(di-ui));

  const dDem = BUILD_DEMAND[dev.build_effort] ?? 2;
  const uWil = BUILD_WILLING[ans.build] ?? 1;
  const buildFit = dDem <= uWil ? 1 : clamp01(1 - .32*(dDem-uWil));

  const stealthFit = (STEALTH_FIT[ans.stealth] || STEALTH_FIT.any)[dev.stealth] ?? .7;

  const imp = { high:1, mid:.5, low:.15 }[ans.support] ?? .5;
  const sRaw = supportScore(dev);
  const supportFit = 1 - imp*(1 - sRaw);

  const raw =
      W.goal*goalFit + W.budget*budgetFit + W.skill*skillFit +
      W.build*buildFit + W.stealth*stealthFit + W.support*supportFit;

  const mult = STATUS_MULT[dev.status] ?? .8;
  const max  = W.goal + W.budget + W.skill + W.build + W.stealth + W.support;

  return {
    dev, per, goalFit, budgetFit, skillFit, buildFit, stealthFit, supportFit, sRaw,
    score: raw*mult, pct: Math.round((raw*mult/max)*100)
  };
}

/* human-readable reasons */
function explain(r, ans){
  const d = r.dev, why = [], warn = [];

  for (const p of r.per){
    const names = p.hits.slice(0,3).map(h => (T.caps[h.key]||{}).label).filter(Boolean);
    if (p.cov >= .55)      why.push(`Strong on <b>${esc(p.goal.label.toLowerCase())}</b>${names.length?`: ${esc(names.join(", "))}`:""}.`);
    else if (p.cov >= .22) why.push(`Partly covers <b>${esc(p.goal.label.toLowerCase())}</b>${names.length?`: ${esc(names.join(", "))}`:""}.`);
    else                   warn.push(`Does little for <b>${esc(p.goal.label.toLowerCase())}</b>. You would need a second device.`);
  }

  const budget = QUIZ.budgets.find(b=>b.id===ans.budget);
  const p = priceNum(d);
  if (isFinite(p) && budget && p > budget.max)
    warn.push(`At ${priceStr(d)} it is over your stated budget.`);
  else if (isFinite(p) && budget && budget.max !== Infinity && p <= budget.max*.5)
    why.push(`Well under budget at ${priceStr(d)}.`);

  const ui = SKILL_ORDER.indexOf(ans.skill), di = SKILL_ORDER.indexOf(d.skill_level);
  if (di > ui) warn.push(`Rated <b>${esc(d.skill_level)}</b>, a step beyond where you placed yourself. ${esc(d.skill_note||"")}`);
  else if (di >= 0) why.push(`Skill level <b>${esc(d.skill_level)}</b> suits you.`);

  const dDem = BUILD_DEMAND[d.build_effort] ?? 2, uWil = BUILD_WILLING[ans.build] ?? 1;
  if (dDem > uWil) warn.push(`Needs more hands-on work than you asked for: <b>${esc(BUILD_LABEL[d.build_effort]||d.build_effort)}</b>.`);
  else if (d.build_effort === "assembled") why.push(`Arrives ready to use.`);

  if (ans.stealth === "covert" && (d.stealth === "overt"))
    warn.push(`Looks like an obvious hacking tool, which is the opposite of what you asked for.`);
  else if (ans.stealth !== "any" && (d.stealth === "covert" || d.stealth === "implant"))
    why.push(`Disguised form factor: <b>${esc(STEALTH_LABEL[d.stealth])}</b>.`);

  const e = d.ecosystem || {};
  if (ans.support === "high"){
    if (e.abandoned_risk === "high" || e.abandoned_risk === "already-abandoned")
      warn.push(`Project looks ${esc(e.abandoned_risk === "already-abandoned" ? "abandoned" : "at risk of abandonment")}, and you said support matters.`);
    else if (e.docs_quality === "excellent" || e.community === "very-active")
      why.push(`Actively maintained with ${esc(e.docs_quality||"decent")} documentation.`);
  }

  if (d.legal && d.legal.risk_level === "high")
    warn.push(`High legal exposure. ${esc((d.legal.notes||"").split(".")[0])}.`);
  if (d.status === "discontinued") warn.push(`Discontinued — you would be buying used.`);
  if (d.status === "out-of-stock") warn.push(`Frequently out of stock.`);
  if (d.status === "vaporware")    warn.push(`We could not confirm this ships at all.`);

  const sib = siblings(d);
  if (sib.length) why.push(`Same hardware also runs ${sib.map(s=>esc(s.firmware||s.name)).join(", ")} — different firmware, different capabilities.`);

  return { why: why.slice(0,6), warn: warn.slice(0,5) };
}

/* main entry: returns { top: [..3], also: [..] } deduped to one build per hardware */
function recommend(ans, db){
  const goals = QUIZ.goals.filter(g => ans.goals.has(g.id));
  const scored = (db || DB).map(d => scoreDevice(d, ans, goals))
                           .sort((a,b) => b.score - a.score);

  const seen = new Set(), uniqueHw = [];
  for (const r of scored){
    if (seen.has(r.dev.hardware_id)) continue;
    seen.add(r.dev.hardware_id);
    uniqueHw.push(r);
  }
  const top = uniqueHw.slice(0,3).map(r => ({ ...r, ...explain(r, ans) }));
  return { top, also: uniqueHw.slice(3,9) };
}
