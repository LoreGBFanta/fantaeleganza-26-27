from pathlib import Path
import ast, py_compile

p=Path("app.py")
s=p.read_text(encoding="utf-8")
start=s.index("def render_card_giocatore_live_v140(live):")
end=s.index("\ndef ", start+10)

new=r'''def render_card_giocatore_live_v140(live):
    """V355 - card Banditore con foto statica per player_id, zero I/O Python runtime."""
    nome = html.escape(str(live.get("nome") or "—"))
    squadra = html.escape(str(live.get("squadra") or "—"))
    _modo_lega = str(st.session_state.get("ml_modalita") or "MANTRA").upper()
    ruolo = html.escape(str(
        live.get("ruolo_classico") if _modo_lega == "CLASSIC"
        else live.get("ruolo_mantra")
    ) or "—")

    _pid = live.get("player_id") or live.get("id") or live.get("Id")
    try:
        _pid = str(int(float(_pid)))
    except Exception:
        _pid = ""

    _foto = (
        f'<div class="fe-v355-photo">'
        f'<img src="app/static/players/{html.escape(_pid)}.jpg" '
        f'alt="{nome}" loading="eager" decoding="async" '
        f'onerror="this.parentElement.style.display=\'none\';'
        f'this.closest(\'.fe-v355-card\').classList.add(\'fe-v355-no-photo\');">'
        f'</div>'
        if _pid else ""
    )

    _css = """
    <style>
    .fe-v355-card{display:grid;grid-template-columns:116px minmax(0,1fr);gap:14px;align-items:stretch}
    .fe-v355-card.fe-v355-no-photo{grid-template-columns:minmax(0,1fr)}
    .fe-v355-photo{width:116px;height:116px;border-radius:12px;overflow:hidden;background:#101820}
    .fe-v355-photo img{width:100%;height:100%;display:block;object-fit:cover;object-position:center top}
    .fe-v355-card .fe-proj-player{margin:0!important;height:100%;box-sizing:border-box}
    @media(max-width:700px){
      .fe-v355-card{grid-template-columns:82px minmax(0,1fr);gap:9px}
      .fe-v355-photo{width:82px;height:96px}
    }
    </style>
    """
    _card = (
        '<div class="fe-v355-card">'
        + _foto
        + '<div class="fe-proj-player"><div class="fe-proj-row">'
        + '<div class="fe-proj-main"><div class="fe-proj-label">GIOCATORE</div>'
        + f'<div class="fe-proj-name">{nome}</div></div>'
        + f'<div class="fe-proj-box"><span>SQUADRA</span><strong>{squadra}</strong></div>'
        + f'<div class="fe-proj-box"><span>RUOLO</span><strong>{ruolo}</strong></div>'
        + '</div></div></div>'
    )
    st.markdown(_css + _card, unsafe_allow_html=True)
'''
out=s[:start]+new+s[end:]
ast.parse(out)
p.write_text(out,encoding="utf-8")
py_compile.compile(str(p),doraise=True)
print("V355 OK: ast.parse + py_compile")

# trigger V355

# trigger after validator
