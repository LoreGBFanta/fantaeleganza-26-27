# FANTAELEGANZA MULTIMODULO V3 - FILE VERIFICATO
import html
import io
import json
import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURAZIONE APP
# ============================================================

st.set_page_config(
    page_title="FANTAELEGANZA 26/27",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SOGLIA_BASE = 500.00
MAX_GIOCATORI = 30
MIN_PORTIERI = 2
MAX_UNDO = 10

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fantacalcio.db"

MAX_SNAPSHOT = 30


def leggi_segreto(nome):
    """
    Legge prima dalle variabili d'ambiente e poi da st.secrets.
    In locale, se non esistono credenziali cloud, l'app continua
    a usare il normale database SQLite fantacalcio.db.
    """

    valore = os.environ.get(
        nome
    )

    if valore:
        return valore

    try:
        valore = st.secrets.get(
            nome
        )
    except Exception:
        valore = None

    return valore


TURSO_DATABASE_URL = leggi_segreto(
    "TURSO_DATABASE_URL"
)

TURSO_AUTH_TOKEN = leggi_segreto(
    "TURSO_AUTH_TOKEN"
)

USA_DATABASE_CLOUD = bool(
    TURSO_DATABASE_URL
    and TURSO_AUTH_TOKEN
)


# ============================================================
# SESSION STATE
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "DASHBOARD"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


# ============================================================
# COLORI INTERFACCIA
# ============================================================

if st.session_state.dark_mode:
    BG_PAGE = "#0b1220"
    BG_CARD = "#121c2d"
    BG_CARD_2 = "#182437"
    TEXT = "#f8fafc"
    TEXT_SOFT = "#aab7ca"
    BORDER = "#29384d"
else:
    BG_PAGE = "#f4f7fb"
    BG_CARD = "#ffffff"
    BG_CARD_2 = "#f8fafc"
    TEXT = "#0f172a"
    TEXT_SOFT = "#64748b"
    BORDER = "#dbe2ea"

NAVY = "#071a2f"
NAVY_2 = "#0c2745"
GOLD = "#f5b51b"
GREEN = "#16a34a"
RED = "#ef4444"
BLUE = "#2563eb"


# ============================================================
# CSS GENERALE
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background: {BG_PAGE};
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1800px;
        padding-top: 0.15rem;
        padding-bottom: 1.2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    /* Rimuove completamente la fascia bianca superiore di Streamlit */
    header[data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        border: 0 !important;
    }}

    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    div[data-testid="stAppViewContainer"] {{
        padding-top: 0 !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT};
    }}

    p {{
        color: {TEXT};
    }}

    /* ======================================================
       HEADER
       ====================================================== */

    .fanta-header {{
        background:
            linear-gradient(
                100deg,
                {NAVY} 0%,
                {NAVY_2} 100%
            );

        border-radius: 0 0 14px 14px;

        padding: 14px 20px;

        margin:
            -0.7rem 0 8px 0;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.15);
    }}

    .fanta-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .fanta-logo {{
        width: 52px;
        height: 52px;

        display: flex;
        align-items: center;
        justify-content: center;

        border: 2px solid {GOLD};

        border-radius: 14px;

        font-size: 29px;

        background:
            rgba(255,255,255,0.06);
    }}

    .fanta-brand-title {{
        color: white;
        font-weight: 900;
        font-size: 30px;
        line-height: 1;
        letter-spacing: 0.2px;
    }}

    .fanta-brand-title span {{
        color: {GOLD};
    }}

    .fanta-brand-subtitle {{
        color: #e2e8f0;
        font-size: 14px;
        margin-top: 5px;
    }}

    /* ======================================================
       METRICHE
       ====================================================== */

    div[data-testid="stMetric"] {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 11px;

        padding: 8px 11px;

        box-shadow:
            0 2px 6px rgba(15,23,42,0.04);

        min-height: 76px;
    }}

    div[data-testid="stMetricLabel"] {{
        font-size: 14px;
        color: {TEXT_SOFT};
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 22px;
        color: {TEXT};
    }}

    /* ======================================================
       PULSANTI
       ====================================================== */

    .stButton > button,
    .stDownloadButton > button {{
        border-radius: 9px;
        min-height: 90px;
        font-weight: 700;
        transition: all 0.15s ease;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        transform: translateY(-1px);
    }}

    /* ======================================================
       NAVBAR
       ====================================================== */

    .nav-title {{
        color: {TEXT_SOFT};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 6px;
        margin-bottom: 4px;
        letter-spacing: 0.7px;
    }}

    /* ======================================================
       TOOLBAR UNDO
       ====================================================== */

    .operation-info {{
        min-height: 90px;
        display: flex;
        align-items: center;
        padding-left: 8px;
        color: {TEXT_SOFT};
        font-size: 12px;
    }}

    /* ======================================================
       CAMPI MANTRA - GRIGLIA COMPATTA
       ====================================================== */

    .modules-intro {{
        color: {TEXT_SOFT};
        font-size: 11px;
        margin: 2px 0 7px 0;
    }}

    .module-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 6px;
        margin-bottom: 8px;
        box-shadow: 0 2px 6px rgba(15,23,42,0.04);
    }}

    .module-title {{
        color: {TEXT};
        text-align: center;
        font-size: 14px;
        font-weight: 900;
        line-height: 1.05;
        margin: 1px 0;
    }}

    .module-summary {{
        color: {TEXT_SOFT};
        text-align: center;
        font-size: 9px;
        margin: 0 0 4px 0;
    }}

    .pitch {{
        position: relative;
        width: 100%;
        min-height: 690px;
        box-sizing: border-box;
        border-radius: 7px;
        padding: 18px 14px;
        overflow: hidden;
        background: repeating-linear-gradient(
            90deg,
            #16833a 0px,
            #16833a 40px,
            #147836 40px,
            #147836 80px
        );
        border: 2px solid #f8fafc;
        box-shadow: inset 0 0 13px rgba(0,0,0,0.14);
    }}

    .pitch:before {{
        content: "";
        position: absolute;
        top: 5px;
        bottom: 5px;
        left: 5px;
        right: 5px;
        border: 1px solid rgba(255,255,255,0.74);
        border-radius: 3px;
        pointer-events: none;
    }}

    .pitch:after {{
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        border: 1px solid rgba(255,255,255,0.68);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
    }}

    .pitch-half-line {{
        position: absolute;
        top: 50%;
        left: 5px;
        right: 5px;
        border-top: 1px solid rgba(255,255,255,0.68);
        z-index: 0;
    }}

    .pitch-line {{
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-evenly;
        align-items: flex-start;
        gap: 12px;
        margin: 30px 0;
    }}

    .player-slot {{
        flex: 1 1 0;
        min-width: 0;
        max-width: 240px;
        border-radius: 6px;
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(255,255,255,0.88);
        text-align: center;
        padding: 9px 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.13);
    }}

    .slot-code {{
        font-size: 14px;
        font-weight: 900;
        color: #0f172a;
        line-height: 1.05;
        margin-bottom: 6px;
        display: flex;
        justify-content: center;
        align-items: baseline;
        gap: 6px;
        flex-wrap: wrap;
    }}

    .slot-coverage {{
        font-size: 12px;
        font-weight: 900;
        line-height: 1;
    }}

    .slot-description {{
        display: none !important;
    }}

    .player-list {{
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 4px;
        width: 100%;
    }}

    .player-name {{
        display: block;
        width: 100%;
        box-sizing: border-box;
        background: #eef2f7;
        border-radius: 5px;
        padding: 5px 7px;
        margin: 0;
        font-size: 14px;
        line-height: 1.25;
        font-weight: 800;
        white-space: normal;
        overflow-wrap: anywhere;
    }}

    .slot-empty {{
        display: inline-block;
        color: #b91c1c;
        background: #fee2e2;
        border-radius: 8px;
        padding: 1px 4px;
        font-size: 7px;
        font-weight: 800;
        line-height: 1.1;
    }}

    /* ======================================================
       POSIZIONI LATERALI
       ====================================================== */

    .position-row {{
        display: grid;

        grid-template-columns:
            68px 1fr auto;

        align-items: center;

        gap: 6px;

        padding:
            4px 0;

        font-size: 11px;

        border-bottom:
            1px solid {BORDER};
    }}

    .position-code {{
        font-weight: 800;
        color: {TEXT};
    }}

    .position-desc {{
        color: {TEXT_SOFT};
    }}

    .position-ok {{
        background: #dcfce7;
        color: #15803d;

        padding:
            2px 7px;

        border-radius: 10px;

        font-weight: 700;
        font-size: 10px;
    }}

    .position-ko {{
        background: #fee2e2;
        color: #dc2626;

        padding:
            2px 7px;

        border-radius: 10px;

        font-weight: 700;
        font-size: 10px;
    }}

    /* ======================================================
       ROSA VUOTA
       ====================================================== */

    .empty-card {{
        background: {BG_CARD};

        border:
            1px solid {BORDER};

        border-radius: 12px;

        padding:
            28px;

        text-align: center;

        margin-top: 8px;

        box-shadow:
            0 2px 8px
            rgba(15,23,42,0.04);
    }}

    .empty-icon {{
        font-size: 40px;
        margin-bottom: 6px;
    }}

    .empty-title {{
        font-size: 19px;
        font-weight: 800;
        color: {TEXT};
    }}

    .empty-text {{
        color: {TEXT_SOFT};
        font-size: 13px;
        margin-top: 5px;
    }}

    /* ======================================================
       FOOTER
       ====================================================== */

    .fanta-footer {{
        margin:
            22px 0 0 0;

        padding:
            11px 18px;

        background: {NAVY};

        border-radius: 10px;

        color:
            #dce5ef;

        font-size: 11px;
    }}

    /* ======================================================
       MOBILE / RESPONSIVE
       ====================================================== */

    /* Vista ROSA desktop/mobile */
    .rosa-mobile-view {{
        display: none;
    }}

    .rosa-desktop-view {{
        display: block;
    }}

    div[class*="st-key-rosa_mobile_view"] {{
        display: none;
    }}

    div[class*="st-key-rosa_desktop_view"] {{
        display: block;
    }}

    @media
    (max-width: 850px) {{

        /* Pagina più compatta su smartphone */
        .block-container {{
            max-width: 100% !important;
            padding-top: 0.10rem !important;
            padding-bottom: 0.8rem !important;
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
        }}

        /* Header */
        .fanta-header {{
            padding: 9px 10px !important;
            border-radius: 0 0 10px 10px !important;
            margin-bottom: 5px !important;
        }}

        .fanta-brand {{
            gap: 8px !important;
        }}

        .fanta-logo {{
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            font-size: 21px !important;
            border-radius: 10px !important;
        }}

        .fanta-brand-title {{
            font-size: 19px !important;
            line-height: 1.05 !important;
        }}

        .fanta-brand-subtitle {{
            font-size: 10px !important;
            margin-top: 2px !important;
        }}

        /* Navigazione e pulsanti */
        .stButton > button,
        .stDownloadButton > button {{
            min-height: 46px !important;
            height: auto !important;
            padding: 0.35rem 0.5rem !important;
            font-size: 12px !important;
            line-height: 1.15 !important;
            border-radius: 8px !important;
            white-space: normal !important;

            /* Mobile: contrasto sempre leggibile */
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        /* Anche il testo interno dei pulsanti deve ereditare
           il colore corretto prima del click */
        .stButton > button *,
        .stDownloadButton > button * {{
            color: inherit !important;
        }}

        /* Pulsanti principali: NAV selezionata, ACQUISTA,
           conferme, modulo attivo, ecc. */
        button[data-testid="stBaseButton-primary"],
        .stButton > button[kind="primary"] {{
            background: #071a2f !important;
            color: #ffffff !important;
            border-color: #071a2f !important;
        }}

        button[data-testid="stBaseButton-primary"] *,
        .stButton > button[kind="primary"] * {{
            color: #ffffff !important;
        }}

        /* Pulsanti secondari / normali */
        button[data-testid="stBaseButton-secondary"] {{
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        button[data-testid="stBaseButton-secondary"] * {{
            color: #0f172a !important;
        }}

        .stButton > button:disabled,
        .stDownloadButton > button:disabled {{
            background: #e2e8f0 !important;
            color: #64748b !important;
            opacity: 1 !important;
        }}

        div[data-testid="stHorizontalBlock"] {{
            gap: 0.35rem !important;
        }}

        /* Tabs scorrevoli orizzontalmente */
        div[data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            overflow-y: hidden !important;
            white-space: nowrap !important;
            flex-wrap: nowrap !important;
            scrollbar-width: thin;
        }}

        button[data-baseweb="tab"] {{
            min-width: max-content !important;
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
            font-size: 12px !important;
            color: #0f172a !important;
            background: #ffffff !important;
        }}

        button[data-baseweb="tab"] * {{
            color: inherit !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #071a2f !important;
            background: #f8fafc !important;
            font-weight: 800 !important;
        }}

        /* ASTA: il nome giocatore personalizzato deve avere
           spazio sufficiente prima del riquadro sottostante */
        .asta-player-mobile-fix {{
            min-height: 96px !important;
            padding-bottom: 18px !important;
            margin-bottom: 10px !important;
            position: relative !important;
            z-index: 2 !important;
            overflow: visible !important;
        }}

        /* Metriche */
        div[data-testid="stMetric"] {{
            min-height: 62px !important;
            padding: 6px 8px !important;
        }}

        div[data-testid="stMetricLabel"] {{
            font-size: 11px !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 17px !important;
        }}

        /* Titoli e testi */
        h1 {{
            font-size: 1.45rem !important;
        }}

        h2 {{
            font-size: 1.25rem !important;
        }}

        h3 {{
            font-size: 1.08rem !important;
        }}

        h4 {{
            font-size: 0.98rem !important;
        }}

        p,
        label,
        .stMarkdown {{
            line-height: 1.25 !important;
        }}

        /* Input */
        div[data-baseweb="select"] > div,
        input,
        textarea {{
            font-size: 16px !important;
        }}

        /* Ricerca giocatore, prezzo, filtri:
           sfondo chiaro e testo scuro sempre visibile */
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        textarea {{
            min-height: 42px !important;
            background: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            border-color: #cbd5e1 !important;
            caret-color: #0f172a !important;
        }}

        div[data-testid="stTextInput"] input::placeholder,
        div[data-testid="stNumberInput"] input::placeholder,
        textarea::placeholder {{
            color: #64748b !important;
            -webkit-text-fill-color: #64748b !important;
            opacity: 1 !important;
        }}

        /* Selectbox: giocatore, filtri, ecc. */
        div[data-baseweb="select"] > div {{
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {{
            color: #0f172a !important;
        }}

        div[data-baseweb="select"] svg {{
            fill: #0f172a !important;
            color: #0f172a !important;
        }}

        /* Menu a tendina aperto */
        ul[role="listbox"],
        div[role="listbox"] {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        li[role="option"],
        div[role="option"] {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        li[role="option"]:hover,
        div[role="option"]:hover {{
            background: #f1f5f9 !important;
            color: #0f172a !important;
        }}

        /* ROSA: su mobile nascondiamo la griglia desktop e
           mostriamo la tabella compatta dedicata */
        .rosa-desktop-view {{
            display: none !important;
        }}

        div[class*="st-key-rosa_mobile_view"] {{
            display: block !important;
        }}

        div[class*="st-key-rosa_desktop_view"] {{
            display: none !important;
        }}

        .rosa-mobile-view {{
            display: block !important;
            width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }}

        .rosa-mobile-table {{
            width: 100% !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            font-size: 10px !important;
            background: #ffffff !important;
        }}

        .rosa-mobile-table th {{
            background: #071a2f !important;
            color: #ffffff !important;
            padding: 7px 3px !important;
            border: 1px solid #cbd5e1 !important;
            font-size: 9px !important;
            line-height: 1.1 !important;
        }}

        .rosa-mobile-table td {{
            color: #0f172a !important;
            padding: 7px 3px !important;
            border: 1px solid #e2e8f0 !important;
            vertical-align: middle !important;
            overflow-wrap: anywhere !important;
            line-height: 1.15 !important;
        }}

        .rosa-mobile-table th:nth-child(1),
        .rosa-mobile-table td:nth-child(1) {{ width: 52% !important; }}
        .rosa-mobile-table th:nth-child(2),
        .rosa-mobile-table td:nth-child(2) {{ width: 24% !important; text-align:center !important; }}
        .rosa-mobile-table th:nth-child(3),
        .rosa-mobile-table td:nth-child(3) {{ width: 24% !important; text-align:center !important; }}

        .rosa-mobile-annulla {{
            display: inline-block !important;
            min-width: 30px !important;
            padding: 5px 6px !important;
            border-radius: 6px !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            font-weight: 800 !important;
            text-align: center !important;
        }}

        /* Tabelle/Dataframe: manteniamo tutti i dati,
           ma consentiamo lo scorrimento orizzontale */
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {{
            overflow-x: auto !important;
            max-width: 100% !important;
        }}

        div[data-testid="stDataFrame"] * {{
            font-size: 11px !important;
        }}

        /* Schede e box */
        .empty-card {{
            padding: 18px 10px !important;
        }}

        .operation-info {{
            min-height: 46px !important;
            font-size: 10px !important;
        }}

        /* ==================================================
           CAMPO MANTRA MOBILE
           ================================================== */

        .module-card {{
            padding: 5px !important;
            margin-bottom: 6px !important;
        }}

        .module-title,
        .module-card-title {{
            font-size: 16px !important;
        }}

        .module-summary,
        .module-card-summary {{
            font-size: 9px !important;
        }}

        .pitch {{
            min-height: auto !important;
            height: auto !important;
            padding: 12px 5px !important;
            border-width: 2px !important;
        }}

        .pitch:after {{
            width: 54px !important;
            height: 54px !important;
        }}

        .pitch-line {{
            flex-wrap: wrap !important;
            gap: 6px !important;
            margin: 18px 0 !important;
            justify-content: center !important;
        }}

        .player-slot {{
            min-width: 112px !important;
            max-width: 155px !important;
            flex: 1 1 112px !important;
            padding: 6px 5px !important;
            border-radius: 6px !important;
        }}

        .slot-code {{
            font-size: 11px !important;
            gap: 4px !important;
            margin-bottom: 4px !important;
        }}

        .slot-coverage {{
            font-size: 10px !important;
        }}

        .player-list {{
            gap: 3px !important;
        }}

        .player-name {{
            font-size: 11px !important;
            line-height: 1.18 !important;
            padding: 4px 5px !important;
        }}

        .slot-empty {{
            font-size: 9px !important;
            padding: 2px 5px !important;
        }}

        /* Dialog più adatti allo smartphone */
        div[data-testid="stDialog"] > div {{
            width: calc(100vw - 1rem) !important;
            max-width: calc(100vw - 1rem) !important;
        }}

        /* Popup/dialog mobile: sfondo chiaro e testo sempre leggibile */
        div[data-testid="stDialog"],
        div[data-testid="stDialog"] > div,
        div[data-testid="stDialog"] section,
        div[role="dialog"],
        div[role="dialog"] > div {{
            background: #ffffff !important;
            color: #0f172a !important;
        }}

        div[data-testid="stDialog"] *,
        div[role="dialog"] * {{
            color: #0f172a !important;
        }}

        /* Titoli, testi, warning, info nei popup */
        div[data-testid="stDialog"] h1,
        div[data-testid="stDialog"] h2,
        div[data-testid="stDialog"] h3,
        div[data-testid="stDialog"] h4,
        div[data-testid="stDialog"] p,
        div[data-testid="stDialog"] label,
        div[role="dialog"] h1,
        div[role="dialog"] h2,
        div[role="dialog"] h3,
        div[role="dialog"] h4,
        div[role="dialog"] p,
        div[role="dialog"] label {{
            color: #0f172a !important;
        }}

        /* Checkbox nei popup */
        div[data-testid="stDialog"] input[type="checkbox"],
        div[role="dialog"] input[type="checkbox"] {{
            accent-color: #071a2f !important;
        }}

        /* Pulsanti popup normali */
        div[data-testid="stDialog"] .stButton > button,
        div[role="dialog"] .stButton > button {{
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        div[data-testid="stDialog"] .stButton > button *,
        div[role="dialog"] .stButton > button * {{
            color: inherit !important;
        }}

        /* Pulsante principale/conferma del popup */
        div[data-testid="stDialog"] button[data-testid="stBaseButton-primary"],
        div[role="dialog"] button[data-testid="stBaseButton-primary"] {{
            background: #071a2f !important;
            color: #ffffff !important;
            border-color: #071a2f !important;
        }}

        div[data-testid="stDialog"] button[data-testid="stBaseButton-primary"] *,
        div[role="dialog"] button[data-testid="stBaseButton-primary"] * {{
            color: #ffffff !important;
        }}

        /* Warning/error/info interni al popup */
        div[data-testid="stDialog"] div[data-testid="stAlert"],
        div[role="dialog"] div[data-testid="stAlert"] {{
            background: #f8fafc !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        div[data-testid="stDialog"] div[data-testid="stAlert"] *,
        div[role="dialog"] div[data-testid="stAlert"] * {{
            color: #0f172a !important;
        }}

        /* Icona X chiusura dialog */
        div[data-testid="stDialog"] button[aria-label="Close"],
        div[role="dialog"] button[aria-label="Close"] {{
            color: #0f172a !important;
            background: #ffffff !important;
        }}

        /* File uploader */
        section[data-testid="stFileUploaderDropzone"] {{
            padding: 0.7rem !important;
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: #cbd5e1 !important;
        }}

        section[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploader"] * {{
            color: #0f172a !important;
        }}

        section[data-testid="stFileUploaderDropzone"] button {{
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }}

        section[data-testid="stFileUploaderDropzone"] button * {{
            color: #0f172a !important;
        }}

        /* Footer */
        .fanta-footer {{
            padding: 8px 10px !important;
            font-size: 9px !important;
        }}
    }}

    @media
    (max-width: 480px) {{

        .fanta-brand-title {{
            font-size: 17px !important;
        }}

        .fanta-brand-subtitle {{
            font-size: 9px !important;
        }}

        .stButton > button,
        .stDownloadButton > button {{
            font-size: 11px !important;
            min-height: 44px !important;
        }}

        .player-slot {{
            min-width: 102px !important;
            max-width: 145px !important;
            flex-basis: 102px !important;
        }}

        .player-name {{
            font-size: 10.5px !important;
        }}

        .pitch-line {{
            margin: 15px 0 !important;
        }}
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RUOLI
# ============================================================

ORDINE_RUOLI = {
    "POR": 1,
    "DC": 2,
    "B": 3,
    "DD": 4,
    "DS": 5,
    "E": 6,
    "M": 7,
    "C": 8,
    "W": 9,
    "T": 10,
    "A": 11,
    "PC": 12
}

ELENCO_RUOLI = [
    "Por",
    "Dc",
    "B",
    "Dd",
    "Ds",
    "E",
    "M",
    "C",
    "W",
    "T",
    "A",
    "Pc"
]


# ============================================================
# DESCRIZIONI POSIZIONI
# ============================================================

DESCRIZIONI_POSIZIONI = {
    "Por": "Portiere",
    "Dc": "Difensore centrale",
    "Dc/B": "Difensore centrale / braccetto",
    "Dd": "Terzino destro",
    "Ds": "Terzino sinistro",
    "E": "Esterno",
    "E/W": "Esterno / ala",
    "M": "Mediano",
    "M/C": "Mediano / centrocampista",
    "C": "Centrocampista",
    "C/T": "Centrocampista / trequartista",
    "W": "Ala",
    "W/T": "Ala / trequartista",
    "W/A": "Ala / attaccante",
    "T": "Trequartista",
    "T/A": "Trequartista / attaccante",
    "T/A/Pc": "Trequartista / attaccante",
    "A": "Attaccante",
    "A/Pc": "Attaccante / punta"
}


# ============================================================
# MODULI
# ============================================================

MODULI = {

    "3-4-3": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("E_SX", "E"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("WA_SX", "W/A"),
            ("APC", "A/Pc"),
            ("WA_DX", "W/A")
        ])
    ],

    "3-4-1-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("E_SX", "E"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("TREQUARTI", [
            ("T", "T")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "3-4-2-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M", "M"),
            ("MC", "M/C"),
            ("E_DX", "E")
        ]),
        ("TREQUARTI", [
            ("T_SX", "T"),
            ("TA_DX", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "3-5-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "3-5-1-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DC_SX", "Dc"),
            ("DC_C", "Dc"),
            ("DC_DX", "Dc/B")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M_SX", "M"),
            ("C", "C"),
            ("M_DX", "M"),
            ("EW_DX", "E/W")
        ]),
        ("TREQUARTI", [
            ("TA", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-3-3": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("CENTROCAMPO", [
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C")
        ]),
        ("ATTACCO", [
            ("WA_SX", "W/A"),
            ("APC", "A/Pc"),
            ("WA_DX", "W/A")
        ])
    ],

    "4-3-1-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("CENTROCAMPO", [
            ("MC", "M/C"),
            ("M", "M"),
            ("C", "C")
        ]),
        ("TREQUARTI", [
            ("T", "T")
        ]),
        ("ATTACCO", [
            ("TAPC", "T/A/Pc"),
            ("APC", "A/Pc")
        ])
    ],

    "4-4-2": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("MC", "M/C"),
            ("C", "C"),
            ("E_DX", "E")
        ]),
        ("ATTACCO", [
            ("APC_SX", "A/Pc"),
            ("APC_DX", "A/Pc")
        ])
    ],

    "4-1-4-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("MEDIANA", [
            ("M", "M")
        ]),
        ("TREQUARTI", [
            ("EW_SX", "E/W"),
            ("CT", "C/T"),
            ("T", "T"),
            ("W_DX", "W")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-4-1-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("CENTROCAMPO", [
            ("EW_SX", "E/W"),
            ("M", "M"),
            ("C", "C"),
            ("EW_DX", "E/W")
        ]),
        ("TREQUARTI", [
            ("TA", "T/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ],

    "4-2-3-1": [
        ("PORTIERE", [
            ("POR", "Por")
        ]),
        ("DIFESA", [
            ("DD", "Dd"),
            ("DC_SX", "Dc"),
            ("DC_DX", "Dc"),
            ("DS", "Ds")
        ]),
        ("MEDIANA", [
            ("M", "M"),
            ("MC", "M/C")
        ]),
        ("TREQUARTI", [
            ("WT_SX", "W/T"),
            ("T", "T"),
            ("WA_DX", "W/A")
        ]),
        ("ATTACCO", [
            ("APC", "A/Pc")
        ])
    ]
}


# ============================================================
# FUNZIONI RUOLI
# ============================================================

def primo_ruolo(ruolo_mantra):

    if ruolo_mantra is None:
        return ""

    ruolo = str(
        ruolo_mantra
    ).strip()

    if ";" in ruolo:
        ruolo = ruolo.split(";")[0].strip()

    return ruolo


def priorita_ruolo(ruolo_mantra):

    return ORDINE_RUOLI.get(
        primo_ruolo(
            ruolo_mantra
        ).upper(),
        999
    )


def ruoli_giocatore(ruolo_mantra):

    if ruolo_mantra is None:
        return set()

    return {
        r.strip().upper()
        for r in str(
            ruolo_mantra
        ).split(";")
        if r.strip()
    }


def ruoli_posizione(posizione):

    return {
        r.strip().upper()
        for r in posizione.split("/")
        if r.strip()
    }


def compatibile(
    ruolo_giocatore,
    posizione
):

    return bool(
        ruoli_giocatore(
            ruolo_giocatore
        ).intersection(
            ruoli_posizione(
                posizione
            )
        )
    )


def e_portiere(ruolo_mantra):

    return (
        "POR"
        in ruoli_giocatore(
            ruolo_mantra
        )
    )


def giocatori_compatibili(
    df_rosa,
    ruolo_posizione
):

    # --------------------------------------------------------
    # SICUREZZA: ROSA ASSENTE
    # --------------------------------------------------------

    if df_rosa is None:

        return pd.DataFrame(
            columns=[
                "Id",
                "R",
                "RM",
                "Nome",
                "Squadra",
                "Qt.A",
                "Qt.I",
                "Diff.",
                "Qt.A M",
                "Qt.I M",
                "Diff.M",
                "FVM",
                "FVM M",
                "Stato",
                "Prezzo"
            ]
        )

    # --------------------------------------------------------
    # SICUREZZA: ROSA VUOTA
    # --------------------------------------------------------

    if df_rosa.empty:

        return df_rosa.copy()

    # --------------------------------------------------------
    # SICUREZZA: COLONNA RM MANCANTE
    # --------------------------------------------------------

    if "RM" not in df_rosa.columns:

        return df_rosa.iloc[
            0:0
        ].copy()

    # --------------------------------------------------------
    # FILTRO COMPATIBILITÀ
    # --------------------------------------------------------

    filtro = df_rosa["RM"].apply(
        lambda x:
        compatibile(
            x,
            ruolo_posizione
        )
    )

    compatibili = (
        df_rosa.loc[
            filtro
        ]
        .copy()
    )

    if compatibili.empty:

        return compatibili

    # --------------------------------------------------------
    # ORDINAMENTO SICURO
    # --------------------------------------------------------

    colonne_ordine = []
    ordine_ascendente = []

    if "FVM" in compatibili.columns:

        colonne_ordine.append(
            "FVM"
        )

        ordine_ascendente.append(
            False
        )

    if "Nome" in compatibili.columns:

        colonne_ordine.append(
            "Nome"
        )

        ordine_ascendente.append(
            True
        )

    if colonne_ordine:

        compatibili = (
            compatibili
            .sort_values(
                by=colonne_ordine,
                ascending=ordine_ascendente,
                na_position="last"
            )
        )

    return compatibili


# ============================================================
# COLORAZIONE NOMI: FVM M + PRIMO RUOLO MANTRA
# ============================================================

SOGLIE_FVM_M = {
    "PC": (110, 70, 40),
    "A": (80, 40, 20),
    "W": (65, 45, 25),
    "T": (85, 45, 20),
    "C": (65, 40, 20),
    "M": (50, 30, 20),
    "E": (80, 25, 15),
    "DS": (25, 15, 10),
    "DD": (25, 15, 10),
    "B": (20, 15, 7),
    "DC": (40, 28, 20),
    "POR": (50, 30, 15)
}

COLORE_VERDE_FVM = "#16a34a"
COLORE_BLU_FVM = "#2563eb"
COLORE_ROSSO_FVM = "#dc2626"
COLORE_NERO_FVM = "#111827"


def colore_fvm_mantra(ruolo_mantra, valore_fvm_m):
    """Usa FVM M e il primo ruolo Mantra (es. Dc;Dd => Dc)."""

    ruolo = primo_ruolo(ruolo_mantra).upper()
    soglie = SOGLIE_FVM_M.get(ruolo)

    if soglie is None:
        return COLORE_NERO_FVM

    try:
        if valore_fvm_m is None or pd.isna(valore_fvm_m):
            return COLORE_NERO_FVM
        valore = float(valore_fvm_m)
    except Exception:
        return COLORE_NERO_FVM

    verde, blu, rosso = soglie

    if valore >= verde:
        return COLORE_VERDE_FVM
    if valore >= blu:
        return COLORE_BLU_FVM
    if valore >= rosso:
        return COLORE_ROSSO_FVM

    return COLORE_NERO_FVM


# ============================================================
# FORMATTAZIONE
# ============================================================

def formatta_crediti(valore):

    try:

        if valore is None:
            return ""

        if pd.isna(valore):
            return ""

        return (
            f"{float(valore):.2f}"
            .replace(".", ",")
        )

    except Exception:

        return ""


# ============================================================
# ECONOMIA
# ============================================================

def calcola_spesa_effettiva(
    valore_acquisti
):

    valore = round(
        float(
            valore_acquisti
            or 0
        ),
        2
    )

    if valore <= SOGLIA_BASE:

        return valore

    eccedenza = round(
        valore
        - SOGLIA_BASE,
        2
    )

    return round(
        SOGLIA_BASE
        + eccedenza * 3,
        2
    )


# ============================================================
# SNAPSHOT AUTOMATICI / RIPRISTINO
# Persistenti anche nella versione Cloud
# ============================================================

TABELLE_SNAPSHOT = [
    "giocatori",
    "costi_svincoli",
    "operazioni"
]


def pulisci_testo_snapshot(
    testo
):

    testo = str(
        testo
        or "OPERAZIONE"
    ).strip()

    caratteri = []

    for carattere in testo:

        if carattere.isalnum():

            caratteri.append(
                carattere
            )

        elif carattere in (
            " ",
            "-",
            "_"
        ):

            caratteri.append(
                "_"
            )

    risultato = "".join(
        caratteri
    )

    while "__" in risultato:

        risultato = (
            risultato.replace(
                "__",
                "_"
            )
        )

    return (
        risultato.strip("_")
        or "OPERAZIONE"
    )


def estrai_tabella_snapshot(
    conn,
    nome_tabella
):

    cur = conn.cursor()

    cur.execute(
        f"SELECT * FROM {nome_tabella}"
    )

    righe = cur.fetchall()

    colonne = [
        descrizione[0]
        for descrizione
        in cur.description
    ]

    return {
        "colonne":
            colonne,

        "righe":
            [
                list(
                    riga
                )
                for riga
                in righe
            ]
    }


def serializza_stato_database(
    conn
):

    contenuto = {
        "versione":
            1,

        "creato_il":
            datetime.now().isoformat(),

        "tabelle":
            {}
    }

    for nome_tabella in (
        TABELLE_SNAPSHOT
    ):

        contenuto[
            "tabelle"
        ][
            nome_tabella
        ] = estrai_tabella_snapshot(
            conn,
            nome_tabella
        )

    return json.dumps(
        contenuto,
        ensure_ascii=False
    )


def elimina_snapshot_eccessivi(
    conn
):

    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM snapshot_archivio
        ORDER BY id DESC
    """)

    ids = [
        riga[0]
        for riga
        in cur.fetchall()
    ]

    da_eliminare = ids[
        MAX_SNAPSHOT:
    ]

    for snapshot_id in (
        da_eliminare
    ):

        cur.execute("""
            DELETE FROM snapshot_archivio
            WHERE id = ?
        """, (
            snapshot_id,
        ))

    conn.commit()


def crea_snapshot_database(
    motivo="MANUALE"
):

    conn = get_connection()

    try:

        stato_json = (
            serializza_stato_database(
                conn
            )
        )

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO snapshot_archivio (
                motivo,
                contenuto_json,
                data_creazione
            )
            VALUES (
                ?, ?,
                CURRENT_TIMESTAMP
            )
        """, (
            pulisci_testo_snapshot(
                motivo
            ),
            stato_json
        ))

        conn.commit()

        elimina_snapshot_eccessivi(
            conn
        )

        try:
            elenco_snapshot.clear()
        except Exception:
            pass

        return True

    finally:

        chiudi_connessione(conn)


@st.cache_data(show_spinner=False)
def elenco_snapshot():

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                motivo,
                data_creazione

            FROM snapshot_archivio

            ORDER BY id DESC

            LIMIT ?
        """, (
            MAX_SNAPSHOT,
        ))

        righe = cur.fetchall()

        risultato = []

        for riga in righe:

            snapshot_id = (
                riga[0]
            )

            motivo = str(
                riga[1]
                or "SNAPSHOT"
            )

            data_raw = str(
                riga[2]
                or ""
            )

            data_testo = (
                data_raw
            )

            try:

                data_ora = (
                    datetime.fromisoformat(
                        data_raw.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                data_testo = (
                    data_ora.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                )

            except Exception:

                pass

            risultato.append({
                "id":
                    snapshot_id,

                "path":
                    snapshot_id,

                "file":
                    f"snapshot_{snapshot_id}",

                "data":
                    data_testo,

                "motivo":
                    motivo.replace(
                        "_",
                        " "
                    )
            })

        return risultato

    finally:

        chiudi_connessione(conn)


def ripristina_snapshot_database(
    snapshot_id
):

    # Prima salviamo sempre lo stato corrente.
    crea_snapshot_database(
        "PRIMA_DEL_RIPRISTINO"
    )

    conn = get_connection()

    try:

        cur = conn.cursor()

        cur.execute("""
            SELECT contenuto_json
            FROM snapshot_archivio
            WHERE id = ?
        """, (
            int(
                snapshot_id
            ),
        ))

        riga = cur.fetchone()

        if riga is None:

            raise FileNotFoundError(
                "Snapshot non trovato."
            )

        contenuto = json.loads(
            riga[0]
        )

        tabelle = contenuto.get(
            "tabelle",
            {}
        )

        # Svuotiamo prima le tabelle operative.
        # L'archivio snapshot NON viene cancellato.
        for nome_tabella in [
            "costi_svincoli",
            "operazioni",
            "giocatori"
        ]:

            cur.execute(
                f"DELETE FROM {nome_tabella}"
            )

        # Ripristino dei dati.
        for nome_tabella in (
            TABELLE_SNAPSHOT
        ):

            dati = tabelle.get(
                nome_tabella
            )

            if not dati:

                continue

            colonne = dati.get(
                "colonne",
                []
            )

            righe = dati.get(
                "righe",
                []
            )

            if (
                not colonne
                or not righe
            ):

                continue

            elenco_colonne = (
                ", ".join(
                    colonne
                )
            )

            placeholders = (
                ", ".join(
                    [
                        "?"
                        for _ in colonne
                    ]
                )
            )

            query = (
                f"INSERT INTO "
                f"{nome_tabella} "
                f"({elenco_colonne}) "
                f"VALUES "
                f"({placeholders})"
            )

            for valori in righe:

                cur.execute(
                    query,
                    tuple(
                        valori
                    )
                )

        conn.commit()

        invalida_cache_dati()

        return True

    finally:

        chiudi_connessione(conn)


def crea_backup_logico_bytes():

    conn = get_connection()

    try:

        contenuto = (
            serializza_stato_database(
                conn
            )
        )

        return contenuto.encode(
            "utf-8"
        )

    finally:

        chiudi_connessione(conn)


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    if USA_DATABASE_CLOUD:

        try:

            import libsql

        except ImportError as errore:

            raise RuntimeError(
                "La modalità Cloud richiede il pacchetto libsql. "
                "Installa le dipendenze da requirements.txt."
            ) from errore

        # Riutilizza la stessa connessione durante tutta la sessione.
        # Evita handshake/connessioni remote ripetute a ogni operazione.
        chiave = "_turso_connessione"

        conn = st.session_state.get(
            chiave
        )

        if conn is None:

            conn = libsql.connect(
                database=(
                    TURSO_DATABASE_URL
                ),
                auth_token=(
                    TURSO_AUTH_TOKEN
                )
            )

            st.session_state[
                chiave
            ] = conn

        return conn

    return sqlite3.connect(
        DB_PATH
    )


def chiudi_connessione(
    conn
):

    # In Cloud la connessione viene mantenuta viva per la sessione.
    # In locale continuiamo a chiuderla normalmente.
    if USA_DATABASE_CLOUD:
        return

    try:
        chiudi_connessione(conn)
    except Exception:
        pass


@st.cache_resource(show_spinner=False)
def inizializza_database():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS giocatori (

            id INTEGER PRIMARY KEY,

            ruolo_classico TEXT,
            ruolo_mantra TEXT,

            nome TEXT NOT NULL,
            squadra TEXT,

            quotazione_attuale REAL,
            quotazione_iniziale REAL,
            differenza REAL,

            quotazione_attuale_mantra REAL,
            quotazione_iniziale_mantra REAL,
            differenza_mantra REAL,

            fvm REAL,
            fvm_mantra REAL,

            stato TEXT
                DEFAULT 'DISPONIBILE',

            prezzo_acquisto REAL
                DEFAULT NULL,

            ultimo_aggiornamento TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS costi_svincoli (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            operazione_id INTEGER,

            giocatore_id INTEGER,

            nome_giocatore TEXT,

            importo REAL NOT NULL,

            data_operazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS operazioni (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            tipo TEXT NOT NULL,

            giocatore_id INTEGER NOT NULL,

            nome_giocatore TEXT,

            stato_prima TEXT,

            prezzo_prima REAL,

            stato_dopo TEXT,

            prezzo_dopo REAL,

            costo_svincolo REAL
                DEFAULT 0,

            data_operazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_archivio (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            motivo TEXT NOT NULL,

            contenuto_json TEXT NOT NULL,

            data_creazione TEXT
                DEFAULT CURRENT_TIMESTAMP
        )
    """)


    cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_operazioni_post_insert

        AFTER INSERT ON operazioni

        BEGIN

            INSERT INTO costi_svincoli (
                operazione_id,
                giocatore_id,
                nome_giocatore,
                importo
            )

            SELECT
                NEW.id,
                NEW.giocatore_id,
                NEW.nome_giocatore,
                NEW.costo_svincolo

            WHERE NEW.costo_svincolo > 0;

            DELETE FROM operazioni

            WHERE id NOT IN (
                SELECT id
                FROM operazioni
                ORDER BY id DESC
                LIMIT 10
            );

        END
    """)

    colonne = {
        r[1]
        for r in cur.execute(
            "PRAGMA table_info(giocatori)"
        ).fetchall()
    }

    if "stato" not in colonne:

        cur.execute("""
            ALTER TABLE giocatori
            ADD COLUMN stato TEXT
            DEFAULT 'DISPONIBILE'
        """)

    if "prezzo_acquisto" not in colonne:

        cur.execute("""
            ALTER TABLE giocatori
            ADD COLUMN prezzo_acquisto REAL
            DEFAULT NULL
        """)

    cur.execute("""
        UPDATE giocatori

        SET stato = 'DISPONIBILE'

        WHERE stato IS NULL
           OR TRIM(stato) = ''
    """)

    conn.commit()
    chiudi_connessione(conn)


# ============================================================
# IMPORT LISTONE
# ============================================================

def importa_listone_nel_database(df):

    """
    Importazione ottimizzata per database Cloud.

    Obiettivi:
    - evitare centinaia di round-trip verso Turso;
    - aggiornare solo i giocatori realmente cambiati;
    - eseguire UPSERT multi-riga a blocchi;
    - mantenere stato e prezzo dei giocatori già presenti.
    """

    # L'import del listone può coinvolgere centinaia di righe.
    # Per mantenere l'operazione veloce sul Cloud NON creiamo
    # automaticamente uno snapshot completo qui.
    #
    # Se serve un punto di sicurezza, usa il pulsante Snapshot
    # prima di caricare il nuovo listone.

    conn = get_connection()
    cur = conn.cursor()

    def pulisci_valore(
        valore
    ):

        if valore is None:
            return None

        try:
            if pd.isna(
                valore
            ):
                return None
        except Exception:
            pass

        return valore

    def normalizza_numero(
        valore
    ):

        valore = pulisci_valore(
            valore
        )

        if valore is None:
            return None

        try:
            return float(
                valore
            )
        except Exception:
            return valore

    try:

        # ----------------------------------------------------
        # 1. UNA SOLA LETTURA DELLO STATO ATTUALE
        # ----------------------------------------------------

        cur.execute("""
            SELECT
                id,
                ruolo_classico,
                ruolo_mantra,
                nome,
                squadra,
                quotazione_attuale,
                quotazione_iniziale,
                differenza,
                quotazione_attuale_mantra,
                quotazione_iniziale_mantra,
                differenza_mantra,
                fvm,
                fvm_mantra

            FROM giocatori
        """)

        esistenti = {}

        for riga in cur.fetchall():

            giocatore_id = int(
                riga[0]
            )

            esistenti[
                giocatore_id
            ] = (
                str(
                    riga[1]
                    or ""
                ).strip(),

                str(
                    riga[2]
                    or ""
                ).strip(),

                str(
                    riga[3]
                    or ""
                ).strip(),

                str(
                    riga[4]
                    or ""
                ).strip(),

                normalizza_numero(
                    riga[5]
                ),

                normalizza_numero(
                    riga[6]
                ),

                normalizza_numero(
                    riga[7]
                ),

                normalizza_numero(
                    riga[8]
                ),

                normalizza_numero(
                    riga[9]
                ),

                normalizza_numero(
                    riga[10]
                ),

                normalizza_numero(
                    riga[11]
                ),

                normalizza_numero(
                    riga[12]
                )
            )

        # ----------------------------------------------------
        # 2. PREPARAZIONE LOCALE: NESSUNA QUERY PER GIOCATORE
        # ----------------------------------------------------

        da_scrivere = []
        nuovi = 0
        aggiornati = 0

        for _, row in df.iterrows():

            try:

                giocatore_id = int(
                    row[
                        "Id"
                    ]
                )

            except Exception:

                continue

            nome = str(
                row.get(
                    "Nome",
                    ""
                )
                or ""
            ).strip()

            if not nome:
                continue

            dati_confronto = (
                str(
                    row.get(
                        "R",
                        ""
                    )
                    or ""
                ).strip(),

                str(
                    row.get(
                        "RM",
                        ""
                    )
                    or ""
                ).strip(),

                nome,

                str(
                    row.get(
                        "Squadra",
                        ""
                    )
                    or ""
                ).strip(),

                normalizza_numero(
                    row.get(
                        "Qt.A"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.I"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Diff."
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.A M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Qt.I M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "Diff.M"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "FVM"
                    )
                ),

                normalizza_numero(
                    row.get(
                        "FVM M"
                    )
                )
            )

            precedente = (
                esistenti.get(
                    giocatore_id
                )
            )

            if precedente is None:

                nuovi += 1

            elif precedente == dati_confronto:

                # Giocatore identico: nessuna scrittura Cloud.
                continue

            else:

                aggiornati += 1

            da_scrivere.append(
                (
                    giocatore_id,
                    *dati_confronto
                )
            )

        # ----------------------------------------------------
        # 3. UPSERT MULTI-RIGA A BLOCCHI
        # ----------------------------------------------------
        #
        # 13 parametri per giocatore.
        # 50 giocatori = 650 parametri per query:
        # abbastanza piccolo per restare compatibile e riduce
        # enormemente i round-trip verso Turso.

        DIMENSIONE_BLOCCO = 50

        colonne = """
            id,
            ruolo_classico,
            ruolo_mantra,
            nome,
            squadra,
            quotazione_attuale,
            quotazione_iniziale,
            differenza,
            quotazione_attuale_mantra,
            quotazione_iniziale_mantra,
            differenza_mantra,
            fvm,
            fvm_mantra
        """

        update_sql = """
            ruolo_classico = excluded.ruolo_classico,
            ruolo_mantra = excluded.ruolo_mantra,
            nome = excluded.nome,
            squadra = excluded.squadra,
            quotazione_attuale = excluded.quotazione_attuale,
            quotazione_iniziale = excluded.quotazione_iniziale,
            differenza = excluded.differenza,
            quotazione_attuale_mantra = excluded.quotazione_attuale_mantra,
            quotazione_iniziale_mantra = excluded.quotazione_iniziale_mantra,
            differenza_mantra = excluded.differenza_mantra,
            fvm = excluded.fvm,
            fvm_mantra = excluded.fvm_mantra,
            ultimo_aggiornamento = CURRENT_TIMESTAMP
        """

        for inizio in range(
            0,
            len(
                da_scrivere
            ),
            DIMENSIONE_BLOCCO
        ):

            blocco = da_scrivere[
                inizio:
                inizio
                + DIMENSIONE_BLOCCO
            ]

            if not blocco:
                continue

            placeholders_riga = (
                "("
                + ", ".join(
                    [
                        "?"
                        for _ in range(
                            13
                        )
                    ]
                )
                + ")"
            )

            placeholders = ", ".join(
                [
                    placeholders_riga
                    for _ in blocco
                ]
            )

            parametri = []

            for valori in blocco:

                parametri.extend(
                    valori
                )

            query = f"""
                INSERT INTO giocatori (
                    {colonne}
                )

                VALUES
                    {placeholders}

                ON CONFLICT(id) DO UPDATE SET
                    {update_sql}
            """

            cur.execute(
                query,
                tuple(
                    parametri
                )
            )

        # Un solo commit finale.
        conn.commit()

    finally:

        chiudi_connessione(
            conn
        )

    # Ricaricheremo i dati una sola volta dopo l'import.
    invalida_cache_dati()

    # Memorizza data e ora dell'ultimo upload completato con successo.
    st.session_state[
        "ultimo_upload_listone"
    ] = datetime.now(
        ZoneInfo(
            "Europe/Rome"
        )
    ).strftime(
        "%d/%m/%Y alle %H:%M:%S"
    )

    return (
        nuovi,
        aggiornati
    )


# ============================================================
# LETTURA DATABASE
# ============================================================

def carica_tutti_giocatori():

    chiave = "_df_giocatori_sessione"

    if chiave in st.session_state:

        return (
            st.session_state[
                chiave
            ].copy()
        )

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT

            id AS Id,

            ruolo_classico AS R,
            ruolo_mantra AS RM,

            nome AS Nome,
            squadra AS Squadra,

            quotazione_attuale
                AS "Qt.A",

            quotazione_iniziale
                AS "Qt.I",

            differenza
                AS "Diff.",

            quotazione_attuale_mantra
                AS "Qt.A M",

            quotazione_iniziale_mantra
                AS "Qt.I M",

            differenza_mantra
                AS "Diff.M",

            fvm AS FVM,

            fvm_mantra
                AS "FVM M",

            stato AS Stato,

            prezzo_acquisto
                AS Prezzo

        FROM giocatori
    """, conn)

    chiudi_connessione(
        conn
    )

    st.session_state[
        chiave
    ] = df.copy()

    return df


# ============================================================
# OPERAZIONI
# ============================================================

def esegui_operazione(
    giocatore_id,
    tipo,
    nuovo_stato,
    nuovo_prezzo=None,
    costo_svincolo=0
):

    # Recupera lo stato precedente dalla copia già in memoria.
    # Nessuna SELECT remota aggiuntiva.
    df_corrente = (
        carica_tutti_giocatori()
    )

    riga = df_corrente[
        df_corrente["Id"]
        == int(
            giocatore_id
        )
    ]

    if riga.empty:
        return

    precedente = riga.iloc[0]

    nome = precedente[
        "Nome"
    ]

    stato_prima = precedente[
        "Stato"
    ]

    prezzo_prima = precedente[
        "Prezzo"
    ]

    conn = get_connection()
    cur = conn.cursor()

    # Prima registriamo la cronologia:
    # il trigger gestisce automaticamente
    # eventuale costo svincolo e limite 10 operazioni.
    cur.execute("""
        INSERT INTO operazioni (

            tipo,
            giocatore_id,
            nome_giocatore,

            stato_prima,
            prezzo_prima,

            stato_dopo,
            prezzo_dopo,

            costo_svincolo
        )

        VALUES (
            ?, ?, ?,
            ?, ?,
            ?, ?,
            ?
        )
    """, (
        tipo,
        int(
            giocatore_id
        ),
        nome,

        stato_prima,
        (
            None
            if pd.isna(
                prezzo_prima
            )
            else float(
                prezzo_prima
            )
        ),

        nuovo_stato,
        nuovo_prezzo,

        float(
            costo_svincolo
            or 0
        )
    ))

    cur.execute("""
        UPDATE giocatori

        SET
            stato = ?,
            prezzo_acquisto = ?

        WHERE id = ?
    """, (
        nuovo_stato,
        nuovo_prezzo,
        int(
            giocatore_id
        )
    ))

    conn.commit()

    chiudi_connessione(
        conn
    )

    # Aggiorna subito la copia locale:
    # il rerun non deve rileggere tutti i 500+ giocatori da Turso.
    maschera = (
        st.session_state[
            "_df_giocatori_sessione"
        ]["Id"]
        == int(
            giocatore_id
        )
    )

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Stato"
    ] = nuovo_stato

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Prezzo"
    ] = nuovo_prezzo

    # Aggiorniamo soltanto le cache secondarie.
    try:
        carica_ultime_operazioni.clear()
    except Exception:
        pass

    try:
        calcola_costi_svincoli.clear()
    except Exception:
        pass

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None


@st.cache_data(show_spinner=False)
def carica_ultime_operazioni():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT

            id AS Id,

            tipo AS Operazione,

            giocatore_id
                AS GiocatoreId,

            nome_giocatore
                AS Giocatore,

            stato_prima
                AS StatoPrima,

            prezzo_prima
                AS PrezzoPrima,

            stato_dopo
                AS StatoDopo,

            prezzo_dopo
                AS PrezzoDopo,

            costo_svincolo
                AS CostoSvincolo,

            data_operazione
                AS Data

        FROM operazioni

        ORDER BY id DESC

        LIMIT 10
    """, conn)

    chiudi_connessione(conn)

    return df


def annulla_ultima_operazione():

    operazioni = (
        carica_ultime_operazioni()
    )

    if operazioni.empty:
        return False

    ultima = operazioni.iloc[0]

    operazione_id = int(
        ultima["Id"]
    )

    giocatore_id = int(
        ultima["GiocatoreId"]
    )

    stato_prima = ultima[
        "StatoPrima"
    ]

    prezzo_prima = ultima[
        "PrezzoPrima"
    ]

    costo_svincolo = float(
        ultima[
            "CostoSvincolo"
        ]
        or 0
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE giocatori

        SET
            stato = ?,
            prezzo_acquisto = ?

        WHERE id = ?
    """, (
        stato_prima,
        (
            None
            if pd.isna(
                prezzo_prima
            )
            else float(
                prezzo_prima
            )
        ),
        giocatore_id
    ))

    if costo_svincolo > 0:

        cur.execute("""
            DELETE FROM costi_svincoli

            WHERE operazione_id = ?
        """, (
            operazione_id,
        ))

    cur.execute("""
        DELETE FROM operazioni

        WHERE id = ?
    """, (
        operazione_id,
    ))

    conn.commit()

    chiudi_connessione(
        conn
    )

    # Aggiorna subito la copia in memoria.
    df_sessione = (
        carica_tutti_giocatori()
    )

    maschera = (
        df_sessione["Id"]
        == giocatore_id
    )

    df_sessione.loc[
        maschera,
        "Stato"
    ] = stato_prima

    df_sessione.loc[
        maschera,
        "Prezzo"
    ] = (
        None
        if pd.isna(
            prezzo_prima
        )
        else float(
            prezzo_prima
        )
    )

    st.session_state[
        "_df_giocatori_sessione"
    ] = df_sessione

    try:
        carica_ultime_operazioni.clear()
    except Exception:
        pass

    try:
        calcola_costi_svincoli.clear()
    except Exception:
        pass

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    return True


def elimina_tutta_la_rosa():
    df_corrente = carica_tutti_giocatori()
    rosa = df_corrente[df_corrente["Stato"] == "MIO"].copy()
    if rosa.empty:
        return 0

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE giocatori
        SET stato = 'DISPONIBILE',
            prezzo_acquisto = NULL
        WHERE stato = 'MIO'
    """)
    cur.execute("DELETE FROM costi_svincoli")
    cur.execute("DELETE FROM operazioni")
    conn.commit()
    chiudi_connessione(conn)

    if "_df_giocatori_sessione" in st.session_state:
        df_sessione = st.session_state["_df_giocatori_sessione"]
        mask = df_sessione["Stato"] == "MIO"
        df_sessione.loc[mask, "Stato"] = "DISPONIBILE"
        df_sessione.loc[mask, "Prezzo"] = None
        st.session_state["_df_giocatori_sessione"] = df_sessione

    try:
        carica_ultime_operazioni.clear()
    except Exception:
        pass
    try:
        calcola_costi_svincoli.clear()
    except Exception:
        pass

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    return int(len(rosa))


# ============================================================
# ECONOMIA DATABASE
# ============================================================

def calcola_valore_acquisti_attivi():

    df = carica_tutti_giocatori()

    if (
        df is None
        or df.empty
        or "Stato" not in df.columns
        or "Prezzo" not in df.columns
    ):
        return 0.0

    prezzi = pd.to_numeric(
        df.loc[
            df["Stato"] == "MIO",
            "Prezzo"
        ],
        errors="coerce"
    ).fillna(0)

    return round(
        float(
            prezzi.sum()
        ),
        2
    )


@st.cache_data(show_spinner=False)
def calcola_costi_svincoli():

    conn = get_connection()

    risultato = pd.read_sql_query("""
        SELECT
            COALESCE(
                SUM(importo),
                0
            ) AS totale

        FROM costi_svincoli
    """, conn)

    chiudi_connessione(conn)

    return round(
        float(
            risultato.iloc[0]["totale"]
            or 0
        ),
        2
    )


def calcola_valore_acquisti_totale():

    return round(
        calcola_valore_acquisti_attivi()
        + calcola_costi_svincoli(),
        2
    )


# ============================================================
# CACHE DATI CLOUD
# ============================================================

def invalida_cache_dati():

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

    if "_df_giocatori_sessione" in st.session_state:
        del st.session_state[
            "_df_giocatori_sessione"
        ]

    try:
        carica_ultime_operazioni.clear()
    except Exception:
        pass

    try:
        calcola_costi_svincoli.clear()
    except Exception:
        pass

    try:
        elenco_snapshot.clear()
    except Exception:
        pass


# ============================================================
# PDF - ROSA E MODULI
# ============================================================

def genera_pdf_rosa_e_moduli(
    df_rosa,
    valore_attivi,
    costi_svincoli,
    valore_acquisti,
    spesa_effettiva
):
    """
    Genera un PDF scaricabile con:
    - rosa completa e tutti i dati disponibili;
    - riepilogo economico;
    - classifica dei moduli;
    - tutti i moduli Mantra con ruoli, copertura e giocatori compatibili.
    """

    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
            KeepTogether
        )
    except ImportError as errore:
        raise RuntimeError(
            "Per creare il PDF è necessario il pacchetto reportlab. "
            "Aggiungi 'reportlab>=4.0,<5' al file requirements.txt."
        ) from errore

    buffer = io.BytesIO()

    pagina = landscape(
        A4
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagina,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title="FANTAELEGANZA 26/27 - Rosa e Moduli",
        author="FANTAELEGANZA 26/27"
    )

    styles = getSampleStyleSheet()

    stile_titolo = ParagraphStyle(
        "TitoloFanta",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=colors.HexColor("#071a2f"),
        alignment=TA_CENTER,
        spaceAfter=7
    )

    stile_sottotitolo = ParagraphStyle(
        "SottotitoloFanta",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#071a2f"),
        spaceBefore=4,
        spaceAfter=5
    )

    stile_testo = ParagraphStyle(
        "TestoFanta",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#111827")
    )

    stile_piccolo = ParagraphStyle(
        "PiccoloFanta",
        parent=stile_testo,
        fontSize=6.7,
        leading=8
    )

    stile_slot = ParagraphStyle(
        "SlotFanta",
        parent=stile_piccolo,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827")
    )

    elementi = []

    # --------------------------------------------------------
    # TESTATA
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "FANTAELEGANZA 26/27",
            stile_titolo
        )
    )

    elementi.append(
        Paragraph(
            "Rosa e moduli Mantra",
            ParagraphStyle(
                "SubTitle",
                parent=stile_testo,
                alignment=TA_CENTER,
                fontSize=10,
                leading=12,
                textColor=colors.HexColor("#64748b")
            )
        )
    )

    elementi.append(
        Paragraph(
            "Generato il "
            + datetime.now().strftime(
                "%d/%m/%Y alle %H:%M"
            ),
            ParagraphStyle(
                "DataPDF",
                parent=stile_piccolo,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#64748b")
            )
        )
    )

    elementi.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # --------------------------------------------------------
    # RIEPILOGO ECONOMICO
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "Riepilogo economico",
            stile_sottotitolo
        )
    )

    dati_economia = [
        [
            "Giocatori in rosa",
            "Valore acquisti attivi",
            "Costi svincoli",
            "Valore totale asta",
            "Spesa effettiva"
        ],
        [
            str(
                len(
                    df_rosa
                )
            ),
            f"{formatta_crediti(valore_attivi)} EUR",
            f"{formatta_crediti(costi_svincoli)} EUR",
            f"{formatta_crediti(valore_acquisti)} EUR",
            f"{formatta_crediti(spesa_effettiva)} EUR"
        ]
    ]

    tab_economia = Table(
        dati_economia,
        colWidths=[
            40 * mm,
            40 * mm,
            40 * mm,
            40 * mm,
            40 * mm
        ]
    )

    tab_economia.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#f8fafc")
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementi.append(
        tab_economia
    )

    elementi.append(
        Spacer(
            1,
            5 * mm
        )
    )

    # --------------------------------------------------------
    # ROSA COMPLETA
    # --------------------------------------------------------

    elementi.append(
        Paragraph(
            "Rosa - dati completi",
            stile_sottotitolo
        )
    )

    colonne_pdf = [
        "Id",
        "R",
        "RM",
        "Nome",
        "Squadra",
        "Qt.A",
        "Qt.I",
        "Diff.",
        "Qt.A M",
        "Qt.I M",
        "Diff.M",
        "FVM",
        "FVM M",
        "Prezzo"
    ]

    intestazioni = [
        "ID",
        "R",
        "RM",
        "NOME",
        "SQUADRA",
        "QT.A",
        "QT.I",
        "DIFF",
        "QT.A M",
        "QT.I M",
        "DIFF.M",
        "FVM",
        "FVM M",
        "PREZZO"
    ]

    dati_rosa = [
        intestazioni
    ]

    if not df_rosa.empty:

        rosa_pdf = (
            df_rosa.copy()
        )

        rosa_pdf[
            "_ordine_ruolo"
        ] = (
            rosa_pdf["RM"]
            .apply(
                priorita_ruolo
            )
        )

        rosa_pdf = (
            rosa_pdf
            .sort_values(
                [
                    "_ordine_ruolo",
                    "Nome"
                ]
            )
        )

        for _, riga in (
            rosa_pdf.iterrows()
        ):

            riga_pdf = []

            for colonna in (
                colonne_pdf
            ):

                valore = (
                    riga.get(
                        colonna,
                        ""
                    )
                )

                if pd.isna(
                    valore
                ):
                    valore = ""

                if colonna == "Prezzo":
                    valore = (
                        formatta_crediti(
                            valore
                        )
                        if valore != ""
                        else ""
                    )

                elif colonna in (
                    "Qt.A",
                    "Qt.I",
                    "Diff.",
                    "Qt.A M",
                    "Qt.I M",
                    "Diff.M",
                    "FVM",
                    "FVM M"
                ):

                    try:
                        valore = (
                            f"{float(valore):g}"
                            if valore != ""
                            else ""
                        )
                    except Exception:
                        pass

                riga_pdf.append(
                    Paragraph(
                        html.escape(
                            str(
                                valore
                            )
                        ),
                        stile_piccolo
                    )
                )

            dati_rosa.append(
                riga_pdf
            )

    larghezze = [
        9 * mm,
        10 * mm,
        18 * mm,
        31 * mm,
        23 * mm,
        14 * mm,
        14 * mm,
        13 * mm,
        16 * mm,
        16 * mm,
        14 * mm,
        14 * mm,
        16 * mm,
        18 * mm
    ]

    tab_rosa = Table(
        dati_rosa,
        colWidths=larghezze,
        repeatRows=1
    )

    tab_rosa.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, 0),
                6
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.25,
                colors.HexColor("#cbd5e1")
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f8fafc")
                ]
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            )
        ])
    )

    elementi.append(
        tab_rosa
    )

    # --------------------------------------------------------
    # CLASSIFICA MODULI
    # --------------------------------------------------------

    elementi.append(
        PageBreak()
    )

    elementi.append(
        Paragraph(
            "Classifica moduli",
            stile_titolo
        )
    )

    classifica = (
        classifica_moduli(
            df_rosa
        )
    )

    dati_classifica = [[
        "POS.",
        "MODULO",
        "PUNTEGGIO",
        "COPERTURA MEDIA",
        "SCOPERTI",
        "SOTTO 60%",
        "AL 100%"
    ]]

    for riga in classifica:

        dati_classifica.append([
            riga[
                "Posizione"
            ],
            riga[
                "Modulo"
            ],
            f"{riga['Punteggio']}/100",
            f"{riga['Copertura media']}%",
            riga[
                "Scoperti"
            ],
            riga[
                "Sotto 60%"
            ],
            riga[
                "Al 100%"
            ]
        ])

    tab_classifica = Table(
        dati_classifica,
        colWidths=[
            18 * mm,
            30 * mm,
            32 * mm,
            38 * mm,
            27 * mm,
            30 * mm,
            27 * mm
        ]
    )

    tab_classifica.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#071a2f")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold"
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.HexColor("#fef3c7")
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    elementi.append(
        tab_classifica
    )

    # --------------------------------------------------------
    # TUTTI I MODULI
    # --------------------------------------------------------

    for nome_modulo in (
        MODULI.keys()
    ):

        elementi.append(
            PageBreak()
        )

        analisi = (
            analizza_modulo(
                df_rosa,
                nome_modulo
            )
        )

        ruoli_al_100, totale_slot, copertura_media = (
            calcola_copertura_modulo(
                df_rosa,
                nome_modulo
            )
        )

        elementi.append(
            Paragraph(
                f"Modulo {html.escape(nome_modulo)}",
                stile_titolo
            )
        )

        elementi.append(
            Paragraph(
                (
                    f"Punteggio strategico: "
                    f"<b>{analisi['Punteggio']}/100</b> &nbsp;&nbsp; "
                    f"Copertura media: "
                    f"<b>{round(copertura_media)}%</b> &nbsp;&nbsp; "
                    f"Ruoli al 100%: "
                    f"<b>{ruoli_al_100}/{totale_slot}</b> &nbsp;&nbsp; "
                    f"Slot scoperti: "
                    f"<b>{analisi['Scoperti']}</b>"
                ),
                ParagraphStyle(
                    "ModuloSummary",
                    parent=stile_testo,
                    alignment=TA_CENTER,
                    fontSize=8.5,
                    leading=11,
                    spaceAfter=5
                )
            )
        )

        contenuto_campo = []

        righe_modulo = (
            MODULI[
                nome_modulo
            ]
        )

        # Attacco in alto, portiere in basso.
        for _, posizioni in reversed(
            righe_modulo
        ):

            celle = []

            numero_posizioni = (
                len(
                    posizioni
                )
            )

            larghezza_cella = (
                247 * mm
                / max(
                    1,
                    numero_posizioni
                )
            )

            for _, ruolo_slot in (
                posizioni
            ):

                possibili = (
                    giocatori_compatibili(
                        df_rosa,
                        ruolo_slot
                    )
                )

                _, percentuale_ruolo = (
                    percentuale_copertura_ruolo(
                        df_rosa,
                        ruolo_slot
                    )
                )

                colore_percentuale = (
                    "#dc2626"
                    if percentuale_ruolo < 60
                    else "#111827"
                )

                parti = [
                    (
                        f"<b>{html.escape(str(ruolo_slot))}</b> "
                        f"<font color='{colore_percentuale}'>"
                        f"<b>{round(percentuale_ruolo)}%</b>"
                        f"</font>"
                    )
                ]

                if possibili.empty:

                    parti.append(
                        "<font color='#dc2626'>-</font>"
                    )

                else:

                    for _, giocatore in (
                        possibili.iterrows()
                    ):

                        nome = html.escape(
                            str(
                                giocatore.get(
                                    "Nome",
                                    ""
                                )
                            )
                        )

                        ruoli_testo = html.escape(
                            str(
                                giocatore.get(
                                    "RM",
                                    ""
                                )
                            )
                        )

                        colore_nome = (
                            colore_fvm_mantra(
                                giocatore.get(
                                    "RM",
                                    ""
                                ),
                                giocatore.get(
                                    "FVM M"
                                )
                            )
                        )

                        parti.append(
                            (
                                f"<font color='{colore_nome}'>"
                                f"{nome} ({ruoli_testo})"
                                f"</font>"
                            )
                        )

                celle.append(
                    Paragraph(
                        "<br/>".join(
                            parti
                        ),
                        stile_slot
                    )
                )

            tab_linea = Table(
                [
                    celle
                ],
                colWidths=[
                    larghezza_cella
                    for _ in celle
                ]
            )

            tab_linea.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#ffffff")
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.HexColor("#e2e8f0")
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#e2e8f0")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    )
                ])
            )

            contenuto_campo.append(
                tab_linea
            )

            contenuto_campo.append(
                Spacer(
                    1,
                    3 * mm
                )
            )

        campo = Table(
            [
                [
                    contenuto_campo
                ]
            ],
            colWidths=[
                260 * mm
            ]
        )

        campo.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#16833a")
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1.2,
                    colors.white
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7 * mm
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm
                )
            ])
        )

        elementi.append(
            campo
        )

    # --------------------------------------------------------
    # NUMERO PAGINA
    # --------------------------------------------------------

    def aggiungi_numero_pagina(
        canvas,
        documento
    ):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7
        )

        canvas.setFillColor(
            colors.HexColor(
                "#64748b"
            )
        )

        canvas.drawRightString(
            pagina[0]
            - 10 * mm,
            5 * mm,
            f"FANTAELEGANZA 26/27 - Pagina {documento.page}"
        )

        canvas.restoreState()

    doc.build(
        elementi,
        onFirstPage=aggiungi_numero_pagina,
        onLaterPages=aggiungi_numero_pagina
    )

    buffer.seek(
        0
    )

    return buffer.getvalue()


# ============================================================
# REGOLE ROSA
# ============================================================

def conta_portieri(df_rosa):

    if df_rosa is None:
        return 0

    if df_rosa.empty:
        return 0

    if "RM" not in df_rosa.columns:
        return 0

    return int(
        df_rosa["RM"]
        .apply(
            e_portiere
        )
        .sum()
    )


def verifica_acquisto_regole(
    df_rosa,
    nuovo_ruolo
):

    numero_attuale = len(
        df_rosa
    )

    portieri_attuali = (
        conta_portieri(
            df_rosa
        )
    )

    if numero_attuale >= MAX_GIOCATORI:

        return (
            False,
            "La rosa ha già raggiunto "
            f"il limite di {MAX_GIOCATORI} giocatori."
        )

    nuovo_e_portiere = (
        e_portiere(
            nuovo_ruolo
        )
    )

    numero_dopo = (
        numero_attuale
        + 1
    )

    portieri_dopo = (
        portieri_attuali
        + (
            1
            if nuovo_e_portiere
            else 0
        )
    )

    slot_rimanenti = (
        MAX_GIOCATORI
        - numero_dopo
    )

    portieri_necessari = max(
        0,
        MIN_PORTIERI
        - portieri_dopo
    )

    if (
        slot_rimanenti
        < portieri_necessari
    ):

        return (
            False,
            "Gli slot rimanenti devono "
            "essere riservati ai portieri."
        )

    return (
        True,
        ""
    )


# ============================================================
# COPERTURA RUOLO / MODULO
# ============================================================

def percentuale_copertura_ruolo(
    df_rosa,
    ruolo_posizione
):
    """
    100% = almeno 4 giocatori compatibili con quel ruolo/slot.
    La percentuale cresce linearmente:
    0 giocatori = 0%
    1 giocatore  = 25%
    2 giocatori  = 50%
    3 giocatori  = 75%
    4 o più      = 100%
    """

    possibili = giocatori_compatibili(
        df_rosa,
        ruolo_posizione
    )

    numero = len(
        possibili
    )

    percentuale = min(
        100.0,
        (
            numero
            / 4
        )
        * 100.0
    )

    return (
        numero,
        percentuale
    )


def colore_percentuale_copertura(
    percentuale
):
    """
    Rosso sotto il 60%, nero dal 60% in su.
    """

    if float(
        percentuale
        or 0
    ) < 60:
        return "#dc2626"

    return "#111827"


def calcola_copertura_modulo(
    df_rosa,
    nome_modulo
):

    totale_ruoli = 0
    ruoli_al_100 = 0
    somma_percentuali = 0.0

    for _, posizioni in MODULI[
        nome_modulo
    ]:

        for _, ruolo_slot in posizioni:

            totale_ruoli += 1

            numero, percentuale = (
                percentuale_copertura_ruolo(
                    df_rosa,
                    ruolo_slot
                )
            )

            somma_percentuali += (
                percentuale
            )

            if numero >= 4:
                ruoli_al_100 += 1

    percentuale_media = (
        somma_percentuali
        / totale_ruoli
        if totale_ruoli
        else 0
    )

    return (
        ruoli_al_100,
        totale_ruoli,
        percentuale_media
    )


def analizza_modulo(
    df_rosa,
    nome_modulo
):
    """
    Analisi strategica del modulo.

    Il punteggio NON è una semplice media:
    - parte dalla copertura media dei singoli slot;
    - penalizza fortemente ogni slot completamente scoperto;
    - penalizza anche gli slot con copertura inferiore al 60%.

    Formula:
    punteggio = copertura_media
                - 15 punti per ogni slot allo 0%
                - 3 punti per ogni slot tra 1% e 59%

    Il risultato finale è limitato tra 0 e 100.
    """

    percentuali = []

    for _, posizioni in MODULI[
        nome_modulo
    ]:

        for _, ruolo_slot in posizioni:

            _, percentuale = (
                percentuale_copertura_ruolo(
                    df_rosa,
                    ruolo_slot
                )
            )

            percentuali.append(
                float(
                    percentuale
                )
            )

    if not percentuali:

        return {
            "Modulo": nome_modulo,
            "Punteggio": 0.0,
            "Copertura media": 0.0,
            "Scoperti": 0,
            "Sotto 60%": 0,
            "Al 100%": 0,
            "Totale slot": 0
        }

    copertura_media = (
        sum(percentuali)
        / len(percentuali)
    )

    scoperti = sum(
        1
        for p in percentuali
        if p == 0
    )

    sotto_60 = sum(
        1
        for p in percentuali
        if 0 < p < 60
    )

    al_100 = sum(
        1
        for p in percentuali
        if p >= 100
    )

    penalita = (
        scoperti * 15
        + sotto_60 * 3
    )

    punteggio = max(
        0.0,
        min(
            100.0,
            copertura_media
            - penalita
        )
    )

    return {
        "Modulo": nome_modulo,
        "Punteggio": round(
            punteggio,
            1
        ),
        "Copertura media": round(
            copertura_media,
            1
        ),
        "Scoperti": scoperti,
        "Sotto 60%": sotto_60,
        "Al 100%": al_100,
        "Totale slot": len(
            percentuali
        )
    }


def classifica_moduli(
    df_rosa
):
    """
    Restituisce la classifica dei moduli dal più adatto al meno adatto.
    """

    risultati = [
        analizza_modulo(
            df_rosa,
            nome_modulo
        )
        for nome_modulo in MODULI
    ]

    risultati = sorted(
        risultati,
        key=lambda x: (
            -x["Punteggio"],
            x["Scoperti"],
            -x["Copertura media"],
            x["Sotto 60%"],
            x["Modulo"]
        )
    )

    for posizione, risultato in enumerate(
        risultati,
        start=1
    ):

        risultato["Posizione"] = (
            posizione
        )

    return risultati


# ============================================================
# POPUP REGOLE
# ============================================================

@st.dialog(
    "Regole FANTAELEGANZA"
)
def mostra_regole():

    st.markdown(
        """
**Regole attualmente gestite dall'app**

- Soglia economica: **500,00 €**
- Parte eccedente 500 €: **moltiplicatore ×3**
- Massimo rosa: **30 giocatori**
- Minimo portieri: **2**
- Lo svincolo non recupera il costo sostenuto
- Sono annullabili le ultime **10 operazioni**
        """
    )


# ============================================================
# POPUP ANNULLA ACQUISTO
# ============================================================

@st.dialog(
    "Conferma annullamento"
)
def conferma_annullamento(
    giocatore_id,
    nome_giocatore
):

    st.write(
        f'Annullare l\'acquisto di '
        f'**"{nome_giocatore}"**?'
    )

    st.caption(
        "Il prezzo verrà eliminato "
        "dalla spesa."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_annulla_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "ANNULLA ACQUISTO",
                "DISPONIBILE",
                None,
                0
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_annulla_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP SVINCOLO
# ============================================================

@st.dialog(
    "Conferma svincolo"
)
def conferma_svincolo(
    giocatore_id,
    nome_giocatore,
    prezzo_giocatore
):

    prezzo = float(
        prezzo_giocatore
        or 0
    )

    st.write(
        f'Svincolare '
        f'**"{nome_giocatore}"**?'
    )

    st.warning(
        "Il giocatore tornerà disponibile, "
        "ma i "
        f"**{formatta_crediti(prezzo)} €** "
        "spesi resteranno conteggiati."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_svincolo_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "SVINCOLO",
                "DISPONIBILE",
                None,
                prezzo
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_svincolo_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP RIPRISTINO AVVERSARIO
# ============================================================

@st.dialog(
    "Ripristina giocatore"
)
def conferma_ripristino_avversario(
    giocatore_id,
    nome_giocatore
):

    st.write(
        f'Rendere nuovamente disponibile '
        f'**"{nome_giocatore}"**?'
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key=f"ok_ripristina_{giocatore_id}"
        ):

            esegui_operazione(
                giocatore_id,
                "RIPRISTINO AVVERSARIO",
                "DISPONIBILE",
                None,
                0
            )

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key=f"no_ripristina_{giocatore_id}"
        ):

            st.rerun()


# ============================================================
# POPUP UNDO
# ============================================================

@st.dialog(
    "Annulla ultima operazione"
)
def conferma_undo():

    operazioni = (
        carica_ultime_operazioni()
    )

    if operazioni.empty:

        st.info(
            "Non ci sono operazioni "
            "da annullare."
        )

        return

    ultima = (
        operazioni.iloc[0]
    )

    st.write(
        "Vuoi annullare "
        "l'ultima operazione?"
    )

    st.warning(
        f"**{ultima['Operazione']}** — "
        f"{ultima['Giocatore']}"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key="ok_undo"
        ):

            annulla_ultima_operazione()

            st.rerun()

    with c2:

        if st.button(
            "ANNULLA",
            use_container_width=True,
            key="no_undo"
        ):

            st.rerun()


# ============================================================
# POPUP SNAPSHOT
# ============================================================

@st.dialog(
    "Snapshot e ripristino"
)
def gestisci_snapshot():

    st.caption(
        "FANTAELEGANZA usa la cronologia UNDO per le normali "
        "operazioni di asta e conserva gli snapshot completi "
        "per i passaggi più delicati, come import listone e ripristino. "
        f"Puoi inoltre crearli manualmente. "
        f"Vengono conservati gli ultimi {MAX_SNAPSHOT} snapshot."
    )

    c1, c2 = st.columns(
        2
    )

    with c1:

        if st.button(
            "📸 CREA SNAPSHOT ORA",
            use_container_width=True,
            key="snapshot_manual"
        ):

            creato = (
                crea_snapshot_database(
                    "MANUALE"
                )
            )

            if creato is not None:

                st.success(
                    "Snapshot creato correttamente."
                )

                st.rerun()

    with c2:

        if st.button(
            "🔄 AGGIORNA ELENCO",
            use_container_width=True,
            key="snapshot_refresh"
        ):

            st.rerun()

    snapshots = (
        elenco_snapshot()
    )

    if not snapshots:

        st.info(
            "Non ci sono ancora snapshot."
        )

        return

    opzioni = []
    mappa = {}

    for elemento in snapshots:

        etichetta = (
            f"{elemento['data']} — "
            f"{elemento['motivo']}"
        )

        opzioni.append(
            etichetta
        )

        mappa[
            etichetta
        ] = (
            elemento[
                "path"
            ]
        )

    scelta = st.selectbox(
        "Snapshot da ripristinare",
        opzioni,
        key="snapshot_select"
    )

    st.warning(
        "Il ripristino sostituirà lo stato attuale "
        "dell'asta. Prima del ripristino verrà "
        "salvato automaticamente anche lo stato corrente."
    )

    conferma = st.checkbox(
        "Confermo il ripristino dello snapshot selezionato",
        key="snapshot_confirm"
    )

    if st.button(
        "⏪ RIPRISTINA SNAPSHOT",
        type="primary",
        use_container_width=True,
        disabled=not conferma,
        key="snapshot_restore"
    ):

        try:

            ripristina_snapshot_database(
                mappa[
                    scelta
                ]
            )

            st.success(
                "Snapshot ripristinato correttamente."
            )

            st.rerun()

        except Exception as errore:

            st.error(
                f"Errore durante il ripristino: {errore}"
            )


# ============================================================
# POPUP BACKUP CLOUD
# ============================================================

@st.dialog(
    "Backup database"
)
def gestisci_backup_cloud():

    st.caption(
        "Il backup viene generato solo quando lo richiedi, "
        "così la normale navigazione dell'app non interroga "
        "inutilmente il database Cloud."
    )

    if "backup_cloud_bytes" not in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if st.session_state.backup_cloud_bytes is None:

        if st.button(
            "☁ PREPARA BACKUP",
            use_container_width=True,
            type="primary",
            key="prepara_backup_cloud"
        ):

            with st.spinner(
                "Preparazione backup..."
            ):

                st.session_state.backup_cloud_bytes = (
                    crea_backup_logico_bytes()
                )

            st.rerun()

    else:

        st.success(
            "Backup pronto."
        )

        st.download_button(
            "⬇ SCARICA BACKUP",
            data=(
                st.session_state.backup_cloud_bytes
            ),
            file_name=(
                "fantaeleganza_backup_cloud.json"
            ),
            mime=(
                "application/json"
            ),
            use_container_width=True,
            key="scarica_backup_cloud"
        )

        if st.button(
            "🔄 GENERA NUOVO BACKUP",
            use_container_width=True,
            key="rigenera_backup_cloud"
        ):

            st.session_state.backup_cloud_bytes = None
            st.rerun()


# ============================================================
# INIZIALIZZAZIONE
# ============================================================

inizializza_database()

df_completo = (
    carica_tutti_giocatori()
)

df_rosa_globale = (
    df_completo[
        df_completo["Stato"]
        == "MIO"
    ]
    .copy()
)

valore_attivi = (
    calcola_valore_acquisti_attivi()
)

costi_svincoli = (
    calcola_costi_svincoli()
)

valore_acquisti = round(
    valore_attivi
    + costi_svincoli,
    2
)

spesa_effettiva = (
    calcola_spesa_effettiva(
        valore_acquisti
    )
)

oltre_soglia = round(
    max(
        0,
        valore_acquisti
        - SOGLIA_BASE
    ),
    2
)

numero_rosa = len(
    df_rosa_globale
)

numero_portieri = (
    conta_portieri(
        df_rosa_globale
    )
)

slot_liberi = max(
    0,
    MAX_GIOCATORI
    - numero_rosa
)


# ============================================================
# HEADER COMPATTO
# ============================================================

head_left, head_refresh, head_snapshot, head_backup, head_rules, head_theme = (
    st.columns(
        [
            5.0,
            0.9,
            1.0,
            0.9,
            0.8,
            1.0
        ],
        vertical_alignment="center"
    )
)

with head_left:

    # IMPORTANTE:
    # stringa HTML senza indentazione iniziale,
    # così Streamlit non la mostra come codice.

    header_html = (
        '<div class="fanta-header">'
        '<div class="fanta-brand">'
        '<div class="fanta-logo">⚽</div>'
        '<div>'
        '<div class="fanta-brand-title">'
        'FANTAELEGANZA <span>26/27</span>'
        '</div>'
        '<div class="fanta-brand-subtitle">'
        'Gestione asta e rosa'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True
    )


with head_refresh:

    if st.button(
        "🔄 Aggiorna",
        use_container_width=True,
        key="btn_aggiorna_app"
    ):

        invalida_cache_dati()
        st.rerun()


with head_snapshot:

    if st.button(
        "📸 Snapshot",
        use_container_width=True,
        key="btn_snapshot"
    ):

        gestisci_snapshot()


with head_backup:

    if USA_DATABASE_CLOUD:

        if st.button(
            "☁ Backup",
            use_container_width=True,
            key="btn_backup_cloud"
        ):

            gestisci_backup_cloud()

    elif DB_PATH.exists():

        with open(
            DB_PATH,
            "rb"
        ) as file_db:

            st.download_button(
                "☁ Backup",
                data=file_db.read(),
                file_name=(
                    "fantaeleganza_backup.db"
                ),
                mime=(
                    "application/octet-stream"
                ),
                use_container_width=True
            )


with head_rules:

    if st.button(
        "❔ Regole",
        use_container_width=True,
        key="btn_regole"
    ):

        mostra_regole()


with head_theme:

    nuovo_dark = st.toggle(
        "🌙 Scuro",
        value=(
            st.session_state.dark_mode
        ),
        key="toggle_dark"
    )

    if (
        nuovo_dark
        != st.session_state.dark_mode
    ):

        st.session_state.dark_mode = (
            nuovo_dark
        )

        st.rerun()


# ============================================================
# RIEPILOGO COMPATTO
# ============================================================

m1, m2, m3, m4, m5, m6, m7 = (
    st.columns(7)
)

m1.metric(
    "💳 Soglia base",
    f"{formatta_crediti(SOGLIA_BASE)} €"
)

m2.metric(
    "🛒 Valore acquisti",
    f"{formatta_crediti(valore_acquisti)} €"
)

m3.metric(
    "🪙 Spesa effettiva",
    f"{formatta_crediti(spesa_effettiva)} €"
)

m4.metric(
    "⚡ Oltre soglia",
    f"{formatta_crediti(oltre_soglia)} €"
)

m5.metric(
    "👥 Giocatori",
    f"{numero_rosa}/{MAX_GIOCATORI}"
)

m6.metric(
    "🧤 Portieri",
    f"{numero_portieri}/{MIN_PORTIERI}"
)

m7.metric(
    "👕 Slot liberi",
    slot_liberi
)


# ============================================================
# NAVBAR
# ============================================================

PAGINE = [
    ("🏠", "DASHBOARD"),
    ("☷", "LISTONE"),
    ("🔨", "ASTA"),
    ("👕", "ROSA"),
    ("▣", "MODULI")
]

st.markdown(
    '<div class="nav-title">Navigazione</div>',
    unsafe_allow_html=True
)

nav_cols = st.columns(5)

for col, (
    icona,
    pagina
) in zip(
    nav_cols,
    PAGINE
):

    with col:

        if st.button(
            f"{icona}  {pagina}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.pagina
                == pagina
                else "secondary"
            ),
            key=f"nav_{pagina}"
        ):

            st.session_state.pagina = (
                pagina
            )

            st.rerun()

sezione = (
    st.session_state.pagina
)


# ============================================================
# TOOLBAR UNDO COMPATTA
# ============================================================

operazioni_undo = (
    carica_ultime_operazioni()
)

undo1, undo2 = st.columns(
    [
        1.7,
        7
    ]
)

with undo1:

    if st.button(
        "↶ ANNULLA ULTIMA OPERAZIONE",
        use_container_width=True,
        disabled=(
            operazioni_undo.empty
        ),
        key="btn_undo_generale"
    ):

        conferma_undo()


with undo2:

    if not operazioni_undo.empty:

        ultima = (
            operazioni_undo.iloc[0]
        )

        testo_ultima = (
            f'<div class="operation-info">'
            f'Ultima operazione annullabile:&nbsp;'
            f'<b>'
            f'{html.escape(str(ultima["Operazione"]))}'
            f' — '
            f'{html.escape(str(ultima["Giocatore"]))}'
            f'</b>'
            f'&nbsp;'
            f'({len(operazioni_undo)}/10)'
            f'</div>'
        )

        st.markdown(
            testo_ultima,
            unsafe_allow_html=True
        )


with st.expander(
    "📜 Ultime operazioni",
    expanded=False
):

    if operazioni_undo.empty:

        st.caption(
            "Nessuna operazione registrata."
        )

    else:

        st.dataframe(
            operazioni_undo[
                [
                    "Operazione",
                    "Giocatore",
                    "Data"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


@st.dialog("Elimina tutta la rosa")
def conferma_elimina_tutta_rosa():
    df_corrente = carica_tutti_giocatori()
    numero = int((df_corrente["Stato"] == "MIO").sum())

    st.warning(
        f"Stai per eliminare tutti i {numero} giocatori presenti nella rosa. "
        "Torneranno DISPONIBILI e i prezzi di acquisto verranno azzerati."
    )
    st.caption(
        "Verranno azzerati anche i costi di svincolo e la cronologia UNDO."
    )

    conferma = st.checkbox(
        "Confermo di voler eliminare tutta la rosa",
        key="conferma_reset_totale_rosa"
    )

    if st.button(
        "🗑️ ELIMINA TUTTA LA ROSA",
        type="primary",
        use_container_width=True,
        disabled=not conferma,
        key="esegui_reset_totale_rosa"
    ):
        eliminati = elimina_tutta_la_rosa()
        st.session_state["messaggio_reset_rosa"] = (
            f"Rosa eliminata: {eliminati} giocatori sono tornati disponibili."
        )
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if sezione == "DASHBOARD":

    st.subheader(
        "📊 Dashboard"
    )

    snapshot_disponibili = (
        elenco_snapshot()
    )

    st.caption(
        f"💾 Protezione attiva — "
        f"{len(snapshot_disponibili)} snapshot disponibili "
        f"(massimo {MAX_SNAPSHOT}) · "
        f"UNDO fino a {MAX_UNDO} operazioni. "
        + (
            "🌐 Database Cloud persistente attivo."
            if USA_DATABASE_CLOUD
            else "💻 Database locale attivo."
        )
    )


    # --------------------------------------------------------
    # STAMPA ROSA E MODULI
    # --------------------------------------------------------

    stampa_col1, stampa_col2 = st.columns(
        [
            1.6,
            4.4
        ]
    )

    with stampa_col1:

        if st.button(
            "🖨️ STAMPA ROSA E MODULI",
            use_container_width=True,
            disabled=(
                numero_rosa == 0
            ),
            key="btn_genera_pdf_rosa_moduli"
        ):

            with st.spinner(
                "Creazione PDF..."
            ):

                try:

                    st.session_state[
                        "pdf_rosa_moduli"
                    ] = (
                        genera_pdf_rosa_e_moduli(
                            df_rosa_globale,
                            valore_attivi,
                            costi_svincoli,
                            valore_acquisti,
                            spesa_effettiva
                        )
                    )

                except Exception as errore:

                    st.session_state[
                        "pdf_rosa_moduli"
                    ] = None

                    st.error(
                        f"Errore durante la creazione del PDF: {errore}"
                    )

    with stampa_col2:

        if st.session_state.get(
            "pdf_rosa_moduli"
        ):

            st.download_button(
                "⬇️ SCARICA PDF ROSA E MODULI",
                data=(
                    st.session_state[
                        "pdf_rosa_moduli"
                    ]
                ),
                file_name=(
                    "FANTAELEGANZA_26-27_ROSA_E_MODULI.pdf"
                ),
                mime=(
                    "application/pdf"
                ),
                use_container_width=True,
                key="download_pdf_rosa_moduli"
            )

        elif numero_rosa > 0:

            st.caption(
                "Premi STAMPA ROSA E MODULI per preparare il PDF scaricabile."
            )

    if numero_rosa == 0:

        st.info(
            "La rosa è ancora vuota. "
            "Vai nella sezione ASTA "
            "per iniziare ad acquistare."
        )

    else:

        if (
            numero_rosa
            == MAX_GIOCATORI
            and numero_portieri
            >= MIN_PORTIERI
        ):

            st.success(
                "✅ Rosa completa e conforme."
            )

        elif (
            numero_portieri
            < MIN_PORTIERI
        ):

            mancanti = (
                MIN_PORTIERI
                - numero_portieri
            )

            st.warning(
                f"⚠️ Mancano ancora "
                f"{mancanti} portieri."
            )

        dleft, dright = st.columns(
            [
                1,
                1
            ]
        )

        with dleft:

            st.markdown(
                "#### Distribuzione rosa"
            )

            distribuzione = (
                df_rosa_globale.copy()
            )

            distribuzione[
                "Primo ruolo"
            ] = (
                distribuzione["RM"]
                .apply(
                    primo_ruolo
                )
            )

            righe = []

            for ruolo in ELENCO_RUOLI:

                gruppo = (
                    distribuzione[
                        distribuzione[
                            "Primo ruolo"
                        ]
                        .str.upper()
                        == ruolo.upper()
                    ]
                )

                if not gruppo.empty:

                    righe.append({
                        "Ruolo":
                            ruolo,

                        "Giocatori":
                            len(
                                gruppo
                            ),

                        "Valore":
                            formatta_crediti(
                                gruppo[
                                    "Prezzo"
                                ]
                                .fillna(0)
                                .sum()
                            )
                    })

            st.dataframe(
                pd.DataFrame(
                    righe
                ),
                use_container_width=True,
                hide_index=True
            )

        with dright:

            st.markdown(
                "#### ⭐ Modulo consigliato"
            )

            classifica = (
                classifica_moduli(
                    df_rosa_globale
                )
            )

            if classifica:

                migliore = (
                    classifica[0]
                )

                st.success(
                    f"**{migliore['Modulo']}** "
                    f"— punteggio strategico "
                    f"**{migliore['Punteggio']}/100** "
                    f"— copertura media "
                    f"**{migliore['Copertura media']}%** "
                    f"— slot scoperti "
                    f"**{migliore['Scoperti']}**"
                )

                tabella_classifica = (
                    pd.DataFrame(
                        classifica
                    )[
                        [
                            "Posizione",
                            "Modulo",
                            "Punteggio",
                            "Copertura media",
                            "Scoperti",
                            "Sotto 60%",
                            "Al 100%"
                        ]
                    ]
                )

                st.dataframe(
                    tabella_classifica,
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# LISTONE
# ============================================================

elif sezione == "LISTONE":

    st.subheader(
        "☷ Listone giocatori"
    )

    file_caricato = st.file_uploader(
        "Carica il listone Fantacalcio.it",
        type=[
            "xlsx",
            "xlsm"
        ]
    )

    if file_caricato is not None:

        try:

            contenuto = (
                file_caricato
                .getvalue()
            )

            excel = pd.ExcelFile(
                io.BytesIO(
                    contenuto
                ),
                engine="openpyxl"
            )

            foglio_listone = None

            for nome_foglio in (
                excel.sheet_names
            ):

                if (
                    nome_foglio
                    .strip()
                    .upper()
                    == "LISTONE"
                ):

                    foglio_listone = (
                        nome_foglio
                    )

                    break

            if foglio_listone is None:

                st.error(
                    "Non trovo il foglio LISTONE."
                )

            else:

                df_excel = pd.read_excel(
                    io.BytesIO(
                        contenuto
                    ),
                    sheet_name=(
                        foglio_listone
                    ),
                    engine="openpyxl",
                    header=1
                )

                df_excel = (
                    df_excel
                    .dropna(
                        axis=1,
                        how="all"
                    )
                    .dropna(
                        axis=0,
                        how="all"
                    )
                )

                df_excel.columns = [
                    str(c).strip()
                    for c
                    in df_excel.columns
                ]

                obbligatorie = {
                    "Id",
                    "R",
                    "RM",
                    "Nome",
                    "Squadra"
                }

                mancanti = (
                    obbligatorie
                    - set(
                        df_excel.columns
                    )
                )

                if mancanti:

                    st.error(
                        "Formato non valido. "
                        "Colonne mancanti: "
                        + ", ".join(
                            sorted(
                                mancanti
                            )
                        )
                    )

                else:

                    nuovi, aggiornati = (
                        importa_listone_nel_database(
                            df_excel
                        )
                    )

                    st.success(
                        "✅ Listone importato con successo — "
                        f"{st.session_state.get('ultimo_upload_listone', '')}. "
                        f"Nuovi: {nuovi} — "
                        f"Aggiornati: {aggiornati}. "
                        "I giocatori invariati non sono stati riscritti."
                    )

        except Exception as errore:

            st.error(
                f"Errore: {errore}"
            )

    df = (
        df_completo.copy()
    )

    if df.empty:

        st.info(
            "Il database è vuoto."
        )

    else:

        f1, f2, f3 = st.columns(3)

        with f1:

            filtro_stato = (
                st.selectbox(
                    "Stato",
                    [
                        "TUTTI",
                        "DISPONIBILE",
                        "MIO",
                        "AVVERSARIO"
                    ]
                )
            )

        with f2:

            filtro_ruolo = (
                st.selectbox(
                    "Primo ruolo",
                    [
                        "TUTTI"
                    ]
                    + ELENCO_RUOLI
                )
            )

        squadre = sorted(
            df[
                "Squadra"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        with f3:

            filtro_squadra = (
                st.selectbox(
                    "Squadra",
                    [
                        "TUTTE"
                    ]
                    + squadre
                )
            )

        ricerca = st.text_input(
            "🔎 Cerca giocatore"
        )

        filtrato = (
            df.copy()
        )

        if (
            filtro_stato
            != "TUTTI"
        ):

            filtrato = (
                filtrato[
                    filtrato[
                        "Stato"
                    ]
                    == filtro_stato
                ]
            )

        if (
            filtro_ruolo
            != "TUTTI"
        ):

            filtrato = (
                filtrato[
                    filtrato[
                        "RM"
                    ]
                    .apply(
                        primo_ruolo
                    )
                    .str.upper()
                    == filtro_ruolo.upper()
                ]
            )

        if (
            filtro_squadra
            != "TUTTE"
        ):

            filtrato = (
                filtrato[
                    filtrato[
                        "Squadra"
                    ]
                    == filtro_squadra
                ]
            )

        if ricerca:

            testo = (
                ricerca
                .lower()
                .strip()
            )

            filtrato = (
                filtrato[
                    filtrato[
                        "Nome"
                    ]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        testo,
                        na=False
                    )
                ]
            )

        filtrato[
            "Priorita"
        ] = (
            filtrato[
                "RM"
            ]
            .apply(
                priorita_ruolo
            )
        )

        filtrato = (
            filtrato
            .sort_values(
                by=[
                    "Priorita",
                    "FVM",
                    "Nome"
                ],
                ascending=[
                    True,
                    False,
                    True
                ],
                na_position="last"
            )
        )

        vista = (
            filtrato[
                [
                    "Id",
                    "R",
                    "RM",
                    "Nome",
                    "Squadra",
                    "Qt.A",
                    "Qt.I",
                    "Diff.",
                    "FVM",
                    "Stato",
                    "Prezzo"
                ]
            ]
            .copy()
        )

        vista[
            "Prezzo"
        ] = (
            vista[
                "Prezzo"
            ]
            .apply(
                formatta_crediti
            )
        )

        st.dataframe(
            vista,
            use_container_width=True,
            hide_index=True,
            height=620
        )


# ============================================================
# ASTA
# ============================================================

elif sezione == "ASTA":

    st.subheader(
        "🔨 Asta"
    )

    df = (
        df_completo.copy()
    )

    if df.empty:

        st.info(
            "Prima devi caricare il listone."
        )

    else:

        tab1, tab2 = st.tabs(
            [
                "🟢 Disponibili",
                "🔴 Venduti agli avversari"
            ]
        )

        # ----------------------------------------------------
        # DISPONIBILI
        # ----------------------------------------------------

        with tab1:

            disponibili = (
                df[
                    df[
                        "Stato"
                    ]
                    == "DISPONIBILE"
                ]
                .copy()
            )

            ricerca = st.text_input(
                "🔎 Cerca giocatore o squadra",
                key="search_asta"
            )

            if ricerca:

                testo = (
                    ricerca
                    .lower()
                    .strip()
                )

                disponibili = (
                    disponibili[
                        (
                            disponibili[
                                "Nome"
                            ]
                            .astype(str)
                            .str.lower()
                            .str.contains(
                                testo,
                                na=False
                            )
                        )
                        |
                        (
                            disponibili[
                                "Squadra"
                            ]
                            .astype(str)
                            .str.lower()
                            .str.contains(
                                testo,
                                na=False
                            )
                        )
                    ]
                )

            disponibili = (
                disponibili
                .sort_values(
                    "Nome"
                )
                .reset_index(
                    drop=True
                )
            )

            if disponibili.empty:

                st.info(
                    "Nessun giocatore disponibile."
                )

            else:

                opzioni = (
                    disponibili
                    .apply(
                        lambda r:
                        f"{r['Nome']} — "
                        f"{r['Squadra']} — "
                        f"{r['RM']}",
                        axis=1
                    )
                    .tolist()
                )

                scelta = (
                    st.selectbox(
                        "Giocatore",
                        opzioni
                    )
                )

                giocatore = (
                    disponibili.iloc[
                        opzioni.index(
                            scelta
                        )
                    ]
                )

                g1, g2, g3, g4 = (
                    st.columns(4)
                )

                colore_nome_asta = (
                    colore_fvm_mantra(
                        giocatore.get(
                            "RM",
                            ""
                        ),
                        giocatore.get(
                            "FVM M"
                        )
                    )
                )

                with g1:

                    st.markdown(
                        f"""
                        <div class="asta-player-mobile-fix">
                            <div style="
                                font-size:0.875rem;
                                color:rgba(49,51,63,0.6);
                                margin-bottom:0.15rem;
                            ">
                                Giocatore
                            </div>
                            <div style="
                                font-size:1.75rem;
                                line-height:1.2;
                                font-weight:600;
                                color:{colore_nome_asta};
                                white-space:normal;
                                overflow-wrap:anywhere;
                            ">
                                {html.escape(str(giocatore["Nome"]))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                g2.metric(
                    "Squadra",
                    giocatore[
                        "Squadra"
                    ]
                )

                g3.metric(
                    "Ruolo",
                    giocatore[
                        "RM"
                    ]
                )

                g4.metric(
                    "FVM",
                    giocatore[
                        "FVM"
                    ]
                )

                prezzo = (
                    st.number_input(
                        "Prezzo di acquisto",
                        min_value=0.10,
                        max_value=5000.00,
                        value=1.00,
                        step=0.10,
                        format="%.2f"
                    )
                )

                prezzo = round(
                    float(
                        prezzo
                    ),
                    2
                )

                nuovo_valore = round(
                    valore_acquisti
                    + prezzo,
                    2
                )

                nuova_spesa = (
                    calcola_spesa_effettiva(
                        nuovo_valore
                    )
                )

                incremento = round(
                    nuova_spesa
                    - spesa_effettiva,
                    2
                )

                p1, p2, p3 = (
                    st.columns(3)
                )

                p1.metric(
                    "Prezzo",
                    f"{formatta_crediti(prezzo)} €"
                )

                p2.metric(
                    "Impatto effettivo",
                    f"{formatta_crediti(incremento)} €"
                )

                p3.metric(
                    "Nuova spesa",
                    f"{formatta_crediti(nuova_spesa)} €"
                )

                valido, motivo = (
                    verifica_acquisto_regole(
                        df_rosa_globale,
                        giocatore[
                            "RM"
                        ]
                    )
                )

                if not valido:

                    st.error(
                        "⛔ " + motivo
                    )

                a1, a2 = (
                    st.columns(2)
                )

                with a1:

                    if st.button(
                        "✅ ACQUISTA",
                        use_container_width=True,
                        type="primary",
                        disabled=(
                            not valido
                        ),
                        key="btn_acquista"
                    ):

                        esegui_operazione(
                            int(
                                giocatore[
                                    "Id"
                                ]
                            ),
                            "ACQUISTO",
                            "MIO",
                            prezzo,
                            0
                        )

                        st.rerun()

                with a2:

                    if st.button(
                        "🔴 VENDUTO AD AVVERSARIO",
                        use_container_width=True,
                        key="btn_avversario"
                    ):

                        esegui_operazione(
                            int(
                                giocatore[
                                    "Id"
                                ]
                            ),
                            "VENDUTO AVVERSARIO",
                            "AVVERSARIO",
                            None,
                            0
                        )

                        st.rerun()

        # ----------------------------------------------------
        # AVVERSARI
        # ----------------------------------------------------

        with tab2:

            avversari = (
                df[
                    df[
                        "Stato"
                    ]
                    == "AVVERSARIO"
                ]
                .copy()
                .sort_values(
                    "Nome"
                )
            )

            if avversari.empty:

                st.info(
                    "Nessun giocatore venduto "
                    "agli avversari."
                )

            else:

                for _, riga in (
                    avversari.iterrows()
                ):

                    cols = (
                        st.columns(
                            [
                                4,
                                2,
                                2,
                                1,
                                0.7
                            ]
                        )
                    )

                    cols[0].write(
                        riga[
                            "Nome"
                        ]
                    )

                    cols[1].write(
                        riga[
                            "Squadra"
                        ]
                    )

                    cols[2].write(
                        riga[
                            "RM"
                        ]
                    )

                    cols[3].write(
                        riga[
                            "FVM"
                        ]
                    )

                    with cols[4]:

                        if st.button(
                            "↩️",
                            key=(
                                "ripristina_"
                                f"{int(riga['Id'])}"
                            ),
                            help=(
                                "Rendi nuovamente "
                                "disponibile"
                            )
                        ):

                            conferma_ripristino_avversario(
                                int(
                                    riga[
                                        "Id"
                                    ]
                                ),
                                riga[
                                    "Nome"
                                ]
                            )


# ============================================================
# ROSA
# ============================================================

elif sezione == "ROSA":

    st.subheader(
        "👕 La mia rosa"
    )

    if "messaggio_reset_rosa" in st.session_state:
        st.success(
            st.session_state.pop(
                "messaggio_reset_rosa"
            )
        )

    df_rosa = (
        df_rosa_globale.copy()
    )

    if not df_rosa.empty:
        if st.button(
            "🗑️ ELIMINA TUTTA LA ROSA",
            key="btn_reset_tutta_rosa"
        ):
            conferma_elimina_tutta_rosa()

    if df_rosa.empty:

        empty_html = (
            '<div class="empty-card">'
            '<div class="empty-icon">👕</div>'
            '<div class="empty-title">'
            'La rosa è ancora vuota'
            '</div>'
            '<div class="empty-text">'
            'Vai nella sezione ASTA '
            'per acquistare i primi giocatori.'
            '</div>'
            '</div>'
        )

        st.markdown(
            empty_html,
            unsafe_allow_html=True
        )

    else:

        df_rosa[
            "Priorita"
        ] = (
            df_rosa["RM"]
            .apply(
                priorita_ruolo
            )
        )

        df_rosa = (
            df_rosa
            .sort_values(
                [
                    "Priorita",
                    "Nome"
                ]
            )
            .reset_index(
                drop=True
            )
        )

        # ----------------------------------------------------
        # VISTA MOBILE - tabella semplice
        # ----------------------------------------------------
        with st.container(
            key="rosa_mobile_view"
        ):

            righe_mobile = []

            for _, giocatore in df_rosa.iterrows():

                nome = html.escape(
                    str(
                        giocatore[
                            "Nome"
                        ]
                    )
                )

                ruolo = html.escape(
                    str(
                        giocatore[
                            "RM"
                        ]
                    )
                )

                prezzo = (
                    formatta_crediti(
                        giocatore[
                            "Prezzo"
                        ]
                    )
                )

                colore_nome = (
                    colore_fvm_mantra(
                        giocatore.get(
                            "RM",
                            ""
                        ),
                        giocatore.get(
                            "FVM M"
                        )
                    )
                )

                righe_mobile.append(
                    "<tr>"
                    f"<td><span style='color:{colore_nome};font-weight:800;'>"
                    f"{nome}</span></td>"
                    f"<td>{ruolo}</td>"
                    f"<td>{prezzo}</td>"
                    "</tr>"
                )

            tabella_mobile_html = (
                "<div class='rosa-mobile-view'>"
                "<table class='rosa-mobile-table'>"
                "<thead>"
                "<tr>"
                "<th>NOME GIOCATORE</th>"
                "<th>RUOLO</th>"
                "<th>PREZZO ACQUISTO</th>"
                "</tr>"
                "</thead>"
                "<tbody>"
                + "".join(
                    righe_mobile
                )
                + "</tbody>"
                "</table>"
                "</div>"
            )

            st.markdown(
                tabella_mobile_html,
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # VISTA DESKTOP - invariata
        # ----------------------------------------------------
        with st.container(
            key="rosa_desktop_view"
        ):

            intestazione = (
                st.columns(
                    [
                        4,
                        2,
                        2,
                        1.2,
                        1.2,
                        1.5,
                        0.7,
                        0.7
                    ]
                )
            )

            titoli = [
                "Nome",
                "Squadra",
                "Ruolo",
                "Qt.",
                "FVM",
                "Prezzo",
                "🗑️",
                "🔓"
            ]

            for col, titolo in zip(
                intestazione,
                titoli
            ):
                col.markdown(
                    f"**{titolo}**"
                )

            for _, giocatore in df_rosa.iterrows():

                cols = (
                    st.columns(
                        [
                            4,
                            2,
                            2,
                            1.2,
                            1.2,
                            1.5,
                            0.7,
                            0.7
                        ]
                    )
                )

                cols[0].write(
                    giocatore["Nome"]
                )
                cols[1].write(
                    giocatore["Squadra"]
                )
                cols[2].write(
                    giocatore["RM"]
                )
                cols[3].write(
                    giocatore["Qt.A"]
                )
                cols[4].write(
                    giocatore["FVM"]
                )
                cols[5].write(
                    formatta_crediti(
                        giocatore["Prezzo"]
                    )
                )

                with cols[6]:
                    if st.button(
                        "🗑️",
                        key=(
                            "elimina_"
                            f"{int(giocatore['Id'])}"
                        ),
                        help="Annulla acquisto"
                    ):
                        conferma_annullamento(
                            int(
                                giocatore["Id"]
                            ),
                            giocatore["Nome"]
                        )

                with cols[7]:
                    if st.button(
                        "🔓",
                        key=(
                            "svincola_"
                            f"{int(giocatore['Id'])}"
                        ),
                        help="Svincola giocatore"
                    ):
                        conferma_svincolo(
                            int(
                                giocatore["Id"]
                            ),
                            giocatore["Nome"],
                            giocatore["Prezzo"]
                        )


# ============================================================
# MODULI
# ============================================================

elif sezione == "MODULI":

    df_rosa = (
        df_rosa_globale.copy()
    )

    classifica_moduli_corrente = (
        classifica_moduli(
            df_rosa
        )
    )

    modulo_consigliato = (
        classifica_moduli_corrente[0][
            "Modulo"
        ]
        if classifica_moduli_corrente
        else list(
            MODULI.keys()
        )[0]
    )

    if "modulo_attivo" not in st.session_state:
        st.session_state.modulo_attivo = (
            modulo_consigliato
        )

    if classifica_moduli_corrente:

        migliore = (
            classifica_moduli_corrente[0]
        )

        st.success(
            f"⭐ **Modulo consigliato: "
            f"{migliore['Modulo']}** "
            f"— punteggio strategico "
            f"**{migliore['Punteggio']}/100** "
            f"— copertura media "
            f"**{migliore['Copertura media']}%** "
            f"— slot scoperti "
            f"**{migliore['Scoperti']}**"
        )

    st.markdown(
        '<div class="module-button-note">'
        'Seleziona il modulo da visualizzare'
        '</div>',
        unsafe_allow_html=True
    )

    lista_moduli = list(
        MODULI.keys()
    )

    # --------------------------------------------------------
    # TASTI MODULO
    # --------------------------------------------------------

    for inizio in range(
        0,
        len(lista_moduli),
        5
    ):

        gruppo_moduli = lista_moduli[
            inizio:
            inizio + 5
        ]

        colonne = st.columns(
            len(gruppo_moduli),
            gap="small"
        )

        for colonna, nome_modulo in zip(
            colonne,
            gruppo_moduli
        ):

            with colonna:

                etichetta_modulo = (
                    f"⭐ {nome_modulo}"
                    if nome_modulo
                    == modulo_consigliato
                    else nome_modulo
                )

                if st.button(
                    etichetta_modulo,
                    use_container_width=True,
                    type=(
                        "primary"
                        if st.session_state.modulo_attivo
                        == nome_modulo
                        else "secondary"
                    ),
                    key=(
                        "btn_modulo_"
                        + nome_modulo
                        .replace("-", "_")
                    )
                ):

                    st.session_state.modulo_attivo = (
                        nome_modulo
                    )

                    st.rerun()

    modulo_scelto = (
        st.session_state.modulo_attivo
    )

    if df_rosa.empty:

        empty_html = (
            '<div class="empty-card">'
            '<div class="empty-icon">⚽</div>'
            '<div class="empty-title">'
            'Nessun giocatore in rosa'
            '</div>'
            '<div class="empty-text">'
            'Acquista almeno un giocatore '
            'dalla sezione ASTA.<br>'
            'Il modulo selezionato verrà compilato '
            'automaticamente.'
            '</div>'
            '</div>'
        )

        st.markdown(
            empty_html,
            unsafe_allow_html=True
        )

    else:

        righe_modulo = (
            MODULI[
                modulo_scelto
            ]
        )

        ruoli_al_100, totale_posizioni, percentuale_media = (
            calcola_copertura_modulo(
                df_rosa,
                modulo_scelto
            )
        )

        percentuale = round(
            percentuale_media
        )

        analisi_corrente = (
            analizza_modulo(
                df_rosa,
                modulo_scelto
            )
        )

        html_campo = (
            '<div class="module-card">'
            '<div class="module-card-title">'
            f'{html.escape(modulo_scelto)}'
            '</div>'
            '<div class="module-card-summary">'
            f'Punteggio strategico '
            f'{analisi_corrente["Punteggio"]}/100'
            f' · copertura media {percentuale}%'
            f' · ruoli con almeno 4 giocatori: '
            f'{ruoli_al_100}/{totale_posizioni}'
            f' · slot scoperti: '
            f'{analisi_corrente["Scoperti"]}'
            '</div>'
            '<div class="pitch">'
            '<div class="pitch-half-line"></div>'
        )

        # Attacco in alto, portiere in basso.
        # Visualizzazione ridotta ai soli ruoli Mantra
        # e ai nomi dei giocatori compatibili.
        for _, posizioni in reversed(
            righe_modulo
        ):

            html_campo += (
                '<div class="pitch-line">'
            )

            for _, ruolo_slot in (
                posizioni
            ):

                possibili = (
                    giocatori_compatibili(
                        df_rosa,
                        ruolo_slot
                    )
                )

                numero_ruolo, percentuale_ruolo = (
                    percentuale_copertura_ruolo(
                        df_rosa,
                        ruolo_slot
                    )
                )

                percentuale_ruolo_arrotondata = round(
                    percentuale_ruolo
                )

                colore_copertura = (
                    colore_percentuale_copertura(
                        percentuale_ruolo
                    )
                )

                html_campo += (
                    '<div class="player-slot">'
                    '<div class="slot-code">'
                    f'<span>{html.escape(str(ruolo_slot))}</span>'
                    '<span class="slot-coverage" '
                    f'style="color:{colore_copertura};">'
                    f'{percentuale_ruolo_arrotondata}%'
                    '</span>'
                    '</div>'
                )

                if possibili.empty:

                    html_campo += (
                        '<span class="slot-empty">'
                        '—'
                        '</span>'
                    )

                else:

                    for _, giocatore in (
                        possibili.iterrows()
                    ):

                        nome = html.escape(
                            str(
                                giocatore[
                                    "Nome"
                                ]
                            )
                        )

                        ruoli_giocatore_testo = html.escape(
                            str(
                                giocatore.get(
                                    "RM",
                                    ""
                                )
                            ).strip()
                        )

                        colore = (
                            colore_fvm_mantra(
                                giocatore.get(
                                    "RM",
                                    ""
                                ),
                                giocatore.get(
                                    "FVM M"
                                )
                            )
                        )

                        nome_con_ruoli = (
                            f"{nome} "
                            f"({ruoli_giocatore_testo})"
                            if ruoli_giocatore_testo
                            else nome
                        )

                        html_campo += (
                            '<div class="player-name" '
                            f'style="color:{colore};">'
                            f'{nome_con_ruoli}'
                            '</div>'
                        )

                html_campo += (
                    '</div>'
                )

            html_campo += (
                '</div>'
            )

        html_campo += (
            '</div>'
            '</div>'
        )

        st.markdown(
            html_campo,
            unsafe_allow_html=True
        )


# ============================================================
# FOOTER
# ============================================================

footer_html = (
    '<div class="fanta-footer">'
    'ⓘ &nbsp;'
    '<b>FANTAELEGANZA 26/27</b>'
    ' — Il tuo assistente per un\'asta perfetta.'
    '</div>'
)

st.markdown(
    footer_html,
    unsafe_allow_html=True
)
