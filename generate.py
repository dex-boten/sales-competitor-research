#!/usr/bin/env python3
"""
Generator for Sales Competitor Research HTML
Reads 3 JSON data files and produces index.html
"""

import json
import os

BASE = '/Users/shkodi6/.openclaw/workspace/sales-competitor-research'

with open(f'{BASE}/data-group-a.json') as f:
    gA = json.load(f)
with open(f'{BASE}/data-group-b.json') as f:
    gB = json.load(f)
with open(f'{BASE}/data-group-c.json') as f:
    gC = json.load(f)

deep = gA['competitors'] + gB['competitors'] + gC['deep_competitors']
light = gC['light_check']

# ── helpers ──────────────────────────────────────────────────────────────────

def e(s):
    if s is None: return '–'
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def g(d, k, default='–'):
    if not isinstance(d, dict): return default
    v = d.get(k)
    if v is None or v == '': return default
    return v

def phase_class(c):
    p = str(g(c,'phase','')).lower()
    if 'public' in p: return 'phase-public'
    if 'growth' in p or 'series c' in p or 'series d' in p or 'late' in p: return 'phase-growth'
    if 'startup' in p or 'series b' in p or 'series a' in p: return 'phase-startup'
    if 'seed' in p or 'early' in p: return 'phase-seed'
    return 'phase-growth'

def phase_label(c):
    p = str(g(c,'phase','')).lower()
    if 'public' in p: return 'Public'
    if 'late' in p or 'series d' in p or 'series c' in p or 'growth' in p: return 'Growth'
    if 'startup' in p or 'series b' in p or 'series a' in p: return 'Startup'
    if 'seed' in p: return 'Seed'
    return 'Growth'

def motion_badges(c, inline=False):
    m = str(g(c,'motion','')).lower()
    sep = ' ' if inline else ' '
    if m == 'plg': return f'<span class="bdg motion-plg">PLG</span>'
    if m == 'slg': return f'<span class="bdg motion-slg">SLG</span>'
    return f'<span class="bdg motion-plg">PLG</span>{sep}<span class="bdg motion-slg">SLG</span>'

def status_bdg(s):
    sl = str(s).lower()
    if sl == 'shipped': return '<span class="bdg st-shipped">Shipped ✓</span>'
    if sl == 'beta': return '<span class="bdg st-beta">Beta</span>'
    if sl == 'roadmap': return '<span class="bdg st-roadmap">Roadmap</span>'
    return f'<span class="bdg st-roadmap">{e(s)}</span>'

def sales_ai_bdg(s):
    sl = str(s).lower()
    if sl == 'yes': return '<span class="bdg st-shipped">Yes</span>'
    if sl == 'partial': return '<span class="bdg st-beta">Partial</span>'
    return '<span class="bdg st-roadmap">No</span>'

def homepage_url(c):
    su = c.get('screenshot_urls', {})
    if su and su.get('homepage'):
        return su['homepage']
    return '#'

def short(s, n=120):
    s = str(s)
    return s[:n] + '…' if len(s) > n else s

# ── cross-cutting analytics ───────────────────────────────────────────────────

motion_counts = {'PLG': 0, 'SLG': 0, 'Both': 0}
ai_framings = []
all_uc_names = []
pricing_models = {'Per-seat': 0, 'Consumption/Credits': 0, 'Usage-based': 0, 'Annual Contract': 0, 'Per-agent': 0, 'Hybrid': 0}
ai_pricing_buckets = {'Included in paid tiers': 0, 'Consumption/Credits add-on': 0, 'AI is the core product': 0}

for c in deep:
    m = str(g(c,'motion','')).lower()
    if m == 'plg': motion_counts['PLG'] += 1
    elif m == 'slg': motion_counts['SLG'] += 1
    else: motion_counts['Both'] += 1

    af = g(c,'ai_framing','')
    if af != '–': ai_framings.append((c.get('name',''), af))

    for uc in c.get('agentic_use_cases', []):
        n = g(uc,'name','')
        if n != '–': all_uc_names.append(n)

    pm = str(g(c,'pricing_model','')).lower()
    if 'per-seat' in pm or 'per seat' in pm:
        pricing_models['Per-seat'] += 1
    if 'consumption' in pm or 'credit' in pm:
        pricing_models['Consumption/Credits'] += 1
    if 'usage' in pm:
        pricing_models['Usage-based'] += 1
    if 'annual contract' in pm:
        pricing_models['Annual Contract'] += 1
    if 'per-agent' in pm or 'per agent' in pm:
        pricing_models['Per-agent'] += 1
    if 'hybrid' in pm:
        pricing_models['Hybrid'] += 1

    aip = str(g(c,'ai_pricing','')).lower()
    cname = str(c.get('id','')).lower()
    if cname in ('11x','artisan','rox','day-ai'):
        ai_pricing_buckets['AI is the core product'] += 1
    elif 'credit' in aip or 'consumption' in aip or 'flex' in aip:
        ai_pricing_buckets['Consumption/Credits add-on'] += 1
    else:
        ai_pricing_buckets['Included in paid tiers'] += 1

# Find most common UC themes
from collections import Counter
uc_words = []
for n in all_uc_names:
    words = n.lower().split()
    for w in words:
        if len(w) > 4 and w not in ('agent','agents','with','from','your','that','this','their','which','have','been','will','into','over','than','then','just'):
            uc_words.append(w)
top_uc = Counter(uc_words).most_common(10)

# ── comparison table ──────────────────────────────────────────────────────────

def render_comparison_table():
    rows = []
    for c in deep:
        cid = e(c.get('id',''))
        name = e(c.get('name',''))
        hp = e(homepage_url(c))
        pclass = phase_class(c)
        plabel = phase_label(c)
        mot = g(c,'motion','–')
        icp_short = e(short(g(c,'icp','–'), 90))
        persona_short = e(short(g(c,'persona','–'), 80))
        pm = e(short(g(c,'pricing_model','–'), 70))
        aip = e(short(g(c,'ai_pricing','–'), 70))
        aif = e(short(g(c,'ai_framing','–'), 80))
        uc_count = len(c.get('agentic_use_cases',[]))
        rows.append(f'''
    <tr>
      <td><a href="#{cid}" class="comp-link">{name}</a></td>
      <td><span class="bdg {pclass}">{plabel}</span></td>
      <td>{motion_badges(c, inline=True)}</td>
      <td>{icp_short}</td>
      <td>{persona_short}</td>
      <td>{pm}</td>
      <td>{aip}</td>
      <td>{aif}</td>
      <td class="uc-num">{uc_count}</td>
    </tr>''')
    return ''.join(rows)

# ── individual competitor section ─────────────────────────────────────────────

def render_comp(c):
    cid = c.get('id','')
    name = c.get('name','')
    hp = homepage_url(c)
    auc = c.get('agentic_use_cases', [])
    tagline = g(c, 'tagline')
    is_monday = cid == 'monday-crm'

    parts = []
    parts.append(f'<section id="{e(cid)}" class="comp-section{"  monday-own" if is_monday else ""}">')

    # ── header ──
    parts.append(f'''
<div class="comp-header">
  <div class="comp-title-row">
    <h2>
      <a href="{e(hp)}" target="_blank" rel="noopener">{e(name)}</a>
      <span class="bdg {phase_class(c)}">{phase_label(c)}</span>
      {motion_badges(c)}
    </h2>
  </div>
  <p class="comp-tagline">{e(tagline)}</p>
</div>''')

    # ── h1/h2 ──
    h1 = g(c, 'h1')
    h2 = g(c, 'h2')
    h1h2_src = g(c, 'h1_h2_source')
    parts.append(f'''
<div class="h1h2-block">
  <div class="block-label">Homepage Headline <a href="{e(h1h2_src)}" target="_blank" class="src-link">source ↗</a></div>
  <p class="h1-text">&#8220;{e(h1)}&#8221;</p>
  <p class="h2-text">{e(h2)}</p>
</div>''')

    # ── company details ──
    funding = g(c, 'funding')
    funding_src = g(c, 'funding_source')
    valuation = g(c, 'valuation', None)
    arr = g(c, 'arr', None)
    parts.append('<div class="detail-row">')
    fsrc_html = f'<a href="{e(funding_src)}" target="_blank" class="src-link">Source ↗</a>' if funding_src != '–' else ''
    parts.append(f'<div class="detail-card"><div class="detail-label">Funding / Company</div><div class="detail-val">{e(funding)}</div>{fsrc_html}</div>')
    if valuation and valuation != '–': parts.append(f'<div class="detail-card"><div class="detail-label">Valuation</div><div class="detail-val">{e(valuation)}</div></div>')
    if arr and arr != '–': parts.append(f'<div class="detail-card"><div class="detail-label">ARR</div><div class="detail-val">{e(arr)}</div></div>')
    parts.append('</div>')

    # ── value prop + promise ──
    vp = g(c, 'value_prop')
    promise = g(c, 'promise')
    parts.append(f'''
<div class="two-col">
  <div class="info-card">
    <div class="block-label">Value Proposition</div>
    <p>{e(vp)}</p>
  </div>
  <div class="info-card promise-card">
    <div class="block-label">Main Promise</div>
    <p class="promise-text">&#8220;{e(promise)}&#8221;</p>
  </div>
</div>''')

    # ── motion + gtm ──
    motion_detail = g(c, 'motion_detail')
    gtm = g(c, 'gtm')
    parts.append(f'''
<div class="two-col">
  <div class="info-card">
    <div class="block-label">Motion {motion_badges(c)}</div>
    <p>{e(motion_detail)}</p>
  </div>
  <div class="info-card">
    <div class="block-label">GTM Approach</div>
    <p>{e(gtm)}</p>
  </div>
</div>''')

    # ── audience ──
    icp = g(c, 'icp')
    persona = g(c, 'persona')
    parts.append(f'''
<div class="two-col">
  <div class="info-card">
    <div class="block-label">ICP</div>
    <p>{e(icp)}</p>
  </div>
  <div class="info-card">
    <div class="block-label">Persona</div>
    <p>{e(persona)}</p>
  </div>
</div>''')

    # ── pricing ──
    tiers = g(c, 'pricing_tiers')
    model = g(c, 'pricing_model')
    ai_p = g(c, 'ai_pricing')
    free = g(c, 'free_tier')
    p_src = g(c, 'pricing_source')
    src_html = f'<a href="{e(p_src)}" target="_blank" class="src-link">source ↗</a>' if p_src != '–' else ''
    parts.append(f'''
<div class="info-card">
  <div class="block-label">Pricing {src_html}</div>
  <table class="pricing-table">
    <tr><th>Tiers</th><td>{e(tiers)}</td></tr>
    <tr><th>Model</th><td>{e(model)}</td></tr>
    <tr><th>AI in Pricing</th><td>{e(ai_p)}</td></tr>
    <tr><th>Free Tier</th><td>{e(free)}</td></tr>
  </table>
</div>''')

    # ── ai framing ──
    ai_frame = g(c, 'ai_framing')
    parts.append(f'''
<div class="ai-framing-row">
  <span class="ai-frame-icon">🧠</span>
  <span class="ai-frame-label">AI Framing:</span>
  <span class="ai-frame-text">{e(ai_frame)}</span>
</div>''')

    # ── agentic use cases ──
    parts.append(f'''
<div class="agentic-section">
  <div class="agentic-hdr">
    <span>🤖 Agentic Use Cases</span>
    <span class="uc-count-badge">{len(auc)} use case{"s" if len(auc) != 1 else ""}</span>
  </div>
  <div class="uc-grid">''')
    if auc:
        for uc in auc:
            uc_name = g(uc, 'name')
            uc_status = g(uc, 'status', 'shipped')
            uc_jtbd = uc.get('jtbd', [])
            uc_int = g(uc, 'integrations')
            jtbd_html = ''.join(f'<li>{e(j)}</li>' for j in uc_jtbd) if uc_jtbd else '<li>–</li>'
            parts.append(f'''
    <div class="uc-card">
      <div class="uc-hdr">
        <span class="uc-name">{e(uc_name)}</span>
        {status_bdg(uc_status)}
      </div>
      <ul class="uc-jtbd">{jtbd_html}</ul>
      <div class="uc-int"><span class="uc-int-label">Integrations:</span> {e(uc_int)}</div>
    </div>''')
    else:
        parts.append('<div class="uc-card"><p>No agentic use cases documented.</p></div>')
    parts.append('</div></div>')

    # ── offering ──
    offering = g(c, 'offering')
    parts.append(f'''
<div class="info-card">
  <div class="block-label">Offering</div>
  <p>{e(offering)}</p>
</div>''')

    # ── ai talk ──
    ai_talk = g(c, 'ai_talk')
    parts.append(f'''
<div class="info-card">
  <div class="block-label">How They Talk About AI</div>
  <p>{e(ai_talk)}</p>
</div>''')

    # ── integrations ──
    integrations_str = g(c, 'integrations')
    parts.append(f'''
<div class="info-card">
  <div class="block-label">Integrations</div>
  <p>{e(integrations_str)}</p>
</div>''')

    # ── g2 reviews ──
    rating = g(c, 'g2_rating')
    count = g(c, 'g2_count')
    stars5 = c.get('g2_5star', [])
    stars1 = c.get('g2_1star', [])

    pos_html = ''
    for rev in stars5:
        q = g(rev, 'quote')
        u = g(rev, 'url', 'https://www.g2.com')
        pos_html += f'''<div class="g2-box g2-pos"><div class="g2-stars">★★★★★</div><p>{e(q)}</p><a href="{e(u)}" target="_blank" class="src-link">View ↗</a></div>'''

    neg_html = ''
    for rev in stars1:
        q = g(rev, 'quote')
        u = g(rev, 'url', 'https://www.g2.com')
        neg_html += f'''<div class="g2-box g2-neg"><div class="g2-stars">★☆☆☆☆</div><p>{e(q)}</p><a href="{e(u)}" target="_blank" class="src-link">View ↗</a></div>'''

    parts.append(f'''
<div class="info-card">
  <div class="block-label">G2 Reviews</div>
  <div class="g2-rating-row">
    <span class="g2-big-rating">{e(rating)}</span>
    <span class="g2-star-display">★</span>
    <span class="g2-count-disp">({e(count)} reviews)</span>
  </div>
  <div class="g2-grid">
    {pos_html}
    {neg_html}
  </div>
</div>''')

    # ── acquisition lps ──
    lps = c.get('acquisition_lps', [])
    if lps:
        lp_items = ''.join(f'<li><a href="{e(lp)}" target="_blank" rel="noopener">{e(lp)}</a></li>' for lp in lps)
        parts.append(f'''
<div class="info-card">
  <div class="block-label">Acquisition Landing Pages</div>
  <ul class="lp-list">{lp_items}</ul>
</div>''')

    # ── screenshot ──
    ss_path = f'{BASE}/screenshots/{cid}/homepage.png'
    if os.path.exists(ss_path):
        parts.append(f'''
<div class="info-card">
  <div class="block-label">Homepage Screenshot</div>
  <img src="screenshots/{e(cid)}/homepage.png" alt="{e(name)} homepage" class="comp-screenshot" loading="lazy">
</div>''')
    else:
        parts.append(f'''
<div class="info-card">
  <div class="block-label">Homepage Screenshot</div>
  <div class="screenshot-placeholder">
    <span>📷 No screenshot captured</span>
    <a href="{e(hp)}" target="_blank" rel="noopener">{e(hp)} ↗</a>
  </div>
</div>''')

    # ── monday angle ──
    monday_angle = g(c, 'monday_angle')
    label = "monday.com — own product notes" if is_monday else "monday.com Angle"
    parts.append(f'''
<div class="monday-angle-box">
  <div class="monday-angle-label">🎯 {label}</div>
  <p>{e(monday_angle)}</p>
</div>''')

    # ── other insights ──
    other = g(c, 'other_insights')
    parts.append(f'''
<div class="info-card">
  <div class="block-label">Other Insights</div>
  <p>{e(other)}</p>
</div>''')

    parts.append('<div class="comp-divider"></div>')
    parts.append('</section>')
    return '\n'.join(parts)

# ── light check cards ─────────────────────────────────────────────────────────

def render_light_card(c):
    name = g(c, 'name')
    cid = g(c, 'id')
    sai = g(c, 'sales_ai', 'no')
    summary = g(c, 'summary')
    source = g(c, 'source')
    return f'''
<div class="light-card">
  <div class="light-card-header">
    <span class="light-name">{e(name)}</span>
    {sales_ai_bdg(sai)}
  </div>
  <div class="light-ai-label">Sales AI: {e(sai).title()}</div>
  <p class="light-summary">{e(summary)}</p>
  <a href="{e(source)}" target="_blank" class="src-link">Source ↗</a>
</div>'''

# ── cross-cutting takeaways ───────────────────────────────────────────────────

def render_takeaways():
    total = len(deep)
    # Motion
    motion_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td><td>{round(v/total*100)}%</td></tr>' for k,v in motion_counts.items())

    # AI framing list
    framing_rows = ''.join(f'<tr><td>{e(n)}</td><td><em>{e(f)}</em></td></tr>' for n,f in ai_framings)

    # Pricing model
    pm_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in pricing_models.items() if v > 0)

    # AI pricing buckets
    aip_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td><td>{round(v/total*100)}%</td></tr>' for k,v in ai_pricing_buckets.items())

    # Most common UC themes
    uc_theme_rows = ''.join(f'<tr><td>{k}</td><td>{v} mentions</td></tr>' for k,v in top_uc[:8])

    # Gaps
    gaps = [
        ("Unified Work OS + CRM", "All competitors are pure-play CRM/sales tools or pure outbound AI — none offer the cross-functional work management + CRM combo that monday.com does."),
        ("Non-sales team visibility", "No competitor gives marketing, delivery, and sales teams a shared live view of the customer journey across departments."),
        ("CRM-to-project handoff", "Once a deal closes, all competitors drop the thread — monday.com owns the post-sale delivery phase."),
        ("Mid-market AI without credits", "Most AI-inclusive tiers (Attio, Apollo, Outreach) use credit systems that cap usage. monday CRM includes AI from Standard with no credit caps."),
        ("Startup-to-enterprise CRM continuity", "Attio targets Series A–D; Salesforce targets enterprise. monday CRM can serve both on one platform without re-implementation."),
    ]
    gap_rows = ''.join(f'<tr><td><strong>{e(g_name)}</strong></td><td>{e(g_desc)}</td></tr>' for g_name, g_desc in gaps)

    return f'''
<div class="takeaways-section">
  <h3 class="section-h3">Cross-Cutting Patterns</h3>
  <p class="section-note">Data-only observations across all {total} deep competitors.</p>

  <div class="takeaway-grid">

    <div class="takeaway-card">
      <div class="tc-label">Motion Breakdown</div>
      <table class="ta-table">
        <thead><tr><th>Motion</th><th>Count</th><th>Share</th></tr></thead>
        <tbody>{motion_rows}</tbody>
      </table>
      <p class="tc-note">Majority have both PLG + SLG — hybrid is the dominant go-to-market in 2026.</p>
    </div>

    <div class="takeaway-card">
      <div class="tc-label">Pricing Model Distribution</div>
      <table class="ta-table">
        <thead><tr><th>Model</th><th>Count</th></tr></thead>
        <tbody>{pm_rows}</tbody>
      </table>
      <p class="tc-note">Per-seat is most common, but consumption/credits is rising fast (Salesforce, Outreach, Attio, Apollo).</p>
    </div>

    <div class="takeaway-card">
      <div class="tc-label">Where AI Sits in Pricing</div>
      <table class="ta-table">
        <thead><tr><th>Placement</th><th>Count</th><th>Share</th></tr></thead>
        <tbody>{aip_rows}</tbody>
      </table>
      <p class="tc-note">Included-in-tier is most common; but enterprise-grade AI often requires consumption spend on top.</p>
    </div>

    <div class="takeaway-card">
      <div class="tc-label">Most Common Agentic UC Themes</div>
      <table class="ta-table">
        <thead><tr><th>Term</th><th>Occurrences</th></tr></thead>
        <tbody>{uc_theme_rows}</tbody>
      </table>
      <p class="tc-note">Meeting prep, deal management, pipeline, and outreach dominate agent use cases across all competitors.</p>
    </div>

  </div>

  <div class="takeaway-card full-width" style="margin-top:20px">
    <div class="tc-label">AI Framing by Competitor</div>
    <table class="ta-table">
      <thead><tr><th>Competitor</th><th>AI Framing Label</th></tr></thead>
      <tbody>{framing_rows}</tbody>
    </table>
  </div>

  <div class="takeaway-card full-width" style="margin-top:20px">
    <div class="tc-label">Gaps Nobody Covers</div>
    <table class="ta-table">
      <thead><tr><th>Gap</th><th>Observation</th></tr></thead>
      <tbody>{gap_rows}</tbody>
    </table>
    <p class="tc-note">Data-only patterns — no messaging recommendations implied.</p>
  </div>

</div>'''

# ── sidebar nav for deep research ─────────────────────────────────────────────

def render_deep_sidebar():
    items = []
    for c in deep:
        cid = e(c.get('id',''))
        name = e(c.get('name',''))
        items.append(f'<a href="#{cid}" class="sidebar-link">{name}</a>')
    return '\n'.join(items)

# ── full HTML ─────────────────────────────────────────────────────────────────

comp_sections = '\n'.join(render_comp(c) for c in deep)
light_cards = '\n'.join(render_light_card(c) for c in light)
comparison_rows = render_comparison_table()
takeaways_html = render_takeaways()
sidebar_links = render_deep_sidebar()

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sales Competitor Research — monday.com AI Workspace</title>
<link rel="stylesheet" href="style.css">
<style>
/* ── Tab system ── */
.tab-nav {{background:#fff;border-bottom:2px solid var(--line);position:sticky;top:0;z-index:30;}}
.tab-nav .wrap {{display:flex;gap:0;padding:0 20px;}}
.tab-btn {{padding:14px 24px;font-size:14px;font-weight:700;color:var(--muted);background:none;border:none;border-bottom:3px solid transparent;cursor:pointer;transition:color .15s,border-color .15s;margin-bottom:-2px;}}
.tab-btn:hover {{color:var(--mday-purple);}}
.tab-btn.active {{color:var(--mday-purple);border-bottom-color:var(--mday-purple);}}
.tab-panel {{display:none;}}
.tab-panel.active {{display:block;}}

/* ── Phase badges ── */
.bdg {{font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;text-transform:uppercase;letter-spacing:.04em;display:inline-block;white-space:nowrap;}}
.phase-public {{background:#1c1c2e;color:#fff;}}
.phase-growth {{background:#0d7f6a;color:#fff;}}
.phase-startup {{background:#f59e0b;color:#1c1c2e;}}
.phase-seed {{background:#dc2626;color:#fff;}}

/* ── Motion badges ── */
.motion-plg {{background:#dbeafe;color:#1d4ed8;}}
.motion-slg {{background:#ede9fe;color:#6d28d9;}}
.motion-both {{background:#f0fdf4;color:#15803d;}}

/* ── Status badges ── */
.st-shipped {{background:#dcfce7;color:#15803d;}}
.st-beta {{background:#fed7aa;color:#92400e;}}
.st-roadmap {{background:#f3f4f6;color:#6b7280;}}

/* ── Competitor section ── */
.comp-section {{padding:40px 0 0;border-top:3px solid var(--line);}}
.comp-section:first-child {{border-top:none;}}
.monday-own {{background:linear-gradient(180deg,#f0f0ff 0%,transparent 200px);}}
.comp-header {{margin-bottom:20px;}}
.comp-title-row h2 {{font-size:28px;margin:0 0 6px;display:flex;flex-wrap:wrap;align-items:center;gap:10px;}}
.comp-title-row h2 a {{color:var(--ink);text-decoration:none;}}
.comp-title-row h2 a:hover {{color:var(--mday-purple);}}
.comp-tagline {{color:var(--muted);font-size:15px;margin:4px 0 0;font-style:italic;}}

/* ── H1/H2 block ── */
.h1h2-block {{background:linear-gradient(135deg,#f5f4ff 0%,#fff 100%);border:1px solid #d9d9ff;border-left:4px solid var(--mday-purple);border-radius:10px;padding:18px 20px;margin:16px 0;}}
.h1-text {{font-size:20px;font-weight:800;color:var(--mday-dark);margin:6px 0 8px;line-height:1.3;}}
.h2-text {{font-size:14px;color:#444;margin:0;line-height:1.5;}}
.block-label {{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:6px;display:flex;align-items:center;gap:8px;}}

/* ── Detail row ── */
.detail-row {{display:flex;flex-wrap:wrap;gap:12px;margin:14px 0;}}
.detail-card {{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;flex:1;min-width:200px;}}
.detail-label {{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:4px;}}
.detail-val {{font-size:13px;color:var(--ink);line-height:1.5;}}

/* ── Info cards ── */
.info-card {{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:12px 0;}}
.promise-card {{background:linear-gradient(135deg,#fffbeb 0%,#fff 100%);border-color:#fcd34d;}}
.promise-text {{font-size:16px;font-weight:600;color:#92400e;font-style:italic;margin:0;}}
.two-col {{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0;}}

/* ── Pricing table ── */
.pricing-table {{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px;}}
.pricing-table th {{text-align:left;padding:9px 12px;width:130px;background:#f8f9ff;color:var(--mday-purple);font-weight:700;border-bottom:1px solid var(--line);border-right:1px solid var(--line);border-radius:0;}}
.pricing-table td {{padding:9px 12px;border-bottom:1px solid var(--line);color:var(--ink);line-height:1.45;vertical-align:top;}}
.pricing-table tr:last-child th,.pricing-table tr:last-child td {{border-bottom:none;}}

/* ── AI Framing ── */
.ai-framing-row {{background:linear-gradient(90deg,#1c1c2e 0%,#2b2f5c 100%);color:#fff;border-radius:10px;padding:14px 20px;margin:12px 0;display:flex;align-items:center;gap:10px;flex-wrap:wrap;}}
.ai-frame-icon {{font-size:20px;}}
.ai-frame-label {{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#a9adff;}}
.ai-frame-text {{font-size:15px;font-weight:700;color:#fff;}}

/* ── Agentic use cases ── */
.agentic-section {{border:1px solid #d9d9ff;border-radius:12px;overflow:hidden;margin:12px 0;}}
.agentic-hdr {{background:linear-gradient(135deg,var(--mday-purple) 0%,#8a7bff 100%);color:#fff;padding:12px 18px;font-weight:800;font-size:14px;display:flex;align-items:center;justify-content:space-between;}}
.uc-count-badge {{background:rgba(255,255,255,.22);padding:2px 10px;border-radius:20px;font-size:12px;font-weight:700;}}
.uc-grid {{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:16px;background:#fbfbff;}}
.uc-card {{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;}}
.uc-hdr {{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:8px;flex-wrap:wrap;}}
.uc-name {{font-size:14px;font-weight:800;color:var(--mday-dark);flex:1;}}
.uc-jtbd {{margin:0 0 10px;padding-left:16px;}}
.uc-jtbd li {{margin:4px 0;font-size:13px;line-height:1.4;}}
.uc-int {{font-size:12px;color:var(--muted);border-top:1px dashed var(--line);padding-top:8px;}}
.uc-int-label {{font-weight:700;color:var(--mday-purple);}}

/* ── G2 ── */
.g2-rating-row {{display:flex;align-items:baseline;gap:6px;margin-bottom:12px;}}
.g2-big-rating {{font-size:28px;font-weight:900;color:var(--ink);}}
.g2-star-display {{color:#f59e0b;font-size:22px;}}
.g2-count-disp {{font-size:13px;color:var(--muted);}}
.g2-grid {{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
.g2-box {{border-radius:10px;padding:14px 16px;}}
.g2-pos {{background:#f0fdf4;border:1.5px solid #86efac;}}
.g2-neg {{background:#fef2f2;border:1.5px solid #fca5a5;}}
.g2-stars {{font-size:14px;color:#f59e0b;margin-bottom:6px;}}
.g2-box p {{font-size:13px;margin:0 0 8px;line-height:1.45;font-style:italic;}}

/* ── Acquisition LPs ── */
.lp-list {{margin:0;padding-left:16px;}}
.lp-list li {{margin:5px 0;}}
.lp-list a {{font-size:13px;color:var(--mday-purple);word-break:break-all;}}

/* ── Screenshot ── */
.comp-screenshot {{width:100%;border-radius:8px;border:1px solid var(--line);margin-top:10px;}}
.screenshot-placeholder {{background:#f1f5f9;border:2px dashed #cbd5e1;border-radius:10px;padding:30px 20px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:8px;}}
.screenshot-placeholder span {{font-size:24px;color:#94a3b8;}}
.screenshot-placeholder a {{font-size:13px;color:var(--mday-purple);}}

/* ── monday angle ── */
.monday-angle-box {{background:linear-gradient(135deg,#eef2ff 0%,#f5f3ff 100%);border:1px solid #a5b4fc;border-left:4px solid #4f46e5;border-radius:10px;padding:16px 20px;margin:12px 0;}}
.monday-angle-label {{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#4f46e5;margin-bottom:6px;}}
.monday-angle-box p {{margin:0;font-size:14px;line-height:1.5;color:#1e1b4b;}}

/* ── Src link ── */
.src-link {{color:var(--mday-purple);text-decoration:none;font-size:12px;}}
.src-link:hover {{text-decoration:underline;}}

/* ── Section divider ── */
.comp-divider {{height:1px;background:var(--line);margin:40px 0 0;}}

/* ── Comparison table ── */
.sortable-table {{width:100%;border-collapse:collapse;font-size:13px;background:#fff;border-radius:12px;overflow:hidden;border:1px solid var(--line);}}
.sortable-table th {{background:var(--mday-dark);color:#fff;padding:11px 13px;text-align:left;font-weight:700;cursor:pointer;user-select:none;white-space:nowrap;}}
.sortable-table th:hover {{background:#2b2f5c;}}
.sortable-table th.sort-asc::after {{content:" ↑";}}
.sortable-table th.sort-desc::after {{content:" ↓";}}
.sortable-table td {{padding:10px 13px;border-bottom:1px solid var(--line);vertical-align:top;}}
.sortable-table tbody tr:nth-child(even) {{background:#fafbff;}}
.sortable-table tbody tr:hover {{background:#f0f0ff;}}
.comp-link {{color:var(--mday-purple);font-weight:700;text-decoration:none;}}
.comp-link:hover {{text-decoration:underline;}}
.uc-num {{font-weight:800;color:var(--mday-purple);text-align:center;}}

/* ── Takeaways ── */
.section-h3 {{font-size:22px;font-weight:800;margin:0 0 4px;}}
.section-note {{color:var(--muted);font-size:14px;margin:0 0 20px;}}
.takeaway-grid {{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.takeaway-card {{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;}}
.takeaway-card.full-width {{grid-column:1/-1;}}
.tc-label {{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:10px;}}
.tc-note {{font-size:12px;color:var(--muted);margin:10px 0 0;font-style:italic;}}
.ta-table {{width:100%;border-collapse:collapse;font-size:13px;}}
.ta-table th {{text-align:left;padding:7px 10px;background:#f8f9ff;color:var(--mday-purple);font-weight:700;border-bottom:1px solid var(--line);}}
.ta-table td {{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;}}
.ta-table tr:last-child td {{border-bottom:none;}}

/* ── Light check ── */
.light-grid {{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}}
.light-card {{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px;}}
.light-card-header {{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;}}
.light-name {{font-size:16px;font-weight:800;color:var(--ink);}}
.light-ai-label {{font-size:11px;color:var(--muted);margin-bottom:8px;}}
.light-summary {{font-size:13px;line-height:1.5;margin:0 0 10px;}}

/* ── Deep research layout ── */
.deep-layout {{display:grid;grid-template-columns:200px 1fr;gap:0;align-items:start;}}
.deep-sidebar {{position:sticky;top:60px;padding:20px 16px 20px 0;max-height:calc(100vh - 80px);overflow-y:auto;}}
.sidebar-link {{display:block;padding:6px 10px;font-size:13px;color:var(--muted);text-decoration:none;border-radius:6px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:2px;}}
.sidebar-link:hover {{background:var(--bg);color:var(--mday-purple);}}
.deep-content {{padding:20px 0;min-width:0;}}

/* ── Overview section header ── */
.overview-section-hdr {{font-size:22px;font-weight:800;margin:32px 0 12px;padding-top:20px;border-top:2px solid var(--line);}}
.overview-section-hdr:first-child {{border-top:none;margin-top:0;padding-top:0;}}

/* ── Responsive ── */
@media(max-width:900px){{
  .two-col,.uc-grid,.g2-grid,.takeaway-grid,.light-grid{{grid-template-columns:1fr;}}
  .deep-layout{{grid-template-columns:1fr;}}
  .deep-sidebar{{display:none;}}
}}
@media(max-width:600px){{
  .comp-title-row h2{{font-size:22px;}}
  .h1-text{{font-size:17px;}}
}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <p class="eyebrow">monday.com · Sales PMM · Competitor Intelligence</p>
    <h1>Sales Competitor Research<br>— monday.com AI Workspace</h1>
    <p class="sub">15 deep competitors + 4 light checks · November 2026 · Data only — no messaging recommendations</p>
    <div class="meta-row">
      <span><b>15</b> deep competitors</span>
      <span><b>4</b> light checks</span>
      <span><b>{sum(len(c.get("agentic_use_cases",[])) for c in deep)}</b> agentic use cases mapped</span>
      <span>Sources linked per claim · G2 blocked by DataDome — ratings from vendor sites</span>
      <span>Compiled <b>November 2026</b></span>
    </div>
  </div>
</header>

<nav class="tab-nav">
  <div class="wrap">
    <button class="tab-btn active" onclick="showTab('overview')">Overview</button>
    <button class="tab-btn" onclick="showTab('deep')">Deep Research</button>
    <button class="tab-btn" onclick="showTab('light')">Light Check</button>
  </div>
</nav>

<main>

<!-- ═══════════════════════════════════════════════════════════ OVERVIEW TAB ═ -->
<div id="tab-overview" class="tab-panel active">
<div class="wrap">

  <h2 class="overview-section-hdr">Comparison at a Glance</h2>
  <p class="section-note">All 15 deep competitors. Click column headers to sort. Click competitor names to jump to full section.</p>
  <div class="scroll">
    <table class="sortable-table" id="compTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Competitor</th>
          <th onclick="sortTable(1)">Phase</th>
          <th onclick="sortTable(2)">Motion</th>
          <th onclick="sortTable(3)">ICP</th>
          <th onclick="sortTable(4)">Persona</th>
          <th onclick="sortTable(5)">Pricing Model</th>
          <th onclick="sortTable(6)">AI in Pricing</th>
          <th onclick="sortTable(7)">AI Framing</th>
          <th onclick="sortTable(8)" style="min-width:60px;text-align:center">Agents</th>
        </tr>
      </thead>
      <tbody>
        {comparison_rows}
      </tbody>
    </table>
  </div>

  {takeaways_html}

</div>
</div>

<!-- ════════════════════════════════════════════════════ DEEP RESEARCH TAB ═══ -->
<div id="tab-deep" class="tab-panel">
<div class="wrap">
  <div class="deep-layout">
    <div class="deep-sidebar">
      <div class="block-label" style="padding:6px 10px 8px;font-size:10px;">JUMP TO</div>
      {sidebar_links}
    </div>
    <div class="deep-content">
      {comp_sections}
    </div>
  </div>
</div>
</div>

<!-- ═══════════════════════════════════════════════════════ LIGHT CHECK TAB ═ -->
<div id="tab-light" class="tab-panel">
<div class="wrap">
  <h2 class="overview-section-hdr">Light Check — Horizontal PM Tools</h2>
  <p class="section-note">4 horizontal platforms checked for sales AI presence. Not deep competitors — context only.</p>
  <div class="light-grid">
    {light_cards}
  </div>
</div>
</div>

</main>

<footer>
  <div class="wrap">
    monday.com AI Workspace · Sales Competitor Research · November 2026 · Data only ·
    G2 direct scraping blocked by DataDome; ratings sourced from vendor sites and knowledge.
    Sources linked per claim throughout.
  </div>
</footer>

<script>
// Tab switching
function showTab(name) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
  window.scrollTo(0, 0);
}}

// Table sorting
let sortDir = {{}};
function sortTable(col) {{
  const table = document.getElementById('compTable');
  const ths = table.querySelectorAll('thead th');
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const dir = sortDir[col] === 'asc' ? 'desc' : 'asc';
  sortDir[col] = dir;
  ths.forEach((th, i) => {{ th.classList.remove('sort-asc','sort-desc'); }});
  ths[col].classList.add(dir === 'asc' ? 'sort-asc' : 'sort-desc');
  rows.sort((a,b) => {{
    const av = a.cells[col].innerText.trim().toLowerCase();
    const bv = b.cells[col].innerText.trim().toLowerCase();
    const an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return dir==='asc' ? an-bn : bn-an;
    return dir==='asc' ? av.localeCompare(bv) : bv.localeCompare(av);
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

// Deep tab: clicking sidebar links activates deep tab first
document.querySelectorAll('.sidebar-link, .comp-link').forEach(a => {{
  a.addEventListener('click', function(evt) {{
    const href = this.getAttribute('href');
    if (href && href.startsWith('#')) {{
      evt.preventDefault();
      // Activate deep tab if not active
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('tab-deep').classList.add('active');
      document.querySelectorAll('.tab-btn')[1].classList.add('active');
      setTimeout(() => {{
        const el = document.querySelector(href);
        if (el) el.scrollIntoView({{behavior:'smooth', block:'start'}});
      }}, 50);
    }}
  }});
}});
</script>

</body>
</html>'''

out_path = f'{BASE}/index.html'
with open(out_path, 'w') as f:
    f.write(HTML)

print(f"Done! Written to {out_path}")
print(f"Deep competitors: {len(deep)}")
print(f"Light checks: {len(light)}")
print(f"Total agentic use cases: {sum(len(c.get('agentic_use_cases',[])) for c in deep)}")
total_chars = len(HTML)
print(f"File size: {total_chars:,} chars ({total_chars//1024} KB)")
