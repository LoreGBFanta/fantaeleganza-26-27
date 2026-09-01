# FANTAELEGANZA MULTIMODULO V3 - FILE VERIFICATO
import html
import io
import json
import math
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


st.markdown("""
<style>
/* ============================================================
   NAVIGAZIONE COMPATTA
   Pulsanti più piccoli senza sacrificare la leggibilità
   ============================================================ */

div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    min-height: 34px !important;
    height: 34px !important;
    padding: 0.20rem 0.60rem !important;
    font-size: 0.88rem !important;
    line-height: 1.15 !important;
    border-radius: 7px !important;
}

/* Mobile: leggermente più alti per facilitare il tap */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
        min-height: 36px !important;
        height: 36px !important;
        padding: 0.22rem 0.45rem !important;
        font-size: 0.86rem !important;
        line-height: 1.15 !important;
    }
}
</style>
""", unsafe_allow_html=True)

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

        padding: 12px 20px;

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
        width: 72px;
        height: 72px;
        min-width: 72px;

        display: flex;
        align-items: center;
        justify-content: center;

        border: 3px solid {GOLD};
        border-radius: 16px;

        background: #ffffff;
        overflow: hidden;
        box-sizing: border-box;
    }}

    .fanta-logo img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center top;
        display: block;
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
            width: 48px !important;
            height: 48px !important;
            min-width: 48px !important;
            border-width: 2px !important;
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

        /* Priorità acquisto ASTA */
        div[data-testid="stHorizontalBlock"] > div {{
            min-width: 0 !important;
        }}

        div[class*="st-key-priorita_click_"] {{
            position: relative !important;
        }}

        div[class*="st-key-priorita_click_"] .stButton {{
            position: absolute !important;
            inset: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 20 !important;
            margin: 0 !important;
        }}

        div[class*="st-key-priorita_click_"] .stButton > button {{
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            opacity: 0 !important;
            cursor: pointer !important;
            border: 0 !important;
            padding: 0 !important;
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
# PRIORITÀ ACQUISTO IN ASTA
# ============================================================

def valuta_priorita_acquisto(
    giocatore,
    df_rosa,
    df_listone
):
    """
    Valuta la priorità di acquisto usando le FASCE qualità
    (VERDE / BLU / ROSSO / NERO), non il valore FVM M puntuale.

    "Rimasti" =
        giocatori ancora DISPONIBILI compatibili con il ruolo
        e appartenenti alla stessa fascia del giocatore selezionato
        oppure a una fascia superiore.

    Esempi:
    - candidato VERDE -> conta solo VERDI
    - candidato BLU   -> conta VERDI + BLU
    - candidato ROSSO -> conta VERDI + BLU + ROSSI
    - candidato NERO  -> conta TUTTI

    Copertura rosa:
        numero di giocatori già presenti in rosa compatibili
        con il ruolo, indipendentemente dalla fascia.

    Priorità:
    - FONDAMENTALE:
        massimo 2 giocatori in rosa
        E meno di 7 pari/superiori per fascia rimasti.
    - NECESSARIO:
        meno di 4 giocatori in rosa
        E meno di 10 pari/superiori per fascia rimasti.
    - FACOLTATIVO:
        tutti gli altri casi.

    Per i multiruolo viene scelta la priorità più alta.
    """

    gerarchia_fasce = {
        "NERO": 1,
        "ROSSO": 2,
        "BLU": 3,
        "VERDE": 4
    }

    fascia_candidato = fascia_iqr_giocatore(
        giocatore.get(
            "RM",
            ""
        ),
        giocatore.get(
            "FVM M"
        )
    )

    livello_fascia_candidato = gerarchia_fasce.get(
        fascia_candidato,
        1
    )

    ruoli_candidato = sorted(
        ruoli_giocatore(
            giocatore.get(
                "RM",
                ""
            )
        )
    )

    if not ruoli_candidato:

        ruolo_principale = primo_ruolo(
            giocatore.get(
                "RM",
                ""
            )
        ).upper()

        ruoli_candidato = (
            [ruolo_principale]
            if ruolo_principale
            else []
        )

    risultati_ruolo = []

    for ruolo in ruoli_candidato:

        ruolo = str(
            ruolo
        ).strip().upper()

        if not ruolo:
            continue

        # ----------------------------------------------------
        # 1. COPERTURA DELLA ROSA NEL RUOLO
        # ----------------------------------------------------

        compatibili_rosa = giocatori_compatibili(
            df_rosa,
            ruolo
        )

        numero_in_rosa = (
            len(
                compatibili_rosa
            )
            if compatibili_rosa is not None
            else 0
        )

        # ----------------------------------------------------
        # 2. GIOCATORI PARI O SUPERIORI PER FASCIA RIMASTI
        # ----------------------------------------------------

        compatibili_listone = giocatori_compatibili(
            df_listone,
            ruolo
        )

        disponibili_equivalenti = 0

        if (
            compatibili_listone is not None
            and not compatibili_listone.empty
        ):

            disponibili = (
                compatibili_listone[
                    compatibili_listone[
                        "Stato"
                    ]
                    .astype(str)
                    .str.upper()
                    == "DISPONIBILE"
                ]
                .copy()
            )

            if not disponibili.empty:

                disponibili[
                    "_fascia_priorita"
                ] = disponibili.apply(
                    lambda r:
                    fascia_iqr_giocatore(
                        r.get(
                            "RM",
                            ""
                        ),
                        r.get(
                            "FVM M"
                        )
                    ),
                    axis=1
                )

                disponibili[
                    "_livello_fascia_priorita"
                ] = disponibili[
                    "_fascia_priorita"
                ].map(
                    gerarchia_fasce
                ).fillna(
                    1
                )

                disponibili_equivalenti = int(
                    (
                        disponibili[
                            "_livello_fascia_priorita"
                        ]
                        >= livello_fascia_candidato
                    )
                    .sum()
                )

        # ----------------------------------------------------
        # 3. CLASSIFICAZIONE
        # ----------------------------------------------------

        if (
            numero_in_rosa <= 2
            and disponibili_equivalenti < 7
        ):

            etichetta = "ACQUISTO FONDAMENTALE"
            livello = 3

        elif (
            numero_in_rosa < 4
            and disponibili_equivalenti < 10
        ):

            etichetta = "ACQUISTO NECESSARIO"
            livello = 2

        else:

            etichetta = "ACQUISTO FACOLTATIVO"
            livello = 1

        risultati_ruolo.append({
            "Etichetta": etichetta,
            "Livello": livello,
            "Ruolo": ruolo,
            "Copertura": int(
                numero_in_rosa
            ),
            "Disponibili": int(
                disponibili_equivalenti
            ),
            "Fascia candidato": fascia_candidato
        })

    if not risultati_ruolo:

        return {
            "Etichetta": "ACQUISTO FACOLTATIVO",
            "Livello": 1,
            "Ruolo": "",
            "Copertura": 0,
            "Disponibili": 0,
            "Fascia candidato": fascia_candidato
        }

    # Priorità più alta. A parità scegliamo il ruolo
    # con meno alternative rimaste e minore copertura.
    migliore = sorted(
        risultati_ruolo,
        key=lambda x: (
            -x["Livello"],
            x["Disponibili"],
            x["Copertura"],
            x["Ruolo"]
        )
    )[0]

    return migliore

def stile_priorita_acquisto(
    etichetta
):
    """
    Colori della casella Priorità acquisto.
    """

    if etichetta == "ACQUISTO FONDAMENTALE":
        return (
            "#fee2e2",
            "#991b1b",
            "#ef4444"
        )

    if etichetta == "ACQUISTO NECESSARIO":
        return (
            "#ffedd5",
            "#9a3412",
            "#f97316"
        )

    return (
        "#dcfce7",
        "#166534",
        "#22c55e"
    )


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
# IQR - INDICE QUALITÀ ROSA
# ============================================================

def punteggio_qualita_giocatore(
    ruolo_mantra,
    valore_fvm_m
):
    """
    Punteggio individuale IQR basato sulle fasce colore FVM M.

    Fasce:
    - Verde = 100
    - Blu   = 70
    - Rosso = 40
    - Nero  = da 0 a 20 in funzione del FVM M

    FVM M = 1 vale sempre 0.
    Per doppi/tripli ruoli vale il primo ruolo Mantra.
    """

    ruolo = primo_ruolo(
        ruolo_mantra
    ).upper()

    soglie = SOGLIE_FVM_M.get(
        ruolo
    )

    if soglie is None:
        return 0.0

    try:
        valore = float(
            valore_fvm_m
        )
    except Exception:
        return 0.0

    if pd.isna(
        valore
    ):
        return 0.0

    verde, blu, rosso = soglie

    if valore <= 1:
        return 0.0

    if valore >= verde:
        return 100.0

    if valore >= blu:
        return 70.0

    if valore >= rosso:
        return 40.0

    # Fascia nera:
    # crescita progressiva da 0 (FVM M = 1)
    # a 20 immediatamente sotto la soglia rossa.
    if rosso <= 1:
        return 0.0

    punteggio_nero = (
        (valore - 1.0)
        / (float(rosso) - 1.0)
        * 20.0
    )

    return round(
        max(
            0.0,
            min(
                20.0,
                punteggio_nero
            )
        ),
        2
    )


def fascia_iqr_giocatore(
    ruolo_mantra,
    valore_fvm_m
):
    """
    Restituisce la fascia IQR del giocatore:
    VERDE / BLU / ROSSO / NERO.
    """

    ruolo = primo_ruolo(
        ruolo_mantra
    ).upper()

    soglie = SOGLIE_FVM_M.get(
        ruolo
    )

    if soglie is None:
        return "NERO"

    try:
        valore = float(
            valore_fvm_m
        )
    except Exception:
        return "NERO"

    if pd.isna(
        valore
    ):
        return "NERO"

    verde, blu, rosso = soglie

    if valore >= verde:
        return "VERDE"

    if valore >= blu:
        return "BLU"

    if valore >= rosso:
        return "ROSSO"

    return "NERO"


def descrizione_iqr(
    valore
):
    """
    Etichetta qualitativa dell'Indice Qualità Rosa.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        return "Rosa debole"

    if valore >= 95:
        return "Rosa eccezionale"

    if valore >= 85:
        return "Rosa eccellente"

    if valore >= 75:
        return "Rosa molto forte"

    if valore >= 60:
        return "Rosa buona"

    if valore >= 40:
        return "Rosa discreta"

    return "Rosa debole"


def calcola_iqr(
    df_rosa,
    df_listone=None,
    max_giocatori=MAX_GIOCATORI
):
    """
    IQR V2 - Indice Qualità Rosa.

    La formula ha tre passaggi:

    1) QUALITÀ BASE
       Ogni giocatore vale:
       Verde 100 / Blu 70 / Rosso 40 / Nero 0..20.
       Gli slot vuoti valgono 0.
       La qualità è calcolata su una rosa completa di 30 giocatori.

    2) DENSITÀ DI FASCE ALTE
       Premia una rosa che contiene un numero elevato di giocatori
       Verdi e Blu, con riferimenti realistici per una lega a 12:
       - 8 Verdi = obiettivo massimo della componente Verdi
       - 12 Verdi+Blu = obiettivo massimo della componente Top
       La densità pesa nella formula base per il 20%.

    3) BONUS OFFENSIVO
       I ruoli offensivi sono Pc, A, W, T e C.
       La presenza di molti Verdi/Blu offensivi chiude fino al 35%
       della distanza residua verso 100.
       Riferimenti:
       - 5 Verdi offensivi
       - 8 Verdi+Blu offensivi

    Proprietà:
    - 30 giocatori Verdi = 100%
    - 30 giocatori con FVM M = 1 = 0%
    - il 100% non viene raggiunto tramite il solo bonus offensivo:
      è necessario che la qualità base sia già 100.
    """

    if (
        df_rosa is None
        or df_rosa.empty
    ):
        return 0.0

    max_giocatori = max(
        1,
        int(
            max_giocatori
        )
    )

    totale_punti = 0.0

    numero_verdi = 0
    numero_blu = 0

    numero_verdi_offensivi = 0
    numero_blu_offensivi = 0

    RUOLI_OFFENSIVI_IQR = {
        "PC",
        "A",
        "W",
        "T",
        "C"
    }

    for _, giocatore in (
        df_rosa.iterrows()
    ):

        ruolo_mantra = giocatore.get(
            "RM",
            ""
        )

        valore_fvm_m = giocatore.get(
            "FVM M"
        )

        ruolo = primo_ruolo(
            ruolo_mantra
        ).upper()

        fascia = fascia_iqr_giocatore(
            ruolo_mantra,
            valore_fvm_m
        )

        totale_punti += (
            punteggio_qualita_giocatore(
                ruolo_mantra,
                valore_fvm_m
            )
        )

        if fascia == "VERDE":

            numero_verdi += 1

            if ruolo in RUOLI_OFFENSIVI_IQR:
                numero_verdi_offensivi += 1

        elif fascia == "BLU":

            numero_blu += 1

            if ruolo in RUOLI_OFFENSIVI_IQR:
                numero_blu_offensivi += 1

    # --------------------------------------------------------
    # 1) QUALITÀ MEDIA SU 30 SLOT
    # --------------------------------------------------------

    qualita_base = (
        totale_punti
        / (
            max_giocatori
            * 100.0
        )
        * 100.0
    )

    # --------------------------------------------------------
    # 2) DENSITÀ FASCE ALTE - LEGA A 12
    # --------------------------------------------------------

    quota_verdi = min(
        1.0,
        numero_verdi
        / 8.0
    )

    quota_top = min(
        1.0,
        (
            numero_verdi
            + numero_blu
        )
        / 12.0
    )

    densita_alta_qualita = (
        quota_verdi
        * 70.0
        + quota_top
        * 30.0
    )

    iqr_base = (
        qualita_base
        * 0.80
        + densita_alta_qualita
        * 0.20
    )

    # --------------------------------------------------------
    # 3) PREMIO OFFENSIVO
    # --------------------------------------------------------
    #
    # Il bonus non è una semplice somma di punti.
    # Chiude una parte della distanza tra l'IQR base e 100,
    # così:
    # - premia le rose con tanti top offensivi;
    # - non permette di superare 100;
    # - 30 Verdi restano esattamente 100.

    quota_verdi_offensivi = min(
        1.0,
        numero_verdi_offensivi
        / 5.0
    )

    quota_top_offensivi = min(
        1.0,
        (
            numero_verdi_offensivi
            + numero_blu_offensivi
        )
        / 8.0
    )

    forza_offensiva = (
        quota_verdi_offensivi
        * 70.0
        + quota_top_offensivi
        * 30.0
    )

    distanza_da_100 = max(
        0.0,
        100.0
        - iqr_base
    )

    bonus_offensivo = (
        distanza_da_100
        * 0.35
        * (
            forza_offensiva
            / 100.0
        )
    )

    iqr_finale = (
        iqr_base
        + bonus_offensivo
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                iqr_finale
            )
        ),
        1
    )




def colore_iqr(
    valore
):
    """
    Colore sintetico dell'indicatore IQR.
    Scala richiesta: NERO -> ROSSO -> BLU -> VERDE.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    if valore >= 85:
        return "#16a34a"

    if valore >= 60:
        return "#2563eb"

    if valore >= 40:
        return "#dc2626"

    return "#111827"


def genera_html_gauge_iqr(
    valore
):
    """
    Crea il tachimetro semicircolare IQR in puro SVG/HTML.
    """

    try:
        valore = float(
            valore
        )
    except Exception:
        valore = 0.0

    valore = max(
        0.0,
        min(
            100.0,
            valore
        )
    )

    cx = 120.0
    cy = 108.0
    r = 86.0

    segmenti = [
        (0.0, 40.0, "#111827"),
        (40.0, 60.0, "#dc2626"),
        (60.0, 85.0, "#2563eb"),
        (85.0, 100.0, "#16a34a")
    ]

    polilinee = []

    for inizio, fine, colore in segmenti:

        punti = []

        passi = 18

        for indice in range(
            passi + 1
        ):

            quota = (
                inizio
                + (
                    fine
                    - inizio
                )
                * indice
                / passi
            )

            angolo = (
                math.pi
                - quota
                / 100.0
                * math.pi
            )

            x = (
                cx
                + r
                * math.cos(
                    angolo
                )
            )

            y = (
                cy
                - r
                * math.sin(
                    angolo
                )
            )

            punti.append(
                f"{x:.1f},{y:.1f}"
            )

        polilinee.append(
            (
                f'<polyline points="{" ".join(punti)}" '
                f'fill="none" stroke="{colore}" '
                f'stroke-width="18" stroke-linecap="butt"/>'
            )
        )

    angolo_indicatore = (
        math.pi
        - valore
        / 100.0
        * math.pi
    )

    lunghezza = 66.0

    x2 = (
        cx
        + lunghezza
        * math.cos(
            angolo_indicatore
        )
    )

    y2 = (
        cy
        - lunghezza
        * math.sin(
            angolo_indicatore
        )
    )

    descrizione = html.escape(
        descrizione_iqr(
            valore
        )
    )

    colore_descrizione = (
        colore_iqr(
            valore
        )
    )

    return (
        '<div class="iqr-gauge-card">'
        '<div class="iqr-gauge-title">⭐ IQR</div>'
        '<svg viewBox="0 0 240 128" class="iqr-gauge-svg" '
        'role="img" aria-label="Indice Qualità Rosa">'
        + "".join(
            polilinee
        )
        + (
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#0f172a" stroke-width="5" '
            'stroke-linecap="round"/>'
        )
        + (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" '
            'fill="#0f172a"/>'
        )
        + '</svg>'
        + (
            f'<div class="iqr-gauge-value">{valore:.1f}%</div>'
        )
        + (
            f'<div class="iqr-gauge-description" '
            f'style="background:{colore_descrizione};">'
            f'{descrizione}</div>'
        )
        + '<div class="iqr-gauge-hint">Tocca / clicca per i dettagli</div>'
        + '</div>'
    )


def dettaglio_iqr_per_ruolo(
    df_rosa
):
    """
    Costruisce la tabella di dettaglio IQR ruolo per ruolo.
    Il ruolo di riferimento è sempre il primo ruolo Mantra.
    """

    colonne = [
        "Ruolo",
        "Giocatori",
        "Verdi",
        "Blu",
        "Rossi",
        "Neri",
        "FVM M medio",
        "Qualità media",
        "Offensivo"
    ]

    if (
        df_rosa is None
        or df_rosa.empty
    ):
        return pd.DataFrame(
            columns=colonne
        )

    ruoli_offensivi = {
        "PC",
        "A",
        "W",
        "T",
        "C"
    }

    righe = []

    for ruolo in SOGLIE_FVM_M.keys():

        selezione = []

        for _, giocatore in (
            df_rosa.iterrows()
        ):

            ruolo_giocatore = primo_ruolo(
                giocatore.get(
                    "RM",
                    ""
                )
            ).upper()

            if ruolo_giocatore == ruolo:
                selezione.append(
                    giocatore
                )

        if not selezione:
            continue

        verdi = 0
        blu = 0
        rossi = 0
        neri = 0
        valori_fvm = []
        punti = []

        for giocatore in selezione:

            fascia = fascia_iqr_giocatore(
                giocatore.get(
                    "RM",
                    ""
                ),
                giocatore.get(
                    "FVM M"
                )
            )

            if fascia == "VERDE":
                verdi += 1
            elif fascia == "BLU":
                blu += 1
            elif fascia == "ROSSO":
                rossi += 1
            else:
                neri += 1

            try:
                valore_fvm = float(
                    giocatore.get(
                        "FVM M"
                    )
                )

                if not pd.isna(
                    valore_fvm
                ):
                    valori_fvm.append(
                        valore_fvm
                    )

            except Exception:
                pass

            punti.append(
                punteggio_qualita_giocatore(
                    giocatore.get(
                        "RM",
                        ""
                    ),
                    giocatore.get(
                        "FVM M"
                    )
                )
            )

        media_fvm = (
            sum(
                valori_fvm
            )
            / len(
                valori_fvm
            )
            if valori_fvm
            else 0.0
        )

        qualita_media = (
            sum(
                punti
            )
            / len(
                punti
            )
            if punti
            else 0.0
        )

        righe.append({
            "Ruolo": ruolo,
            "Giocatori": len(
                selezione
            ),
            "Verdi": verdi,
            "Blu": blu,
            "Rossi": rossi,
            "Neri": neri,
            "FVM M medio": round(
                media_fvm,
                1
            ),
            "Qualità media": f"{qualita_media:.1f}%",
            "Offensivo": (
                "Sì"
                if ruolo in ruoli_offensivi
                else "No"
            )
        })

    return pd.DataFrame(
        righe,
        columns=colonne
    )


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
# BUDGET ASTA
# ============================================================

def leggi_budget_asta():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT valore
            FROM configurazione_app
            WHERE chiave = 'budget_asta'
        """)

        riga = cur.fetchone()

    finally:

        chiudi_connessione(
            conn
        )

    if not riga:

        return float(
            SOGLIA_BASE
        )

    try:

        return float(
            riga[0]
        )

    except Exception:

        return float(
            SOGLIA_BASE
        )


def salva_budget_asta(
    valore
):

    try:

        valore = round(
            max(
                0.0,
                float(
                    valore
                )
            ),
            2
        )

    except Exception:

        valore = float(
            SOGLIA_BASE
        )

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO configurazione_app (
                chiave,
                valore
            )
            VALUES (
                'budget_asta',
                ?
            )

            ON CONFLICT(chiave)
            DO UPDATE SET
                valore = excluded.valore
        """, (
            str(
                valore
            ),
        ))

        conn.commit()

    finally:

        chiudi_connessione(
            conn
        )

    return valore


def aggiorna_budget_da_widget():

    try:

        nuovo_budget = round(
            float(
                st.session_state.get(
                    "budget_asta_input",
                    SOGLIA_BASE
                )
            ),
            2
        )

    except Exception:

        nuovo_budget = float(
            SOGLIA_BASE
        )

    budget_corrente = round(
        float(
            st.session_state.get(
                "budget_asta_corrente",
                SOGLIA_BASE
            )
        ),
        2
    )

    if nuovo_budget == budget_corrente:
        return

    st.session_state[
        "budget_asta_corrente"
    ] = (
        salva_budget_asta(
            nuovo_budget
        )
    )


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

    # In Cloud la connessione viene mantenuta viva per tutta
    # la sessione: evita handshake e riconnessioni ripetute.
    if USA_DATABASE_CLOUD:
        return

    try:
        conn.close()
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
        CREATE TABLE IF NOT EXISTS configurazione_app (

            chiave TEXT PRIMARY KEY,

            valore TEXT
        )
    """)


    # La cronologia viene gestita direttamente in Python.
    # Rimuoviamo l'eventuale trigger creato dalle release precedenti:
    # su Turso/libsql può generare ValueError durante alcuni ripristini.
    cur.execute("""
        DROP TRIGGER IF EXISTS trg_operazioni_post_insert
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

        # Il DataFrame è già mantenuto coerente dalle operazioni.
        # Restituiamo il riferimento per evitare copie da 500+ righe
        # a ogni rerun; le funzioni che devono modificarlo usano .copy().
        return st.session_state[
            chiave
        ]

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
    df_corrente = carica_tutti_giocatori()

    giocatore_id_db = int(
        giocatore_id
    )

    riga = df_corrente[
        df_corrente["Id"]
        == giocatore_id_db
    ]

    if riga.empty:
        return

    precedente = riga.iloc[0]

    # Tutti i parametri vengono convertiti in tipi Python nativi.
    # È importante con Turso/libsql perché valori pandas/numpy
    # possono produrre ValueError in alcuni percorsi operativi.
    nome = str(
        precedente.get(
            "Nome",
            ""
        )
    )

    stato_prima = str(
        precedente.get(
            "Stato",
            ""
        )
    )

    prezzo_prima_raw = precedente.get(
        "Prezzo"
    )

    prezzo_prima = (
        None
        if pd.isna(
            prezzo_prima_raw
        )
        else float(
            prezzo_prima_raw
        )
    )

    tipo_db = str(
        tipo
    )

    nuovo_stato_db = str(
        nuovo_stato
    )

    nuovo_prezzo_db = (
        None
        if nuovo_prezzo is None
        or pd.isna(
            nuovo_prezzo
        )
        else float(
            nuovo_prezzo
        )
    )

    costo_svincolo_db = float(
        costo_svincolo
        or 0
    )

    conn = get_connection()
    cur = conn.cursor()

    try:

        # ------------------------------------------------------
        # 1. REGISTRA OPERAZIONE
        # ------------------------------------------------------

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
            tipo_db,
            giocatore_id_db,
            nome,
            stato_prima,
            prezzo_prima,
            nuovo_stato_db,
            nuovo_prezzo_db,
            costo_svincolo_db
        ))

        # lastrowid non è sempre affidabile allo stesso modo
        # tra sqlite3 e libsql: recuperiamo esplicitamente l'id.
        cur.execute(
            "SELECT last_insert_rowid()"
        )

        riga_id = cur.fetchone()

        operazione_id = (
            int(
                riga_id[0]
            )
            if riga_id
            and riga_id[0] is not None
            else 0
        )

        # ------------------------------------------------------
        # 2. EVENTUALE COSTO SVINCOLO
        # ------------------------------------------------------

        if costo_svincolo_db > 0:

            cur.execute("""
                INSERT INTO costi_svincoli (
                    operazione_id,
                    giocatore_id,
                    nome_giocatore,
                    importo
                )
                VALUES (?, ?, ?, ?)
            """, (
                operazione_id,
                giocatore_id_db,
                nome,
                costo_svincolo_db
            ))

        # ------------------------------------------------------
        # 3. AGGIORNA STATO GIOCATORE
        # ------------------------------------------------------

        cur.execute("""
            UPDATE giocatori

            SET
                stato = ?,
                prezzo_acquisto = ?

            WHERE id = ?
        """, (
            nuovo_stato_db,
            nuovo_prezzo_db,
            giocatore_id_db
        ))

        # ------------------------------------------------------
        # 4. CRONOLOGIA: CONSERVA SOLO LE ULTIME 10 OPERAZIONI
        # ------------------------------------------------------

        cur.execute("""
            DELETE FROM operazioni

            WHERE id NOT IN (
                SELECT id
                FROM operazioni
                ORDER BY id DESC
                LIMIT ?
            )
        """, (
            int(
                MAX_UNDO
            ),
        ))

        conn.commit()

    except Exception:

        try:
            conn.rollback()
        except Exception:
            pass

        raise

    finally:

        chiudi_connessione(
            conn
        )

    # ----------------------------------------------------------
    # AGGIORNAMENTO CACHE LOCALE
    # ----------------------------------------------------------

    maschera = (
        st.session_state[
            "_df_giocatori_sessione"
        ]["Id"]
        == giocatore_id_db
    )

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Stato"
    ] = nuovo_stato_db

    st.session_state[
        "_df_giocatori_sessione"
    ].loc[
        maschera,
        "Prezzo"
    ] = nuovo_prezzo_db

    aggiorna_cronologia_locale_dopo_operazione(
        operazione_id,
        tipo_db,
        giocatore_id_db,
        nome,
        stato_prima,
        prezzo_prima,
        nuovo_stato_db,
        nuovo_prezzo_db,
        costo_svincolo_db
    )

    if costo_svincolo_db > 0:

        st.session_state[
            "_costi_svincoli_sessione"
        ] = round(
            calcola_costi_svincoli()
            + costo_svincolo_db,
            2
        )

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

def carica_ultime_operazioni():

    chiave = "_ultime_operazioni_sessione"

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

    chiudi_connessione(
        conn
    )

    st.session_state[
        chiave
    ] = df.copy()

    return df


def aggiorna_cronologia_locale_dopo_operazione(
    operazione_id,
    tipo,
    giocatore_id,
    nome,
    stato_prima,
    prezzo_prima,
    stato_dopo,
    prezzo_dopo,
    costo_svincolo
):

    chiave = "_ultime_operazioni_sessione"

    colonne = [
        "Id",
        "Operazione",
        "GiocatoreId",
        "Giocatore",
        "StatoPrima",
        "PrezzoPrima",
        "StatoDopo",
        "PrezzoDopo",
        "CostoSvincolo",
        "Data"
    ]

    nuova = pd.DataFrame(
        [
            {
                "Id": int(
                    operazione_id
                    or 0
                ),
                "Operazione": tipo,
                "GiocatoreId": int(
                    giocatore_id
                ),
                "Giocatore": nome,
                "StatoPrima": stato_prima,
                "PrezzoPrima": prezzo_prima,
                "StatoDopo": stato_dopo,
                "PrezzoDopo": prezzo_dopo,
                "CostoSvincolo": float(
                    costo_svincolo
                    or 0
                ),
                "Data": datetime.now(
                    ZoneInfo(
                        "Europe/Rome"
                    )
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        ],
        columns=colonne
    )

    precedente = (
        st.session_state.get(
            chiave
        )
    )

    if (
        precedente is None
        or precedente.empty
    ):

        storico = nuova

    else:

        storico = pd.concat(
            [
                nuova,
                precedente
            ],
            ignore_index=True
        ).head(
            MAX_UNDO
        )

    st.session_state[
        chiave
    ] = storico

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

    # Rimuove localmente l'operazione appena annullata.
    storico = st.session_state.get(
        "_ultime_operazioni_sessione"
    )

    if (
        storico is not None
        and not storico.empty
    ):

        st.session_state[
            "_ultime_operazioni_sessione"
        ] = (
            storico[
                storico["Id"]
                != operazione_id
            ]
            .reset_index(
                drop=True
            )
        )

    if costo_svincolo > 0:

        st.session_state[
            "_costi_svincoli_sessione"
        ] = round(
            max(
                0.0,
                calcola_costi_svincoli()
                - costo_svincolo
            ),
            2
        )

    if "backup_cloud_bytes" in st.session_state:
        st.session_state.backup_cloud_bytes = None

    if "pdf_rosa_moduli" in st.session_state:
        st.session_state.pdf_rosa_moduli = None

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


def calcola_costi_svincoli():

    chiave = "_costi_svincoli_sessione"

    if chiave in st.session_state:

        return round(
            float(
                st.session_state[
                    chiave
                ]
                or 0
            ),
            2
        )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COALESCE(
                SUM(importo),
                0
            )

        FROM costi_svincoli
    """)

    riga = cur.fetchone()

    chiudi_connessione(
        conn
    )

    totale = round(
        float(
            (
                riga[0]
                if riga
                else 0
            )
            or 0
        ),
        2
    )

    st.session_state[
        chiave
    ] = totale

    return totale

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

    chiavi_sessione = [
        "backup_cloud_bytes",
        "pdf_rosa_moduli",
        "_df_giocatori_sessione",
        "_ultime_operazioni_sessione",
        "_costi_svincoli_sessione"
    ]

    for chiave in chiavi_sessione:

        if chiave in st.session_state:

            if chiave in (
                "backup_cloud_bytes",
                "pdf_rosa_moduli"
            ):

                st.session_state[
                    chiave
                ] = None

            else:

                del st.session_state[
                    chiave
                ]

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
        "SLOT DEBOLI",
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
                "Deboli"
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


def qualita_media_ruolo_slot(
    df_rosa,
    ruolo_posizione
):
    """
    Qualità media (0-100) dei giocatori compatibili con uno slot.

    Usa lo stesso punteggio individuale dell'IQR:
    Verde 100 / Blu 70 / Rosso 40 / Nero 0-20.
    Se non esistono giocatori compatibili, la qualità è 0%.
    """

    possibili = giocatori_compatibili(
        df_rosa,
        ruolo_posizione
    )

    if possibili.empty:
        return 0.0

    punteggi = []

    for _, giocatore in possibili.iterrows():

        punteggi.append(
            punteggio_qualita_giocatore(
                giocatore.get(
                    "RM",
                    ""
                ),
                giocatore.get(
                    "FVM M"
                )
            )
        )

    if not punteggi:
        return 0.0

    return round(
        sum(
            punteggi
        )
        / len(
            punteggi
        ),
        1
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

    Nuove definizioni:
    - SLOT SCOPERTO: slot con 2 o meno giocatori compatibili.
    - SLOT DEBOLE: slot che non raggiunge almeno 3 giocatori
      compatibili oppure non raggiunge almeno il 50% di qualità media.
      Gli slot allo 0% sono inclusi automaticamente tra i deboli.

    Il punteggio strategico considera:
    - copertura media;
    - penalità di profondità per gli slot scoperti;
    - penalità qualitativa per gli slot deboli.

    Penalità:
    - 6 punti per ogni slot scoperto;
    - 4 punti per ogni slot debole.
    """

    dati_slot = []

    for _, posizioni in MODULI[
        nome_modulo
    ]:

        for _, ruolo_slot in posizioni:

            numero, percentuale = (
                percentuale_copertura_ruolo(
                    df_rosa,
                    ruolo_slot
                )
            )

            qualita_media = (
                qualita_media_ruolo_slot(
                    df_rosa,
                    ruolo_slot
                )
            )

            dati_slot.append({
                "Ruolo": ruolo_slot,
                "Numero": int(
                    numero
                ),
                "Copertura": float(
                    percentuale
                ),
                "Qualita": float(
                    qualita_media
                )
            })

    if not dati_slot:

        return {
            "Modulo": nome_modulo,
            "Punteggio": 0.0,
            "Copertura media": 0.0,
            "Scoperti": 0,
            "Deboli": 0,
            "Ruoli deboli": "",
            "Al 100%": 0,
            "Totale slot": 0
        }

    copertura_media = (
        sum(
            s["Copertura"]
            for s in dati_slot
        )
        / len(
            dati_slot
        )
    )

    scoperti = sum(
        1
        for s in dati_slot
        if s["Numero"] <= 2
    )

    slot_deboli = [
        s
        for s in dati_slot
        if (
            s["Numero"] < 3
            or s["Qualita"] < 50
        )
    ]

    deboli = len(
        slot_deboli
    )

    ruoli_deboli = ", ".join(
        s["Ruolo"]
        for s in slot_deboli
    )

    al_100 = sum(
        1
        for s in dati_slot
        if s["Numero"] >= 4
    )

    penalita = (
        scoperti * 6
        + deboli * 4
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
        "Deboli": deboli,
        "Ruoli deboli": ruoli_deboli,
        "Al 100%": al_100,
        "Totale slot": len(
            dati_slot
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
            x["Deboli"],
            -x["Copertura media"],
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
# POPUP PRIORITÀ ACQUISTO
# ============================================================

@st.dialog(
    "Giocatori disponibili per ruolo",
    width="large"
)
def mostra_dettaglio_priorita_acquisto(
    giocatore,
    priorita,
    df_listone
):

    nome_giocatore = html.escape(
        str(
            giocatore.get(
                "Nome",
                ""
            )
        )
    )

    st.markdown(
        f"### {nome_giocatore}"
    )

    ruoli_candidato = sorted(
        ruoli_giocatore(
            giocatore.get(
                "RM",
                ""
            )
        ),
        key=lambda r: ORDINE_RUOLI.get(
            str(r).upper(),
            999
        )
    )

    if not ruoli_candidato:

        ruolo_principale = primo_ruolo(
            giocatore.get(
                "RM",
                ""
            )
        ).upper()

        if ruolo_principale:
            ruoli_candidato = [
                ruolo_principale
            ]

    if not ruoli_candidato:

        st.info(
            "Il giocatore selezionato non ha ruoli Mantra validi."
        )
        return

    st.caption(
        "Giocatori ancora disponibili, separati per ciascun ruolo "
        "Mantra del giocatore selezionato."
    )

    ordine_fasce = {
        "VERDE": 1,
        "BLU": 2,
        "ROSSO": 3,
        "NERO": 4
    }

    # Una colonna per ciascun ruolo: le tabelle vengono affiancate.
    colonne_ruolo = st.columns(
        len(
            ruoli_candidato
        ),
        gap="small"
    )

    for colonna, ruolo_riferimento in zip(
        colonne_ruolo,
        ruoli_candidato
    ):

        ruolo_riferimento = str(
            ruolo_riferimento
        ).strip().upper()

        with colonna:

            st.markdown(
                f"### {ruolo_riferimento}"
            )

            compatibili = giocatori_compatibili(
                df_listone,
                ruolo_riferimento
            )

            if (
                compatibili is None
                or compatibili.empty
            ):

                st.info(
                    "Nessun giocatore disponibile."
                )
                continue

            disponibili = (
                compatibili[
                    compatibili[
                        "Stato"
                    ]
                    .astype(str)
                    .str.upper()
                    == "DISPONIBILE"
                ]
                .copy()
            )

            if disponibili.empty:

                st.warning(
                    "Nessun giocatore disponibile."
                )
                continue

            # Manteniamo il criterio qualitativo per l'ordinamento,
            # ma non mostriamo più FVM e FASCIA nella tabella.
            disponibili[
                "_fascia"
            ] = disponibili.apply(
                lambda r:
                fascia_iqr_giocatore(
                    r.get(
                        "RM",
                        ""
                    ),
                    r.get(
                        "FVM M"
                    )
                ),
                axis=1
            )

            disponibili[
                "_ordine_fascia"
            ] = disponibili[
                "_fascia"
            ].map(
                ordine_fasce
            ).fillna(
                99
            )

            disponibili[
                "_fvm_m_num"
            ] = pd.to_numeric(
                disponibili[
                    "FVM M"
                ],
                errors="coerce"
            )

            disponibili = (
                disponibili
                .sort_values(
                    [
                        "_ordine_fascia",
                        "_fvm_m_num",
                        "Nome"
                    ],
                    ascending=[
                        True,
                        False,
                        True
                    ],
                    na_position="last"
                )
                .reset_index(
                    drop=True
                )
            )

            st.caption(
                f"{len(disponibili)} disponibili"
            )

            righe_html = []

            for _, riga in disponibili.iterrows():

                nome = html.escape(
                    str(
                        riga.get(
                            "Nome",
                            ""
                        )
                    )
                )

                squadra = html.escape(
                    str(
                        riga.get(
                            "Squadra",
                            ""
                        )
                    )
                )

                ruolo = html.escape(
                    str(
                        riga.get(
                            "RM",
                            ""
                        )
                    )
                )

                colore_nome = colore_fvm_mantra(
                    riga.get(
                        "RM",
                        ""
                    ),
                    riga.get(
                        "FVM M"
                    )
                )

                righe_html.append(
                    "<tr>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-weight:800;"
                    f"font-size:0.78rem;"
                    f"color:{colore_nome};'>"
                    f"{nome}</td>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-size:0.74rem;'>"
                    f"{squadra}</td>"
                    f"<td style='padding:5px 6px;"
                    f"border:1px solid #e5e7eb;"
                    f"font-size:0.74rem;"
                    f"text-align:center;'>"
                    f"{ruolo}</td>"
                    "</tr>"
                )

            tabella_html = (
                "<div style='overflow-x:auto;'>"
                "<table style='width:100%;"
                "border-collapse:collapse;"
                "table-layout:fixed;"
                "background:#ffffff;'>"
                "<colgroup>"
                "<col style='width:48%;'>"
                "<col style='width:32%;'>"
                "<col style='width:20%;'>"
                "</colgroup>"
                "<thead>"
                "<tr style='background:#071a2f;"
                "color:#ffffff;'>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:left;'>"
                "GIOCATORE</th>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:left;'>"
                "SQUADRA</th>"
                "<th style='padding:6px;"
                "border:1px solid #d1d5db;"
                "font-size:0.72rem;"
                "text-align:center;'>"
                "RUOLO</th>"
                "</tr>"
                "</thead>"
                "<tbody>"
                + "".join(
                    righe_html
                )
                + "</tbody>"
                "</table>"
                "</div>"
            )

            st.markdown(
                tabella_html,
                unsafe_allow_html=True
            )


# ============================================================
# POPUP IQR - INDICE QUALITÀ ROSA
# ============================================================

@st.dialog(
    "IQR - Indice Qualità Rosa",
    width="large"
)
def mostra_dettaglio_iqr(
    valore_iqr,
    df_rosa
):

    st.markdown(
        genera_html_gauge_iqr(
            valore_iqr
        ),
        unsafe_allow_html=True
    )

    st.markdown(
        "### Come viene calcolato l'IQR"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            "**1. Qualità della rosa**"
        )

        st.caption(
            "Ogni giocatore vale in base alla fascia FVM M "
            "del primo ruolo Mantra: Verde 100, Blu 70, "
            "Rosso 40, Nero 0–20. Gli slot vuoti valgono 0."
        )

    with c2:

        st.markdown(
            "**2. Densità fasce alte**"
        )

        st.caption(
            "Premia il numero di giocatori Verdi e Blu. "
            "Riferimenti calibrati per una lega a 12: "
            "8 Verdi e 12 Verdi+Blu."
        )

    with c3:

        st.markdown(
            "**3. Bonus ruoli offensivi**"
        )

        st.caption(
            "Premia la presenza di Verdi/Blu nei ruoli "
            "Pc, A, W, T e C. Riferimenti: "
            "5 Verdi offensivi e 8 Verdi+Blu offensivi."
        )

    st.markdown(
        "### Dettaglio qualità per ruolo"
    )

    dettaglio = (
        dettaglio_iqr_per_ruolo(
            df_rosa
        )
    )

    if dettaglio.empty:

        st.info(
            "La rosa è ancora vuota."
        )

    else:

        st.dataframe(
            dettaglio,
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        "### Scala qualitativa"
    )

    st.markdown(
        """
- **0–39%** — Rosa debole
- **40–59%** — Rosa discreta
- **60–74%** — Rosa buona
- **75–84%** — Rosa molto forte
- **85–94%** — Rosa eccellente
- **95–100%** — Rosa eccezionale
        """
    )

    st.info(
        "L'IQR è un indicatore sintetico pensato per una lega a 12: "
        "combina qualità complessiva, densità di fasce alte e "
        "forza dei ruoli offensivi. "
        "30 giocatori Verdi = 100%; "
        "30 giocatori con FVM M = 1 = 0%."
    )


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

if "budget_asta_corrente" not in st.session_state:

    st.session_state[
        "budget_asta_corrente"
    ] = (
        leggi_budget_asta()
    )

if "budget_asta_input" not in st.session_state:

    st.session_state[
        "budget_asta_input"
    ] = (
        st.session_state[
            "budget_asta_corrente"
        ]
    )

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

budget_asta = float(
    st.session_state.get(
        "budget_asta_corrente",
        SOGLIA_BASE
    )
)

budget_rimanente = round(
    budget_asta
    - spesa_effettiva,
    2
)


iqr = (
    calcola_iqr(
        df_rosa_globale,
        df_completo,
        MAX_GIOCATORI
    )
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
        '<div class="fanta-logo">''<img src="data:image/jpeg;base64,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" alt="FantaEleganza">''</div>'
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



st.markdown(
    """
    <style>

    div[class*="st-key-iqr_card_clickable"] {
        position: relative !important;
        min-height: 154px !important;
        border: 1px solid #dbe2ea;
        border-radius: 12px;
        background: #ffffff;
        padding: 6px 7px 7px 7px;
        overflow: hidden;
    }

    div[class*="st-key-iqr_card_clickable"]:hover {
        border-color: #2563eb;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.10);
    }

    div[class*="st-key-iqr_card_clickable"] .stButton {
        position: absolute !important;
        inset: 0 !important;
        z-index: 20 !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }

    div[class*="st-key-iqr_card_clickable"] .stButton > button {
        width: 100% !important;
        height: 100% !important;
        min-height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
        padding: 0 !important;
        border: none !important;
    }

    .iqr-gauge-card {
        text-align: center;
        width: 100%;
        pointer-events: none;
    }

    .iqr-gauge-title {
        font-size: 12px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: -7px;
    }

    .iqr-gauge-svg {
        width: 100%;
        max-width: 150px;
        height: 76px;
        display: block;
        margin: 0 auto -2px auto;
    }

    .iqr-gauge-value {
        font-size: 20px;
        line-height: 1;
        font-weight: 800;
        color: #0f172a;
        margin-top: -2px;
    }

    .iqr-gauge-description {
        display: inline-block;
        color: #ffffff;
        font-size: 9px;
        font-weight: 800;
        line-height: 1.1;
        padding: 4px 7px;
        border-radius: 6px;
        margin-top: 5px;
    }

    .iqr-gauge-hint {
        font-size: 7px;
        color: #64748b;
        margin-top: 4px;
    }

    @media (max-width: 850px) {

        div[class*="st-key-iqr_card_clickable"] {
            min-height: 142px !important;
            padding: 5px !important;
        }

        .iqr-gauge-svg {
            max-width: 135px;
            height: 68px;
        }

        .iqr-gauge-value {
            font-size: 18px;
        }

        .iqr-gauge-description {
            font-size: 8px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RIEPILOGO COMPATTO
# ============================================================

m1, m2, m3, m4, m5, m6, m7, m8 = (
    st.columns(8)
)

m1.metric(
    "💳 Soglia base",
    f"{formatta_crediti(SOGLIA_BASE)} €"
)

with m2:

    st.number_input(
        "💰 Budget",
        min_value=0.0,
        step=10.0,
        format="%.2f",
        key="budget_asta_input",
        on_change=aggiorna_budget_da_widget,
        help=(
            "Budget totale che hai deciso di destinare all'asta. "
            "Il valore viene salvato nel database Cloud e resta "
            "disponibile anche da altri dispositivi."
        )
    )

m3.metric(
    "💵 Budget rimanente",
    f"{formatta_crediti(budget_rimanente)} €",
    delta=(
        "Disponibile"
        if budget_rimanente >= 0
        else "Budget superato"
    ),
    delta_color=(
        "off"
        if budget_rimanente >= 0
        else "inverse"
    ),
    help=(
        "Budget impostato meno Spesa effettiva. "
        "La Spesa effettiva include la maggiorazione prevista "
        "oltre la soglia base."
    )
)

m4.metric(
    "🪙 Spesa effettiva",
    f"{formatta_crediti(spesa_effettiva)} €"
)

m5.metric(
    "⚡ Oltre soglia",
    f"{formatta_crediti(oltre_soglia)} €"
)

m6.metric(
    "👥 Giocatori",
    f"{numero_rosa}/{MAX_GIOCATORI}"
)

m7.metric(
    "🧤 Portieri",
    f"{numero_portieri}/{MIN_PORTIERI}"
)

with m8:

    with st.container(
        key="iqr_card_clickable"
    ):

        st.markdown(
            genera_html_gauge_iqr(
                iqr
            ),
            unsafe_allow_html=True
        )

        if st.button(
            "Apri dettaglio IQR",
            key="btn_apri_dettaglio_iqr",
            help="Apri il dettaglio dell'Indice Qualità Rosa"
        ):

            mostra_dettaglio_iqr(
                iqr,
                df_rosa_globale
            )


# ============================================================
# NAVBAR
# ============================================================

PAGINE = [
    ("🏠", "DASHBOARD"),
    ("☷", "LISTONE"),
    ("🔨", "ASTA"),
    ("👕", "ROSA"),
    ("▣", "MODULI"),
    ("🔴", "VENDUTI AD AVVERSARI")
]

st.markdown(
    '<div class="nav-title">Navigazione</div>',
    unsafe_allow_html=True
)

nav_cols = st.columns(6)

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

                numero_giocatori = len(
                    gruppo
                )

                righe.append({
                    "Ruolo":
                        ruolo,

                    "Giocatori":
                        numero_giocatori,

                    "Valore":
                        formatta_crediti(
                            gruppo[
                                "Prezzo"
                            ]
                            .fillna(0)
                            .sum()
                        )
                        if not gruppo.empty
                        else "0,00"
                })

            df_distribuzione = (
                pd.DataFrame(
                    righe
                )
            )

            def colora_riga_ruolo(
                riga
            ):

                numero = int(
                    riga[
                        "Giocatori"
                    ]
                )

                # 0-1: rosso
                if numero < 2:

                    colore = (
                        "background-color: #fee2e2; "
                        "color: #991b1b; "
                        "font-weight: 700;"
                    )

                # 3: giallo
                elif numero == 3:

                    colore = (
                        "background-color: #fef3c7; "
                        "color: #92400e; "
                        "font-weight: 700;"
                    )

                # 4 o più: verde
                elif numero >= 4:

                    colore = (
                        "background-color: #dcfce7; "
                        "color: #166534; "
                        "font-weight: 700;"
                    )

                # Esattamente 2: neutro
                else:

                    colore = ""

                return [
                    colore
                    for _ in riga.index
                ]

            st.dataframe(
                df_distribuzione.style.apply(
                    colora_riga_ruolo,
                    axis=1
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
                    f"**{migliore['Scoperti']}** "
                    f"— slot deboli "
                    f"**{migliore['Deboli']}**"
                    + (
                        f" ({migliore['Ruoli deboli']})"
                        if migliore[
                            "Ruoli deboli"
                        ]
                        else ""
                    )
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
                            "Deboli",
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

            foglio_tutti = None

            for nome_foglio in (
                excel.sheet_names
            ):

                if (
                    nome_foglio
                    .strip()
                    .upper()
                    == "TUTTI"
                ):

                    foglio_tutti = (
                        nome_foglio
                    )

                    break

            if foglio_tutti is None:

                st.error(
                    "Non trovo il foglio Tutti."
                )

            else:

                df_excel = pd.read_excel(
                    io.BytesIO(
                        contenuto
                    ),
                    sheet_name=(
                        foglio_tutti
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

    st.markdown(
        """
        <style>
        /* VERSIONE B - CONSOLE ASTA COMPATTA */
        div[data-testid="stNumberInput"] input {
            font-size:1.22rem !important;
            font-weight:800 !important;
            text-align:center !important;
            min-height:58px !important;
            border:2px solid #94a3b8 !important;
            border-radius:10px !important;
            background:#ffffff !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
            border:2px solid #94a3b8 !important;
            border-radius:10px !important;
            background:#ffffff !important;
            min-height:50px !important;
        }

        div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div,
        div[data-testid="stNumberInput"]:focus-within input {
            border-color:#071a2f !important;
            box-shadow:0 0 0 3px rgba(7,26,47,.10) !important;
        }

        /* STRISCIA OPERATIVA ASTA: stessa altezza reale per tutti i blocchi */
        div[class*="st-key-btn_acquista_"] .stButton,
        div[class*="st-key-btn_avversario_"] .stButton {
            height:76px !important;
        }

        div[class*="st-key-btn_acquista_"] .stButton > button,
        div[class*="st-key-btn_avversario_"] .stButton > button {
            min-height:76px !important;
            height:76px !important;
            width:100% !important;
            font-weight:900 !important;
            font-size:1rem !important;
            border-radius:8px !important;
            padding-top:0 !important;
            padding-bottom:0 !important;
        }

        /* OFFERTA: alza l'intero controllo, compresi +/- */
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInput"] [data-baseweb="input"],
        div[data-testid="stNumberInput"] [data-baseweb="base-input"] {
            min-height:76px !important;
            height:76px !important;
        }

        div[data-testid="stNumberInput"] input {
            min-height:76px !important;
            height:76px !important;
            font-size:1.22rem !important;
            font-weight:800 !important;
            text-align:center !important;
            border-radius:8px 0 0 8px !important;
            padding-top:0 !important;
            padding-bottom:0 !important;
        }

        div[data-testid="stNumberInput"] button {
            height:38px !important;
            min-height:38px !important;
        }

        /* Metriche: riferimento visivo per l'altezza della riga */
        div[data-testid="stMetric"] {
            min-height:76px !important;
            height:76px !important;
            padding:8px 12px !important;
            display:flex !important;
            flex-direction:column !important;
            justify-content:center !important;
            box-sizing:border-box !important;
        }

        @media (max-width:768px) {
            div[data-testid="stNumberInput"] input {
                font-size:1.08rem !important;
                min-height:52px !important;
            }

            div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
                min-height:46px !important;
            }

            div[class*="st-key-btn_acquista_"] .stButton > button,
            div[class*="st-key-btn_avversario_"] .stButton > button {
                min-height:68px !important;
                height:68px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    df = df_completo.copy()

    if df.empty:
        st.info("Prima devi caricare il listone.")

    else:
        disponibili = (
            df[
                df["Stato"] == "DISPONIBILE"
            ]
            .copy()
            .sort_values("Nome")
            .reset_index(drop=True)
        )

        if disponibili.empty:

            st.info(
                "Nessun giocatore disponibile."
            )

        else:

            opzioni_asta = (
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

            scelta = st.selectbox(
                "🔎 CERCA GIOCATORE / SQUADRA / RUOLO",
                options=opzioni_asta,
                index=None,
                placeholder=(
                    "Scrivi nome, squadra o ruolo…"
                ),
                key="search_select_asta"
            )

            if scelta is None:

                st.info(
                    "⌨️ Scrivi poche lettere: il giocatore viene proposto "
                    "subito. Puoi cercare anche per squadra o ruolo."
                )

            else:

                giocatore = (
                    disponibili.iloc[
                        opzioni_asta.index(
                            scelta
                        )
                    ]
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

                priorita_acquisto = (
                    valuta_priorita_acquisto(
                        giocatore,
                        df_rosa_globale,
                        df_completo
                    )
                )

                (
                    bg_priorita,
                    fg_priorita,
                    bordo_priorita
                ) = stile_priorita_acquisto(
                    priorita_acquisto[
                        "Etichetta"
                    ]
                )

                g1, g2, g3, g4, g5 = (
                    st.columns(
                        [
                            1.20,
                            0.95,
                            0.95,
                            0.75,
                            1.25
                        ]
                    )
                )

                with g1:

                    st.markdown(
                        f"""
                        <div class="asta-player-mobile-fix">
                            <div style="
                                font-size:0.875rem;
                                color:rgba(49,51,63,0.65);
                                margin-bottom:0.15rem;
                            ">
                                Giocatore
                            </div>
                            <div style="
                                font-size:1.35rem;
                                line-height:1.15;
                                font-weight:700;
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
                    giocatore["Squadra"]
                )

                g3.metric(
                    "Ruolo",
                    giocatore["RM"]
                )

                g4.metric(
                    "FVM",
                    giocatore["FVM"]
                )

                with g5:

                    dettaglio_priorita = (
                        f"Ruolo {priorita_acquisto['Ruolo']} · "
                        f"fascia {priorita_acquisto['Fascia candidato'].title()} · "
                        f"in rosa {priorita_acquisto['Copertura']} · "
                        f"rimasti {priorita_acquisto['Disponibili']}"
                    )

                    with st.container(
                        key=(
                            "priorita_click_"
                            f"{int(giocatore['Id'])}"
                        )
                    ):

                        st.markdown(
                            f"""
                            <div style="
                                min-height:72px;
                                border:2px solid {bordo_priorita};
                                border-radius:10px;
                                background:{bg_priorita};
                                padding:9px 10px;
                                display:flex;
                                flex-direction:column;
                                justify-content:center;
                                box-sizing:border-box;
                                cursor:pointer;
                            ">
                                <div style="
                                    font-size:0.78rem;
                                    color:#475569;
                                    margin-bottom:4px;
                                    font-weight:600;
                                ">
                                    Priorità acquisto
                                </div>
                                <div style="
                                    font-size:1.00rem;
                                    line-height:1.10;
                                    font-weight:800;
                                    color:{fg_priorita};
                                ">
                                    {html.escape(
                                        priorita_acquisto[
                                            "Etichetta"
                                        ]
                                    )}
                                </div>
                                <div style="
                                    font-size:0.66rem;
                                    line-height:1.15;
                                    color:#64748b;
                                    margin-top:4px;
                                ">
                                    {html.escape(
                                        dettaglio_priorita
                                    )}
                                </div>
                                <div style="
                                    font-size:0.62rem;
                                    line-height:1.1;
                                    color:#64748b;
                                    margin-top:5px;
                                    font-weight:600;
                                ">
                                    Giocatori disponibili
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "Giocatori disponibili",
                            key=(
                                "btn_priorita_"
                                f"{int(giocatore['Id'])}"
                            ),
                        ):

                            mostra_dettaglio_priorita_acquisto(
                                giocatore,
                                priorita_acquisto,
                                df_completo
                            )

                chiave_prezzo = (
                    "offerta_asta_"
                    f"{int(giocatore['Id'])}"
                )

                if chiave_prezzo not in st.session_state:
                    st.session_state[
                        chiave_prezzo
                    ] = 1.00

                c1, c2, c3, c4, c5 = (
                    st.columns(
                        [
                            1.15,
                            1.20,
                            1.20,
                            0.85,
                            0.85
                        ],
                        vertical_alignment="bottom"
                    )
                )

                with c1:

                    prezzo = st.number_input(
                        "Offerta",
                        min_value=0.10,
                        max_value=5000.00,
                        step=0.10,
                        format="%.2f",
                        key=chiave_prezzo,
                        label_visibility="collapsed"
                    )

                prezzo = round(
                    float(prezzo),
                    2
                )

                nuovo_valore = round(
                    valore_acquisti + prezzo,
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

                valido, motivo = (
                    verifica_acquisto_regole(
                        df_rosa_globale,
                        giocatore["RM"]
                    )
                )

                with c2:

                    if st.button(
                        "✅ ACQUISTA",
                        use_container_width=True,
                        type="primary",
                        disabled=(not valido),
                        key=(
                            "btn_acquista_"
                            f"{int(giocatore['Id'])}"
                        )
                    ):

                        esegui_operazione(
                            int(giocatore["Id"]),
                            "ACQUISTO",
                            "MIO",
                            prezzo,
                            0
                        )

                        st.rerun()

                with c3:

                    if st.button(
                        "🔴 VENDUTO AD AVVERSARIO",
                        use_container_width=True,
                        key=(
                            "btn_avversario_"
                            f"{int(giocatore['Id'])}"
                        )
                    ):

                        esegui_operazione(
                            int(giocatore["Id"]),
                            "VENDUTO AVVERSARIO",
                            "AVVERSARIO",
                            None,
                            0
                        )

                        st.rerun()

                with c4:

                    st.metric(
                        "Impatto effettivo",
                        f"{formatta_crediti(incremento)} €"
                    )

                with c5:

                    st.metric(
                        "Nuova spesa",
                        f"{formatta_crediti(nuova_spesa)} €"
                    )

                if not valido:

                    st.error(
                        "⛔ " + motivo
                    )



# ============================================================
# VENDUTI AD AVVERSARI
# ============================================================

elif sezione == "VENDUTI AD AVVERSARI":

    st.subheader("🔴 Venduti ad avversari")

    avversari = (
        df_completo[
            df_completo["Stato"] == "AVVERSARIO"
        ]
        .copy()
        .sort_values("Nome")
        .reset_index(drop=True)
    )

    if avversari.empty:

        st.info("Nessun giocatore venduto agli avversari.")

    else:

        st.caption(
            f"Giocatori venduti agli avversari: {len(avversari)}"
        )

        intestazione = st.columns(
            [4, 2, 2, 1, 0.8]
        )

        for col, titolo in zip(
            intestazione,
            ["Giocatore", "Squadra", "Ruolo", "FVM", "Ripristina"]
        ):
            col.markdown(f"**{titolo}**")

        for _, riga in avversari.iterrows():

            cols = st.columns(
                [4, 2, 2, 1, 0.8],
                vertical_alignment="center"
            )

            colore_nome = colore_fvm_mantra(
                riga.get("RM", ""),
                riga.get("FVM M")
            )

            cols[0].markdown(
                f"<span style='color:{colore_nome};font-weight:800;'>"
                f"{html.escape(str(riga['Nome']))}</span>",
                unsafe_allow_html=True
            )
            cols[1].write(riga["Squadra"])
            cols[2].write(riga["RM"])
            cols[3].write(riga["FVM"])

            with cols[4]:
                if st.button(
                    "↩️",
                    key=f"ripristina_{int(riga['Id'])}",
                    help="Rendi nuovamente disponibile",
                    use_container_width=True
                ):
                    conferma_ripristino_avversario(
                        int(riga["Id"]),
                        riga["Nome"]
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
            f"**{migliore['Scoperti']}** "
            f"— slot deboli "
            f"**{migliore['Deboli']}**"
            + (
                f" ({migliore['Ruoli deboli']})"
                if migliore[
                    "Ruoli deboli"
                ]
                else ""
            )
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
            f' · slot deboli: '
            f'{analisi_corrente["Deboli"]}'
            + (
                f' ({html.escape(analisi_corrente["Ruoli deboli"])})'
                if analisi_corrente[
                    "Ruoli deboli"
                ]
                else ""
            )
            + '</div>'
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
