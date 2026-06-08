"""HTML renderer: generates self-contained LinkedWith.HTML from the JSON store."""
import os
from pathlib import Path
from jinja2 import Environment

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LinkedWith</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; margin: 0; padding: 8px; }
    .table-wrap { overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 6px 8px; white-space: nowrap; text-align: left; }
    th[data-sortable] { cursor: pointer; user-select: none; background: #f5f5f5; }
    th[data-sortable]:hover { background: #e8e8e8; }
    tr:nth-child(even) { background: #fafafa; }
  </style>
</head>
<body>
  <h2>LinkedWith</h2>
  {% if linkedin_date %}<p style="margin:0 0 4px;color:#666;font-size:12px;">Refreshed with LinkedIn data from {{ linkedin_date }}</p>{% endif %}
  <p>{{ rows|length }} connections</p>
  <div class="table-wrap">
    <table id="contacts">
      <thead>
        <tr>
          <th data-sortable>First Name <span class="si"></span></th>
          <th data-sortable>Last Name <span class="si"></span></th>
          <th>Company</th>
          <th>Position</th>
          <th data-sortable>Connected On <span class="si"></span></th>
          <th data-sortable>Most Recent Message <span class="si"></span></th>
          <th>Email</th>
          <th>Phone</th>
          <th data-sortable>Notes <span class="si"></span></th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
        <tr>
          <td data-sort="{{ row.first_name }}">{{ row.first_name }}</td>
          <td data-sort="{{ row.last_name }}">{{ row.last_name }}</td>
          <td>{{ row.company }}</td>
          <td>{{ row.position }}</td>
          <td data-sort="{{ row.connected_on }}">{{ row.connected_on }}</td>
          <td data-sort="{{ row.most_recent_message }}">{{ row.most_recent_message }}</td>
          <td>{{ row.user_email }}</td>
          <td>{{ row.user_phone }}</td>
          <td data-sort="{{ row.user_notes }}">{{ row.user_notes }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  <script>
  (function(){
    var col=-1,dir=1;
    function sentinel(v){return v===''?'0000-00-00':v;}
    function getVal(row,c){var cell=row.cells[c];return cell?(sentinel(cell.getAttribute('data-sort')||'')):'0000-00-00';}
    function sort(c){
      var tbl=document.getElementById('contacts'),tb=tbl.tBodies[0];
      var rows=Array.from(tb.rows);
      if(c===col){dir=-dir;}else{dir=1;col=c;}
      rows.sort(function(a,b){var av=getVal(a,c).toLowerCase(),bv=getVal(b,c).toLowerCase();return av<bv?dir:av>bv?-dir:0;});
      rows.forEach(function(r){tb.appendChild(r);});
      Array.from(tbl.tHead.rows[0].cells).forEach(function(th,i){
        var s=th.querySelector('.si');
        if(!s)return;
        s.textContent=i===col?(dir===-1?' \u25BC':' \u25B2'):'';
      });
    }
    window.onload=function(){
      var ths=document.getElementById('contacts').tHead.rows[0].cells;
      Array.from(ths).forEach(function(th,i){
        if(th.hasAttribute('data-sortable')){th.addEventListener('click',function(){sort(i);});}
      });
      sort(4); // Connected On descending
    };
  })();
  </script>
</body>
</html>"""


def render_html(store: dict, output_path: Path, linkedin_date: str = "") -> None:
    """Render store to a self-contained HTML file at output_path (atomic write).

    Args:
        store: Dict keyed by normalized LinkedIn URL with connection records.
        output_path: Path where the HTML file will be written.
        linkedin_date: YYYY-MM-DD date string from the source ZIP filename, shown as subtitle.
    """
    env = Environment(autoescape=True)
    template = env.from_string(HTML_TEMPLATE)

    rows = []
    for rec in store.values():
        rows.append({
            "first_name": rec.get("first_name") or "",
            "last_name": rec.get("last_name") or "",
            "company": rec.get("company") or "",
            "position": rec.get("position") or "",
            "connected_on": rec.get("connected_on") or "",
            "most_recent_message": rec.get("most_recent_message") or "",
            "user_email": rec.get("user_email") or "",
            "user_phone": rec.get("user_phone") or "",
            "user_notes": rec.get("user_notes") or "",
        })

    html = template.render(rows=rows, linkedin_date=linkedin_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.parent / (output_path.name + ".tmp")
    tmp.write_text(html, encoding="utf-8")
    os.replace(tmp, output_path)
