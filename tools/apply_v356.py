from pathlib import Path
import ast, py_compile
p=Path("app.py")
s=p.read_text(encoding="utf-8")
start=s.index("def render_card_giocatore_live_v140(live):")
end=s.index("\ndef ", start+10)
new=r'''def _icona_ruolo_v356(codice):
    """Icone oro inline: nessun file, I/O, query o chiamata esterna."""
    base = 'viewBox="0 0 92 58" class="fe-v356-svg" aria-hidden="true"'
    g = '#D4AF37'
    common = f'stroke="{g}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    ball = f'<circle cx="72" cy="43" r="6" stroke="{g}" stroke-width="3" fill="none"/>'
    icons = {
        "POR": f'<svg {base}><g {common}><rect x="4" y="8" width="28" height="42"/><path d="M8 16h20M13 10v38M21 10v38"/><circle cx="49" cy="25" r="5"/><path d="M45 30L31 40M44 31L57 39M35 38L21 48M55 38L68 48"/><circle cx="73" cy="14" r="6"/></g></svg>',
        "DC": f'<svg {base}><g {common}><circle cx="35" cy="20" r="5"/><path d="M34 26L43 36L62 42M43 36L24 45M35 28L21 34"/>{ball}</g></svg>',
        "B": f'<svg {base}><g {common}><circle cx="31" cy="19" r="5"/><path d="M31 25L42 35L57 42M40 34L22 45M34 28L49 25"/><circle cx="61" cy="17" r="5"/><path d="M61 23L65 36M64 29L76 25M64 36L76 47"/><circle cx="53" cy="39" r="6"/></g></svg>',
        "DD": f'<svg {base}><g {common}><circle cx="38" cy="13" r="5"/><path d="M38 19L46 32M44 25L58 20M45 31L31 43M45 32L60 43"/><circle cx="66" cy="45" r="6"/></g></svg>',
        "DS": f'<svg {base}><g {common}><circle cx="54" cy="13" r="5"/><path d="M54 19L46 32M48 25L34 20M47 31L61 43M47 32L32 43"/><circle cx="26" cy="45" r="6"/></g></svg>',
        "E": f'<svg {base}><g {common}><circle cx="40" cy="12" r="5"/><path d="M40 18L48 31M46 24L59 19M47 31L34 44M47 32L61 43"/><path d="M21 25h9M16 34h12"/></g></svg>',
        "M": f'<svg {base}><g {common}><circle cx="31" cy="14" r="5"/><path d="M31 20L39 33M37 26L50 30M38 33L27 46M38 34L50 46"/><circle cx="62" cy="15" r="5"/><path d="M62 21L57 34M58 27L48 30M57 34L66 46"/><circle cx="52" cy="42" r="6"/></g></svg>',
        "C": f'<svg {base}><g {common}><circle cx="35" cy="13" r="5"/><path d="M35 19L43 32M41 25L55 21M43 32L31 45M43 33L57 43"/><circle cx="72" cy="43" r="6"/><path d="M60 42h5"/></g></svg>',
        "W": f'<svg {base}><g {common}><circle cx="31" cy="13" r="5"/><path d="M31 19L39 32M37 25L50 20M39 32L28 45M39 33L54 42"/><circle cx="72" cy="35" r="6"/><path d="M56 41Q66 28 78 23"/></g></svg>',
        "T": f'<svg {base}><g {common}><circle cx="38" cy="12" r="5"/><path d="M38 18L46 31M44 24L57 20M46 31L34 44M46 32L59 42"/><circle cx="67" cy="45" r="6"/><path d="M60 51Q71 55 79 47"/></g></svg>',
        "A": f'<svg {base}><g {common}><circle cx="35" cy="12" r="5"/><path d="M35 18L43 31M41 24L54 19M43 31L30 44M43 32L63 39"/><circle cx="76" cy="40" r="6"/><path d="M65 38h5M70 32l5 3"/></g></svg>',
        "PC": f'<svg {base}><g {common}><circle cx="43" cy="20" r="5"/><path d="M43 26L47 39M46 31L58 26M47 39L37 50M47 39L59 49"/><circle cx="48" cy="8" r="6"/><path d="M55 8h13M61 4l7 4-7 4"/></g></svg>',
    }
    return icons.get(codice, "")


def render_card_giocatore_live_v140(live):
    """V356 - PRE CARD V346 + icona del ruolo Mantra più offensivo."""
    nome = html.escape(str(live.get("nome") or "—"))
    squadra = html.escape(str(live.get("squadra") or "—"))
    _modo_lega = str(st.session_state.get("ml_modalita") or "MANTRA").upper()
    _ruolo_raw = str(
        live.get("ruolo_classico") if _modo_lega == "CLASSIC"
        else live.get("ruolo_mantra")
    ) or "—"
    ruolo = html.escape(_ruolo_raw)

    _ordine = ["POR", "DC", "B", "DD", "DS", "E", "M", "C", "W", "T", "A", "PC"]
    if _modo_lega == "CLASSIC":
        _tokens = [{"P":"POR", "D":"DC", "C":"C", "A":"A"}.get(_ruolo_raw.strip().upper(), "")]
    else:
        import re as _re
        _tokens = [x.upper() for x in _re.findall(r"Por|Dc|Dd|Ds|Pc|B|E|M|C|W|T|A", _ruolo_raw, flags=_re.I)]
    _tokens = [x for x in _tokens if x in _ordine]
    _ruolo_icona = max(_tokens, key=lambda x: _ordine.index(x)) if _tokens else ""
    _icona = _icona_ruolo_v356(_ruolo_icona)

    st.markdown(
        f"""
        <style>
        .fe-v356-name-row{{display:flex;align-items:center;gap:14px;min-width:0}}
        .fe-v356-role{{display:flex;align-items:center;justify-content:center;flex:0 0 92px;width:92px;height:58px}}
        .fe-v356-svg{{width:92px;height:58px;display:block}}
        @media(max-width:700px){{
          .fe-v356-name-row{{gap:7px}}
          .fe-v356-role{{flex-basis:68px;width:68px;height:44px}}
          .fe-v356-svg{{width:68px;height:44px}}
        }}
        </style>
        <div class="fe-proj-player">
          <div class="fe-proj-row">
            <div class="fe-proj-main">
              <div class="fe-proj-label">GIOCATORE</div>
              <div class="fe-v356-name-row">
                <span class="fe-proj-name">{nome}</span>
                <span class="fe-v356-role">{_icona}</span>
              </div>
            </div>
            <div class="fe-proj-box"><span>SQUADRA</span><strong>{squadra}</strong></div>
            <div class="fe-proj-box"><span>RUOLO</span><strong>{ruolo}</strong></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
'''
out=s[:start]+new+s[end:]
ast.parse(out)
p.write_text(out,encoding="utf-8")
py_compile.compile(str(p),doraise=True)
print("V356 OK: ast.parse + py_compile")
