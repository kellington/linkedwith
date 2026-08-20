"""HTML renderer: generates self-contained LinkedWith.HTML from the JSON store.

Output is a single offline file (no CDN, no external requests) with live search,
facet chips, a year filter, sorting, and two views (cards for mobile, table for
desktop). All data is embedded as a JSON array and drawn client-side.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedWith</title>
  <style>
    :root {
      --bg: #faf9f7; --card: #ffffff; --ink: #1b1a17; --muted: #6b675f;
      --line: #e4e0d8; --accent: #2d6a8e; --accent-soft: #e7eff4;
      --shadow: 0 1px 2px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.04);
      --radius: 12px;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #16181a; --card: #1e2124; --ink: #e8e6e1; --muted: #9a958c;
        --line: #2e3236; --accent: #7fb6d6; --accent-soft: #212c33;
        --shadow: 0 1px 2px rgba(0,0,0,.3), 0 4px 12px rgba(0,0,0,.2);
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 0 1.25rem 4rem; background: var(--bg); color: var(--ink);
      font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
      -webkit-font-smoothing: antialiased;
    }
    header {
      position: sticky; top: 0; z-index: 10; background: var(--bg);
      padding: 1.25rem 0 .8rem; border-bottom: 1px solid var(--line);
      margin-bottom: 1.25rem;
    }
    .wrap { max-width: 1180px; margin: 0 auto; }
    h1 { margin: 0 0 .15rem; font-size: 1.4rem; letter-spacing: -.015em; }
    .sub { color: var(--muted); font-size: .82rem; margin-bottom: .8rem; }
    .sub b { color: var(--ink); }
    #q {
      width: 100%; padding: .7rem .9rem; font-size: 1rem; font-family: inherit;
      color: var(--ink); background: var(--card); border: 1px solid var(--line);
      border-radius: var(--radius); outline: none; transition: border-color .12s;
      -webkit-appearance: none;
    }
    #q:focus { border-color: var(--accent); }
    #q::placeholder { color: var(--muted); }
    .bar { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center;
           justify-content: space-between; margin-top: .7rem; }
    .chips { display: flex; flex-wrap: wrap; gap: .4rem; }
    .chip {
      padding: .28rem .7rem; font-size: .78rem; border-radius: 999px; cursor: pointer;
      border: 1px solid var(--line); background: var(--card); color: var(--muted);
      user-select: none; transition: all .12s; white-space: nowrap;
    }
    .chip:hover { border-color: var(--accent); }
    .chip.on { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); font-weight: 600; }
    .tools { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; }
    select {
      font: inherit; font-size: .78rem; padding: .28rem 1.6rem .28rem .6rem;
      color: var(--muted); background: var(--card); border: 1px solid var(--line);
      border-radius: 999px; cursor: pointer; outline: none; -webkit-appearance: none;
      appearance: none;
      background-image: linear-gradient(45deg, transparent 50%, currentColor 50%),
                        linear-gradient(135deg, currentColor 50%, transparent 50%);
      background-position: right .75rem center, right .55rem center;
      background-size: 5px 5px, 5px 5px; background-repeat: no-repeat;
    }
    select:focus { border-color: var(--accent); }
    .views { display: inline-flex; border: 1px solid var(--line); border-radius: 999px;
             overflow: hidden; background: var(--card); }
    .views button {
      font: inherit; font-size: .78rem; padding: .28rem .75rem; border: 0; cursor: pointer;
      background: transparent; color: var(--muted);
    }
    .views button.on { background: var(--accent-soft); color: var(--accent); font-weight: 600; }

    .grid { display: grid; gap: .8rem; align-items: start;
            grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); }
    .card {
      background: var(--card); border: 1px solid var(--line); border-radius: var(--radius);
      padding: .85rem 1rem; box-shadow: var(--shadow); overflow-wrap: anywhere;
    }
    .nm { font-weight: 650; font-size: 1.02rem; letter-spacing: -.01em; }
    .nm a { color: inherit; text-decoration: none; }
    .nm a:hover { color: var(--accent); }
    .role { color: var(--muted); font-size: .84rem; margin-top: .1rem; }
    .co { cursor: pointer; border-bottom: 1px dotted var(--line); }
    .co:hover { color: var(--accent); border-color: var(--accent); }
    .tags { display: flex; flex-wrap: wrap; gap: .3rem; margin-top: .5rem; }
    .g {
      display: inline-block; padding: .12rem .5rem; font-size: .7rem;
      text-transform: uppercase; letter-spacing: .05em; border-radius: 4px;
      background: var(--accent-soft); color: var(--accent); font-weight: 600;
    }
    .g.dim { background: transparent; color: var(--muted); border: 1px solid var(--line); }
    .rows { margin-top: .6rem; display: flex; flex-direction: column; gap: .18rem; }
    .r { display: flex; gap: .5rem; font-size: .85rem; align-items: baseline; }
    .k { color: var(--muted); flex: 0 0 4rem; font-size: .74rem; text-transform: uppercase; letter-spacing: .04em; }
    .v { min-width: 0; }
    .v a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--line); }
    .v a:hover { border-color: var(--accent); color: var(--accent); }
    .note { margin-top: .55rem; padding-top: .5rem; border-top: 1px dashed var(--line);
            font-size: .82rem; color: var(--muted); white-space: pre-wrap; }

    /* The table gets its own scrollport (rather than riding the page scroll) so
       the sticky column headers have something to stick to. Its height is set by
       fitTable() to exactly the space left under the page header. */
    .table-wrap { overflow: auto; border: 1px solid var(--line); border-radius: var(--radius);
                  background: var(--card); box-shadow: var(--shadow);
                  -webkit-overflow-scrolling: touch; }
    /* separate (not collapse) — Chrome paints a sticky th *behind* the rows when
       borders are collapsed. border-spacing:0 keeps it looking collapsed. */
    table { border-collapse: separate; border-spacing: 0; width: 100%; font-size: .84rem; }
    th, td { padding: .5rem .7rem; text-align: left; border-bottom: 1px solid var(--line);
             white-space: nowrap; }
    th { position: sticky; top: 0; z-index: 5; background: var(--card);
         cursor: pointer; user-select: none; box-shadow: inset 0 -1px 0 var(--line);
         font-size: .72rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
    th:hover { color: var(--accent); }
    th.on { color: var(--accent); }
    tbody tr:hover { background: var(--accent-soft); }
    td a { color: inherit; text-decoration: none; border-bottom: 1px solid var(--line); }
    td a:hover { color: var(--accent); border-color: var(--accent); }
    td.wide { white-space: normal; min-width: 15rem; max-width: 26rem; }

    mark { background: var(--accent-soft); color: inherit; padding: 0 .1em; border-radius: 2px; }
    #none { text-align: center; color: var(--muted); padding: 3rem 0; display: none; }
    kbd { font: inherit; font-size: .75rem; padding: .05rem .3rem; border: 1px solid var(--line);
          border-radius: 4px; background: var(--card); }
    [hidden] { display: none !important; }
    @media (max-width: 640px) {
      body { padding: 0 .75rem 3rem; }
      .k { flex-basis: 3.4rem; }
    }
  </style>
</head>
<body>
<header><div class="wrap">
  <h1>LinkedWith</h1>
  <div class="sub">
    <b id="shown">{{ total }}</b> of {{ total }} connections
    &middot; <span id="stat"></span>
    {%- if linkedin_date %} &middot; LinkedIn data from {{ linkedin_date }}{% endif %}
    &middot; built {{ generated }}
    &middot; press <kbd>/</kbd> to search, <kbd>esc</kbd> to clear
  </div>
  <input id="q" type="search" placeholder="Search name, company, position, email, phone, notes&hellip;" autocomplete="off">
  <div class="bar">
    <div class="chips" id="chips"></div>
    <div class="tools">
      <select id="year"></select>
      <select id="sort">
        <option value="connected:-1">Connected &mdash; newest</option>
        <option value="connected:1">Connected &mdash; oldest</option>
        <option value="msg:-1">Last message &mdash; recent</option>
        <option value="last:1">Name &mdash; A&ndash;Z</option>
        <option value="company:1">Company &mdash; A&ndash;Z</option>
      </select>
      <div class="views" id="views">
        <button data-v="cards" class="on">Cards</button><button data-v="table">Table</button>
      </div>
    </div>
  </div>
</div></header>

<div class="wrap">
  <div class="grid" id="grid"></div>
  <div class="table-wrap" id="tablewrap" hidden>
    <table id="tbl">
      <thead><tr id="head"></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div id="none">No connections match that.</div>
</div>

<script>
const ROWS = {{ rows_json|safe }};

const $ = id => document.getElementById(id);
const grid = $('grid'), tablewrap = $('tablewrap'), tbody = $('tbody'), head = $('head');
const q = $('q'), shown = $('shown'), none = $('none');

const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

// One lowercased haystack per row, built once — filtering 700+ rows on every
// keystroke has to touch strings that are already prepared.
ROWS.forEach(r => {
  r.name = [r.first, r.last].filter(Boolean).join(' ');
  r.contact = r.email || r.phone ? 1 : 0;
  r.year = (r.connected || '').slice(0, 4);
  r._h = [r.name, r.company, r.position, r.email, r.phone, r.notes, r.connected, r.msg]
    .join(' ').toLowerCase();
});

const COUNT = f => ROWS.filter(FILTERS[f]).length;
const FILTERS = {
  msg:     r => !!r.msg,
  notes:   r => !!r.notes,
  contact: r => !!r.contact,
};
const LABELS = { msg: 'Messaged', notes: 'Notes', contact: 'Email / phone' };

const COLS = [
  {k: 'first',    t: 'First'},
  {k: 'last',     t: 'Last'},
  {k: 'company',  t: 'Company'},
  {k: 'position', t: 'Position', wide: 1},
  {k: 'connected',t: 'Connected'},
  {k: 'msg',      t: 'Last message'},
  {k: 'email',    t: 'Email'},
  {k: 'phone',    t: 'Phone'},
  {k: 'notes',    t: 'Notes', wide: 1},
];

const state = {terms: [], on: new Set(), year: '', key: 'connected', dir: -1, view: 'cards'};

function hi(text, terms) {
  let out = esc(text);
  for (const t of terms) {
    if (!t) continue;
    out = out.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'),
                      '<mark>$1</mark>');
  }
  return out;
}

// Blanks always sort last, whichever direction is active — an empty "last
// message" is never the most interesting row on the page.
function cmp(a, b) {
  const av = (a[state.key] || '').toLowerCase(), bv = (b[state.key] || '').toLowerCase();
  if (av !== bv) {
    if (!av) return 1;
    if (!bv) return -1;
    return (av < bv ? -1 : 1) * state.dir;
  }
  const an = (a.last + a.first).toLowerCase(), bn = (b.last + b.first).toLowerCase();
  return an < bn ? -1 : an > bn ? 1 : 0;
}

function line(k, html) {
  return '<div class="r"><span class="k">' + k + '</span><span class="v">' + html + '</span></div>';
}

function card(r, terms) {
  const nm = hi(r.name, terms) || '(no name)';
  let h = '<div class="card"><div class="nm">' +
    (r.url ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + nm + '</a>' : nm) +
    '</div>';
  if (r.position || r.company) {
    let role = hi(r.position, terms);
    if (r.company) {
      const co = '<span class="co" data-q="' + esc(r.company) + '">' + hi(r.company, terms) + '</span>';
      role = role ? role + ' &middot; ' + co : co;
    }
    h += '<div class="role">' + role + '</div>';
  }
  h += '<div class="tags">';
  if (r.connected) h += '<span class="g dim">connected ' + esc(r.connected) + '</span>';
  if (r.msg) h += '<span class="g">messaged ' + esc(r.msg) + '</span>';
  h += '</div><div class="rows">';
  if (r.email) h += line('email', '<a href="mailto:' + esc(r.email) + '">' + hi(r.email, terms) + '</a>');
  if (r.phone) h += line('phone', '<a href="tel:' + esc(r.phone.replace(/[^0-9+]/g, '')) + '">' + hi(r.phone, terms) + '</a>');
  h += '</div>';
  if (r.notes) h += '<div class="note">' + hi(r.notes, terms) + '</div>';
  return h + '</div>';
}

function row(r, terms) {
  return '<tr>' + COLS.map(c => {
    const v = r[c.k] || '';
    let cell = hi(v, terms);
    if (c.k === 'first' && r.url) cell = '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + cell + '</a>';
    if (c.k === 'email' && v) cell = '<a href="mailto:' + esc(v) + '">' + cell + '</a>';
    if (c.k === 'phone' && v) cell = '<a href="tel:' + esc(v.replace(/[^0-9+]/g, '')) + '">' + cell + '</a>';
    return '<td' + (c.wide ? ' class="wide"' : '') + '>' + cell + '</td>';
  }).join('') + '</tr>';
}

function drawHead() {
  head.innerHTML = COLS.map(c => {
    const on = c.k === state.key;
    return '<th data-k="' + c.k + '"' + (on ? ' class="on"' : '') + '>' + c.t +
      (on ? (state.dir === 1 ? ' ▲' : ' ▼') : '') + '</th>';
  }).join('');
}

function draw() {
  const hits = ROWS.filter(r =>
    (!state.year || r.year === state.year) &&
    [...state.on].every(f => FILTERS[f](r)) &&
    state.terms.every(t => r._h.includes(t))
  ).sort(cmp);

  if (state.view === 'cards') {
    grid.innerHTML = hits.map(r => card(r, state.terms)).join('');
  } else {
    drawHead();
    tbody.innerHTML = hits.map(r => row(r, state.terms)).join('');
  }
  shown.textContent = hits.length;
  none.style.display = hits.length ? 'none' : 'block';
}

$('chips').innerHTML = Object.keys(FILTERS).map(f =>
  '<span class="chip" data-f="' + f + '">' + LABELS[f] + ' <b>' + COUNT(f) + '</b></span>').join('');
$('chips').addEventListener('click', e => {
  const chip = e.target.closest('.chip');
  if (!chip) return;
  const f = chip.dataset.f;
  state.on.has(f) ? state.on.delete(f) : state.on.add(f);
  chip.classList.toggle('on', state.on.has(f));
  draw();
});

const years = [...new Set(ROWS.map(r => r.year).filter(Boolean))].sort().reverse();
$('year').innerHTML = '<option value="">Any year</option>' +
  years.map(y => '<option value="' + y + '">Connected ' + y +
    ' (' + ROWS.filter(r => r.year === y).length + ')</option>').join('');
$('year').addEventListener('change', e => { state.year = e.target.value; draw(); });

$('sort').addEventListener('change', e => {
  const [k, d] = e.target.value.split(':');
  state.key = k; state.dir = +d; draw();
});

head.addEventListener('click', e => {
  const th = e.target.closest('th');
  if (!th) return;
  const k = th.dataset.k;
  // Dates read best newest-first on the first click; text reads best A–Z.
  state.dir = state.key === k ? -state.dir : (k === 'connected' || k === 'msg' ? -1 : 1);
  state.key = k;
  $('sort').value = k + ':' + state.dir;
  draw();
});

$('views').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  state.view = b.dataset.v;
  [...e.currentTarget.children].forEach(c => c.classList.toggle('on', c === b));
  grid.hidden = state.view !== 'cards';
  tablewrap.hidden = state.view !== 'table';
  draw();
  fitTable();
});

grid.addEventListener('click', e => {
  const co = e.target.closest('.co');
  if (!co) return;
  q.value = co.dataset.q;
  state.terms = [co.dataset.q.toLowerCase()];
  draw();
  window.scrollTo(0, 0);
});

q.addEventListener('input', () => {
  const raw = q.value.trim().toLowerCase();
  state.terms = raw ? raw.split(/\s+/) : [];
  draw();
});
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); q.select(); }
  if (e.key === 'Escape') { q.value = ''; state.terms = []; q.blur(); draw(); }
});

$('stat').textContent = COUNT('msg') + ' messaged · ' + COUNT('contact') + ' with email or phone';

// Size the table's scrollport to the space left below the sticky page header, so
// the page itself never scrolls in table view — otherwise the whole table (sticky
// column headers included) slides up underneath the header.
function fitTable() {
  if (tablewrap.hidden) return;
  const pad = parseFloat(getComputedStyle(document.body).paddingBottom) || 0;
  tablewrap.style.maxHeight =
    Math.max(260, window.innerHeight - tablewrap.offsetTop - pad - 8) + 'px';
}
window.addEventListener('resize', fitTable);

draw();
</script>
</body>
</html>"""


def _rows_from_store(store: dict) -> list[dict]:
    """Flatten the store into the row dicts the template embeds as JSON."""
    rows = []
    for rec in store.values():
        rows.append({
            "first": rec.get("first_name") or "",
            "last": rec.get("last_name") or "",
            "company": rec.get("company") or "",
            "position": rec.get("position") or "",
            "connected": rec.get("connected_on") or "",
            "msg": rec.get("most_recent_message") or "",
            # user_email wins over the LinkedIn-supplied address (D-01 fields are hand-curated).
            "email": rec.get("user_email") or rec.get("email") or "",
            "phone": rec.get("user_phone") or "",
            "notes": rec.get("user_notes") or "",
            "url": rec.get("url") or "",
        })
    return rows


def _json_for_script(rows: list[dict]) -> str:
    """JSON-encode rows for inlining in a <script> block.

    Escaping <, > and & as \\u sequences keeps a value containing "</script>"
    from terminating the block early.
    """
    raw = json.dumps(rows, ensure_ascii=False)
    return raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_html(store: dict, output_path: Path, linkedin_date: str = "") -> None:
    """Render store to a self-contained HTML file at output_path (atomic write).

    Args:
        store: Dict keyed by normalized LinkedIn URL with connection records.
        output_path: Path where the HTML file will be written.
        linkedin_date: YYYY-MM-DD date string from the source ZIP filename, shown as subtitle.
    """
    env = Environment(autoescape=True)
    template = env.from_string(HTML_TEMPLATE)

    rows = _rows_from_store(store)
    html = template.render(
        rows_json=_json_for_script(rows),
        total=len(rows),
        linkedin_date=linkedin_date,
        generated=datetime.now().astimezone().strftime("%Y-%m-%d"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.parent / (output_path.name + ".tmp")
    tmp.write_text(html, encoding="utf-8")
    os.replace(tmp, output_path)
